"""Keep one filtered EMG stream alive across calibration, menus and gameplay."""
import time
from collections import deque

from PyQt6.QtCore import QObject, QTimer

from app import config
from app.input.emg_reader import SerialEMGReader
from app.input.mock_emg_reader import MockEMGReader
from app.input.emg_factory import create_emg_reader


class EMGSession(QObject):
    def __init__(self, parent=None, serial_factory=None):
        super().__init__(parent)
        self.serial_factory = serial_factory
        self.reader = None
        self.key = None
        self.value, self.active = 0., False
        self.sequence = 0
        self.samples = deque(maxlen=5000)
        self.timer = QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.poll)

    def acquire(self, settings, use_mock_emg=None):
        mock = (config.USE_MOCK_EMG or settings['emg_input_mode'] == 'mock') if use_mock_emg is None else use_mock_emg
        key = (mock, settings['emg_port'], settings['emg_baudrate'],
               settings['emg_device_id'], settings['emg_signal'], settings.get('emg_backend', 'legacy'))
        failed = self.reader is not None and bool(getattr(self.reader, 'error', None))
        # Saving a discovered USB identity must not reopen the already matching port.
        same_connected_device = (self.reader is not None and not failed and not mock and self.key is not None
            and not self.key[0] and getattr(self.reader, 'connected', getattr(self.reader, 'serial', None) is not None)
            and key[5] == self.key[5]
            and (key[5] == 'oymotion' or (key[2] == self.key[2] and key[4] == self.key[4]))
            and (key[1] == 'auto' or key[1] == self.reader.port)
            and (not key[3] or key[3] == self.reader.connected_identity))
        if same_connected_device:
            self.key = key
            self.reader.requested_port = settings['emg_port']
            self.reader.device_id = settings['emg_device_id']
        if self.reader is None or key != self.key or failed:
            self.shutdown()
            self.key = key
            self.reader = MockEMGReader(settings['emg_threshold']) if mock else create_emg_reader(
                settings, serial_factory=self.serial_factory)
            self.poll()
            self.timer.start()
        lease = EMGLease(self, self.reader)
        lease.set_thresholds(settings['emg_threshold'], settings['emg_release_threshold'])
        return lease

    def poll(self):
        if self.reader is None:
            return
        try:
            self.value, self.active = self.reader.read()
            for value in getattr(self.reader, 'samples', [self.value] if isinstance(self.reader, MockEMGReader) else []):
                self.sequence += 1
                self.samples.append((self.sequence, value))
        except Exception:
            self.value, self.active = 0., False

    def shutdown(self):
        self.timer.stop()
        if self.reader is not None:
            self.reader.close()
        self.reader = self.key = None
        self.value, self.active = 0., False
        self.samples.clear()


class EMGLease:
    def __init__(self, session, reader):
        self.session = session
        self.reader = reader
        self.closed = False
        self.sequence = session.sequence
        self.samples = []

    def __getattr__(self, name):
        return getattr(self.reader, name)

    @property
    def is_serial(self):
        return not isinstance(self.reader, MockEMGReader)

    @property
    def signal_fresh(self):
        if self.closed or self.reader is not self.session.reader:
            return False
        if hasattr(self.reader, 'signal_fresh'):
            return self.reader.signal_fresh
        return not self.is_serial or (self.reader.serial is not None
                                      and time.monotonic() - self.reader._last_sample < .15)

    @property
    def threshold(self):
        return self.reader.threshold

    @threshold.setter
    def threshold(self, value):
        self.set_thresholds(value, getattr(self.reader, 'release_threshold', None))

    def set_thresholds(self, value, release=None):
        if (self.reader.threshold == value
                and getattr(self.reader, 'release_threshold', None) == release):
            return
        if hasattr(self.reader, 'set_thresholds'):
            self.reader.set_thresholds(value, release)
        else:
            self.reader.threshold = value
            self.reader.release_threshold = release
        self.session.active = False

    def read(self):
        if self.closed or self.reader is not self.session.reader:
            self.samples = []
            return 0., False
        self.samples = [value for seq, value in self.session.samples if seq > self.sequence]
        self.sequence = self.session.sequence
        return self.session.value, bool(self.session.active and self.signal_fresh)

    def set_space_pressed(self, pressed):
        self.reader.set_space_pressed(pressed)
        if not self.is_serial:
            self.session.poll()

    def close(self):
        self.closed = True
