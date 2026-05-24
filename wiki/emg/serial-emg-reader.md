시리얼 EMG 리더

목적

시리얼 EMG 리더의 동작과 폴백 로직을 설명한다.

확인된 사실

EXTRACTED: SerialEMGReader의 기본값은 COM3, baudrate 9600이다.
EXTRACTED: 리더는 짧은 타임아웃으로 pyserial Serial 연결을 시도한다.
EXTRACTED: pyserial이 없거나 포트가 실패하면 MockEMGReader로 폴백한다.
EXTRACTED: 입력 라인은 filtered: 123 같은 형식을 포함해 숫자 값을 파싱한다.
EXTRACTED: 리더는 숫자 값과 임계값 기반 활성화 플래그를 반환한다.

관련 파일

[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

흐름

시리얼 열기 -> 라인 읽기 -> 숫자 추출 -> 임계값 비교 -> 활성화
시리얼 실패 -> 모의 리더 사용

비고

README는 실제 센서에 대해 다른 baudrate를 제안한다. contradictions를 참고한다.

TODO

운영용 EMG 디바이스의 기본 baudrate를 확인한다.
