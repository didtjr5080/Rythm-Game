"""App-local hand pointer. No OS cursor movement or global input injection."""
import math
import time

from PyQt6 import sip
from PyQt6.QtCore import QEvent, QObject, QPoint, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QEnterEvent, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QAbstractScrollArea, QComboBox, QWidget

from app.input.hand_gestures import FoldGestures
from app.ui.theme import lab_font


def alive(widget):
    return widget is not None and not sip.isdeleted(widget)


class CursorRing(QWidget):
    def __init__(self, screen):
        super().__init__(screen)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.point = QPointF()
        self.scrolling = False
        self.pending = False
        self.hide()

    def move_ring(self, point, scrolling, pending=False):
        old = QRectF(self.point.x()-105, self.point.y()-28, 210, 58)
        self.point, self.scrolling = QPointF(point), scrolling
        self.pending = pending
        new = QRectF(point.x()-105, point.y()-28, 210, 58)
        self.update(old.united(new).toAlignedRect())
        self.show()
        self.raise_()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setFont(lab_font(9, True))
        color = QColor('#C4B5FD' if self.scrolling else '#FBBF24' if self.pending else '#6EE7B7')
        p.setBrush(QColor(color.red(), color.green(), color.blue(), 24))
        p.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 60), 7))
        p.drawEllipse(self.point, 18, 18)
        p.setPen(QPen(color, 2))
        p.drawEllipse(self.point, 16, 16)
        p.setBrush(color)
        p.drawEllipse(self.point, 2, 2)
        if self.scrolling:
            x = self.point.x()+24 if self.point.x()+92 < self.width() else self.point.x()-90
            p.drawText(QRectF(x, self.point.y()-10, 65, 20), 'SCROLL')


