# SZH-GJD001 전용 ESP8266 필터

EXTRACTED: 후속 비교 펌웨어는 기존 v2 식별과 EMG1 출력을 유지하면서 대역통과 우회 RMS를 추가 전송합니다. [필터 우회 비교 버전](emg-no-bandpass-comparison.md)에서 두 경로의 차이와 별도 EXE를 확인할 수 있습니다.

EXTRACTED: 사용자가 현재 센서도 SZH-GJD001 sEMG라고 재확인했습니다. sEMG 명칭만으로 출력 처리 방식을 정하지 않고 이 모델의 판매처 예제를 근거로 구현했습니다.

## 근거와 변경

EXTRACTED: [판매처 제품 페이지](https://www.devicemart.co.kr/goods/view?no=15019582)의 [GJD001_code.ino](https://www.devicemart.co.kr/goods/download?id=15019582&rank=1)는 A0, 500Hz 샘플링, 115200 baud와 60–100Hz Butterworth 대역통과 필터를 사용합니다. 필터 계수는 4개 2차 섹션입니다. 이전 게임의 20–200Hz 필터를 이 센서에 복사하지 않았습니다.

EXTRACTED: `firmware/esp8266_emg/szh_gjd001_filter.h`의 계수는 `scipy.signal.butter(4, [60, 100], fs=500, btype='bandpass', output='sos')`와 일치합니다. 판매처 예제와 같은 주파수 응답입니다. 출력 부호가 바뀌는 필터 파형을 게임 입력으로 쓰기 위해 추가한 RMS는 본 프로젝트의 구현이며 판매처 예제에 포함된 기능으로 주장하지 않습니다.

EXTRACTED: 처리 순서:

1. ESP8266 A0를 500Hz로 측정합니다.
2. 시작/ZERO 후 250표본으로 초기 기준을 수집합니다. 이때 힘을 빼고 있어야 합니다.
3. 기준을 뺀 원신호에 판매처 예제와 같은 60–100Hz 대역통과 필터를 적용합니다.
4. 20표본(40ms) RMS를 계산해 음수가 없는 ADC 진폭 단위 활동값을 만듭니다.
5. 기존 EMG1 패킷의 filtered 필드로 50Hz 전송합니다.
6. PC에서 중앙값 3표본·EMA 평활화 후 표시/판정/자동 임계값 보정에 사용합니다.

EXTRACTED: 샘플 시각은 2ms 간격을 기준으로 진행합니다. 한 주기 이상 누락되면 필터를 초기화하며 없는 표본을 복제하지 않습니다. Nano 펌웨어는 이번 센서 수정 대상이 아니므로 기존 처리를 유지합니다.

INFERRED: 이 경로는 PC 수신 후 50Hz 데이터에 원신호 대역통과를 적용하는 것보다 판매처 예제의 신호 처리 조건에 부합합니다. 실제 보드의 샘플 간격, 전극 접촉 잡음과 수축 인식 성능은 별도 실측이 필요합니다. 판매처 대역 자체가 60Hz 경계를 포함하므로 이번 구현을 60Hz 전원 잡음 제거 완료라고 해석하면 안 됩니다. 별도의 노치 필터는 추가하지 않았습니다.

## 펌웨어와 EXE의 관계

EXTRACTED: 새 ESP8266 펌웨어는 `EMG_DEVICE:ESP8266_A0:2`로 식별합니다. 앱은 v1도 읽지만 상태에 펌웨어 업데이트 필요를 표시하고 ESP8266 v1에서는 새 센서 자동 보정을 시작하지 않습니다. v2의 직접 A0 선택은 진단 표시만 가능하며 수축 입력/자동 보정은 차단합니다. SZH-GJD001에는 Filtered activity를 선택합니다.

EXTRACTED: EXE를 교체하는 것만으로 보드의 필터는 바뀌지 않습니다. 새 펌웨어 업로드 후 임계값을 다시 보정해야 합니다. 기존 임계값은 이전 처리의 진폭 기준이므로 그대로 신뢰하지 않습니다.

## 빌드·검증

EXTRACTED: ESP8266 Arduino core 3.1.2의 `esp8266:esp8266:nodemcuv2` 설정으로 컴파일했습니다. 바이너리는 `release/firmware-szh-gjd001-v2/esp8266_emg.ino.bin`입니다. COM 포트 검색 당시 CP210x 장치는 COM3으로 나타났습니다. USB 칩 명칭만으로 MCU 종류를 다시 확정하지 않습니다.

```powershell
arduino-cli compile --fqbn esp8266:esp8266:nodemcuv2 --build-path build/firmware/szh-gjd001-v2 --output-dir release/firmware-szh-gjd001-v2 firmware/esp8266_emg
.venv311/Scripts/python.exe -m unittest WorkOrder.verify_emg_serial WorkOrder.verify_emg_processing WorkOrder.verify_szh_filter
```

EXTRACTED: 회귀 검사 20개가 통과했습니다. 펌웨어 계수와 필터 주파수 응답, DC 억제·80Hz 진폭, v2 식별·RAW 진단 차단·연결 해제 초기화를 포함합니다. 오프스크린 Qt 검사에서 구형 펌웨어/RAW 모드 보정 거부와 v2 안정·수축 보정 성공을 확인했습니다. 이는 실제 보드에서 필터 코드를 실행해 얻은 측정 결과는 아닙니다.

EXTRACTED: 사용자에게 COM3가 센서 보드이며 백업 후 업로드해도 된다는 확인을 받았습니다. COM3는 ESP8266EX·4MB 플래시로 식별됐습니다. 기존 리듬 게임이 포트를 점유해 정상 종료를 요청한 뒤 진행했습니다. 전체 4,194,304바이트를 `build/firmware/esp8266-com3-before-szh-v2-20261117.bin`에 백업하고 SHA256을 기록했습니다. 백업은 로컬에만 두며 배포 ZIP에 넣지 않습니다. 새 펌웨어를 업로드하고 esptool의 쓰기 해시 검증을 통과했습니다.

EXTRACTED: 앱 리더로 6초간 실수신을 확인했으며 v2 식별과 마지막 약 5초간 249표본 수신을 확인했습니다. `release/szh-gjd001-live-check.json`에 요약만 기록했습니다. 해당 구간의 직접 A0 범위는 2–986, PC 평활화 활동값 범위는 약 170–345였습니다. 이 구간의 안정/수축 상태는 지정하지 않았으므로 잡음 바닥이나 근수축 성능으로 해석하지 않습니다.

EXTRACTED: 새 EXE는 기존 파일 잠금을 피하기 위해 `dist_windows_szh_v4/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`에 생성했습니다. `release/EMG-Motion-Rhythm-windows-x64-2026.11.17.4.zip`과 SHA256 파일을 생성했습니다. `release/self-test-2026.11.17.4.json`의 ok=true, 자체 검사 11개 항목 통과를 확인했습니다. 이전 ZIP은 유지합니다.

TODO: 새 EXE에서 Filtered activity를 선택하고 실제 안정·수축 상태로 임계값을 다시 보정합니다. 두 상태의 분리 정도와 판정 지연을 확인합니다. 현재 실수신 요약만으로 이 작업이 완료됐다고 주장하지 않습니다.

[Mermaid 흐름](../diagrams/emg-auto-calibration.md)은 Mermaid 지원 미리보기로 엽니다. Graphify는 저장소 루트에서 `graphify .`로 수동 실행합니다.
