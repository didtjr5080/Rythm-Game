입력 개요

목적

레인 선택과 EMG 활성화가 게임 입력으로 결합되는 방식을 요약한다.

확인된 사실

EXTRACTED: 카메라가 사용 가능할 때 손 추적이 레인 선택을 제공한다.
EXTRACTED: EMG 활성화는 프레임마다 읽혀 레인 상태와 결합된다.
EXTRACTED: SPACE는 테스트용 모의 EMG 입력을 활성화한다.
EXTRACTED: 키보드 레인 폴백은 A/S/D 및 Left/Down/Right 키를 지원한다.
EXTRACTED: 손 추적이 실패했더라도 수동 레인이 설정되어 있으면 수동 레인 선택이 사용된다.

관련 파일

[app/input/input_fusion.py](app/input/input_fusion.py)
[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)
[README.md](README.md)

흐름

Camera frame -> MediaPipe tracking -> Lane selection
Keyboard lane input -> Manual lane override
EMG reader -> Activation
Lane + Activation -> GameInputState

비고

카메라 추적이 불가능해도 수동 레인 입력으로 테스트가 가능하다.

TODO

수동 입력과 손 추적이 동시에 존재할 때의 동작을 확인한다.