class HandCursorController(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.screen = self.overlay = None
        self._source = None
        self.gestures = FoldGestures()
        self.position = self._target = None
        self._hover = None
        self._stamp = None
        self._last_time = None
        self._scroll_area = None
        self._scroll_origin = self._hand_y = .5
        self._scroll_fraction = 0.
        self._dispatching = False
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.poll)
        QApplication.instance().installEventFilter(self)

    def attach(self, screen, source):
        self.detach()
        self.screen, self._source = screen, source
        self.overlay = CursorRing(screen)
        self.overlay.setGeometry(screen.rect())
        screen.installEventFilter(self)
        self.timer.start(16)

    def detach(self):
        self.timer.stop()
        self._suspend()
        if alive(self.screen): self.screen.removeEventFilter(self)
        if alive(self.overlay): self.overlay.deleteLater()
        self.screen = self.overlay = self._source = None

    def _suspend(self):
        self.gestures.reset()
        self.position = self._target = None
        self._stamp = self._last_time = None
        self._scroll_area = None
        self._scroll_fraction = 0.
        self._set_hover(None)
        if alive(self.overlay): self.overlay.hide()

    def _belongs(self, widget):
        while alive(widget):
            if widget is self.screen: return True
            widget = widget.parentWidget()
        return False

    def _can_control(self):
        popup = QApplication.activePopupWidget()
        return (alive(self.screen) and self.screen.isVisible()
                and QApplication.applicationState() == Qt.ApplicationState.ApplicationActive
                and QApplication.activeModalWidget() is None
                and (self.window.isActiveWindow() or self._belongs(popup)))

    def eventFilter(self, watched, event):
        if self.screen is None: return False
        if event.type() == QEvent.Type.Resize and watched is self.screen:
            self._suspend()
            if alive(self.overlay): self.overlay.setGeometry(self.screen.rect())
        if event.type() == QEvent.Type.ApplicationDeactivate:
            self._suspend()
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Escape:
            self._suspend()
        return False

    @staticmethod
    def _palm(hand):
        points = hand.get('landmarks')
        if points is not None and len(points) == 21:
            x = sum(points[i][0] for i in (0,5,9,13,17))/5
            y = sum(points[i][1] for i in (0,5,9,13,17))/5
        else:
            x, y = hand.get('x'), hand.get('y')
        if x is None or y is None or not math.isfinite(x) or not math.isfinite(y):
            return None
        return max(0., min(1., (x-.15)/.7)), max(0., min(1., (y-.12)/.76))

    def poll(self):
        if self._dispatching: return
        if not self._can_control():
            self._suspend()
            return
        source = self._source() if self._source is not None else None
        sample = source.hand_sample() if source is not None else None
        if sample is None or not sample[1].get('hand_visible'):
            self._suspend()
            return
        stamp, hand = sample
        palm = self._palm(hand)
        if palm is None:
            self._suspend()
            return
        now = time.monotonic()
        dt = min(.05, max(0., now-self._last_time)) if self._last_time is not None else 1/60
        self._last_time = now
        count = hand.get('finger_count')
        states = hand.get('finger_states') or {}
        fingers = ('index','middle','ring','pinky')
        closed = count == 0 or (all(k in states for k in fingers) and not any(states[k] for k in fingers))
        self._hand_y = palm[1]
        if self.position is None:
            self.position = QPointF(palm[0]*(self.screen.width()-1), palm[1]*(self.screen.height()-1))
        if not self.gestures.scrolling and count is not None and count >= 3:
            self._target = QPointF(palm[0]*(self.screen.width()-1), palm[1]*(self.screen.height()-1))
        if not self.gestures.scrolling and not self.gestures.waiting_for_second_fold and self._target is not None and not closed:
            alpha = 1-math.exp(-dt/.07)
            self.position += (self._target-self.position)*alpha
        action = None
        if stamp != self._stamp:
            self._stamp = stamp
            action = self.gestures.feed(count, closed, now, QPointF(self.position))
        else:
            action = self.gestures.advance(now)
        if action is not None:
            kind, point = action
            if kind == 'click':
                self._click(point)
                return
            self._scroll_area = self._find_scroll_area(self.position) if self.gestures.scrolling else None
            self._scroll_origin = self._hand_y
            self._scroll_fraction = 0.
        if self.gestures.scrolling:
            self._scroll(dt)
        else:
            self._move(self.position)
        if alive(self.overlay): self.overlay.move_ring(self.position, self.gestures.scrolling, self.gestures.waiting_for_second_fold)

    def _target_at(self, point):
        if not alive(self.screen) or not self.screen.rect().contains(point.toPoint()): return None
        global_point = self.screen.mapToGlobal(point.toPoint())
        popup = QApplication.activePopupWidget()
        if alive(popup):
            if not self._belongs(popup) or not popup.rect().contains(popup.mapFromGlobal(global_point)):
                return None
            return popup.childAt(popup.mapFromGlobal(global_point)) or popup
        return self.screen.childAt(point.toPoint()) or self.screen

    def _set_hover(self, target):
        if target is self._hover: return
        if alive(self._hover):
            self._hover.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, False)
            QApplication.sendEvent(self._hover, QEvent(QEvent.Type.Leave))
        self._hover = target
        if alive(target) and self.position is not None:
            global_point = self.screen.mapToGlobal(self.position.toPoint())
            local = QPointF(target.mapFromGlobal(global_point))
            target.setAttribute(Qt.WidgetAttribute.WA_UnderMouse, True)
            QApplication.sendEvent(target, QEnterEvent(local, QPointF(self.window.mapFromGlobal(global_point)), QPointF(global_point)))

    def _mouse(self, target, kind, point, button, buttons):
        global_point = self.screen.mapToGlobal(point.toPoint())
        local = QPointF(target.mapFromGlobal(global_point))
        QApplication.sendEvent(target, QMouseEvent(kind, local, QPointF(global_point), button, buttons, Qt.KeyboardModifier.NoModifier))

    def _move(self, point):
        target = self._target_at(point)
        self._set_hover(target)
        if alive(target):
            self._mouse(target, QEvent.Type.MouseMove, point, Qt.MouseButton.NoButton, Qt.MouseButton.NoButton)

    def _click(self, point):
        if not self._can_control(): return
        popup = QApplication.activePopupWidget()
        if alive(popup) and self._belongs(popup):
            global_point = self.screen.mapToGlobal(point.toPoint())
            if not popup.rect().contains(popup.mapFromGlobal(global_point)):
                popup.close()
                return
            # Combo popups use native mouse-grab state that virtual events do
            # not alter. Activate only an enabled row in this screen's popup.
            for combo in self.screen.findChildren(QComboBox):
                view = combo.view()
                if view.window() is not popup: continue
                local = view.viewport().mapFromGlobal(global_point)
                if not view.viewport().rect().contains(local): return
                index = view.indexAt(local)
                if index.isValid() and index.flags() & Qt.ItemFlag.ItemIsEnabled and index.flags() & Qt.ItemFlag.ItemIsSelectable:
                    combo.setCurrentIndex(index.row())
                    combo.activated.emit(index.row())
                    combo.textActivated.emit(combo.currentText())
                    combo.hidePopup()
                return
        target = self._target_at(point)
        if not alive(target) or not target.isEnabled(): return
        screen = self.screen
        self._dispatching = True
        try:
            target.setFocus(Qt.FocusReason.MouseFocusReason)
            self._mouse(target, QEvent.Type.MouseButtonPress, point, Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton)
            if alive(target) and self.screen is screen and self._can_control():
                self._mouse(target, QEvent.Type.MouseButtonRelease, point, Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton)
        finally:
            self._dispatching = False

    def _find_scroll_area(self, point):
        target = self._target_at(point)
        while alive(target) and self._belongs(target):
            if isinstance(target, QAbstractScrollArea): return target
            target = target.parentWidget()
        return next((area for area in self.screen.findChildren(QAbstractScrollArea)
                     if area.isVisible() and area.verticalScrollBar().maximum()>0), None)

    def _scroll(self, dt):
        if not alive(self._scroll_area): return
        displacement = self._hand_y-self._scroll_origin
        if abs(displacement)<.04:
            self._scroll_fraction = 0.
            return
        rate = math.copysign(min(1., (abs(displacement)-.04)/.16)*12, displacement)
        self._scroll_fraction += rate*dt
        steps = int(self._scroll_fraction)
        if steps:
            self._scroll_fraction -= steps
            bar = self._scroll_area.verticalScrollBar()
            bar.setValue(bar.value()+steps*max(1,bar.singleStep()))
