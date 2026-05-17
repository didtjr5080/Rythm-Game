APP_STYLE = """
* {
    font-family: "Segoe UI", "Arial";
    font-size: 14px;
}
QMainWindow, QWidget {
    background: #0b0d14;
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
    background: #151a24;
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
    background: #26dac1;
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
    background: #151a24;
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
    border-left: 8px solid #26dac1;
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
    background: #26dac1;
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
    background: #26dac1;
    border-color: #80fff0;
}
"""
