EMG 임계값

목적

EMG 임계값이 활성화와 게임 플레이에 미치는 영향을 설명한다.

확인된 사실

EXTRACTED: EMG ON 임계값은 설정에서 조정 가능하며 현재 새 설치 기본값은 12이다. 기존 사용자 저장값은 우선한다.
EXTRACTED: 증가형 입력은 OFF 미만 4표본으로 재준비한 뒤 ON 이상 2표본에서 활성화된다. 감소형(OFF>ON)은 OFF 초과 4표본으로 재준비하고 ON 이하 2표본에서 활성화된다. 자동 보정은 측정값으로 ON과 OFF를 따로 정하며 품질 조건으로 거부하지 않는다. 저장된 OFF가 없으면 기본 증가형과 ON의 60%를 사용한다. ON=0에서는 입력을 차단한다.
EXTRACTED: [높은 안정값 보정 수정](../../docs/emg-calibration-hysteresis.md)과 [센서별 필터](../../docs/szh-gjd001-filter.md)를 참고한다.
EXTRACTED: 최신 [측정값 직접 보정](../../docs/emg-direct-calibration.md)은 차이·흔들림·분리 거부 조건을 제거하고 소수점 ON/OFF를 저장한다. 이전 v7의 잡음 기반 방식은 변경 이력으로 남긴다.

관련 파일

[app/config.py](app/config.py)
[app/settings.py](app/settings.py)
[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

흐름

EMG 값 -> 임계값 비교 -> 활성화 플래그 -> 판정

비고

INFERRED: 임계값이 너무 낮으면 오입력이 증가할 수 있다. 너무 높으면 입력이 누락될 수 있다.
EXTRACTED: 설정 화면에 안정·수축 자동 보정과 실시간 입력 테스트가 구현돼 있다.

TODO

실제 착용 상태에서 안정/수축 분리와 ON/OFF 판정을 확인한다.
