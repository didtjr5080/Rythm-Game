APP_STYLE = """
* {
    font-family: "Segoe UI", "Arial";
    font-size: 14px;
}
QMainWindow, QWidget {
    background: #080B12;
    color: #eef2f8;
}
QLabel#brand {
    font-size: 24px;
    font-weight: 900;
    color: #ffffff;
}
QLabel#title {
    font-size: 36px;
    font-weight: 900;
    color: #f7fbff;
}
QLabel#heroTitle {
    font-size: 40px;
    font-weight: 900;
    color: #ffffff;
}
QLabel#subtitle {
    font-size: 15px;
    color: #9ba8bc;
}
QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 800;
    color: #f7fbff;
}
QLabel#muted {
    color: #9ba8bc;
}
QLabel#topBadge {
    color: #8ff7e8;
    font-weight: 800;
    padding: 2px 0;
}
QLabel#greenBadge {
    color: #9df84a;
    font-weight: 900;
    padding: 2px 0;
}
QLabel#statusPill {
    color: #f3f8ff;
    font-weight: 800;
    padding: 2px 0;
}
QLabel#statusPill[ready="true"] {
    color: #bffff5;
}
QLabel#statusPill[ready="false"] {
    color: #ffe2df;
}
QFrame#panel {
    background: rgba(18,25,38,148);
    border: 1px solid #2a3140;
    border-radius: 12px;
}
QFrame#heroPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #182936, stop:0.42 #10192c, stop:0.72 #3a1737, stop:1 #0f1117);
    border: 1px solid #32465d;
    border-radius: 14px;
}
QFrame#bottomBar {
    background: #151a20;
    border: 1px solid #2a3140;
    border-radius: 12px;
}
QPushButton {
    background: #252d3b;
    border: 1px solid #3a4558;
    border-radius: 9px;
    color: #f5f7fb;
    font-weight: 750;
    padding: 10px 14px;
}
QPushButton:hover {
    background: #303a4c;
    border-color: #68ddcf;
}
QPushButton:pressed {
    background: #1d2532;
}
QPushButton#primary {
    background: #10B981;
    border-color: #80fff0;
    color: #061310;
}
QPushButton#primary:hover {
    background: #58ffe8;
}
QPushButton#danger {
    background: #3a2530;
    border-color: #ba5874;
    color: #ffe8ef;
}
QPushButton#danger:hover {
    background: #5b3142;
}
QComboBox {
    background: #111722;
    border: 1px solid #3a4558;
    border-radius: 8px;
    color: #f5f7fb;
    padding: 8px 10px;
}
QComboBox QAbstractItemView {
    background: rgba(18,25,38,148);
    color: #f5f7fb;
    selection-background-color: #35455d;
}
QListWidget, QTextEdit {
    background: #0e121a;
    border: 1px solid #293243;
    border-radius: 10px;
    color: #e8edf5;
    padding: 8px;
}
QListWidget#beatmapList::item {
    background: #232a38;
    border-left: 8px solid #10B981;
    border-radius: 8px;
    margin: 5px 2px;
    padding: 13px 12px;
    color: #f4f7fb;
}
QListWidget#beatmapList::item:alternate {
    border-left-color: #eb4fb8;
}
QListWidget#beatmapList::item:selected {
    background: #35455d;
    border: 1px solid #b6f7ff;
    border-left: 8px solid #f7ce46;
    color: #ffffff;
}
QSlider::groove:horizontal {
    height: 6px;
    background: #2c3444;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #10B981;
    width: 18px;
    height: 18px;
    margin: -6px 0;
    border-radius: 9px;
}
QCheckBox {
    font-size: 16px;
    font-weight: 750;
    spacing: 10px;
}
QCheckBox::indicator {
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 1px solid #526179;
    background: #111722;
}
QCheckBox::indicator:checked {
    background: #10B981;
    border-color: #80fff0;
}
"""


import math
from functools import lru_cache
from pathlib import Path
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QRadialGradient, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QWidget, QFrame

