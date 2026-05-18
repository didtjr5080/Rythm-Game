import re

from app import config
from app.input.mock_emg_reader import MockEMGReader


class SerialEMGReader:
    def __init__(self, port: str = "COM3", baudrate: int = 9600, threshold: int | None = None):
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

    @staticmethod
    def _extract_value(line: str) -> float | None:
        filtered_match = re.search(r"filtered\s*:\s*(-?\d+)", line, re.IGNORECASE)
        if filtered_match:
            return float(filtered_match.group(1))

        numbers = re.findall(r"-?\d+", line)
        if not numbers:
            return None
        return float(numbers[-1])

    def read(self) -> tuple[float, bool]:
        if self.serial is None:
            return self.fallback.read()
        try:
            line = self.serial.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                return 0.0, False
            value = self._extract_value(line)
            if value is None:
                return 0.0, False
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


if __name__ == "__main__":
    reader = SerialEMGReader()
    print("EMG reader test started. Press Ctrl+C to stop.")
    try:
        while True:
            value, activated = reader.read()
            print(f"EMG value: {value:.2f} | activated: {activated}")
    except KeyboardInterrupt:
        print("EMG reader test stopped.")
    finally:
        reader.close()

