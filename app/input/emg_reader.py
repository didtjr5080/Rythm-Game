import re
import time

from app import config
from app.input.mock_emg_reader import MockEMGReader


class SerialEMGReader:
    def __init__(self, port: str | None = None, baudrate: int | None = None, threshold: int | None = None):
        self.port = port if port is not None else config.EMG_PORT
        self.baudrate = baudrate if baudrate is not None else config.EMG_BAUDRATE
        self.threshold = threshold if threshold is not None else config.EMG_THRESHOLD
        self.serial = None
        self.fallback = MockEMGReader(self.threshold)
        self.last_value = 0.0
        self.activated_until = 0.0
        try:
            import serial

            if self.port is None:
                self.port = self._find_serial_port(serial)
            if self.port is None:
                print("No EMG serial port found. Falling back to MockEMGReader.")
                return
            self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=0.05)
            time.sleep(0.2)
            self.serial.reset_input_buffer()
        except ImportError:
            print("pyserial is not installed. Falling back to MockEMGReader.")
        except Exception as exc:
            print(f"Could not open EMG serial port {self.port}: {exc}. Falling back to MockEMGReader.")

    def set_space_pressed(self, pressed: bool):
        self.fallback.set_space_pressed(pressed)

    @staticmethod
    def _find_serial_port(_serial_module) -> str | None:
        try:
            from serial.tools import list_ports

            ports = list(list_ports.comports())
        except Exception as exc:
            print(f"Could not list EMG serial ports: {exc}")
            return None
        if not ports:
            return None
        preferred = [
            port
            for port in ports
            if any(keyword in port.description.lower() for keyword in ("usb", "serial", "arduino", "ch340"))
        ]
        selected = preferred[0] if preferred else ports[0]
        print(f"Auto-selected EMG serial port {selected.device}: {selected.description}")
        return selected.device

    @staticmethod
    def _extract_value(line: str) -> float | None:
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

    def read(self) -> tuple[float, bool]:
        if self.serial is None:
            return self.fallback.read()
        try:
            lines = []
            line = self.serial.readline().decode("utf-8", errors="ignore").strip()
            if line:
                lines.append(line)
            while self.serial.in_waiting:
                line = self.serial.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    lines.append(line)

            value = None
            for line in reversed(lines):
                value = self._extract_value(line)
                if value is not None:
                    break
            if value is None:
                return self.last_value, time.monotonic() <= self.activated_until

            self.last_value = value
            if value >= self.threshold:
                self.activated_until = time.monotonic() + (config.EMG_INPUT_HOLD_MS / 1000)
            return value, time.monotonic() <= self.activated_until
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

