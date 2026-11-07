"""Shared OpenCV camera connection for all desktop screens."""
import sys


class CameraSource:
    def __init__(self, settings, enabled=True):
        self.capture = None
        self.cv2 = None
        self.pending_frame = None
        self.status = 'CAMERA DISABLED'
        self.error = ''
        self.index = int(settings.get('camera_index', 0))
        if not enabled or not settings.get('camera_enabled', True):
            return
        try:
            import cv2
            self.cv2 = cv2
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY] if sys.platform == 'win32' else [cv2.CAP_ANY]
            width, height = map(int, settings.get('camera_resolution', '1280x720').split('x'))
            for backend in backends:
                capture = cv2.VideoCapture(self.index, backend)
                if not capture.isOpened():
                    capture.release()
                    continue
                capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                capture.set(cv2.CAP_PROP_FPS, 30)
                capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                ok, frame = capture.read()
                if ok and frame is not None:
                    self.capture = capture
                    self.pending_frame = frame
                    h, w = frame.shape[:2]
                    self.status = f'LIVE CAMERA {self.index} / {w}x{h}'
                    return
                capture.release()
            self.status = f'CAMERA {self.index} UNAVAILABLE'
            self.error = 'Check the selected device, close other camera apps, and enable Windows camera access for desktop apps.'
        except Exception as exc:
            self.status = f'CAMERA ERROR / {exc}'

    def read(self):
        if self.pending_frame is not None:
            frame, self.pending_frame = self.pending_frame, None
            return frame
        if self.capture is None:
            return None
        try:
            ok, frame = self.capture.read()
            if ok and frame is not None:
                h, w = frame.shape[:2]
                self.status = f'LIVE CAMERA {self.index} / {w}x{h}'
                return frame
            self.status = f'CAMERA {self.index} / FRAME READ FAILED'
        except Exception as exc:
            self.status = f'CAMERA READ ERROR / {exc}'
        return None

    def release(self):
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.pending_frame = None


def rgb_pixmap(rgb):
    """Copy numpy pixels so Qt never holds a dangling camera frame buffer."""
    from PyQt6.QtGui import QImage, QPixmap
    if rgb is None:
        return None
    height, width = rgb.shape[:2]
    image = QImage(rgb.data, width, height, rgb.strides[0], QImage.Format.Format_RGB888)
    return QPixmap.fromImage(image.copy())


def draw_camera_frame(painter, target, pixmap):
    """Fit the full frame; return the exact image bounds for landmark alignment."""
    from PyQt6.QtCore import QRectF
    ratio = min(target.width()/pixmap.width(), target.height()/pixmap.height())
    width, height = pixmap.width()*ratio, pixmap.height()*ratio
    fitted = QRectF(target.center().x()-width/2, target.center().y()-height/2, width, height)
    painter.drawPixmap(fitted, pixmap, QRectF(pixmap.rect()))
    return fitted
