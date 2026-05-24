EMG 임계값

목적

EMG 임계값이 활성화와 게임 플레이에 미치는 영향을 설명한다.

확인된 사실

EXTRACTED: EMG 임계값은 설정에서 조정 가능하며 기본값은 400이다.
EXTRACTED: 현재 값이 임계값 이상이면 EMG 활성화가 true가 된다.

관련 파일

[app/config.py](app/config.py)
[app/settings.py](app/settings.py)
[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

흐름

EMG 값 -> 임계값 비교 -> 활성화 플래그 -> 판정

비고

INFERRED: 임계값이 너무 낮으면 오입력이 증가할 수 있다. 너무 높으면 입력이 누락될 수 있다.
INFERRED: 향후 재활 워크플로우에서는 세션별 기준선 보정이 필요할 수 있다.

TODO

Calibration UI에서 임계값 테스트 모드를 제공하는지 확인한다.
