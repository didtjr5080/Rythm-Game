"""Hand-controlled result buttons/history with shared native camera ownership."""
import os
import sys
import time
import json
import tempfile
from pathlib import Path
from unittest.mock import patch,PropertyMock

os.environ['QT_QPA_PLATFORM']='offscreen'
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PyQt6.QtCore import QPointF,Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication,QPushButton,QListWidgetItem
from app import config
config.USE_CAMERA=True;config.USE_MOCK_EMG=True;config.SAVE_SESSION_LOG=False
from app.ui.main_window import MainWindow
from app.ui.result_screen import ResultScreen
from app.ui.start_screen import StartScreen
from app.ui.game_widget import GameWidget
from app.ui.results_browser_screen import ResultsBrowserScreen
from app.ui.theme import APP_STYLE,font_families
from app.i18n import tr

created=[]
class Worker:
    capture=None;_thread=None;last_error=None;error='';status='FAKE';diagnostic_summary='FAKE';backend_is_mediapipe=True
    def __init__(self,settings,enabled=True):self.closes=0;created.append(self)
    def set_flip(self,flip):self.flip=flip
    def read(self):return None
    def track(self,frame):return dict(hand_visible=False,frame=None)
    def hand_sample(self):return None
    def close(self):self.closes+=1

app=QApplication([]);font_families();app.setStyleSheet(APP_STYLE)
with tempfile.TemporaryDirectory() as folder,patch.object(ResultsBrowserScreen,'results_dir',new_callable=PropertyMock,return_value=Path(folder)),patch('app.input.video_session.LiveVideoWorker',Worker),patch.object(ResultScreen,'_save_result',lambda self:setattr(self,'result_path',Path('hand-result-test.json'))):
    window=MainWindow();window.activateWindow();QTest.qWait(30)
    worker=window.centralWidget().bio.camera_source._worker
    def hand_click(text=None, point=None):
        screen=window.centralWidget();cursor=window.hand_cursor
        cursor.timer.stop();cursor._suspend()
        QApplication.setActiveWindow(window)
        if point is None:
            button=next(b for b in screen.findChildren(QPushButton) if b.text()==text)
            point=QPointF(button.mapTo(screen,button.rect().center()))
        assert screen.rect().contains(point.toPoint())
        class Source:
            def hand_sample(self):return self.sample
        source=Source();cursor._source=lambda:source
        base=time.monotonic();clock=[base]
        with patch('app.ui.hand_cursor.time.monotonic',side_effect=lambda:clock[0]):
            for delta,count in ((0.,5),(.12,5),(.16,0),(.26,0),(.72,0)):
                clock[0]=base+delta
                source.sample=(clock[0],dict(hand_visible=True,finger_count=count,
                    x=.15+.7*point.x()/(screen.width()-1),y=.12+.76*point.y()/(screen.height()-1),
                    finger_states=dict.fromkeys(('thumb','index','middle','ring','pinky'),count!=0)))
                cursor.poll()
        assert window.centralWidget() is screen  # Click delivery must finish first.
        QTest.qWait(40)

    window.show_game_widget();QTest.qWait(30)
    assert window.hand_cursor.screen is None
    for _ in range(3):
        game=window.centralWidget();game.timer.stop();game.finish_game();QTest.qWait(30)
        result=window.centralWidget()
        assert isinstance(result,ResultScreen)
        assert window.hand_cursor.screen is result
        assert window._navigation_video._worker is worker
        hand_click('Play Again')
        assert isinstance(window.centralWidget(),GameWidget)
        assert window.hand_cursor.screen is None
        assert window.centralWidget().video_worker._worker is worker
    window.centralWidget().timer.stop();window.centralWidget().finish_game();QTest.qWait(30)
    hand_click('Back to Start')
    assert isinstance(window.centralWidget(),StartScreen)
    window.show_results_browser_screen();QTest.qWait(30)
    browser=window.centralWidget()
    assert isinstance(browser,ResultsBrowserScreen) and window.hand_cursor.screen is browser
    assert window._navigation_video._worker is worker
    hand_click(tr('refresh',browser.language))
    hand_click(tr('refresh',browser.language))
    record=Path(folder)/'session.json'
    record.write_text(json.dumps(dict(score=1234,accuracy=96.8)))
    browser.result_list.blockSignals(True)
    browser.result_list.clear()
    for i in range(200):
        item=QListWidgetItem(f'Session {i}')
        item.setData(Qt.ItemDataRole.UserRole,str(record))
        browser.result_list.addItem(item)
    browser.result_list.blockSignals(False)
    QTest.qWait(20)
    cursor=window.hand_cursor;cursor.timer.stop()
    cursor.position=QPointF(browser.result_list.mapTo(browser,browser.result_list.rect().center()))
    cursor.gestures.scrolling=True;cursor._scroll_area=browser.result_list
    cursor._scroll_origin=.5;cursor._hand_y=.8
    for _ in range(20):cursor._scroll(.05)
    assert browser.result_list.verticalScrollBar().value()>0
    viewport=browser.result_list.viewport()
    index=browser.result_list.indexAt(viewport.rect().center())
    point=QPointF(viewport.mapTo(browser,viewport.rect().center()))
    hand_click(point=point)
    assert browser.result_list.currentRow()==index.row() and browser.detail_grid.count()>1
    hand_click(tr('refresh',browser.language))
    assert browser.result_list.count()==0 and browser.empty_label.isVisible()
    hand_click(tr('back',browser.language))
    assert isinstance(window.centralWidget(),StartScreen)
    assert len(created)==1 and worker.closes==0
    window.close();assert worker.closes==1
print('PASS: fold clicks on Play Again/Back to Start/history Back; result/history pointer scope; real history scrolling; disabled in game; one shared camera throughout; final release')
