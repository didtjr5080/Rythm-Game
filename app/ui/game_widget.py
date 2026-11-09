import time
import math
from collections import deque

from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap, QLinearGradient, QPolygonF, QPainterPath
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget

from app import config
from app.analytics.game_metrics import calculate_game_metrics
from app.analytics.session_logger import SessionLogger
from app.audio.audio_player import AudioPlayer
from app.game.rhythm_game_engine import RhythmGameEngine
from app.i18n import tr
from app.input.input_fusion import GameInputState, InputFusion
from app.settings import load_settings
from app.input.camera import draw_camera_frame
from app.input.live_video import open_live_video


from app.ui.theme import (draw_aurora_background, draw_frosted_glass_card, draw_crystal_note,
    draw_circular_gauge, draw_hand_skeleton_overlay, draw_waveform, text, finger_summary)

LANE_NAMES = [str(i+1) for i in range(config.LANE_COUNT)]


class GameWidget(QWidget):
    def __init__(self, main_window, notes_path: str | None = None, song_path: str | None = None):
        super().__init__()
        self.main_window = main_window
        self.song_path = song_path
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings = load_settings()
        self.language = self.settings["language"]
        self.engine = RhythmGameEngine.from_json_file(notes_path) if notes_path else RhythmGameEngine()
        self.video_worker = open_live_video(self.main_window, self.settings, enabled=config.USE_CAMERA)
        self.input_fusion = InputFusion(
            use_camera=config.USE_CAMERA and self.settings["camera_enabled"],
            emg_threshold=int(self.settings["emg_threshold"]),
            camera_flip=bool(self.settings["camera_flip"]),
            hand_tracker=self.video_worker if config.USE_CAMERA and self.settings['camera_enabled'] else None,
        )
        self.session_logger = SessionLogger()
        self.audio_player = AudioPlayer(self.song_path, volume=self.settings["music_volume"])
        self.start_time = time.monotonic()
        self.current_input = GameInputState(None, 0.0, False, False, None, None, None, time.time(), None, None, None)
        self.ar_camera = False
        self.raw_history = deque(maxlen=120)
        self.filtered_history = deque(maxlen=120)
        self.ripples = []
        self.previous_activation = False
        self.camera_pixmap = None
        self.camera_debug_pixmap = None
        self.camera_flip = bool(self.settings["camera_flip"])
        self.manual_lane: int | None = None
        self.input_delays_ms: list[float] = []
        self.result_flash: str | None = None
        self.result_flash_time_ms = -9999
        self.finished = False
        self.cv2 = None
        self.capture = None
        self.back_button = QPushButton(tr("back", self.language), self)
        self.back_button.setObjectName("danger")
        self.back_button.clicked.connect(self.abort_game)
        self.back_button.setFixedSize(96, 38)
        self._open_camera()
        self.audio_player.play()
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(max(1, int(1000 / config.FPS)))

    def _open_camera(self):
        import cv2
        self.camera_source = self.video_worker
        self.capture = None
        self.cv2 = cv2

    def _read_camera_frame(self):
        return self.camera_source.read()

    def _update_camera_pixmap(self, frame):
        frame_key = (id(frame), self.camera_flip)
        if frame is not None and getattr(self, '_camera_frame_key', None) == frame_key:
            return
        self._camera_frame_key = frame_key
        self._camera_frame_reference = frame
        if frame is None or self.cv2 is None:
            self.camera_pixmap = None
            self.camera_debug_pixmap = None
            return
        try:
            if self.camera_flip:
                frame = self.cv2.flip(frame, 1)
            rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            image = QImage(rgb.data, width, height, channels * width, QImage.Format.Format_RGB888)
            self.camera_pixmap = QPixmap.fromImage(image.copy())
            self.camera_debug_pixmap = None
        except Exception:
            self.camera_pixmap = None
            self.camera_debug_pixmap = None

    def _playback_time_ms(self):
        if self.song_path and not self.audio_player.error:
            return self.audio_player.position_ms
        return int((time.monotonic()-self.start_time)*1000)

    def _should_finish(self, current_time_ms):
        if self.song_path and not self.audio_player.error:
            return self.audio_player.finished
        return self.engine.is_finished(current_time_ms)

    def game_loop(self):
        current_time_ms = self._playback_time_ms()
        raw_frame = self._read_camera_frame()
        input_state, _tracked_frame = self.input_fusion.read(raw_frame)
        if not input_state.hand_visible and self.manual_lane is not None:
            input_state.lane = self.manual_lane
            input_state.hand_visible = True
            input_state.hand_x = (self.manual_lane + 0.5) / config.LANE_COUNT
            input_state.hand_y = 0.5
        self.current_input = input_state
        self._update_camera_pixmap(raw_frame)

        self.raw_history.append(self.input_fusion.raw_emg_value)
        self.filtered_history.append(self.input_fusion.filtered_emg_value)
        if input_state.emg_activated and not self.previous_activation:
            self.ripples.append((current_time_ms, input_state.lane if input_state.lane is not None else config.LANE_COUNT//2))
        self.previous_activation = input_state.emg_activated
        self.ripples = [(t,l) for t,l in self.ripples if current_time_ms-t<800]
        if self.song_path and self.audio_player.loading:
            self.update()
            return
        result = self.engine.update(input_state, current_time_ms)
        note_index = self.engine.last_judged_note_index
        if result in {"PERFECT", "GOOD"} and 0 <= note_index < len(self.engine.notes):
            delay = current_time_ms - self.engine.notes[note_index].hit_time_ms
            self.input_delays_ms.append(delay)
            self.input_fusion.last_timing_error_ms = delay
            self.ripples.append((current_time_ms, self.engine.notes[note_index].lane))
        if result:
            self.result_flash = result
            self.result_flash_time_ms = current_time_ms
        self.session_logger.log(current_time_ms, input_state, note_index, result)

        if self._should_finish(current_time_ms):
            self.finish_game()
            return
        self.update()

    def finish_game(self):
        if self.finished:
            return
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
        self.camera_source.release()
        self.input_fusion.close()
        session_paths = self.session_logger.save() if config.SAVE_SESSION_LOG else None
        metrics = calculate_game_metrics(self.engine.score_state, self.session_logger.rows, self.input_delays_ms)
        self.main_window.show_result_screen(metrics, session_paths=session_paths)

    def abort_game(self):
        if self.finished:
            return
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
        self.camera_source.release()
        self.input_fusion.close()
        self.main_window.show_start_screen()

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus(Qt.FocusReason.OtherFocusReason)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.back_button.move(self.width() - self.back_button.width() - 18, 16)

    def eventFilter(self, watched, event):
        if self.finished:
            return False
        if event.type() in (QEvent.Type.ApplicationDeactivate, QEvent.Type.WindowDeactivate):
            self.input_fusion.set_space_pressed(False)
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease) and event.isAutoRepeat():
            return event.key() in self._handled_keys()
        if event.type() == QEvent.Type.KeyPress:
            self._handle_key(event.key(), True)
            return event.key() in self._handled_keys()
        if event.type() == QEvent.Type.KeyRelease:
            self._handle_key(event.key(), False)
            return event.key() == Qt.Key.Key_Space
        return False

    @staticmethod
    def _handled_keys():
        return {
            Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_4, Qt.Key.Key_5,
            Qt.Key.Key_Space,
            Qt.Key.Key_Escape,
            Qt.Key.Key_Left,
            Qt.Key.Key_Down,
            Qt.Key.Key_Right,
            Qt.Key.Key_A,
            Qt.Key.Key_S,
            Qt.Key.Key_D,
            Qt.Key.Key_F,
            Qt.Key.Key_V,
        }

    def keyPressEvent(self, event):
        self._handle_key(event.key(), True)

    def keyReleaseEvent(self, event):
        self._handle_key(event.key(), False)

    def _handle_key(self, key, pressed: bool):
        if key == Qt.Key.Key_Escape and pressed:
            self.finish_game()
            return
        if key == Qt.Key.Key_Space:
            self.input_fusion.set_space_pressed(pressed)
        elif not pressed:
            return
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.manual_lane = 0
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.manual_lane = config.LANE_COUNT//2
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.manual_lane = config.LANE_COUNT-1
        elif Qt.Key.Key_1 <= key <= Qt.Key.Key_5:
            self.manual_lane = key - Qt.Key.Key_1
        elif key == Qt.Key.Key_V:
            self.ar_camera = not self.ar_camera
        elif key == Qt.Key.Key_F:
            self.camera_flip = not self.camera_flip
            self.input_fusion.set_camera_flip(self.camera_flip)
            print(f"Camera flip set to {self.camera_flip}")

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale=min(self.width()/1280, self.height()/720)
        offset_x=(self.width()-1280*scale)/2
        offset_y=(self.height()-720*scale)/2
        p.fillRect(self.rect(),QColor('#080B12'))
        p.translate(offset_x,offset_y)
        p.scale(scale,scale)
        draw_aurora_background(p, QRectF(0,0,1280,720))
        if self.ar_camera and self.camera_pixmap is not None:
            p.save(); p.setOpacity(.18); p.drawPixmap(QRectF(0,0,1280,720),self.camera_pixmap,QRectF(self.camera_pixmap.rect())); p.restore()
        top, bottom = 216.,720.
        def edge(y):
            t=(y-top)/(bottom-top)
            return 640-(90+320*t), 640+(90+320*t)
        def lane_x(y,lane):
            left,right=edge(y); return left+(right-left)*(lane+.5)/config.LANE_COUNT
        g=QLinearGradient(0,top,0,bottom); g.setColorAt(0,QColor(16,24,39,25)); g.setColorAt(1,QColor(70,90,105,165))
        poly=QPolygonF([QPointF(550,top),QPointF(730,top),QPointF(1050,bottom),QPointF(230,bottom)])
        p.setBrush(g); p.setPen(QPen(QColor(210,240,240,90),2)); p.drawPolygon(poly)
        lane=self.current_input.lane
        if lane is not None:
            left,right=edge(bottom); tw=180/config.LANE_COUNT; bw=(right-left)/config.LANE_COUNT
            beam=QLinearGradient(0,top,0,bottom); beam.setColorAt(0,QColor(16,185,129,0)); beam.setColorAt(1,QColor(16,185,129,55))
            p.setBrush(beam); p.setPen(Qt.PenStyle.NoPen); p.drawPolygon(QPolygonF([QPointF(550+tw*lane,top),QPointF(550+tw*(lane+1),top),QPointF(left+bw*(lane+1),bottom),QPointF(left+bw*lane,bottom)]))
        for i in range(config.LANE_COUNT+1):
            p.setPen(QPen(QColor('#6EE7B7' if i==0 else '#C4B5FD') if i in (0,config.LANE_COUNT) else QColor(200,220,230,55),2 if i in (0,config.LANE_COUNT) else 1))
            p.drawLine(QPointF(550+i*180/config.LANE_COUNT,top),QPointF(230+i*820/config.LANE_COUNT,bottom))
        judge_y=720*float(self.settings['judgement_line_y_ratio'])
        left,right=edge(judge_y)
        laser=QLinearGradient(left,0,right,0); laser.setColorAt(0,QColor('#6EE7B7')); laser.setColorAt(1,QColor('#C4B5FD'))
        p.setPen(QPen(laser,3)); p.drawLine(QPointF(left,judge_y),QPointF(right,judge_y))
        now=self._playback_time_ms()
        # Map the existing engine's travel distance so hit time stays exactly on the laser.
        travel=max(1,(judge_y-top)/int(self.settings['note_speed'])*1000)
        for note in reversed(self.engine.notes_in_time_range(now-travel*.13, now+travel)):
            if note.judged: continue
            progress=1-(note.hit_time_ms-now)/travel
            if not 0<=progress<=1.13: continue
            depth=progress**1.65
            y=top+(judge_y-top)*depth
            x=lane_x(y,note.lane); size=14+depth*64
            draw_crystal_note(p,QRectF(x-size/2,y-size*.65,size,size*.7),note.lane==2)
        for born,lane in self.ripples:
            age=(now-born)/800; x=lane_x(judge_y,lane)
            for ring in range(4):
                radius=18+age*105+ring*15
                p.setBrush(Qt.BrushStyle.NoBrush); p.setPen(QPen(QColor(185,255,235,max(0,int((1-age)*170-ring*25))),2))
                p.drawEllipse(QPointF(x,judge_y),radius,radius*.28)
        if self.settings.get('show_judgement_text',True):
            active=self.result_flash and now-self.result_flash_time_ms<650
            label=self.result_flash if active else 'SONIC LAB'
            text(p,QRectF(390,90,500,58),label,32,'#F43F5E' if label=='MISS' else '#F8FAFC')
            text(p,QRectF(430,148,420,34),f'{self.engine.score_state.combo} COMBO',21,'#6EE7B7')
            if active: text(p,QRectF(390,460,500,55),label,30)
        if self.settings.get('show_game_hud',True):
            self._draw_lab_hud(p)
        if self.song_path:
            status = self.audio_player.error or ('LOADING AUDIO...' if self.audio_player.loading else f'{self.audio_player.position_ms/1000:.0f}s / {self.audio_player.duration_seconds:.0f}s')
            text(p,QRectF(320,626,640,22),status,10,'#94A3B8')
        text(p,QRectF(300,654,680,24),self.camera_source.status+' / 1-5 FINGERS = LANES 1-5 / FIST = NO LANE',9,'#94A3B8')
        tracker=self.input_fusion.tracker
        if tracker and not tracker.backend_is_mediapipe:
            text(p,QRectF(340,35,600,48),'MEDIAPIPE INACTIVE / CHECK CAMERA TEST IN SETTINGS',13,'#FB923C')
        text(p,QRectF(280,687,720,24),'1-5: LANE / SPACE: DEMO ONLY  /  F: FLIP  /  V: AR CAMERA',10,'#94A3B8')

    def _draw_lab_hud(self,p):
        draw_frosted_glass_card(p,QRectF(42,100,282,190),'EMG DSP FILTER & THRESHOLD')
        draw_waveform(p,QRectF(62,155,242,105),self.raw_history,self.filtered_history)
        draw_frosted_glass_card(p,QRectF(42,320,250,220),'EMG BIO-SIGNAL')
        ratio=self.input_fusion.emg_mvc_ratio
        draw_circular_gauge(p,QRectF(88,357,157,157),ratio,f'{ratio*100:.0f}%','MVC ACTIVE')
        text(p,QRectF(50,516,234,18),getattr(self.input_fusion.emg_reader,'status','MOCK EMG'),8,'#94A3B8')
        draw_frosted_glass_card(p,QRectF(940,70,300,245),'LIVE WEBCAM FEED & HAND TRACKING')
        view=QRectF(952,110,276,185)
        p.save(); clip=QPainterPath(); clip.addRoundedRect(view,8,8); p.setClipPath(clip)
        if self.camera_pixmap is not None:
            image_bounds=draw_camera_frame(p,view,self.camera_pixmap)
            p.fillRect(view,QColor(8,11,18,45))
        else:
            p.fillRect(view,QColor(8,16,24,180))
            for i in range(12):
                p.setPen(QColor(100,180,170,22)); x=view.x()+i*25; p.drawLine(QPointF(x,view.top()),QPointF(x,view.bottom()))
        landmarks=self.input_fusion.hand_landmarks_norm
        if landmarks or self.camera_pixmap is None:
            draw_hand_skeleton_overlay(p,image_bounds if landmarks and self.camera_pixmap is not None else view.adjusted(20,5,-20,-20),landmarks,time.monotonic(),finger_states=self.input_fusion.finger_states)
        lane=self.current_input.lane
        for i in range(config.LANE_COUNT):
            cell=QRectF(view.x()+i*view.width()/config.LANE_COUNT,view.y(),view.width()/config.LANE_COUNT,view.height())
            p.setBrush(Qt.BrushStyle.NoBrush); p.setPen(QPen(QColor('#6EE7B7') if i==lane else QColor(255,255,255,40),2 if i==lane else 1)); p.drawRect(cell)
            text(p,QRectF(cell.x(),cell.bottom()-22,cell.width(),20),LANE_NAMES[i],8)
        p.restore()
        fallback=not self.input_fusion.hand_landmarks_norm
        text(p,QRectF(950,298,280,16),('LIVE CAMERA / NO LANDMARKS' if self.camera_pixmap is not None else 'CAMERA UNAVAILABLE / SIMULATION') if fallback else 'LIVE 21-POINT TRACKING',8,'#94A3B8')
        draw_frosted_glass_card(p,QRectF(1010,337,230,100),'LIVE CALIBRATION')
        count=self.current_input.finger_count
        text(p,QRectF(1024,376,200,22),f"FINGERS: {count if count is not None else '--'} / {self.current_input.hand_label or '--'}",11)
        text(p,QRectF(1024,400,200,18),finger_summary(self.input_fusion.finger_states),8,'#94A3B8')
        lane=self.current_input.lane
        text(p,QRectF(1024,417,200,16),f'LANE: {LANE_NAMES[lane] if lane is not None else chr(45)}',9,'#6EE7B7')
        draw_frosted_glass_card(p,QRectF(1010,450,230,60))
        error=self.input_fusion.last_timing_error_ms
        text(p,QRectF(1018,465,214,30),f'TIMING ERROR: {error:+.0f}ms' if error is not None else 'TIMING ERROR: --',12,'#C4B5FD')
        draw_frosted_glass_card(p,QRectF(1010,525,230,94),'SCORE')
        text(p,QRectF(1020,561,210,45),f'{self.engine.score_state.score:07,d}',27)

    def closeEvent(self, event):
        self.timer.stop()
        app = QApplication.instance()
        if app is not None: app.removeEventFilter(self)
        self.audio_player.stop()
        self.camera_source.release()
        self.input_fusion.close()
        super().closeEvent(event)
