# 대역통과 필터 우회 비교 버전

EXTRACTED: 사용자가 기존 필터 버전과 비교할 별도 빌드를 요청했습니다. 새 EXE 이름은 `EMG-Motion-Rhythm-No-Bandpass.exe`이며 출력 폴더는 `dist_windows_no_bandpass/EMG-Motion-Rhythm-No-Bandpass`입니다. 기존 v5 EXE 폴더와 ZIP은 유지합니다.

## 무엇을 비교하는가

| 단계 | 기존 필터 신호 | NO BANDPASS 신호 |
|---|---|---|
| A0 측정 | 500Hz | 같은 500Hz ADC 표본 |
| 초기 DC 기준 | 처음 250표본 평균 | 동일 표본으로 계산한 같은 기준 |
| 60–100Hz 대역통과 | 적용 | 우회 |
| RMS | 20표본 / 40ms | 20표본 / 40ms |
| PC 전송 | 50Hz EMG1 | 50Hz EMG1_BYPASS |
| PC 평활화·판정 | 중앙값 3표본·EMA, ON/OFF | 같은 처리 |

EXTRACTED: 위 표는 `firmware/esp8266_emg/szh_gjd001_filter.h`, `esp8266_emg.ino`, `app/input/emg_reader.py`에서 확인한 처리입니다. NO BANDPASS는 대역통과만 우회하며 DC 제거·RMS·PC 평활화까지 모두 제거한 원시 ADC 모드는 아닙니다. 50Hz 직접 A0를 500Hz RMS처럼 다루지 않습니다.

## 사용 순서

1. 한 번에 EMG 앱 하나만 실행합니다. COM3는 여러 앱이 동시에 사용할 수 없습니다.
2. 비교 EXE를 실행합니다. 새 설치의 기본 선택은 `NO BANDPASS / DC removed RMS (comparison)`입니다.
3. 힘을 뺀 상태에서 Connect / Test EMG를 누릅니다. 펌웨어는 연결/리셋 후 초기 DC 기준을 수집합니다.
4. 화면의 `BP RMS`(대역통과 적용)와 `NO BP RMS`(우회)를 확인합니다. `VALUE`와 ACTIVE는 선택한 모드의 처리 결과입니다.
5. 안정 측정 → 수축 측정 → Save를 진행합니다. P95/P10·차이, ON/OFF 및 실제 판정 반응을 확인합니다.
6. 같은 EXE에서 신호 종류를 Filtered activity로 바꾸고 Connect / Test EMG 후 다시 보정해 비교할 수 있습니다. 모드 변경 시 이전 보정은 해제됩니다. 전극 위치와 동작을 가능한 한 유지합니다.

INFERRED: 우회 값이 더 크다고 잡음이 적거나 근육 신호가 더 좋다고 판단할 수 없습니다. 안정/수축 구간 분리와 입력 재현성을 비교해야 합니다. 실제 사용자 동작을 지정한 비교 결과가 없으므로 어느 모드가 더 낫다고 확정하지 않습니다.

## 통신·호환성

EXTRACTED: 기존 v2 식별과 EMG1 메시지는 유지합니다. 비교 펌웨어는 같은 seq로 아래 메시지를 추가합니다.

```text
EMG_DEVICE:ESP8266_A0:2
EMG1 raw:512 filtered:40 seq:123
EMG1_BYPASS rms:80 seq:123
```

EXTRACTED: 기존 리더는 EMG1_BYPASS를 숫자 입력으로 오인하지 않고 무시합니다. 새 앱의 Filtered 모드도 확장 메시지를 활성 판정에 사용하지 않습니다. NO BANDPASS 모드는 EMG1의 filtered 값이나 기존 숫자 메시지로 대체하지 않습니다. 비교 메시지가 없으면 입력을 활성화하지 않고 펌웨어 업데이트를 안내합니다.

## 빌드와 검사

EXTRACTED: `EMG-Motion-Rhythm.spec`에 빌드 선택을 추가했습니다. `EMG_NO_BANDPASS_BUILD=1`일 때 비교 EXE 이름을 사용하고 `packaging/no_bandpass.marker`를 앱 리소스로 포함합니다. 이 리소스가 있는 빌드의 새 설치 기본 신호만 unfiltered이며 일반 빌드의 기본 envelope는 유지합니다. 저장된 사용자 설정은 우선합니다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --distpath dist_windows_no_bandpass --workpath build/no-bandpass EMG-Motion-Rhythm.spec
Remove-Item Env:EMG_NO_BANDPASS_BUILD
```

EXTRACTED: 비교 펌웨어는 Arduino ESP8266 core 3.1.2, nodemcuv2 설정으로 컴파일했습니다. 파일은 `release/firmware-szh-comparison/esp8266_emg.ino.bin`입니다. 회귀 검사 27개에서 비교 모드 보정, 확장 패킷 범위·파싱, 선택하지 않은 경로의 판정 차단, 구형 펌웨어 대체 사용 금지와 설정 저장을 확인했습니다.

EXTRACTED: 사용자의 게임 종료 확인 후 COM3 ESP8266EX의 4MB 전체 플래시를 `build/firmware/esp8266-com3-before-comparison-20261117.bin`에 백업하고 SHA256을 기록했습니다. 비교 펌웨어를 업로드하고 쓰기 해시 검증을 통과했습니다. 백업은 배포하지 않습니다.

EXTRACTED: 6초간 앱 리더로 두 경로를 실수신했습니다. 초기 1초 이후 약 5초간 우회 표본 249개를 받았고 bypass_available=true였습니다. 이 구간의 펌웨어 BP RMS는 176–343, NO BP RMS는 428–491이었습니다. 자세·안정/수축 상태를 지정하지 않은 구간이므로 어느 모드의 성능이 더 좋다는 결론은 내리지 않습니다. 요약은 `release/no-bandpass-live-check.json`에 있습니다.

EXTRACTED: 비교 EXE 자체 검사 11개 항목이 통과했습니다. `release/self-test-no-bandpass-2026.11.17.6.json`의 ok=true와 default_emg_signal=unfiltered를 확인했습니다. 배포 파일은 `release/EMG-Motion-Rhythm-No-Bandpass-windows-x64-2026.11.17.6.zip`입니다.

TODO: 실제 착용 상태에서 각 모드의 안정/수축 분리와 지연을 비교합니다. 신호 종류를 바꿀 때마다 안정/수축을 다시 보정합니다.

[다이어그램](../diagrams/emg-auto-calibration.md)은 Mermaid 지원 Markdown 미리보기로 엽니다. Graphify는 저장소 루트에서 `graphify .`로 수동 실행합니다.
