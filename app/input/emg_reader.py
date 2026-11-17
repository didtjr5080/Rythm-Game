import math
import re
import time
import serial
from app import config
from app.input.emg_devices import discover_emg_devices
from app.input.emg_processing import ActivityFilter


class SerialEMGReader:
    def __init__(self, port=None, baudrate=None, threshold=None, device_id='', signal='envelope', release_threshold=None):
        self.requested_port = port or config.EMG_PORT or 'auto'
        self.port = None
        self.connected_identity = ""
        self.device_id = device_id or ''
        self.signal = signal
        self.baudrate = baudrate or config.EMG_BAUDRATE
        self.threshold = config.EMG_THRESHOLD if threshold is None else threshold
        self.release_threshold = release_threshold
        self.serial = None
        self._armed = False
        self._low_samples = 0
        self._high_samples = 0
        self._active = False
        self.last_value = 0.0
        self.activity_filter = ActivityFilter()
        self.samples = []
        self.raw_value = 0.0
        self.envelope_value = 0.0
        self.unfiltered_value = 0.0
        self.bypass_available = False
        self.status = 'SEARCHING FOR EMG'
        self.error = None
        self.verified = False
        self.board_name = ''
        self.firmware_version = 0
        self._buffer = b''
        self._last_sample = 0.0
        self._opened_at = 0.0
        self._next_search = 0.0
        self._queue = []
        self._closed = False
        self._connect()

    def set_space_pressed(self, pressed):
        pass  # Keyboard simulation is available only in explicit mock mode.

    @property
    def release_level(self):
        if self.release_threshold is not None and 0 <= self.release_threshold <= 1023:
            return self.release_threshold
        return self.threshold*.6

    @property
    def falling_activation(self):
        return self.release_level > self.threshold

    def set_thresholds(self, threshold, release=None):
        self.threshold = threshold
        self.release_threshold = release
        self._armed = self._active = False
        self._low_samples = self._high_samples = 0

    def _connect(self):
        now = time.monotonic()
        if self._closed or now < self._next_search:
            return
        self._next_search = now + 1.0
        try:
            if not self._queue:
                devices = discover_emg_devices()
                if self.requested_port == 'auto':
                    devices = [d for d in devices if d['candidate']]
                    devices.sort(key=lambda d: d['identity'] != self.device_id if self.device_id else False)
                elif self.device_id:
                    # Follow a USB serial identity when Windows assigns a new COM number.
                    devices = [d for d in devices if d['identity'] == self.device_id]
                else:
                    devices = [d for d in devices if d['port'] == self.requested_port]
                self._queue = devices
            if not self._queue:
                self.status = 'NO EMG DEVICE / INPUT DISABLED'
                return
            device = self._queue.pop(0)
            self.serial = serial.Serial(device['port'], self.baudrate, timeout=0, write_timeout=.1)
            self.port = device['port']
            self.connected_identity = device['identity']
            self._opened_at = now
            self._buffer = b''
            self._last_sample = 0.0
            self.verified = False
            self.error = None
            self.status = f'{self.port} / WAITING FOR EMG FIRMWARE'
            self.serial.write(b'EMG?\n')
        except Exception as exc:
            self.error = str(exc)
            self._disconnect(f'EMG CONNECTION FAILED / {exc}')

    def _disconnect(self, status):
        if self.serial is not None:
            try: self.serial.close()
            except Exception: pass
        self.serial = None
        self.verified = False
        self.board_name = ''
        self.firmware_version = 0
        self.last_value = self.raw_value = self.envelope_value = 0.0
        self.unfiltered_value = 0.0
        self.bypass_available = False
        self._buffer = b''
        self._armed = self._active = False
        self._low_samples = self._high_samples = 0
        self.activity_filter = ActivityFilter()
        self.status = status

    @staticmethod
    def parse_packet(line):
        match = re.fullmatch(r'EMG1 raw:(\d{1,4}) filtered:(\d{1,4}) seq:(\d+)', line.strip())
        if not match:
            return None
        raw, envelope, sequence = map(int, match.groups())
        if raw > 1023 or envelope > 1023:
            return None
        return raw, envelope, sequence

    @staticmethod
    def _extract_value(line: str) -> float | None:
        if line.startswith(('EMG_DEVICE:', 'EMG1')): return None
        leading_match = re.match(r"\s*(-?\d+(?:\.\d+)?)", line)
        if leading_match:
            return float(leading_match.group(1))

        labeled_patterns = (
            r"filtered\s*:\s*(-?\d+(?:\.\d+)?)",
            r"activityRaw\s*:\s*(-?\d+(?:\.\d+)?)",
            r"activity_mV\s*:\s*(-?\d+(?:\.\d+)?)",
            r"raw\s*:\s*(-?\d+(?:\.\d+)?)",
            r"avgRaw\s*:\s*(-?\d+(?:\.\d+)?)",
        )
        for pattern in labeled_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return float(match.group(1))

        numbers = re.findall(r"-?\d+(?:\.\d+)?", line)
        if not numbers:
            return None
        return float(numbers[0])

    def read(self):
        self.samples = []
        now = time.monotonic()
        if self._last_sample and now-self._last_sample >= .15:
            self._armed = self._active = False
            self._low_samples = self._high_samples = 0
            self.activity_filter = ActivityFilter()
        if self.serial is None:
            self._connect()
            return 0.0, False
        try:
            count = min(self.serial.in_waiting, 4096)
            if count:
                self._buffer += self.serial.read(count)
            if len(self._buffer) > 8192:
                self._buffer = b''
            lines = self._buffer.split(b'\n')
            self._buffer = lines.pop()
            for raw_line in lines:
                line = raw_line.decode('ascii',errors='ignore').strip()
                identity=re.fullmatch(r'EMG_DEVICE:(NANO_A0|ESP8266_A0|ESP32_GPIO34):([12])',line)
                if identity:
                    self.verified = True
                    self.board_name=identity.group(1)
                    self.firmware_version=int(identity.group(2))
                    continue
                packet = self.parse_packet(line)
                bypass = re.fullmatch(r'EMG1_BYPASS rms:(\d{1,4}) seq:(\d+)', line)
                if bypass:
                    level = int(bypass.group(1))
                    if level > 1023:
                        continue
                    self.unfiltered_value = level
                    self.bypass_available = True
                    if self.signal != 'unfiltered':
                        continue
                    value = level
                elif packet is not None:
                    self.raw_value, self.envelope_value, _ = packet
                    self.verified = True
                    if self.signal == 'unfiltered':
                        self.status = f'{self.port} / WAITING FOR NO-BANDPASS DATA / COMPARISON FIRMWARE REQUIRED'
                        continue
                    value = self.raw_value if self.signal == 'raw' else self.envelope_value
                elif self.requested_port != 'auto' and self.signal != 'unfiltered':
                    value = self._extract_value(line)
                    if value is None: continue
                    self.raw_value = self.envelope_value = value
                else:
                    continue
                try:
                    value = self.activity_filter.update(float(value))
                except ValueError:
                    self._disconnect('INVALID EMG SAMPLE / INPUT DISABLED')
                    self.samples = []
                    return 0.0, False
                self.samples.append(value)
                self.last_value = value
                self._last_sample = now
                self.status = f'{self.port} / '+((self.board_name or 'EMG')+' CONNECTED' if self.verified else 'LEGACY SERIAL DATA')
                if self.board_name == 'ESP8266_A0':
                    self.status += (' / SZH-GJD001 NO BANDPASS / DC + RMS' if self.signal == 'unfiltered'
                                    else ' / SZH-GJD001 60-100Hz RMS' if self.firmware_version == 2
                                    else ' / LEGACY FILTER: FIRMWARE UPDATE REQUIRED')
                # Require rest before each contraction; reject isolated noise peaks.
                diagnostic_raw = self.board_name == 'ESP8266_A0' and self.firmware_version == 2 and self.signal == 'raw'
                if diagnostic_raw:
                    self.status += ' / RAW DIAGNOSTIC ONLY: SELECT FILTERED ACTIVITY'
                if diagnostic_raw or not math.isfinite(value) or self.threshold <= 0:
                    self._armed = self._active = False
                    self._low_samples = self._high_samples = 0
                elif (value > self.release_level if self.falling_activation else value < self.release_level):
                    self._low_samples += 1
                    self._high_samples = 0
                    self._active = False
                    if self._low_samples >= 4:
                        self._armed = True
                elif (value <= self.threshold if self.falling_activation else value >= self.threshold):
                    self._low_samples = 0
                    self._high_samples += 1
                    if self._armed and self._high_samples >= 2:
                        self._active = True
                        self._armed = False
                else:
                    self._low_samples = self._high_samples = 0
            if not self._last_sample and now-self._opened_at > 3.5:
                self._disconnect(f'{self.port} / '+('NO BANDPASS DATA: UPDATE COMPARISON FIRMWARE' if self.signal == 'unfiltered' else 'NO COMPATIBLE EMG DATA'))
                return 0.0, False
            if self._last_sample and now-self._last_sample > 1.0:
                self._disconnect(f'{self.port} / EMG SIGNAL LOST / RECONNECTING')
                return 0.0, False
            return self.last_value, self._active and now-self._last_sample < .15
        except Exception as exc:
            self.error = str(exc)
            self._disconnect(f'EMG DISCONNECTED / {exc}')
            return 0.0, False

    def close(self):
        self._closed = True
        self._disconnect('EMG CLOSED')
