# 게임 시작 후 100% 초과 표시 수정

EXTRACTED: 기존 게임 HUD는 `InputFusion.emg_mvc_ratio = filtered_emg_value / max(1, ON)`을 백분율로 표시하며 MVC ACTIVE라고 표기했습니다. ON은 입력 판정 임계값이며 최대 수축값으로 측정된 값이 아닙니다. 따라서 현재 활동값이 ON보다 크면 100%를 넘는 표시였습니다. 감소형에서는 이완값이 ON보다 높으므로 이완 중에도 100% 초과로 보일 수 있었습니다.

EXTRACTED: 이번 수정에서 이 비율 계산과 MVC 백분율 표시를 제거했습니다. 게임 HUD는 다음을 표시합니다.

- 실제 판정에 사용하는 EMG 활동값: 소수점 두 자리
- ACTIVE/REST 상태: 실제 `emg_activated` 값
- ON/OFF: 소수점 세 자리
- UP/DOWN: 증가형/감소형 방향

EXTRACTED: 원형 테두리는 활성 상태를 표시하며 활성일 때 채워집니다. 측정한 최대 수축 대비 강도나 백분율을 의미하지 않습니다. 실제 수신 신호·보정 계산·ON/OFF 저장·수축 판정은 이번 표시 수정으로 변경하지 않습니다. 숫자를 100%로 잘라 숨기거나 시작 시 새 임계값으로 재계산하지 않습니다.

## 저장값 확인과 검사

EXTRACTED: 사용자의 실행 중인 v2026.11.17.8 앱 경로와 설정 파일을 읽기 전용으로 확인했을 때 선택 신호는 unfiltered, ON=39.544, OFF=38.552였습니다. 이는 확인 시점의 저장값이며 게임 내 실시간 활동값을 측정한 결과는 아닙니다.

EXTRACTED: Settings에서 보정을 마친 뒤 Save를 눌러야 해당 값이 게임에 사용됩니다. Back은 새 보정값을 저장하지 않습니다. 게임은 마지막으로 저장한 설정을 읽습니다.

EXTRACTED: 회귀 검사 34개가 통과했습니다. 실제 임시 설정 파일에 증가형·감소형 소수점 ON/OFF를 저장하고 실제 GameWidget을 생성한 뒤 리더 값과 설정 파일 바이트가 변경되지 않았는지 확인했습니다. HUD에 200.00과 REST가 전달되고 백분율 값이 전달되지 않는 것도 확인했습니다. 물리 카메라·시리얼·스피커는 사용하지 않았습니다.

```powershell
.venv311/Scripts/python.exe -m unittest WorkOrder.verify_emg_serial WorkOrder.verify_emg_processing WorkOrder.verify_szh_filter WorkOrder.verify_emg_calibration_ui
```

INFERRED: 이번에 확인된 100% 초과 표시는 잘못 해석될 수 있는 계산·표기 때문입니다. 별도로 실제 신호값이 화면 전환 전후 달라지는 현상까지 설명하거나 해결했다고 주장하지 않습니다. 그 경우 동일 신호 모드·실제 활동값·연결 상태를 별도로 비교해야 합니다.

EXTRACTED: Windows 2026.11.17.9 EXE는 `dist_windows_emg_display/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`에 생성했습니다. `release/self-test-emg-display-2026.11.17.9.json`의 ok=true와 자체 검사 11개 항목 통과를 확인했습니다. 배포 파일명은 `release/EMG-Motion-Rhythm-EMG-Display-windows-x64-2026.11.17.9.zip`입니다. 사용자 설정은 ZIP에 포함하지 않습니다.

EXTRACTED: ZIP 생성 후 기존 v8 앱의 최신 설정 파일을 새 로컬 실행 폴더로 그대로 복사했습니다. 복사 시점의 기존 파일은 ON=20.213, OFF=10.967, unfiltered였으며 복사된 파일 바이트와 로드된 ON/OFF가 원본과 같은지 확인했습니다. 앞서 확인한 39.544/38.552와는 확인 시점이 다릅니다. 이번 작업의 코드·도구는 기존 v8 설정 파일에 쓰지 않았습니다. 배포 ZIP에는 사용자 설정을 넣지 않았고 SHA256을 검증했습니다.

TODO: 실제 사용자 환경에서 설정 화면과 게임 화면의 활동값·ON/OFF를 비교합니다. 보드 업로드는 필요 없습니다.

[다이어그램](../diagrams/emg-auto-calibration.md)은 Mermaid 지원 미리보기로 확인하며, Graphify 수동 실행은 저장소 루트의 `graphify .`입니다.
