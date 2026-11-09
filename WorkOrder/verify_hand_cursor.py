"""App-local pointer, fold disambiguation, scroll mode, scope and focus guards."""
import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PyQt6.QtCore import QEvent, QObject, QPointF, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QDialog, QListWidget, QMainWindow, QPushButton, QScrollArea, QVBoxLayout, QWidget
from app.input.hand_gestures import FoldGestures
from app.ui.hand_cursor import HandCursorController
from app.ui.theme import APP_STYLE, font_families

g = FoldGestures()
for t in (0., .12): assert g.feed(5, False, t, 'first') is None
for t in (.16, .26): assert g.feed(0, True, t, 'first') is None
assert g.advance(.72) == ('click', 'first')
assert g.feed(0, True, 1., 'held') is None
assert g.advance(2.) is None  # Held fist never repeats.
g.reset()
for t,c in ((0.,5),(.12,5),(.16,0),(.26,0),(.30,5),(.42,5),(.46,0)):
    assert g.feed(c,c==0,t,'anchor') is None
assert g.feed(0,True,.56,'anchor') == ('scroll','anchor')
assert g.scrolling and g.advance(2.) is None
g.reset()
assert g.feed(0,True,3.,'unarmed') is None
assert g.feed(0,True,4.,'unarmed') is None

app = QApplication([])
font_families(); app.setStyleSheet(APP_STYLE)
window = QMainWindow()
root = QWidget()
layout = QVBoxLayout(root)
button = QPushButton('Click target')
listing = QListWidget()
listing.addItems([f'Song {i}' for i in range(150)])
layout.addWidget(button); layout.addWidget(listing)
window.setCentralWidget(root); window.resize(800,600)
window.show(); window.activateWindow(); app.processEvents()
controller = HandCursorController(window)

class Source:
    sample = None
    def hand_sample(self): return self.sample

source = Source()
controller.attach(root, lambda: source)
controller.timer.stop()
assert controller._can_control()
clicks = []
button.clicked.connect(lambda: clicks.append(True))
clock = [0.]
cursor_before = QCursor.pos()

def feed(t, count, point=None, visible=True):
    clock[0] = t
    if point is None: point = QPointF(button.mapTo(root,button.rect().center()))
    source.sample = (t, dict(hand_visible=visible, finger_count=count,
        x=.15+.7*point.x()/(root.width()-1), y=.12+.76*point.y()/(root.height()-1),
        finger_states=dict.fromkeys(('thumb','index','middle','ring','pinky'), count!=0)))
    controller.poll()

with patch('app.ui.hand_cursor.time.monotonic',side_effect=lambda:clock[0]):
    for t,c in ((0.,5),(.12,5),(.16,0),(.26,0),(.72,0),(1.,0)):
        feed(t,c)
    assert len(clicks)==1
    assert controller.overlay.isVisible()
    assert controller._target_at(controller.position) is button  # Transparent overlay.
    controller._suspend()
    anchor=QPointF(listing.viewport().mapTo(root,listing.viewport().rect().center()))
    for t,c in ((2.,5),(2.12,5),(2.16,0),(2.26,0),(2.30,5),(2.42,5),(2.46,0),(2.56,0)):
        feed(t,c,anchor)
    assert controller.gestures.scrolling and len(clicks)==1
    assert controller._scroll_area is listing
    down=QPointF(anchor.x(),min(root.height()-2,anchor.y()+root.height()*.25))
    for i in range(20): feed(2.6+i*.05,5,down)
    assert listing.verticalScrollBar().value()>0
    app.processEvents()
    assert window.grab().save(str(Path(__file__).with_name('hand_cursor_preview.png')))
    for t,c in ((4.,5),(4.12,5),(4.16,0),(4.26,0),(4.30,5),(4.42,5),(4.46,0),(4.56,0)):
        feed(t,c,anchor)
    assert not controller.gestures.scrolling and len(clicks)==1
    # Tracking loss cancels a pending click; returning with a fist cannot arm.
    controller._suspend()
    for t,c in ((5.,5),(5.12,5),(5.16,0),(5.26,0)): feed(t,c)
    feed(5.3,0,visible=False)
    for t in (6.,6.2,6.8): feed(t,0)
    assert len(clicks)==1
    # Focus loss must cancel a pending click.
    for t,c in ((7.,5),(7.12,5),(7.16,0),(7.26,0)): feed(t,c)
    other=QWidget(); other.show(); other.activateWindow(); app.processEvents()
    assert not controller._can_control()
    feed(8.,0)
    assert len(clicks)==1 and not controller.overlay.isVisible()
    other.close(); window.activateWindow(); app.processEvents()
    modal=QDialog(window); modal.setWindowModality(Qt.WindowModality.ApplicationModal); modal.show(); app.processEvents()
    assert not controller._can_control()
    modal.close(); window.activateWindow(); app.processEvents()
    # ESC exits scroll mode and cancels gestures without consuming keyboard input.
    controller.gestures.scrolling=True
    QTest.keyClick(root,Qt.Key.Key_Escape)
    assert not controller.gestures.scrolling
    controller._click(QPointF(-10,-10))
    assert len(clicks)==1
    # A Qt hover handler can synchronously resize the page and cancel the pointer.
    class ResizeOnEnter(QObject):
        def eventFilter(self, watched, event):
            if event.type()==QEvent.Type.Enter:
                root.resize(root.width()-1,root.height()-1)
            return False
    controller._suspend()
    resize_filter=ResizeOnEnter(button)
    button.installEventFilter(resize_filter)
    feed(9.,5)
    assert controller.position is None  # poll must not draw/move a cancelled pointer.
    button.removeEventFilter(resize_filter)
assert QCursor.pos()==cursor_before  # No operating-system cursor movement.
controller.detach(); window.close()
print('PASS: one fold/one click; double fold suppresses click; scroll on/off and real list movement; stale/focus/modal/ESC guards; transparent circle; no OS cursor movement')

from app import config
config.USE_CAMERA=False; config.USE_MOCK_EMG=True
from app.ui.main_window import MainWindow
main=MainWindow(); app.processEvents()
assert main.hand_cursor.screen is main.centralWidget()
main.show_settings_screen(); app.processEvents()
assert main.hand_cursor.screen is main.centralWidget()
assert main.centralWidget().preview_source is not None
main.hand_cursor.timer.stop()
main.activateWindow(); app.processEvents()
screen=main.centralWidget()
combo=screen.camera_index_combo
screen.findChild(QScrollArea).ensureWidgetVisible(combo)
app.processEvents()
main.hand_cursor.position=QPointF(combo.mapTo(screen,combo.rect().center()))
main.hand_cursor._click(main.hand_cursor.position)
app.processEvents()
assert QApplication.activePopupWidget() is not None
with patch.object(QApplication, 'applicationState', return_value=Qt.ApplicationState.ApplicationInactive):
    assert not main.hand_cursor._can_control()
QTest.qWait(300)
view=combo.view()
target=view.model().index(2,0)
point=QPointF(screen.mapFromGlobal(view.viewport().mapToGlobal(view.visualRect(target).center())))
main.hand_cursor._click(point)
app.processEvents()
assert combo.currentIndex()==2
main.show_calibration_screen(); app.processEvents()
assert main.hand_cursor.screen is None
main.show_game_widget(); app.processEvents()
assert main.hand_cursor.screen is None
main.centralWidget().abort_game(); app.processEvents()
assert main.hand_cursor.screen is main.centralWidget()
main.close()
print('PASS: automatic main/settings attachment; shared camera preview; app-owned combo popup selection; disabled in calibration/game; page changes reset gestures')
