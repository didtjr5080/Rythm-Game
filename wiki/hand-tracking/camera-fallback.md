카메라 폴백

목적

카메라 또는 추적이 불가능할 때 게임이 어떻게 동작하는지 설명한다.

확인된 사실

EXTRACTED: 카메라를 열 수 없으면 게임은 계속 진행되며 키보드 레인 폴백이 유지된다.
EXTRACTED: MediaPipe import 실패는 콘솔 메시지로 처리되며 손 추적이 비활성화된다.
EXTRACTED: 손이 보이지 않으면 수동 레인 입력이 적용된다.

관련 파일

[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[README.md](README.md)

흐름

카메라 실패 -> 손 데이터 없음 -> 수동 레인 폴백 -> 게임 계속

비고

이 폴백 경로는 컴퓨터 비전 실패 시에도 UI가 응답하도록 보장한다.

TODO

콘솔 로그 외 추가 사용자 메시지가 UI에 표시되는지 확인한다.
