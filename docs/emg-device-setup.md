# EMG 장치 설정과 펌웨어

## 현재 확인된 장치

EXTRACTED: 이번 작업에서 COM5는 CP210x USB 시리얼 장치로 나타났고, Espressif esptool의 칩 식별 결과는 **ESP8266EX**였습니다. 사용자에게 표시된 보드 명칭만으로 ESP32라고 판단하지 않았습니다.

EXTRACTED: 사용자가 이후 A0를 찾았으며 센서 모델은 `SZH-GJD001`, 전원은 3V3라고 알려주었습니다. COM5의 ESP8266에 제공 펌웨어를 업로드하고 플래시 해시를 검증했으며, 프로젝트 수신기로 실제 식별·데이터 프레임 수신을 확인했습니다. 덮어쓴 구간을 포함하는 기존 플래시 첫 512KiB는 로컬 `build/firmware/`에 백업하고 배포하지 않습니다.

AMBIGUOUS: 보드의 A0 분압 회로와 최대 허용 전압은 회로도 없이 확정하지 않았습니다. 근육 수축/이완에 따른 변화와 임계값 조정은 현장 검증이 필요합니다.

EXTRACTED: [SZH-GJD001 판매처](https://www.devicemart.co.kr/goods/view?no=15019582)는 3.3V~5.5V 전원을 명시하며, 제공 예제는 A0 입력·500Hz·115200 baud를 사용합니다. 센서 전원 범위를 출력 전압 범위로 간주하지 않습니다.

EXTRACTED: NodeMCU의 `D0`는 GPIO16입니다. ESP8266의 외부 아날로그 입력은 `analogRead(A0)`를 사용합니다. 칩 자체 ADC 범위는 0~1V이고, 개발 보드의 분압 회로 유무에 따라 보드 단자 허용 전압은 달라집니다. 보드·센서 사진 또는 제조사 핀맵으로 확인한 뒤 배선해야 합니다.

공식 근거: [NodeMCU 핀 정의](https://github.com/esp8266/Arduino/blob/master/variants/nodemcu/pins_arduino.h), [ESP8266 Arduino 아날로그 입력](https://arduino-esp8266.readthedocs.io/en/2.5.2/reference.html#analog-input).

## 전시용 PC 설정

1. 설정의 **EMG input mode**에서 실제 센서 또는 모의 입력을 선택합니다.
2. **EMG device / COM port**에서 자동 탐색 또는 검색된 장치를 선택합니다. 목록은 2초마다 갱신되며 **Refresh EMG Devices**로 즉시 갱신할 수 있습니다.
3. 제공 펌웨어는 **115200 baud**를 사용합니다.
4. **Connect / Test EMG**에서 장치 상태, RAW, FILTERED, 선택된 VALUE와 활성 여부를 확인합니다.
5. 사용할 신호와 임계값을 정하고 저장합니다. 선택 사항은 게임·캘리브레이션에도 적용됩니다.

EXTRACTED: 자동 모드는 Arduino/CH340/FTDI/CP210x 등 후보 USB 장치에만 연결을 시도하고, 제공 펌웨어의 식별·데이터 프레임을 확인합니다. 임의의 숫자를 보내는 다른 시리얼 장치는 자동 모드에서 EMG 데이터로 인정하지 않습니다. 명시적으로 포트를 선택한 경우에는 기존 숫자·라벨 기반 펌웨어 형식도 읽습니다.

EXTRACTED: 수동 선택 장치의 USB VID/PID/시리얼 식별자를 저장하므로 같은 장치가 다른 COM 번호로 바뀌면 다시 찾습니다. 연결 끊김·수신 중단 시 기존 활성 상태를 지우고 재검색합니다. USB 시리얼 드라이버가 설치되지 않은 장치는 운영체제에서 먼저 인식되어야 합니다.

## 신호 선택

- **Filtered activity / raw EMG sensor**: 펌웨어에서 DC 기준 제거 → 절대값 → 평활화한 근활성 값을 사용합니다.
- **Direct A0 / sensor ENV output**: 센서 모듈이 이미 처리한 ENV/SIG 출력을 제공한다면 A0 원시 ADC 값을 사용합니다.

EXTRACTED: 펌웨어는 500Hz로 ADC를 읽고 50Hz로 전송하며 식별 응답은 1초마다 반복합니다. 시작 후 약 0.5초 동안 기준값을 수집하므로 이때는 근육을 이완합니다. 전송값은 0~1023 범위이며, 보드가 아닌 사용자 PC에서 임계값을 변경합니다.

## 준비된 펌웨어

| 파일 | 컴파일 대상 | 입력 |
| --- | --- | --- |
| `firmware/nano_emg/nano_emg.ino` | classic Nano ATmega328P | A0 |
| `firmware/esp8266_emg/esp8266_emg.ino` | ESP8266 NodeMCU 호환 보드 | A0 |

EXTRACTED: Nano의 신형·구형 부트로더 구성과 ESP8266 NodeMCU 구성은 컴파일을 통과했습니다. 이는 현재 보드의 배선·전압 적합성이나 실제 EMG 수신을 검증한 것은 아닙니다.

Nano 컴파일만 수행하기:

```powershell
.venv311/Scripts/python.exe firmware/upload_nano.py --compile-only
```

Nano 업로드(대상이 실제 Nano인 경우에만):

```powershell
.venv311/Scripts/python.exe firmware/upload_nano.py --port COM4
```

EXTRACTED: Nano 업로더는 신형 부트로더를 먼저 시도하고 필요하면 구형 구성으로 재시도하며 업로드 검증을 요청합니다. [Arduino 공식 부트로더 안내](https://support.arduino.cc/hc/en-us/articles/4401874304274-Select-the-right-processor-for-Arduino-Nano)를 참고하세요. 이 Nano 명령을 ESP8266인 COM5에 사용하면 안 됩니다.

## 통신 형식과 검증

```text
EMG_DEVICE:ESP8266_A0:1
EMG1 raw:512 filtered:40 seq:2
```

EXTRACTED: `EMG?` 명령으로 식별 응답을 요청하고 `ZERO`로 기준 수집을 다시 시작할 수 있습니다. Nano 식별자는 `NANO_A0`입니다. 수신기는 부분 프레임·잘못된 범위·시퀀스 숫자의 오인식을 처리하고, 같은 화면 갱신 사이에 발생한 임계값 초과도 포착합니다.

```powershell
.venv311/Scripts/python.exe WorkOrder/verify_emg_serial.py
```

EXTRACTED: 자동 탐색, COM 번호 변경, USB 식별자 불일치, 부분 프레임, 원시/처리 값 선택, 순간 활성, 수신 중단 및 재연결은 모의 시리얼 테스트로 검증했습니다. COM5 실제 업로드와 실측 프레임 수신도 확인했습니다. 근육 수축/이완에 따른 값 변화와 임계값은 현장에서 확인해야 합니다.
