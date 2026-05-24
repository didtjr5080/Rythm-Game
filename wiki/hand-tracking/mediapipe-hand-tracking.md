MediaPipe 손 추적

목적

MediaPipe 추적이 손 데이터를 게임 레인으로 매핑하는 방식을 설명한다.

확인된 사실

EXTRACTED: MediaPipe는 사용 가능할 때 손과 랜드마크를 감지한다.
EXTRACTED: 트래커는 손가락 수로 레인을 선택한다 (1, 2, 3 손가락 -> 레인 0, 1, 2).
EXTRACTED: 손가락 수로 레인이 매핑되지 않으면 x 좌표를 폴백으로 사용한다.
EXTRACTED: 카메라 플립으로 입력 화면을 좌우 반전할 수 있다.
EXTRACTED: 추적 실패 시 앱을 중단하지 않고 빈 결과를 반환한다.

관련 파일

[app/input/mediapipe_tracker.py](app/input/mediapipe_tracker.py)
[app/input/input_fusion.py](app/input/input_fusion.py)
[app/ui/game_widget.py](app/ui/game_widget.py)

흐름

Camera frame -> MediaPipe Hands -> Landmarks -> Finger count -> Lane
레인 누락 시 -> x 좌표 -> 레인 폴백

비고

MediaPipe가 설치되지 않으면 손 추적이 비활성화되지만 앱은 계속 실행된다.

TODO

손 라벨 데이터가 추적 외 다른 곳에서 사용되는지 확인한다.
