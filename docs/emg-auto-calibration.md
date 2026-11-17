# EMG 필터링과 자동 임계값 보정

EXTRACTED: 최신 보정은 [측정값 직접 보정](emg-direct-calibration.md)입니다. 신호 차이·흔들림에 따른 보정 거부 조건을 제거했으며 감소형 변화도 적용합니다. 초기 안정 측정 후 12초 동안 힘빼기/수축을 3회 반복합니다.

EXTRACTED: 후속 SZH-GJD001 센서 수정은 [전용 필터 설명](szh-gjd001-filter.md)을 우선 참고합니다. ESP8266 v2는 센서 판매처 예제의 500Hz·60–100Hz 필터와 본 프로젝트의 40ms RMS를 사용합니다. PC 필터만으로 보드의 원신호 처리가 바뀌지는 않습니다.

EXTRACTED: 2026-11-17 사용자 승인으로 이번 작업에 필요한 EMG 입력·UI 변경을 허용받았습니다. `app/main.py`, 손 추적, 노트 생성, legacy_web은 변경하지 않았습니다.

## 사용 방법

EXTRACTED: Settings에서 Real EMG sensor와 장치/COM 포트, baud rate, 신호 종류를 선택하고 Connect / Test EMG를 누릅니다. 연결된 신호가 표시되면 다음 순서로 진행합니다.

1. 힘을 빼고 `1. 안정 상태 측정`을 누른 뒤 약 4초 유지합니다.
2. `2. 3회 반복 수축 / 임계값 자동 보정`을 누른 뒤 약 12초간 화면 안내에 맞춰 힘빼기 2초·힘주기 2초를 3회 반복합니다.
3. 완료된 임계값과 ACTIVE 표시를 확인합니다. 힘을 빼면 해제되고 다시 힘을 주면 활성화되어야 합니다.
4. Save를 눌러 기존 `app/data/settings.json`에 저장합니다. Back은 보정값을 저장하지 않습니다.

EXTRACTED: 초기 안정 측정은 처음 0.75초를 버리고 3초 동안 실제 수신 표본을 수집합니다. 반복 측정은 각 2초 구간의 첫 0.5초를 버리고 수집합니다. 각 구간에 실제 측정값이 있으면 계산하며 최소 표본 수 품질 조건은 없습니다. UI 반복 조회는 표본으로 세지 않습니다. 연결/포트/신호 종류 변경 시 안정 측정부터 다시 진행합니다. 측정 중 150ms 이상 신호가 없으면 취소합니다. 측정 중에는 임계값 숫자 입력을 잠급니다.

## 신호 경로와 계산

EXTRACTED: `firmware/nano_emg/nano_emg.ino`는 500Hz ADC 측정에서 DC 추정·정류·평활화를 수행하고 raw/filtered 패킷을 50Hz로 전송합니다. `envelope` 선택은 펌웨어의 filtered 값을, `raw` 선택은 센서 자체 ENV 출력을 A0에 연결한 경우의 직접 값을 사용합니다. `raw` 선택을 고속 RAW 파형 분석 기능으로 해석하면 안 됩니다.

EXTRACTED: `ActivityFilter`는 선택한 값에 3표본 중앙값과 계수 0.4 지수 평활화를 적용합니다. 필터는 UI 프레임이 아니라 수신 패킷마다 실행됩니다. 연결 해제·150ms 이상 공백에서 초기화됩니다. 음수·비유한·1023 초과 활동값은 입력을 차단합니다. 현재 10비트 ADC 활동값 범위를 전제로 합니다.

EXTRACTED: 판정, InputFusion의 filtered 표시, 설정 화면 ACTIVITY, 자동 보정에 같은 필터 값을 사용합니다. 별도의 UI 평활화는 제거했습니다. OFF 미만 4표본으로 재준비, ON 이상 2표본으로 활성화합니다. 자동 보정값이 없으면 기존 ON의 60%를 OFF로 사용합니다. 필터 추가로 수축/이완 판정에 수 표본 지연이 생길 수 있습니다.

EXTRACTED: 초기 안정과 이완 3구간 중앙값들을 합친 중앙값 R, 수축 3구간 중앙값들을 합친 중앙값 A로 ON/OFF를 계산합니다. 차이나 흔들림 기준으로 거부하지 않습니다.

