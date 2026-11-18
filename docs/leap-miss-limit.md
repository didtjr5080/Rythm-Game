# Leap 핀치 모드: 연속 MISS 10회 종료

EXTRACTED: 핀치 모드에서 노트 판정 MISS가 10회 연속 발생하면 즉시 게임을 종료하고 결과 화면으로 이동한다. 음악이 아직 재생 중이어도 종료한다. 음악·게임 타이머·핀치 입력을 종료하는 기존 finish_game 경로를 사용한다.

EXTRACTED: PERFECT 또는 GOOD 판정은 연속 MISS 수를 0으로 초기화한다. 판정이 없는 프레임은 연속 횟수에 영향을 주지 않는다. 10회에 도달하면 이후 노트를 판정하지 않는다. 새 게임은 0회부터 시작한다.

EXTRACTED: 결과에는 `end_reason=10_consecutive_misses`와 `consecutive_misses=10`을 기록하고 `GAME OVER / 10 CONSECUTIVE MISSES`를 표시한다. 남은 노트를 추가 MISS로 계산하지 않는다.

EXTRACTED: 사용자의 근전도 보류 요청에 따라 EMG 동작과 입력·채보는 수정하지 않았다. 이 종료 제한은 Leap 핀치 모드에만 적용하며 근전도 모드에는 적용하지 않는다. 근전도 모드 자체를 삭제하거나 메뉴에서 숨기지는 않았다.

## 검증

EXTRACTED: 새 EXE는 `dist_windows_leap_miss10_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. `_internal`을 포함한 폴더 전체를 사용한다. 이전 설정·개인별 핀치 보정과 저장 음악·채보가 있으면 새 폴더에 복사하고 이전 폴더는 유지한다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_leap_miss10_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_miss_limit docs.check_rest_baseline docs.check_emg_assistance docs.check_game_modes docs.check_pinch_judgement docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -q
```

EXTRACTED: 소스 검사 49개 통과. 9회 유지·10회 종료, PERFECT/GOOD 초기화, 무판정 프레임 유지, 종료 후 득점 방지, EMG 12회 MISS에서도 계속 진행, 음악 재생 중 실제 GameWidget 종료·결과 기록을 확인했다.

EXTRACTED: 새 EXE 자체 검사 15항목 통과(`ok=true`, `pinch_consecutive_miss_limit=10`). 보고서는 `release/self-test-leap-miss10-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 기존 설정·핀치 보정 2개 파일을 보존하고 `README-LEAP-MISS10.txt`를 포함했다.

AMBIGUOUS: 실제 Leap 장치와 음악 재생 중 10회 연속 MISS 종료를 현장에서 확인해야 한다.

[Mermaid 흐름](../diagrams/leap-miss-limit.md)은 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