BG_DEEP_AURORA = "#080B12"
AURORA_EMERALD_GLOW = QColor(16,185,129,56)
AURORA_VIOLET_GLOW = QColor(139,92,246,56)
GLASS_SURFACE_BG = QColor(18,25,38,148)
GLASS_SURFACE_HIGHLIGHT = QColor(255,255,255,20)
GLASS_BORDER_LIGHT = QColor(255,255,255,61)
GLASS_BORDER_ACTIVE = CRYSTAL_EMERALD_CORE = "#10B981"
CRYSTAL_VIOLET_CORE = "#8B5CF6"
TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
STATUS_MISS_CORAL = "#F43F5E"


@lru_cache(maxsize=1)
def font_families():
    families=QFontDatabase.families()
    # The offscreen Qt platform does not enumerate installed Windows fonts.
    if not families:
        for name in ('bahnschrift.ttf','segoeui.ttf','malgun.ttf'):
            path=Path('C:/Windows/Fonts')/name
            if path.exists(): QFontDatabase.addApplicationFont(str(path))
        families=QFontDatabase.families()
    return set(families)


@lru_cache(maxsize=64)
def lab_font(size=12, bold=False):
    available = font_families()
    family = next((f for f in ("Orbitron", "Rajdhani", "Bahnschrift", "Segoe UI Semibold", "Malgun Gothic") if f in available), "Sans Serif")
    font = QFont(family, size)
    font.setBold(bold)
    return font


def text(p, rect, value, size=12, color=TEXT_PRIMARY, align=Qt.AlignmentFlag.AlignCenter):
    p.setFont(lab_font(size)); p.setPen(QColor(color))
    p.drawText(QRectF(rect), align, str(value))


def _paint_aurora_background(p, rect):
    r=QRectF(rect); w=r.width(); h=r.height()
    p.fillRect(r,QColor(BG_DEEP_AURORA))
    for cx, color in ((w*.2,AURORA_EMERALD_GLOW),(w*.83,AURORA_VIOLET_GLOW)):
        glow=QRadialGradient(QPointF(cx,h*.45),w*.48)
        glow.setColorAt(0,color); glow.setColorAt(1,QColor(0,0,0,0)); p.fillRect(r,glow)
    for side,color in ((0,CRYSTAL_EMERALD_CORE),(1,CRYSTAL_VIOLET_CORE)):
        path=QPainterPath(QPointF(-30,h*(.53+side*.2)))
        path.cubicTo(w*.3,h*(.8-side*.5),w*.4,h*(.02+side*.9),w+30,h*.34)
        for width,alpha in ((64,5),(36,8),(20,14),(8,25),(2,44)):
            c=QColor(color); c.setAlpha(alpha); p.setPen(QPen(c,width)); p.drawPath(path)
    for i in range(85):
        x=(i*137.51)%w; y=(i*i*19.37)%h
        p.setPen(QColor(160,240,230,35+(i%4)*18)); p.drawPoint(QPointF(x,y))


@lru_cache(maxsize=4)
def _aurora_pixmap(width,height):
    from PyQt6.QtGui import QPixmap,QPainter
    pixmap=QPixmap(width,height)
    painter=QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    _paint_aurora_background(painter,QRectF(0,0,width,height)); painter.end()
    return pixmap


def draw_aurora_background(p,rect):
    r=QRectF(rect)
    if r.width()>0 and r.height()>0:
        pixmap=_aurora_pixmap(int(r.width()),int(r.height()))
        p.drawPixmap(r,pixmap,QRectF(pixmap.rect()))


def draw_frosted_glass_card(p, rect, title="", accent_color=None, tilt_deg=0.0):
    p.save(); r=QRectF(rect)
    if tilt_deg:
        p.translate(r.center()); p.rotate(tilt_deg); p.translate(-r.center())
    g=QLinearGradient(r.topLeft(),r.bottomRight())
    g.setColorAt(0,QColor(170,195,206,48)); g.setColorAt(.45,GLASS_SURFACE_BG); g.setColorAt(1,QColor(110,120,145,48))
    p.setBrush(g); p.setPen(QPen(GLASS_BORDER_LIGHT,1.2)); p.drawRoundedRect(r,14,14)
    p.setPen(QPen(QColor(accent_color or TEXT_SECONDARY),.7))
    for x,y,sx,sy in ((r.left()+12,r.top()+38,1,1),(r.right()-12,r.top()+38,-1,1),(r.left()+12,r.bottom()-12,1,-1),(r.right()-12,r.bottom()-12,-1,-1)):
        p.drawLine(QPointF(x,y),QPointF(x+10*sx,y)); p.drawLine(QPointF(x,y),QPointF(x,y+10*sy))
    if title: text(p,QRectF(r.left()+16,r.top()+10,r.width()-32,24),title,10,TEXT_SECONDARY,Qt.AlignmentFlag.AlignLeft)
    p.restore()


