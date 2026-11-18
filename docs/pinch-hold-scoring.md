# 기준선 핀치 유지 판정 (EMG 제외)

EXTRACTED: 이후 [게임 선택과 두 모드 채보](game-modes.md)를 추가했다. 이 문서의 EMG 제외 규칙은 **핀치 모드**에 적용한다. 별도의 근전도 모드는 박자 수축과 긴 근활성 유지 노트를 사용한다.

EXTRACTED: 이번 요청으로 게임 점수 조건에서 EMG를 제외했다. 오른손의 올바른 레인 핀치를 유지하고 있을 때 노트가 기준선에 도착하면 판정한다. 노트마다 핀치를 다시 시작하거나 손을 펼칠 필요가 없다. 개인 보정과 직접 핀치 전환, MIDDLE → RING 채보 제약을 유지한다.

## 판정 동작

EXTRACTED: `judge_note()`는 노트 예정 시각보다 이르면 판정하지 않는다. 예정 시각 이후 손이 감지되고 입력 레인이 노트 레인과 같으면 점수를 부여한다. `emg_activated`와 EMG 수축 시작 여부를 확인하지 않는다. 같은 핀치를 유지해도 같은 레인의 다음 노트가 도착하면 각각 한 번씩 득점한다.

EXTRACTED: 기존 시간 허용값을 유지하여 도착 시각부터 50ms 이내는 PERFECT(1000점), 50ms 초과~100ms 이내는 GOOD(500점), 100ms를 넘기면 MISS이다. 렌더링·입력 갱신 간격 때문에 도착 시각을 정확히 0ms에 읽지 못하는 경우를 허용한다. 기준선 도착 이전에는 미리 득점하지 않는다.

EXTRACTED: 잘못된 레인, 핀치 없음, 손 추적 손실은 득점하지 않는다. 이미 판정된 노트는 재득점하지 않는다. EMG 활성 상태만으로 점수를 받을 수 없다.

## 입력과 화면

EXTRACTED: 게임은 `InputFusion(use_emg=False)`로 실행하여 실제·모의 EMG 리더를 생성하거나 읽지 않는다. 기존 로그 필드의 EMG 값은 0/False이며 실제 EMG 측정 결과가 아니다. 설정 화면의 EMG 테스트·보정과 메인 화면의 기존 입력 구성은 유지한다.

EXTRACTED: 게임에서 숫자키·방향키·SPACE로 손 상태를 대신 만드는 경로를 제외했다. 게임 득점은 실제 추적 핀치로 판정한다. ESC 종료는 유지한다. 게임 HUD의 EMG 파형·게이지 대신 핀치 유지 안내를 표시하고 새 결과에는 `PINCH HOLD` 모드를 표시한다. 기존 EMG 방식 저장 결과의 표시는 유지한다.

## 검증과 실행

EXTRACTED: 새 실행 파일은 `dist_windows_leap_pinch_hold_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. 파일명은 기존 빌드 설정을 유지하지만 게임은 EMG를 사용하지 않는다. `_internal`을 포함한 폴더 전체를 사용한다. 이전 직접 핀치 전환 빌드의 개인별 보정 파일을 검증 후 복사했으며 이전 실행 폴더는 유지했다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_leap_pinch_hold_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_pinch_judgement docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 소스 검사 21개 통과. EMG 없이 연속 노트 득점, 도착 전 판정 금지, 시각 경계, 핀치 해제·오레인·손 놓침 시 실패, 노트 중복 득점 방지, 게임의 실제·모의 EMG 장치 미생성, 키보드의 가짜 핀치 득점 방지와 화면 렌더링을 검사했다. 기존 기능 회귀 검사도 통과했다.

EXTRACTED: 새 EXE 자체 검사 11항목 통과(`ok=true`, `gameplay_emg_enabled=false`). 게임의 EMG 리더 미생성, EMG=False인 상태에서 같은 핀치로 연속 노트 각각 1000점, 중복 득점 방지를 확인했다. 보고서는 `release/self-test-leap-pinch-hold-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다.

AMBIGUOUS: 실제 Leap 장치에서 음악과 기준선 시각에 맞춰 플레이하는 검증은 남아 있다.

[Mermaid 판정 흐름](../diagrams/pinch-hold-scoring.md)은 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
EXTRACTED: 최신 핀치도 [Leap 전용](pinch-leap-only.md)이며 EMG 일치·가중치 조건은 제거했습니다. 시작 전 Leap 보정은 매 게임 진행합니다.
