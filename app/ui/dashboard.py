"""Shared, data-driven Sonic Lab dashboard instruments."""
import math
import time
from PyQt6.QtCore import QRectF, Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient, QPainterPath
from PyQt6.QtWidgets import QWidget
from app.input.camera import CameraSource, rgb_pixmap, draw_camera_frame
from app.ui.theme import (draw_waveform, draw_crystal_note, draw_circular_gauge,
    draw_hand_skeleton_overlay, text, finger_summary)


class Instrument(QWidget):
    def __init__(self, kind, parent=None):
        super().__init__(parent)
        self.kind=kind; self.metrics={}; self.analysis={}; self.notes=[]
        self.finger_states=None; self.hand_diagnostic=''; self.camera_pixmap=None; self.landmarks=None; self.threshold=400; self.ratio=0; self.sensor_status='PREVIEW // NOT CONNECTED'
        self.setMinimumSize(180,230)
        self.timer=QTimer(self); self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def start_live(self):
        self.live_requested=True
        if hasattr(self,'live_timer') and self.live_timer.isActive(): return
        from app import config
        from app.input.input_fusion import InputFusion
        from app.settings import load_settings
        settings=load_settings()
        self.fusion=InputFusion(use_camera=config.USE_CAMERA and settings['camera_enabled'],emg_threshold=settings['emg_threshold'],camera_flip=settings['camera_flip'])
        self.camera_source=CameraSource(settings,enabled=config.USE_CAMERA)
        self.capture=self.camera_source.capture
        self.live_timer=QTimer(self); self.live_timer.timeout.connect(self.refresh_live); self.live_timer.start(100)

    def refresh_live(self):
        frame=self.camera_source.read()
        state,_=self.fusion.read(frame)
        self.camera_pixmap=rgb_pixmap(self.fusion.latest_frame_rgb)
        self.hand_diagnostic=f"FINGERS: {state.finger_count if state.finger_count is not None else '--'} / {state.hand_label or '--'} / {state.tracker_status or '--'}"
        self.finger_states=self.fusion.finger_states
        self.landmarks=self.fusion.hand_landmarks_norm
        reader=self.fusion.emg_reader
        connected=hasattr(reader,'serial') and reader.serial is not None
        self.sensor_status=self.camera_source.status+' / '+('TRACKED' if self.landmarks else 'NO HAND')
        self.update()

    def stop_live(self):
        if hasattr(self,'live_timer'): self.live_timer.stop()
        if hasattr(self,'fusion'): self.fusion.close()
        if hasattr(self,'camera_source'): self.camera_source.release()
        self.capture=None

    def showEvent(self,event):
        super().showEvent(event)
        if getattr(self,'live_requested',False) and not self.live_timer.isActive():
            self.start_live()

    def hideEvent(self,event):
        self.stop_live(); super().hideEvent(event)

    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        scale=min(self.width()/300,self.height()/420)
        p.translate((self.width()-300*scale)/2,(self.height()-420*scale)/2)
        p.scale(scale,scale)
        if self.kind=='song': self._song(p)
        elif self.kind=='performance': self._performance(p)
        else: self._bio(p)

    def _song(self,p):
        energy=self.analysis.get('energy',[])
        preview=not len(energy)
        values=list(energy) if not preview else [220+140*math.sin(i*.13)**2+90*math.sin(i*.32) for i in range(100)]
        if len(values)>180: values=values[::max(1,len(values)//180)]
        if not preview:
            peak=max(values) or 1; values=[v/peak*550 for v in values]
        draw_waveform(p,QRectF(10,15,280,100),values)
        text(p,QRectF(5,130,290,64),f"{self.analysis.get('bpm',0):.0f} BPM" if self.analysis else '-- BPM',35)
        text(p,QRectF(10,198,280,22),'ILLUSTRATIVE WAVEFORM' if preview else 'AUDIO ENVELOPE',9,'#94A3B8')
        text(p,QRectF(10,248,280,26),'CRYSTAL NOTE DENSITY',12)
        p.setPen(QPen(QColor('#6EE7B7'),1)); p.drawLine(12,325,288,325)
        total=len(self.notes)
        for i,note in enumerate(self.notes[:18]):
            x=18+(i*43)%258; y=300+(note.lane-1)*15
            draw_crystal_note(p,QRectF(x,y,13,12),note.lane==2)
        duration=self.analysis.get('duration',0)
        density=total/duration if duration else None
        text(p,QRectF(5,365,290,28),f'NOTES: {total}     DENSITY: '+(f'{density:.1f}/s' if density is not None else '--'),12,'#94A3B8')

    def _performance(self,p):
        m=self.metrics; accuracy=m.get('accuracy',0)
        rank=('S+' if accuracy>=95 else 'S' if accuracy>=90 else 'A' if accuracy>=80 else 'B' if accuracy>=65 else 'C') if m else 'READY'
        text(p,QRectF(0,0,300,25),'RANK' if m else 'SESSION',12,'#94A3B8')
        path=QPainterPath(); from app.ui.theme import lab_font
        font=lab_font(52,True); path.addText(0,0,font,rank)
        bounds=path.boundingRect(); p.save(); p.translate(150-bounds.center().x(),88)
        g=QLinearGradient(0,-65,0,10); g.setColorAt(0,QColor('#6EE7B7')); g.setColorAt(1,QColor('#C4B5FD')); p.fillPath(path,g); p.restore()
        draw_circular_gauge(p,QRectF(65,105,170,170),accuracy/100,f'{accuracy:.1f}%','ACCURACY',full_circle=True)
        total=max(1,sum(m.get(k,0) for k in ('perfect_count','good_count','miss_count')))
        for i,(label,key,color) in enumerate((('PERFECT','perfect_count','#6EE7B7'),('GOOD','good_count','#A3E635'),('MISS','miss_count','#F43F5E'))):
            y=292+i*36; count=m.get(key,0)
            text(p,QRectF(15,y,180,24),label,16,color,Qt.AlignmentFlag.AlignLeft)
            text(p,QRectF(220,y,65,24),count,16)
            p.fillRect(QRectF(15,y+27,270,3),QColor(255,255,255,25)); p.fillRect(QRectF(15,y+27,270*count/total,3),QColor(color))
        text(p,QRectF(0,404,300,16),f"SCORE {m.get('score',0):,}  /  MAX COMBO {m.get('max_combo',0)}" if m else 'SELECT A SONG / CALIBRATE / PLAY',9,'#94A3B8')

    def _bio(self,p):
        text(p,QRectF(5,0,290,25),self.hand_diagnostic or ('HAND 1: ACTIVE' if self.landmarks else ('LIVE CAMERA / NO HAND' if self.camera_pixmap is not None else 'SIMULATED HAND PREVIEW')),9,'#94A3B8')
        view=QRectF(10,28,280,205)
        if self.camera_pixmap is not None:
            p.save(); clip=QPainterPath(); clip.addRoundedRect(view,8,8); p.setClipPath(clip)
            image_bounds=draw_camera_frame(p,view,self.camera_pixmap)
            p.fillRect(view,QColor(8,11,18,40)); p.restore()
        if self.landmarks or self.camera_pixmap is None:
            draw_hand_skeleton_overlay(p,image_bounds if self.landmarks and self.camera_pixmap is not None else QRectF(30,28,240,205),self.landmarks,time.monotonic(),finger_states=self.finger_states)
        text(p,QRectF(10,231,280,18),finger_summary(self.finger_states),9,'#94A3B8')
        draw_circular_gauge(p,QRectF(72,250,156,146),self.threshold/580,str(self.threshold),'EMG THRESHOLD')
        text(p,QRectF(0,235,65,22),'0',9,'#94A3B8'); text(p,QRectF(237,235,60,22),'580',9,'#94A3B8')
        text(p,QRectF(0,397,300,23),self.sensor_status,8,'#6EE7B7')