def draw_circular_gauge(p, rect, value, label="", caption="", full_circle=False):
    r=QRectF(rect); side=min(r.width(),r.height()); ring=QRectF(r.center().x()-side*.4,r.center().y()-side*.4,side*.8,side*.8)
    p.save(); p.setBrush(Qt.BrushStyle.NoBrush)
    start,span=(90,360) if full_circle else (225,270)
    for i in range(60):
        a=math.radians(-start+i*span/60); c=r.center()
        p.setPen(QPen(QColor(TEXT_SECONDARY),1))
        p.drawLine(QPointF(c.x()+math.cos(a)*side*.49,c.y()+math.sin(a)*side*.49),QPointF(c.x()+math.cos(a)*side*.46,c.y()+math.sin(a)*side*.46))
    p.setPen(QPen(QColor(80,110,120,70),8)); p.drawArc(ring,start*16,-span*16)
    g=QLinearGradient(ring.topLeft(),ring.bottomRight()); g.setColorAt(0,QColor("#6EE7B7")); g.setColorAt(1,QColor(CRYSTAL_VIOLET_CORE))
    p.setPen(QPen(g,6)); p.drawArc(ring,start*16,-int(span*16*max(0,min(1,value))))
    if full_circle:
        p.setPen(QPen(QColor(110,231,183,45),2)); p.drawEllipse(ring.adjusted(-6,-6,6,6))
    text(p,QRectF(r.left(),r.center().y()-22,r.width(),40),label,22)
    text(p,QRectF(r.left(),r.center().y()+18,r.width(),24),caption,9,TEXT_SECONDARY)
    p.restore()


def draw_crystal_note(p, rect, violet=False):
    r=QRectF(rect); c=QColor(CRYSTAL_VIOLET_CORE if violet else CRYSTAL_EMERALD_CORE)
    x,y,w,h=r.x(),r.y(),r.width(),r.height(); d=h*.42
    p.save()
    trail=QLinearGradient(x,y-h*2,x,y+h)
    trail.setColorAt(0,QColor(0,0,0,0)); trail.setColorAt(1,QColor(c.red(),c.green(),c.blue(),75))
    p.fillRect(QRectF(x+w*.1,y-h*2,w*.8,h*3),trail)
    glow=QRadialGradient(r.center(),w); glow.setColorAt(0,QColor(c.red(),c.green(),c.blue(),80)); glow.setColorAt(1,QColor(0,0,0,0)); p.fillRect(r.adjusted(-w,-h,w,h),glow)
    faces=[[(x,y+d),(x+w*.18,y),(x+w*.85,y),(x+w,y+d)],[(x,y+d),(x+w,y+d),(x+w*.87,y+h),(x+w*.05,y+h)],[(x+w,y+d),(x+w*.85,y),(x+w*.87,y+h)]]
    for i,face in enumerate(faces):
        fill=QColor(c); fill.setAlpha(105+i*35); p.setBrush(fill); p.setPen(QPen(QColor("#C4B5FD" if violet else "#A7F3D0"),1)); p.drawPolygon(QPolygonF([QPointF(*v) for v in face]))
    p.drawLine(QPointF(x,y+d),QPointF(x+w*.87,y+h)); p.drawLine(QPointF(x+w,y+d),QPointF(x+w*.05,y+h)); p.restore()


def demo_hand(phase=0):
    points=[(.52,.88)]
    for finger,(tx,ty) in enumerate(((.17,.53),(.32,.15),(.50,.09),(.67,.17),(.81,.33))):
        for j in range(4):
            t=(j+1)/4; points.append((.52+(tx-.52)*t+math.sin(phase)*.015,.82+(ty-.82)*t))
    return points


