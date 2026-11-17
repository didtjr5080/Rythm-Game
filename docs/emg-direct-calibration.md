# 측정값 직접 보정 — 신호 품질 거부 조건 제거

EXTRACTED: 후속 [게임 표시 수정](emg-game-display.md)에서 ON 대비 비율을 MVC 백분율로 표시하던 부분을 제거하고 실제 활동값·ON/OFF·방향을 표시합니다. 보정 계산은 그대로입니다.

EXTRACTED: 사용자가 신호 차이·흔들림 등의 판단 기준으로 보정을 거부하지 말고 측정값을 적용하도록 요청했습니다. 고정 차이 5, 잡음 대비 2배, 모든 반복의 P95/P10 분리, 증가형만 허용하던 조건을 제거했습니다. 펌웨어·필터는 변경하지 않았습니다.

## 사용 방법

1. Connect / Test EMG 후 초기 안정 측정 약 4초를 진행합니다.
2. 화면 안내에 맞춰 힘빼기 2초 → 힘주기 2초를 3회 반복합니다(약 12초).
3. `측정값 보정 적용` 안내에서 증가형/감소형, ON/OFF를 확인하고 Save를 누릅니다.
4. 힘을 뺐다가 다시 주어 ACTIVE를 확인합니다. 한 번의 수축을 유지하면 기존 규칙대로 최대 한 노트만 판정합니다.

## 계산과 방향

EXTRACTED: 각 구간의 중앙값을 대표값으로 사용합니다. 초기 안정과 이완 3구간의 대표값 4개를 다시 중앙값으로 합치고, 수축 3구간 대표값도 중앙값으로 합칩니다. 값을 비교해 품질을 승인/거부하지 않습니다.

```text
R = median(초기 안정 중앙값, 이완1 중앙값, 이완2 중앙값, 이완3 중앙값)
A = median(수축1 중앙값, 수축2 중앙값, 수축3 중앙값)
ON  = round(R + 0.60 × (A − R), 3)
OFF = round(R + 0.20 × (A − R), 3)
```

EXTRACTED: A가 R보다 작으면 OFF > ON이며 리더는 감소형으로 작동합니다. 증가형은 OFF 미만 4표본으로 재준비 후 ON 이상 2표본에서 활성화합니다. 감소형은 OFF 초과 4표본으로 재준비 후 ON 이하 2표본에서 활성화합니다. 방향은 ON/OFF 순서로 복원되므로 별도 사용자 프로필·방향 설정 키를 만들지 않았습니다. 화면에 DIR: UP/DOWN을 표시합니다.

EXTRACTED: 예를 들어 R=200, A=170이면 ON=182, OFF=194입니다. 작은 차이, 겹치는 구간, 한 번의 약한 수축, 같은 값, ADC 범위 끝값이라도 계산·저장합니다. 값 범위는 0..1023이며 소수점을 유지합니다. 수동 ON 변경 또는 입력 소스 변경 시 기존 OFF를 해제하는 동작은 유지합니다.

EXTRACTED: 구간에 수신된 값 자체가 없거나 값이 비유한/ADC 범위 밖인 경우에는 계산하지 않습니다. 최소 60/30표본이라는 수량 조건도 제거했으며 각 구간에 실제 측정값이 있으면 계산합니다. 연결 끊김·부분/잘못된 시리얼 패킷 처리는 유지합니다. 이는 신호 품질 승인 조건이 아니라 측정 데이터 유무·숫자 형식 검사입니다.

EXTRACTED: R과 A가 같아도 보정값을 저장하지만 동일 신호에서 두 동작을 구분하는 새로운 정보를 만들지는 않습니다. 이번 변경은 보정 거부를 없앤 것이며 실제 인식 정확도를 보증하지 않습니다.

## 검증

EXTRACTED: 회귀 검사 33개를 통과했습니다. 작거나 같은 값·잡음이 큰 값·감소형·짧은 측정·ADC 끝값의 보정 적용, 감소형 수축/이완 반복 판정, 소수점·역순 ON/OFF 저장과 실제 GameWidget 전달, Qt 증가/동일/감소형 적용을 검사했습니다.

```powershell
.venv311/Scripts/python.exe -m unittest WorkOrder.verify_emg_serial WorkOrder.verify_emg_processing WorkOrder.verify_szh_filter WorkOrder.verify_emg_calibration_ui
```

EXTRACTED: Windows 2026.11.17.8 EXE를 `dist_windows_direct_calibration/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`에 생성했습니다. `release/self-test-direct-2026.11.17.8.json`에서 자체 검사 11개 항목 통과와 ok=true를 확인했습니다. 배포 파일은 `release/EMG-Motion-Rhythm-Direct-Calibration-windows-x64-2026.11.17.8.zip`입니다. 기존 비교 펌웨어와 호환되며 기본 신호는 NO BANDPASS입니다. Filtered activity에도 같은 직접 보정이 적용됩니다.

TODO: 실제 사용자 측정값으로 Save 후 증가형/감소형 동작을 확인합니다. 보드 재업로드는 필요 없습니다.

[다이어그램](../diagrams/emg-auto-calibration.md)은 Mermaid 지원 미리보기로 열고, Graphify는 저장소 루트에서 `graphify .`로 수동 실행합니다.