```text
span = A - R
ON = round(R + 0.60 * span, 3)
OFF = round(R + 0.20 * span, 3)
```

EXTRACTED: 신호 겹침·흔들림·감소·같은 값·ADC 범위 끝값도 계산·저장합니다. 데이터가 없는 구간이나 잘못된 숫자만 계산할 수 없습니다. ON/OFF 순서에 따라 증가형/감소형을 적용합니다. 소수점 ON/OFF는 함께 저장되며 게임과 별도 보정 화면에서도 사용합니다. 임계값 숫자 입력이나 입력 소스를 수동 변경하면 보정 OFF를 해제하고 기본 증가형 60% 해제 규칙으로 돌아갑니다. [현재 계산과 검증](emg-direct-calibration.md)을 참고하세요.

## 이전 프로젝트와의 관계

EXTRACTED: 참고한 `C:/EMGcontrol/GAME/EMGGoalGame/emg_game/live.py`는 안정/수축 단계를 분리하고 신호 부족·연결 끊김을 거부합니다. 이번 구현도 이 흐름을 따르되 자세 판정은 추가하지 않았습니다.

EXTRACTED: 이전 프로젝트 `emg_game/ai_features.py`의 20–200Hz Butterworth 필터는 500Hz RAW 입력을 전제로 합니다. 현재 PC 입력 50Hz에 그대로 적용하지 않았습니다. 최초 2026.11.17.3 작업에서는 펌웨어를 변경하지 않았으며, 후속 SZH-GJD001 작업에서 ESP8266의 필터를 센서 판매처 예제 기준으로 변경했습니다.

INFERRED: 순간 스파이크 제거와 표시/판정 신호 통일은 임계값 조정의 일관성을 개선할 수 있습니다. 실제 전극 잡음·전원 잡음 제거 성능은 현장 측정으로 확인해야 합니다. 이번 필터는 고속 RAW 대역통과/노치 필터를 대신하지 않습니다.

EXTRACTED: 사용자가 현재도 SZH-GJD001을 사용한다고 확인했습니다. 후속 업로드에서 COM3 ESP8266의 펌웨어 v2 식별과 실수신을 확인했습니다. AMBIGUOUS: 안정·수축 상태를 지정한 신호 품질과 인식 성능은 아직 확인하지 않았습니다. 최신 EXE와 백업·업로드 결과는 [센서 전용 설명](szh-gjd001-filter.md)을 참고합니다.

## 검증과 TODO

EXTRACTED: `python -m unittest WorkOrder.verify_emg_serial WorkOrder.verify_emg_processing`의 17개 검사 통과. 단일 스파이크, 지속 수축, 오래된 표본, 연결 해제/재연결, 잘못된 입력, 임계값 저장, 안정/수축 분리 및 보정 거부 조건을 검사했습니다.

EXTRACTED: 후속 빌드에서 Python 3.11 가상환경과 PyQt6를 설치했습니다. 오프스크린 설정 화면의 안정/수축 보정, 구분 부족 시 임계값 유지, 신호 끊김 취소, 저장 전달값을 확인했습니다. 동일 환경에서 회귀 검사 17개도 통과했습니다.

EXTRACTED: `build_windows.ps1 -Version 2026.11.17.3`으로 이번 변경을 포함한 EXE와 `release/EMG-Motion-Rhythm-windows-x64-2026.11.17.3.zip`을 생성했습니다. `release/self-test.json`의 `ok`는 true이며 MediaPipe 네이티브 추론, 한글 모델 경로, Qt 렌더링, 오디오 분석, 데스크톱 화면 import 등 11개 검사 항목을 통과했습니다. ZIP은 EXE와 `_internal` 폴더 전체를 포함합니다.

TODO: 실제 센서의 안정/수축 판정과 필터 지연을 확인합니다. GUI 검사는 오프스크린·모의 신호로 진행했으므로 물리 EMG 장치의 성능 검증은 남아 있습니다.

다이어그램: [자동 보정 흐름](../diagrams/emg-auto-calibration.md)을 Mermaid 지원 Markdown 미리보기로 엽니다. Graphify는 저장소 루트에서 `graphify .`로 수동 실행합니다. 이번 작업에서는 실행하지 않았으므로 기존 graphify-out은 최신 구조를 반영하지 않습니다.
