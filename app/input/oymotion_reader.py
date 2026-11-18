"""Official USB dongle SDK on a worker; GUI consumes all-channel activity snapshots."""
import ctypes as C
import re
import threading
import time
from collections import deque
from serial.tools.list_ports import comports

from app.input.oymotion_activity import OYMotionActivity
from app.input.oymotion_sdk import OYMotionSDK


class OYMotionReader:
    def __init__(self, port='auto', threshold=0., device_id='', **unused):
        if port != 'auto' and not re.fullmatch(r'COM[1-9][0-9]*', port, re.I):
            raise ValueError('Choose Auto or a Windows COM port for the OYMotion dongle.')
        self.port = self.requested_port = port
        self.device_id = device_id
        self.connected_identity = ''
        self.threshold = threshold
        self.release_threshold = None
        self.status = 'OYMOTION USB / STARTING 8CH 12BIT 500HZ'
        self.error = None
        self.verified = self.connected = self._configured = False
        self.board_name = 'OYMotion'
        self._last_sample = 0.
        self.samples = []
        self.raw_value = self.last_value = 0.
        self.channel_rms = (0.,)*8
        self.sample_count = self.invalid_packets = 0
        self.processor = OYMotionActivity()
        self._pending = deque(maxlen=5000)
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._device = self._connecting = None
        self._found = {}
        self._scan_active = False
        self._next_scan = 0.
        self._thread = threading.Thread(target=self._run, name='oymotion-usb-emg', daemon=True)
        self._thread.start()

    @property
    def signal_fresh(self):
        return (self.connected and self._configured and not self._stop.is_set()
                and self._last_sample > 0 and time.monotonic()-self._last_sample < .15)

    def fail(self, exc):
        self.error = str(exc)
        self.status = 'OYMOTION ERROR / ' + str(exc)
        self._stop.set()

    def _run(self):
        sdk = None
        try:
            if self.port == 'auto':
                ports = [p.device for p in comports() if p.vid == 0x0403 and p.pid == 0x6001]
                if len(ports) == 1:
                    self.port = ports[0]
            sdk = self.sdk = OYMotionSDK(self)
            self._config_callback = sdk.result_type(self._config_done)
            self._switch_callback = sdk.result_type(self._switch_done)
            sdk.open(0 if self.port == 'auto' else int(self.port[3:]))
            self._scan_active = True
            self.status = 'OYMOTION USB / SCANNING FOR ARMBAND'
            while not self._stop.is_set():
                result = sdk.dll.hub_run(20)
                if result not in (0, 7):
                    raise RuntimeError(f'SDK polling failed: {result}')
                if not self._scan_active and self._device is None and self._connecting is None and time.monotonic() >= self._next_scan:
                    self._found.clear()
                    result = sdk.dll.hub_start_scan()
                    self._scan_active = result == 0
                    self._next_scan = time.monotonic()+1
                self._stop.wait(.001)
        except Exception as exc:
            self.fail(exc)
        finally:
            if sdk is not None:
                handle = self._device or self._connecting
                if handle is not None:
                    sdk.dll.device_enable_data_notification(handle, 0)
                    sdk.dll.device_disconnect(handle)
                sdk.close()
            self.connected = False

    def on_found(self, handle):
        try:
            name = self.sdk.text(handle)
            address = self.sdk.text(handle, 'address')
            if self.device_id.startswith('oymotion:') and self.device_id != 'oymotion:'+address:
                return
            self._found[handle] = (name, address)
            if self._scan_active:
                self.sdk.dll.hub_stop_scan()
        except Exception as exc:
            self.fail(exc)

    def on_scan_finished(self):
        self._scan_active = False
        self._next_scan = time.monotonic()+1
        if self._stop.is_set() or self._device is not None or self._connecting is not None:
            return
        for handle in self._found:
            if self.sdk.dll.device_connect(handle) == 0:
                self._connecting = handle
                self.status = 'OYMOTION USB / CONNECTING ARMBAND'
                break

    def on_connected(self, handle):
        try:
            self._device, self._connecting = handle, None
            self.connected = True
            name, address = self._found.get(handle, ('OYMotion', ''))
            self.connected_identity = 'oymotion:'+address
            self.board_name = name
            self.status = 'OYMOTION / CONFIGURING 8CH 12BIT 500HZ'
            self.sdk.check(self.sdk.dll.device_enable_data_notification(handle, 0), 'pause data')
            self.sdk.check(self.sdk.dll.device_set_emg_config(
                handle, 500, 0xFF, 128, 12, self._config_callback), 'set 500Hz/12bit/all channels')
        except Exception as exc:
            self.fail(exc)

    def _config_done(self, handle, result):
        try:
            self.sdk.check(result, '500Hz/12bit configuration acknowledgement')
            self.sdk.check(self.sdk.dll.device_set_data_switch(handle, 0x80, self._switch_callback), 'raw data switch')
        except Exception as exc:
            self.fail(exc)

    def _switch_done(self, handle, result):
        try:
            self.sdk.check(result, 'raw data switch acknowledgement')
            self.sdk.check(self.sdk.dll.device_enable_data_notification(handle, 1), 'start raw data')
            self._configured = self.verified = True
            self.status = 'OYMOTION / 8CH 12BIT 500HZ / WAITING FOR RAW DATA'
        except Exception as exc:
            self.fail(exc)

    def on_disconnected(self, handle, reason):
        if handle not in (self._device, self._connecting):
            return
        self.connected = self._configured = self.verified = False
        self._device = self._connecting = None
        self._last_sample = 0.
        with self._lock:
            self.processor = OYMotionActivity()
            self._pending.clear()
        self.status = 'OYMOTION / DISCONNECTED / SCANNING AGAIN'
        self._next_scan = time.monotonic()+1

    def on_data(self, handle, data_type, length, pointer):
        if handle != self._device or data_type != 8 or not self._configured or not pointer:
            return
        if length <= 0 or length > 4096 or length % 16:
            self.invalid_packets += 1
            return
        try:
            payload = C.string_at(pointer, length)  # Copy before SDK reuses the callback buffer.
            with self._lock:
                self._pending.extend(self.processor.feed(payload))
                self.channel_rms = self.processor.channel_rms
                self.sample_count = self.processor.sample_count
                self._last_sample = time.monotonic()
            self.status = 'OYMOTION / 8CH 12BIT 500HZ / ALL-CHANNEL AC RMS'
        except ValueError:
            self.invalid_packets += 1

    def read(self):
        with self._lock:
            self.samples = list(self._pending)
            self._pending.clear()
            self.last_value = self.raw_value = self.processor.activity
        return self.last_value, False  # Game uses its 3-second baseline, not a legacy ON/OFF flag.

    def set_thresholds(self, threshold, release=None):
        self.threshold, self.release_threshold = threshold, release

    def set_space_pressed(self, pressed):
        pass

    def close(self):
        self._stop.set()
        self._thread.join(timeout=3)
