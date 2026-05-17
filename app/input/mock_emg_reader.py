from app import config


class MockEMGReader:
    def __init__(self, threshold: int | None = None):
        self.threshold = threshold if threshold is not None else config.EMG_THRESHOLD
        self.space_pressed = False

    def set_space_pressed(self, pressed: bool):
        self.space_pressed = pressed

    def read(self) -> tuple[float, bool]:
        value = 700.0 if self.space_pressed else 120.0
        return value, value >= self.threshold

    def close(self):
        pass
