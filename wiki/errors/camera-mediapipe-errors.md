카메라 및 MediaPipe 오류

목적

카메라와 추적 실패 시나리오를 요약한다.

확인된 사실

EXTRACTED: 카메라 열기 실패는 처리되며 키보드 폴백이 유지된다.
EXTRACTED: MediaPipe import 실패는 콘솔 메시지와 함께 손 추적을 비활성화한다.
EXTRACTED: 프레임 단위 추적 실패는 빈 결과를 반환한다.
INFERRED: 카메라 권한 문제는 VideoCapture를 열지 못하게 할 수 있다.
INFERRED: 프레임 지연은 추적 안정성을 낮출 수 있다.

관련 파일

[app/ui/game_widget.py](app/ui/game_widget.py)
[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)

흐름

카메라 열기 -> 프레임 캡처 -> 손 추적 -> 실패 시 폴백

비고

추적 실패는 게임 루프를 중단하지 않는다.

TODO

UI에 추가 오류 표시가 있는지 확인한다.
