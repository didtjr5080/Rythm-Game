# 높은 안정 신호에서의 자동 보정 실패 수정

EXTRACTED: 아래는 v2026.11.17.5의 수정 기록입니다. 고정 차이 5 기준을 제거한 최신 방식은 [안정 잡음·반복 수축 보정](emg-adaptive-calibration.md)을 참고하세요.

EXTRACTED: 사용자 스크린샷에는 SZH-GJD001 v2 연결과 VALUE 323, ACTIVE False, 안정·수축 구분 부족 안내가 표시돼 있습니다. INFERRED: 실제 신호 차이 부족 또는 보정 계산의 높은 안정값 처리 문제가 가능한 원인입니다. 스크린샷에는 두 측정 구간의 값이 없어 어느 원인인지 확정하지 않습니다.

EXTRACTED: 이전 계산의 `ceil(noise / 0.55)`는 기존 OFF=ON×0.6 조건을 맞추기 위한 항이었습니다. 안정 300·수축 400처럼 구분 가능한 일정 신호도 ON이 546이 되어 보정을 거부하는 문제가 있었습니다. 수축 판정 ON과 이완 해제 OFF를 별도로 계산·저장하도록 수정했습니다.

EXTRACTED: 현재 계산은 안정 P95와 수축 P10 차이를 사용합니다. ON은 차이의 60%, OFF는 20% 위치이며, 예시 300/400에서는 ON 360/OFF 320이 됩니다. 표본 부족·포화·겹침·역전은 계속 거부합니다. 실패 시 P95/P10/차이를 표시하고 기존 ON/OFF를 보존합니다. 안정 측정 후에는 중앙값을, 성공 후에는 안정/수축 중앙값과 ON/OFF를 표시합니다.

EXTRACTED: 저장 키는 기존 `emg_threshold`와 새 `emg_release_threshold`입니다. OFF가 없거나 ON 이상인 잘못된 값이면 기본 ON×0.6을 사용합니다. 사용자 설정을 자동 덮어쓰지 않으며 Save를 눌러야 저장됩니다. 보정 ON/OFF를 적용할 때 기존 활성·재준비 상태를 지웁니다. 임계값을 수동 변경하거나 입력 소스를 바꾸면 보정 OFF를 해제합니다. 게임 InputFusion과 별도 CalibrationScreen도 저장된 OFF를 사용합니다.

EXTRACTED: 다음 회귀 검사 24개를 통과했습니다. 높은 안정값에서 보정 성공, 수축/이완 반복 판정, 보정값 저장/유효성, 게임으로의 OFF 전달, 보정 실패 시 값 유지, 수동 임계값 변경 시 OFF 해제를 포함합니다.

```powershell
.venv311/Scripts/python.exe -m unittest WorkOrder.verify_emg_serial WorkOrder.verify_emg_processing WorkOrder.verify_szh_filter WorkOrder.verify_emg_calibration_ui
```

EXTRACTED: 이번 수정은 앱의 보정·판정 경계 처리 변경입니다. ESP8266 필터나 보드 펌웨어는 변경하지 않습니다.

EXTRACTED: Windows 빌드 2026.11.17.5의 EXE는 `dist_windows_szh_v5/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`입니다. `release/self-test-2026.11.17.5.json`에서 ok=true와 자체 검사 11개 항목 통과를 확인했습니다. 배포 ZIP 파일명은 `EMG-Motion-Rhythm-windows-x64-2026.11.17.5.zip`입니다.

TODO: 새 EXE에서 안정·수축을 다시 측정합니다. 실패하면 새 안내의 안정 P95·수축 P10·차이를 확인해 실제 신호 겹침 여부를 판단합니다. 스크린샷의 실제 실패 원인이 계산 제한 하나였다고 단정하지 않습니다.

[다이어그램](../diagrams/emg-auto-calibration.md)은 Mermaid 지원 미리보기로 확인하고 Graphify는 루트에서 `graphify .`로 수동 실행합니다.
