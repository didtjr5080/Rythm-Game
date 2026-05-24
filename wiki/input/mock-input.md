모의 입력

목적

실제 EMG 센서나 카메라 없이 게임을 테스트하는 방법을 문서화한다.

확인된 사실

EXTRACTED: SPACE 키는 모의 EMG 활성화를 토글한다.
EXTRACTED: 모의 EMG는 SPACE가 눌리면 높은 값, 아니면 낮은 값을 사용한다.
EXTRACTED: 손 추적이 보이지 않을 때 A/S/D 또는 Left/Down/Right로 레인 폴백을 제공한다.
EXTRACTED: 손이 보이지 않으면 수동 레인 입력이 사용된다.

관련 파일

[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[README.md](README.md)

흐름

SPACE 누름 -> 모의 EMG 값 -> 활성화 확인
A/S/D 또는 Left/Down/Right 누름 -> 수동 레인 -> 레인 선택

비고

카메라 없이도 수동 레인 입력과 모의 EMG로 테스트가 가능하다.

TODO

Calibration 또는 Settings 화면에서 추가 단축키가 있는지 확인한다.