def finger_summary(states):
    if not states: return 'T:-- I:-- M:-- R:-- P:--'
    return '  '.join(f'{label}:{int(states[name])}' for label,name in zip('TIMRP',('thumb','index','middle','ring','pinky')))


def draw_hand_skeleton_overlay(p, rect, landmarks=None, phase=0, finger_states=None):
    r=QRectF(rect); points=landmarks or demo_hand(phase)
    if len(points)!=21: return
    pts=[QPointF(r.x()+float(v[0])*r.width(),r.y()+float(v[1])*r.height()) for v in points]
    p.save()
    for f in range(5):
        name=('thumb','index','middle','ring','pinky')[f]
        color=QColor(('#6EE7B7' if finger_states[name] else '#FB923C') if finger_states else (CRYSTAL_VIOLET_CORE if f>2 else '#6EE7B7'))
        chain=[0]+list(range(1+f*4,5+f*4))
        for a,b in zip(chain,chain[1:]):
            glow=QColor(color); glow.setAlpha(35); p.setPen(QPen(glow,9)); p.drawLine(pts[a],pts[b]); p.setPen(QPen(color,1.4)); p.drawLine(pts[a],pts[b])
    p.setPen(Qt.PenStyle.NoPen)
    for v in pts: p.setBrush(QColor("#CFFAFE")); p.drawEllipse(v,2.8,2.8)
    if finger_states:
        p.setFont(lab_font(max(8,int(r.width()/60)),True))
        for label,name,tip in zip('TIMRP',('thumb','index','middle','ring','pinky'),(4,8,12,16,20)):
            p.setPen(QColor('#6EE7B7' if finger_states[name] else '#FB923C'))
            p.drawText(QPointF(pts[tip].x()+5,pts[tip].y()-5),label)
    p.restore()


def draw_waveform(p, rect, raw, filtered=None):
    r=QRectF(rect)
    for values,color in ((raw,CRYSTAL_VIOLET_CORE),(filtered or raw,"#6EE7B7")):
        if len(values)<2: continue
        values=list(values); peak=max(580,max(values),1); pts=[QPointF(r.x()+i*r.width()/(len(values)-1),r.bottom()-max(0,v)/peak*r.height()) for i,v in enumerate(values)]
        path=QPainterPath(pts[0])
        for a,b in zip(pts,pts[1:]): path.cubicTo(QPointF((a.x()+b.x())/2,a.y()),QPointF((a.x()+b.x())/2,b.y()),b)
        fill=QPainterPath(path); fill.lineTo(r.bottomRight()); fill.lineTo(r.bottomLeft()); fill.closeSubpath()
        g=QLinearGradient(r.topLeft(),r.bottomLeft()); c=QColor(color); c.setAlpha(70); g.setColorAt(0,c); g.setColorAt(1,QColor(0,0,0,0)); p.fillPath(fill,g)
        p.setPen(QPen(QColor(color),1.4)); p.drawPath(path)
    for i in range(31):
        x=r.x()+i*r.width()/30; p.setPen(QColor(148,163,184,90)); p.drawLine(QPointF(x,r.bottom()+5),QPointF(x,r.bottom()+9+i%3*2))


class AuroraScreen(QWidget):
    def paintEvent(self,event):
        from PyQt6.QtGui import QPainter
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); draw_aurora_background(p,self.rect())


class GlassPanel(QFrame):
    def __init__(self,title="",parent=None):
        super().__init__(parent); self.title=title
    def paintEvent(self,event):
        from PyQt6.QtGui import QPainter
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); draw_frosted_glass_card(p,QRectF(self.rect()).adjusted(1,1,-1,-1),self.title)

APP_STYLE += """
QWidget { background: transparent; color: #F8FAFC; font-family: 'Bahnschrift', 'Segoe UI', 'Malgun Gothic'; }
QMainWindow { background: #080B12; }
QLabel#title { font-size: 26px; }
QLabel#heroTitle { font-size: 26px; }
QFrame#panel, QFrame#bottomBar { background: rgba(18,25,38,148); border-color: rgba(255,255,255,61); }
QPushButton:disabled { color: #64748b; }
"""
