모순점 및 애매한 내용

목적

문서가 구현된 코드와 정렬되도록 불일치나 불확실한 주장들을 강조한다.

확인된 사실

EXTRACTED: README는 Serial EMG baudrate를 115200으로 설정하라고 안내한다.
EXTRACTED: 코드의 SerialEMGReader 기본 baudrate는 9600이다.
AMBIGUOUS: 현재 배포에서 9600 또는 115200 중 어느 값이 기본값인지 불명확하다.
INFERRED: 미래 임상 분석 기능은 아이디어로 언급되지만 현재 코드에는 구현되어 있지 않다.

관련 파일

[README.md](README.md)
[app/input/emg_reader.py](app/input/emg_reader.py)

흐름

요구사항(README) -> 구현(코드) -> 애매함 문서화 -> 런타임 기본값 변경 금지

비고

배포에서 다른 baudrate를 사용한다면 코드 변경이 아닌 설정 가이드로 문서화한다.

TODO

운영용 EMG 센서의 기본 baudrate를 확인한다.
