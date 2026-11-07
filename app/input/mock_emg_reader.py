from app import config


class MockEMGReader:
    def __init__(self, threshold: int | None = None):
        self.threshold = threshold if threshold is not None else config.EMG_THRESHOLD
        self.space_pressed = False

    def set_space_pressed(self, pressed: bool):
        self.space_pressed = pressed

    def read(self) -> tuple[float, bool]:
        value = max(700.0, float(self.threshold)) if self.space_pressed else 50.0
        return value, self.space_pressed and value >= self.threshold

    def close(self):
        pass
