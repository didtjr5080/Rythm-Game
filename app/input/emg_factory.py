"""Select the explicitly configured hardware backend; never reinterpret its bytes."""
from app.input.emg_reader import SerialEMGReader
from app.input.oymotion_reader import OYMotionReader


def create_emg_reader(settings, threshold=None, serial_factory=None):
    factory = serial_factory or (OYMotionReader if settings.get('emg_backend') == 'oymotion' else SerialEMGReader)
    return factory(port=settings['emg_port'], baudrate=settings['emg_baudrate'],
                   threshold=settings['emg_threshold'] if threshold is None else threshold,
                   device_id=settings['emg_device_id'], signal=settings['emg_signal'],
                   release_threshold=settings['emg_release_threshold'])
