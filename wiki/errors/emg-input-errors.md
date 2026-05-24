EMG 입력 오류

목적

EMG 관련 오류 조건과 폴백을 정리한다.

확인된 사실

EXTRACTED: pyserial이 없으면 MockEMGReader로 폴백한다.
EXTRACTED: 시리얼 포트 열기 실패 시 MockEMGReader로 폴백한다.
EXTRACTED: 시리얼 읽기 오류는 메시지를 출력하고 해당 프레임에 모의 값을 반환한다.
INFERRED: COM 포트 또는 baudrate 불일치는 실제 EMG 읽기를 막는다.
INFERRED: 숫자 값이 파싱되지 않으면 잘못된 시리얼 데이터는 무시될 수 있다.

관련 파일

[app/input/emg_reader.py](app/input/emg_reader.py)
[app/input/mock_emg_reader.py](app/input/mock_emg_reader.py)

흐름

포트 열기 -> 라인 읽기 -> 값 파싱 -> 활성화 -> 오류 시 폴백

비고

모의 EMG는 하드웨어가 없을 때도 게임을 플레이 가능하게 한다.

TODO

UI에 실시간 EMG 연결 상태가 표시되는지 확인한다.
