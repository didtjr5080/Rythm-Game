설정 시스템

목적

로컬 설정에 저장되는 게임 및 UI 옵션을 설명한다.

확인된 사실

EXTRACTED: 설정은 app/data/settings.json에서 로드되며 기본값은 app/settings.py에 있다.
EXTRACTED: 옵션에는 HUD 표시, 음악 음량, 판정 텍스트, 카메라 디버그, 카메라 플립, 노트 속도, 판정선 위치, EMG 임계값이 포함된다.
EXTRACTED: 창 모드와 해상도도 설정에 저장된다.
EXTRACTED: 노트 기본 속도는 450에서 360으로 낮췄다. 같은 이동 거리를 더 오래 보여주며 음악 재생 속도와 노트 판정 시각은 유지한다. 기존 저장 설정은 기본값보다 우선한다.

관련 파일

[app/settings.py](app/settings.py)
[README.md](README.md)

흐름

설정 로드 -> UI와 게임에 적용 -> app/data/settings.json에 저장

비고

설정 값은 로드/저장 시 안전한 범위로 클램프된다.

TODO

SettingsScreen에서 설정 업데이트가 저장되는 위치를 확인한다.
