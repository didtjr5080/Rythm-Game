from app import config
from app.input.mock_emg_reader import MockEMGReader


class SerialEMGReader:
    def __init__(self, port: str = "COM3", baudrate: int = 115200, threshold: int | None = None):
        self.port = port
        self.baudrate = baudrate
        self.threshold = threshold if threshold is not None else config.EMG_THRESHOLD
        self.serial = None
        self.fallback = MockEMGReader(self.threshold)
        try:
            import serial

            self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0.01)
        except ImportError:
            print("pyserial is not installed. Falling back to MockEMGReader.")
        except Exception as exc:
            print(f"Could not open EMG serial port {self.port}: {exc}. Falling back to MockEMGReader.")

    def set_space_pressed(self, pressed: bool):
        self.fallback.set_space_pressed(pressed)

    def read(self) -> tuple[float, bool]:
        if self.serial is None:
            return self.fallback.read()
        try:
            line = self.serial.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                return 0.0, False
            value = float(line)
            return value, value >= self.threshold
        except Exception as exc:
            print(f"EMG read failed: {exc}. Using mock value for this frame.")
            return self.fallback.read()

    def close(self):
        try:
            if self.serial is not None:
                self.serial.close()
        except Exception:
            pass

