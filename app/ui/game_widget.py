import time
import math
from app.performance import timings

from PyQt6.QtCore import QEvent, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap, QLinearGradient, QPolygonF, QPainterPath
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton, QWidget

from app import config
from app.analytics.game_metrics import calculate_game_metrics
from app.analytics.session_logger import SessionLogger
from app.audio.audio_player import AudioPlayer
from app.game.rhythm_game_engine import RhythmGameEngine
from app.i18n import tr
from app.input.input_fusion import GameInputState, InputFusion
from app.input.leap_tracker import LeapPinchTracker
from app.input.rest_baseline import RestBaseline
from app.settings import load_settings
from app.input.camera import draw_camera_frame


from app.ui.theme import (draw_aurora_background, draw_frosted_glass_card, draw_crystal_note,
    draw_circular_gauge, draw_hand_skeleton_overlay, draw_waveform, text, finger_summary)

LANE_NAMES = [str(i+1) for i in range(config.LANE_COUNT)]


class GameWidget(QWidget):
    def __init__(self, main_window, notes_path: str | None = None, song_path: str | None = None, mode='pinch', profile_id=None, guest_leap_thresholds=None):
        store = getattr(main_window, 'profile_store', None)
        person = store.get(profile_id) if store is not None and profile_id is not None else None
        if profile_id is not None and person is None:
            raise ValueError('선택한 프로필이 삭제되었습니다.')
        if mode == 'pinch_extension' and (store is None or profile_id is None or not store.unlocked(profile_id)):
            raise ValueError('상위 모드는 같은 프로필로 기본 두 게임을 정상 완주한 뒤 열립니다.')
        if person and mode != 'emg' and person['pinch'] is None:
            raise ValueError('이 프로필의 핀치 보정이 필요합니다.')
        super().__init__()
        self.profile_store = store
        self.player_profile_id = profile_id
        self.player_profile_name = person['name'] if person else None
        self._emg_baseline_reused = bool(person and person.get('emg') and mode != 'pinch')
        self.main_window = main_window
        self.song_path = song_path
        self.mode = mode
        self.rest_baseline = RestBaseline() if mode in ('emg', 'pinch_extension') else None
        if self.rest_baseline is not None and self._emg_baseline_reused:
            self.rest_baseline = RestBaseline.from_saved(person['emg'])
        self.lane_count = 1 if mode == 'emg' else config.LANE_COUNT
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.settings = load_settings()
        self.language = self.settings["language"]
        self.engine = RhythmGameEngine.from_json_file(notes_path, mode=mode) if notes_path else RhythmGameEngine(mode=mode)
        self.input_fusion = InputFusion(
            use_camera=False,
            emg_threshold=self.settings["emg_threshold"],
            camera_flip=bool(self.settings["camera_flip"]),
            use_leap=mode in ('pinch', 'pinch_extension'),
            produce_rgb=False,
            use_emg=mode in ('emg', 'pinch_extension'),
            emg_session=getattr(main_window,'emg_session',None),
            leap_thresholds=(person['pinch'] if person else guest_leap_thresholds) if mode != 'emg' else None,
        )
        self.session_logger = SessionLogger()
        self.audio_player = AudioPlayer(self.song_path, volume=self.settings["music_volume"])
        self.start_time = time.monotonic()
        self.current_input = GameInputState(None, 0.0, False, False, None, None, None, time.time(), None, None, None)
        self.ar_camera = False
        self.ripples = []
        self.camera_pixmap = None
        self.camera_debug_pixmap = None
        self.camera_flip = bool(self.settings["camera_flip"])
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
        if self.rest_baseline is None or self.rest_baseline.ready:
            self.audio_player.play()
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(max(1, int(1000 / config.FPS)))

    def _playback_time_ms(self):
        if self.rest_baseline is not None and not self.rest_baseline.ready:
            return 0
        if self.song_path:
            if self.audio_player.error:
                return 0
            if self.audio_player.finished:
                if not hasattr(self, '_audio_finished_at'):
                    self._audio_finished_at = time.monotonic()
                return self.audio_player.position_ms + int((time.monotonic()-self._audio_finished_at)*1000)
            return self.audio_player.position_ms
        return int((time.monotonic()-self.start_time)*1000)

    def _should_finish(self, current_time_ms):
        if self.engine.miss_limit_reached:
            return True
        if self.song_path and not self.audio_player.error:
            if self.mode == 'emg' and self.audio_player.finished and any(
                    n.holding and current_time_ms <= n.end_time_ms+config.EMG_HOLD_DROPOUT_MS
                    for n in self.engine.notes):
                return False
            return self.audio_player.finished
        return self.engine.is_finished(current_time_ms)

    def game_loop(self):
        if self.finished:
            return
        if self.song_path and self.audio_player.error:
            error = str(self.audio_player.error)
            owner = self.main_window
            self.abort_game()
            QMessageBox.warning(owner, '음악 재생 실패', error)
            return
        tick_started = time.perf_counter()
        if hasattr(self, '_previous_tick'): timings.add('gui_tick_interval_ms', (tick_started-self._previous_tick)*1000)
        self._previous_tick = tick_started
        current_time_ms = self._playback_time_ms()
        raw_frame = None
        input_state, _tracked_frame = self.input_fusion.read(raw_frame)
        if self.mode == 'pinch':
            input_state.pinch_input_source = 'leap_only'
        elif self.mode == 'pinch_extension':
            input_state.pinch_input_source = 'leap_and_emg_extension'
        if self.rest_baseline is not None:
            if not self.rest_baseline.ready:
                reader = self.input_fusion.emg_reader
                samples = getattr(reader, 'samples', None)
                if samples is None:
                    samples = [input_state.emg_value]  # Explicit demo reader has no packet list.
                self.rest_baseline.measure(samples, input_state.emg_signal_fresh, time.monotonic())
                input_state.emg_activated = False
                input_state.lane = None
                self.current_input = input_state
                if self.rest_baseline.ready:
                    if self.profile_store is not None and self.player_profile_id is not None:
                        try:
                            self.profile_store.save_emg(self.player_profile_id, self.rest_baseline.baseline, self.rest_baseline.samples)
                        except (OSError, ValueError) as exc:
                            owner = self.main_window
                            self.abort_game()
                            QMessageBox.warning(owner, '근전도 기준 저장 실패', str(exc))
                            return
                    self.start_time = time.monotonic()
                    self.audio_player.play()
                self.update()
                return
            input_state.emg_activated = self.rest_baseline.active(input_state.emg_value, input_state.emg_signal_fresh)
            if self.mode == 'emg':
                input_state.lane = 0 if input_state.emg_activated else None
        self.current_input = input_state
        timings.add('gui_input_and_pixmap_ms', (time.perf_counter()-tick_started)*1000)

        self.ripples = [(t,l) for t,l in self.ripples if current_time_ms-t<800]
        if self.song_path and self.audio_player.loading:
            self.update()
            return
        result = self.engine.update(input_state, current_time_ms)
        note_index = self.engine.last_judged_note_index
        if result in {"PERFECT", "GOOD"} and 0 <= note_index < len(self.engine.notes):
            delay = current_time_ms - self.engine.notes[note_index].end_time_ms
            self.input_delays_ms.append(delay)
            self.input_fusion.last_timing_error_ms = delay
            self.ripples.append((current_time_ms, self.engine.notes[note_index].lane))
        if result:
            self.result_flash = result
            self.result_flash_time_ms = current_time_ms
        self.session_logger.log(current_time_ms, input_state, note_index, result)
        timings.add('gui_tick_work_ms', (time.perf_counter()-tick_started)*1000)

        if self._should_finish(current_time_ms):
            if self.song_path and self.audio_player.finished and not self.audio_player.error:
                self.engine.finalize_unjudged_notes()
            self.finish_game(reason='miss_limit' if self.engine.miss_limit_reached else 'completed')
            return
        self.update()

    def finish_game(self, reason='manual'):
        if self.finished:
            return
        normal_end = (reason == 'completed' and
                      (self.audio_player.finished if self.song_path else self.engine.is_finished(self._playback_time_ms())))
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
        self.input_fusion.close()
        from app.background import jobs
        self.main_window._last_session_logger = self.session_logger
        session_paths = jobs.submit(self.session_logger.save) if config.SAVE_SESSION_LOG else None
        metrics = calculate_game_metrics(self.engine.score_state, self.session_logger.rows, self.input_delays_ms)
        metrics['input_mode'] = self.mode if self.mode != 'pinch' else 'pinch_hold'
        completed = (normal_end and not self.engine.miss_limit_reached
                     and not self.audio_player.error and bool(self.engine.notes)
                     and all(n.judged for n in self.engine.notes))
        metrics['completed_successfully'] = completed
        metrics['end_reason'] = ('song_completed' if self.song_path else 'sample_completed') if completed else 'manual_exit'
        metrics['player_profile_id'] = self.player_profile_id
        metrics['player_profile_name'] = self.player_profile_name
        if completed and self.profile_store is not None and self.player_profile_id is not None:
            try:
                self.profile_store.record_completion(self.player_profile_id, self.mode)
            except (OSError, ValueError) as exc:
                metrics['profile_save_error'] = str(exc)
        if self.mode == 'pinch':
            metrics['pinch_input_source'] = 'leap_only'
        elif self.mode == 'pinch_extension':
            metrics['pinch_input_source'] = 'leap_and_emg_extension'
        if self.engine.miss_limit_reached:
            metrics['end_reason'] = '10_consecutive_misses'
            metrics['consecutive_misses'] = self.engine.consecutive_misses
        holds = [n for n in self.engine.notes if n.duration_ms]
        metrics['hold_note_count'] = len(holds)
        metrics['hold_success_count'] = sum(n.result in ('PERFECT', 'GOOD') for n in holds)
        metrics['hold_target_duration_ms'] = sum(n.duration_ms for n in holds)
        if self.rest_baseline is not None:
            metrics['emg_rest_baseline'] = self.rest_baseline.baseline
            metrics['emg_activation_delta'] = 0.
            metrics['emg_baseline_method'] = 'minimum'
            metrics['emg_baseline_duration_seconds'] = self.rest_baseline.DURATION
            metrics['emg_baseline_samples'] = list(self.rest_baseline.samples)
            metrics['emg_baseline_reused'] = self._emg_baseline_reused
        self.main_window.show_result_screen(metrics, session_paths=session_paths)
        timings.flush()

    def abort_game(self):
        if self.finished:
            return
        self.finished = True
        self.timer.stop()
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self.audio_player.stop()
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

    def _handled_keys(self):
        return {Qt.Key.Key_Escape, Qt.Key.Key_Space} if self.rest_baseline is not None else {Qt.Key.Key_Escape}

    def keyPressEvent(self, event):
        self._handle_key(event.key(), True)

    def keyReleaseEvent(self, event):
        self._handle_key(event.key(), False)

    def _handle_key(self, key, pressed: bool):
        if self.rest_baseline is not None and key == Qt.Key.Key_Space:
            self.input_fusion.set_space_pressed(pressed)
            return
        if key == Qt.Key.Key_Escape and pressed:
            if self.rest_baseline is not None and not self.rest_baseline.ready:
                self.abort_game()
                return
            self.finish_game()
            return

    def paintEvent(self, event):
        paint_started = time.perf_counter()
        if hasattr(self, '_previous_paint'): timings.add('paint_interval_ms', (paint_started-self._previous_paint)*1000)
        self._previous_paint = paint_started
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale=min(self.width()/1280, self.height()/720)
        offset_x=(self.width()-1280*scale)/2
        offset_y=(self.height()-720*scale)/2
        p.fillRect(self.rect(),QColor('#080B12'))
        p.translate(offset_x,offset_y)
        p.scale(scale,scale)
        draw_aurora_background(p, QRectF(0,0,1280,720))
        text(p,QRectF(44,52,650,26),'PLAYER: '+(self.player_profile_name or 'PRACTICE / UNSAVED'),12,'#94A3B8')
        if self.rest_baseline is not None and not self.rest_baseline.ready:
            text(p,QRectF(240,170,800,70),'EMG RECORDING / 3.0 SECONDS',28,'#6EE7B7')
            remaining = self.rest_baseline.remaining(time.monotonic())
            text(p,QRectF(300,270,680,80),f'{remaining:.1f}s',40)
            text(p,QRectF(240,380,800,40),f'EMG ACTIVITY: {self.current_input.emg_value:.4f}',20)
            status = getattr(self.input_fusion.emg_reader, 'status', 'DEMO EMG')
            text(p,QRectF(160,455,960,35),status,11,'#94A3B8')
            text(p,QRectF(160,510,960,35),'RECORD 3.0 SECONDS / EXTENSION AT OR ABOVE MINIMUM',13,'#94A3B8')
            timings.add('paint_work_ms', (time.perf_counter()-paint_started)*1000)
            return
        if self.ar_camera and self.camera_pixmap is not None:
            p.save(); p.setOpacity(.18); p.drawPixmap(QRectF(0,0,1280,720),self.camera_pixmap,QRectF(self.camera_pixmap.rect())); p.restore()
        top, bottom = 216.,720.
        def edge(y):
            t=(y-top)/(bottom-top)
            return 640-(90+320*t), 640+(90+320*t)
        def lane_x(y,lane):
            left,right=edge(y); return left+(right-left)*(lane+.5)/self.lane_count
        g=QLinearGradient(0,top,0,bottom); g.setColorAt(0,QColor(16,24,39,25)); g.setColorAt(1,QColor(70,90,105,165))
        poly=QPolygonF([QPointF(550,top),QPointF(730,top),QPointF(1050,bottom),QPointF(230,bottom)])
        p.setBrush(g); p.setPen(QPen(QColor(210,240,240,90),2)); p.drawPolygon(poly)
        lane=self.current_input.lane
        if lane is not None:
            left,right=edge(bottom); tw=180/self.lane_count; bw=(right-left)/self.lane_count
            beam=QLinearGradient(0,top,0,bottom); beam.setColorAt(0,QColor(16,185,129,0)); beam.setColorAt(1,QColor(16,185,129,55))
            p.setBrush(beam); p.setPen(Qt.PenStyle.NoPen); p.drawPolygon(QPolygonF([QPointF(550+tw*lane,top),QPointF(550+tw*(lane+1),top),QPointF(left+bw*(lane+1),bottom),QPointF(left+bw*lane,bottom)]))
        for i in range(self.lane_count+1):
            p.setPen(QPen(QColor('#6EE7B7' if i==0 else '#C4B5FD') if i in (0,self.lane_count) else QColor(200,220,230,55),2 if i in (0,self.lane_count) else 1))
            p.drawLine(QPointF(550+i*180/self.lane_count,top),QPointF(230+i*820/self.lane_count,bottom))
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
            if note.duration_ms and now >= note.hit_time_ms:
                progress = 1.
            if not 0<=progress<=1.13: continue
            depth=progress**1.65
            y=top+(judge_y-top)*depth
            x=lane_x(y,note.lane); size=14+depth*64
            if note.duration_ms:
                tail_progress = max(0., min(1., 1-(note.end_time_ms-now)/travel))
                tail_y = top+(judge_y-top)*tail_progress**1.65
                tail_x = lane_x(tail_y,note.lane)
                tail_width = 10+tail_progress*18
                body = QPolygonF([QPointF(tail_x-tail_width,tail_y),QPointF(tail_x+tail_width,tail_y),
                                  QPointF(x+size*.3,y),QPointF(x-size*.3,y)])
                p.setBrush(QColor(110,231,183,150) if note.holding else QColor(196,181,253,120))
                p.setPen(QPen(QColor('#6EE7B7' if note.holding else '#C4B5FD'),2))
                p.drawPolygon(body)
                p.drawLine(QPointF(tail_x-tail_width,tail_y),QPointF(tail_x+tail_width,tail_y))
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
        if self.mode == 'emg':
            reader = self.input_fusion.emg_reader
            text(p,QRectF(300,654,680,24),getattr(reader,'status','MOCK EMG / SPACE TO CONTRACT'),9,'#94A3B8')
            text(p,QRectF(280,687,720,24),'EMG: CONTRACT ON BEAT / HOLD LONG NOTES / REST BETWEEN NOTES',10,'#94A3B8')
        else:
            text(p,QRectF(300,654,680,24),getattr(self.input_fusion.tracker,'status','LEAP WAITING')+' / THUMB + INDEX/MIDDLE/RING/PINKY = 1/2/3/4',9,'#94A3B8')
            tracker=self.input_fusion.tracker
            if tracker and tracker.last_error:
                text(p,QRectF(340,35,600,48),tracker.last_error,13,'#FB923C')
            instruction = ('LEAP PINCH + ARMBAND EXTENSION TOGETHER / ESC: FINISH'
                           if self.mode == 'pinch_extension' else 'LEAP MOTION ONLY / HOLD AT THE LINE / ESC: FINISH')
            text(p,QRectF(280,687,720,24),instruction,10,'#94A3B8')
        timings.add('paint_work_ms', (time.perf_counter()-paint_started)*1000)

    def _draw_lab_hud(self,p):
        if self.mode == 'emg':
            draw_frosted_glass_card(p,QRectF(42,100,282,270),'EMG RHYTHM + HOLD')
            active = self.current_input.emg_activated
            draw_circular_gauge(p,QRectF(88,145,157,137),float(active),f'{self.current_input.emg_value:.4f}',
                                ('신전' if self.language == 'ko' else 'EXTENSION') if active else 'BELOW MIN')
            reader = self.input_fusion.emg_reader
            text(p,QRectF(52,305,262,22),f'MIN {self.rest_baseline.baseline:.4f} / EXT >= MIN',10,'#94A3B8')
            text(p,QRectF(52,335,262,22),f'BEAT +/-{config.EMG_JUDGE_WINDOW_MS}ms / DIP {config.EMG_HOLD_DROPOUT_MS}ms',9,'#94A3B8')
            draw_frosted_glass_card(p,QRectF(940,70,300,245),'ONE LANE / EMG INPUT ONLY')
            text(p,QRectF(950,120,280,30),'EXTENSION: VALUE >= MINIMUM',10,'#6EE7B7')
            text(p,QRectF(950,165,280,30),'HOLD: KEEP ACTIVE UNTIL TAIL',10,'#C4B5FD')
            text(p,QRectF(950,210,280,30),'RELAX BEFORE THE NEXT NOTE',10,'#94A3B8')
            channels = getattr(self.input_fusion.emg_reader,'channel_rms',None)
            if channels is not None:
                text(p,QRectF(942,253,296,22),'8CH RMS: '+', '.join(f'{v:.0f}' for v in channels),8,'#6EE7B7')
            holding = next((n for n in self.engine.notes if n.holding),None)
            if holding:
                remaining = max(0,holding.end_time_ms-self._playback_time_ms())/1000
                text(p,QRectF(350,390,580,50),f'HOLD {remaining:.1f}s',28,'#6EE7B7')
            self._draw_score_hud(p)
            return
        draw_frosted_glass_card(p,QRectF(42,100,282,190),'ADVANCED PINCH + EXT' if self.mode == 'pinch_extension' else 'PINCH HOLD MODE')
        text(p,QRectF(52,145,262,40),'HOLD THE MATCHING PINCH',12,'#6EE7B7')
        text(p,QRectF(52,192,262,30),'WHEN THE NOTE REACHES THE LINE',9,'#94A3B8')
        text(p,QRectF(52,232,262,30),'LEAP + ARMBAND EXTENSION' if self.mode == 'pinch_extension' else 'LEAP MOTION ONLY',10,'#94A3B8')
        if self.mode == 'pinch_extension':
            extension = self.current_input.emg_activated and self.current_input.emg_signal_fresh
            state = 'EXTENSION READY' if extension else 'EXTENSION REQUIRED'
            draw_frosted_glass_card(p,QRectF(42,315,282,155),'PINCH + EXTENSION')
            text(p,QRectF(52,357,262,30),state,12,'#6EE7B7' if extension else '#FB923C')
            text(p,QRectF(52,397,262,22),f'EMG {self.current_input.emg_value:.4f} / MIN {self.rest_baseline.baseline:.4f}',10,'#94A3B8')
            text(p,QRectF(52,430,262,22),getattr(self.input_fusion.emg_reader,'status','EMG WAITING'),8,'#94A3B8')
        self._draw_camera_hud(p)
        self._draw_score_hud(p)

    def _draw_camera_hud(self,p):
        draw_frosted_glass_card(p,QRectF(940,70,300,245),'LEAP MOTION / RIGHT HAND')
        for i, name in enumerate(('INDEX','MIDDLE','RING','PINKY')):
            color = '#6EE7B7' if self.current_input.lane == i else '#94A3B8'
            text(p,QRectF(952,115+i*35,276,30),f'{i+1}: THUMB + {name}',12,color)
        text(p,QRectF(950,275,280,30),getattr(self.input_fusion.tracker,'status','LEAP WAITING'),8,'#94A3B8')

    def _draw_score_hud(self, p):
        draw_frosted_glass_card(p,QRectF(1010,337,230,100),'LIVE CALIBRATION')
        count=self.current_input.finger_count
        status = (('신전' if self.language == 'ko' else 'EXTENSION') if self.current_input.emg_activated else 'BELOW MINIMUM') if self.mode == 'emg' else f"PINCH: {self.current_input.hand_label or '--'}"
        text(p,QRectF(1024,376,200,22),status,11)
        detail = 'SUSTAIN UNTIL THE TAIL' if self.mode == 'emg' else finger_summary(self.input_fusion.finger_states)
        text(p,QRectF(1024,400,200,18),detail,8,'#94A3B8')
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
        self.input_fusion.close()
        super().closeEvent(event)
