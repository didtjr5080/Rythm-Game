# 게임 선택과 세 모드 채보

EXTRACTED: 2026.11.18.6부터 기존 두 모드 외에 **핀치 + 신전 상위 모드**를 추가했다. Leap핀치와 유효한 암밴드 신전이 같은 판정 순간에 필요하다. 기본 두 모드는 보존했다. [상위 모드](pinch-extension-mode.md)를 참고한다. 아래 두 모드 설명은 기본 모드 기록이다.

EXTRACTED: 2026-11-18 최신 규칙은 두 모드 모두 **연속 MISS 10회 즉시 종료**, 근전도는 **1초 이상 긴 유지 노트만 생성**이다. PERFECT/GOOD이면 연속 횟수는 0이 된다. 아래 일반 박자 수축 노트 설명보다 [현재 규칙](game-rule-update.md)을 우선한다.

EXTRACTED: 현재 근전도 입력은 수동 보정 대신 [시작 전 3초 안정 기준 +0.01](emg-rest-baseline.md)을 사용한다. 근전도 게임 선택 후 측정이 끝나야 음악과 노트가 시작한다. 핀치 보정은 유지한다.

EXTRACTED: 이후 [EMG 보정·게임 값 일치와 입력 인정 범위 확대](emg-assisted-input.md)를 적용했다. 현재 근전도 박자 인정은 ±350ms/PERFECT 150ms이며 긴 노트에서 400ms 이내의 짧은 활성 저하 후 회복을 허용한다. 아래 ±100ms/즉시 해제 실패 설명은 초기 두 모드 구현 기록이다.

EXTRACTED: 메인 화면의 **게임 시작**을 **게임 선택**으로 변경했다. 게임 선택 화면에서 선택한 노래로 **근전도 리듬·유지 게임** 또는 **핀치 리듬 게임**을 시작한다. 노래가 없으면 각 모드의 샘플 채보를 사용한다. 결과 화면의 다시하기는 같은 모드를 유지하며 게임 선택으로 돌아가 다른 모드를 고를 수도 있다.

| 모드 | 입력 | 레인 | 목표 |
| --- | --- | --- | --- |
| 근전도 리듬·유지 | EMG 센서 | 1 | 박자에 맞춘 새 수축과 긴 근활성 유지 |
| 핀치 리듬 | Leap Motion 오른손 | 4 | 기준선에서 해당 레인 핀치 유지 |

EXTRACTED: 근전도 모드는 Leap 트래커를 생성하지 않고, 핀치 모드는 EMG 리더를 생성하지 않는다. 웹캠과 MediaPipe 입력은 계속 비활성화한다. 기존 EMG 센서 처리·필터·ON/OFF 임계값 코드는 수정하지 않고 게임 판정에서 활용한다.

## 노트 생성과 저장

1. 음악을 추가하거나 저장된 음악을 불러온다.
2. **노트 생성**을 한 번 누른다. 같은 곡 분석을 사용해 두 모드의 채보를 함께 저장한다.
3. **게임 선택**에서 원하는 모드를 고른다.

EXTRACTED: `save_notes_json(..., analysis=analysis)`가 핀치 노트와 EMG 노트를 한 파일에 원자적으로 저장한다. 기존 `notes` 필드는 핀치 채보를 유지하며 `emg_notes`에 1레인 EMG 채보를 추가한다. 스키마 버전은 2이다. EMG 긴 노트는 `duration_ms > 0`, 짧은 노트는 `duration_ms = 0`이다.

```json
{
  "schema_version": 2,
  "lane_count": 4,
  "notes": [{"note_id": 0, "lane": 0, "hit_time_ms": 2000}],
  "emg_notes": [
    {"note_id": 0, "lane": 0, "hit_time_ms": 2000, "duration_ms": 0},
    {"note_id": 1, "lane": 0, "hit_time_ms": 3000, "duration_ms": 0},
    {"note_id": 2, "lane": 0, "hit_time_ms": 4000, "duration_ms": 2000}
  ]
}
```

EXTRACTED: 위 JSON은 형식 설명용 축약 예시이다. 실제 핀치·EMG 채보의 노트 수와 시각은 모드별로 다르다. 핀치 채보에는 MIDDLE → RING 전환 금지 규칙을 유지한다.

EXTRACTED: EMG 시작 시각은 오디오 분석의 `beats`를 사용한다. 박자가 없으면 BPM 기반 박자 격자를 사용하며, BPM이 없거나 지원 범위 20~300 밖이면 120을 사용한다. 처음 2초는 준비 구간으로 둔다. 짧은 노트 두 개 뒤에 긴 노트를 만드는 패턴을 반복한다. 긴 노트는 보통 네 박 길이이며 BPM에 따라 약 1~4초 범위에서 박 단위 길이를 선택한다.

EXTRACTED: 다음 노트까지 최소 `max(900ms, 두 박 길이)`의 휴식 간격을 확보한다. 긴 노트는 종료 후 이 간격을 적용하므로 다른 노트와 겹치지 않는다. 곡 종료 200ms 전까지 긴 노트가 끝나도록 줄이며 1초를 확보하지 못하면 짧은 노트로 만든다. 매우 짧은 곡은 긴 노트가 없거나 준비 구간 이후 노트가 없을 수 있다.

EXTRACTED: 이전 형식 채보도 로딩할 수 있다. EMG 채보가 없는 파일은 기본 박자 격자로 EMG 채보를 메모리에서 만든다. 원본 파일을 덮어쓰지 않는다. 실제 곡에서 검출한 박자를 사용하려면 **노트 생성**으로 다시 저장한다.

## EMG 판정과 긴 노트

EXTRACTED: 짧은 노트는 예정 시각 ±100ms 안에 **새로운 근활성 시작**이 있어야 한다. 기존 ON/OFF 임계값과 실제 센서 리더의 휴식 후 재활성 조건을 사용한다. 미리 계속 수축한 채로 다음 짧은 노트를 자동 득점할 수 없다. 시작 오차 50ms 이내는 PERFECT(1000점), 그 외 허용 범위는 GOOD(500점)이다.

EXTRACTED: 긴 노트도 박자에 맞춰 새로 수축해야 시작된다. 시작 후에는 꼬리가 기준선을 지날 때까지 활성 상태를 유지해야 한다. 유지 도중 비활성화되거나 게임 입력 검사 간격이 250ms보다 길면 MISS이다. 꼬리까지 유지해야 한 번 득점하며 중간에는 점수를 주지 않는다. 판정 등급은 시작 오차를 기준으로 정한다. 실제 센서 데이터 신선도 검사는 기존 EMG 리더에서 수행한다.

EXTRACTED: 긴 노트의 몸통·꼬리를 화면에 그리며 유지 중 남은 시간을 표시한다. 머리는 기준선에 고정되고 꼬리가 내려오며 짧아진다. 판정창이 지나도 활성 긴 노트는 표시와 판정을 유지한다. 샘플 게임 종료는 마지막 긴 노트의 끝 시각까지 고려한다.

EXTRACTED: 결과에 `input_mode`, `hold_note_count`, `hold_success_count`, `hold_target_duration_ms`를 저장한다. 결과 화면은 EMG 긴 노트 성공 개수를 표시하고 결과 목록은 EMG/PINCH/LEGACY를 구분한다. 실제 누적 근활성 시간 측정값을 새로 계산하는 기능은 추가하지 않았다.

EXTRACTED: Settings에서 실제 EMG 장치·신호 유형·임계값을 설정하고 연결 테스트·보정을 할 수 있다. 명시적 Demo/SPACE 모드에서는 SPACE로 수축을 모의한다. 실제 센서 모드에서는 SPACE가 입력을 대신하지 않는다.

## 핀치 모드 유지 사항

EXTRACTED: 기존 4레인 기준선 핀치 유지 판정, 개인별 핀치 보정, 손을 펼치지 않는 직접 전환을 유지한다. EMG는 필요하지 않다. 노트 도착 전에는 득점하지 않으며 기존 +100ms 허용 구간을 사용한다.

## 검증과 TODO

EXTRACTED: 새 실행 파일은 `dist_windows_dual_mode_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. `_internal`을 포함한 전체 폴더를 사용한다. 이전 핀치 유지 빌드의 설정·개인별 보정 파일 2개를 새 폴더에 복사했다. 이전 폴더는 변경하지 않았다. 새 실행 폴더에는 `README-DUAL-MODE.txt`와 `self-test.json`을 포함했다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_dual_mode_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_game_modes docs.check_pinch_judgement docs.check_pinch_switch docs.check_leap_calibration docs.check_lane_transition docs.check_leap_input -v
```

EXTRACTED: 소스 검사 30개 통과. 두 채보 저장·모드별 로딩, 이전 초 단위 채보 호환, 박자 격자·휴식 간격·곡 종료, EMG 신규 수축 판정, 긴 노트 종료 득점·중도 해제·입력 공백 실패, 긴 노트 가시성·종료 시각을 검사했다. 실제 게임 선택 버튼으로 두 모드를 전환하고 EMG 모드가 Leap를 열지 않으며 핀치 모드가 EMG를 열지 않는 것과 렌더링·데모 키 처리를 확인했다. 기존 회귀 검사도 통과했다.

EXTRACTED: 새 EXE 자체 검사 13항목 통과(`ok=true`, `game_modes=[pinch, emg]`, `emg_hold_notes_enabled=true`). 실제 오디오를 분석해 두 채보를 같은 파일에 저장하고 각각 로딩했다. 게임 선택·EMG 단독 입력·긴 노트 렌더링·꼬리 종료 득점·중도 해제 실패를 검사했다. 보고서는 `release/self-test-dual-mode-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 보고서의 `gameplay_emg_enabled=false`는 기본 검사 게임인 핀치 모드의 상태이며 별도 EMG 모드의 리더 생성은 별도로 검증했다.

AMBIGUOUS: 실제 EMG 센서와 Leap 장치를 연결한 음악 동기·근활성 유지 플레이는 현장 확인이 필요하다. 유지 길이와 휴식 간격은 게임 생성 규칙이며 개인별 훈련 처방을 검증한 값은 아니다.

[Mermaid 모드·채보 흐름](../diagrams/game-modes.md)은 Mermaid 지원 Markdown 미리보기에서 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 자동 갱신하지 않았다.
EXTRACTED: 최신 핀치는 [Leap만 사용](pinch-leap-only.md)하며 armband는 별도 근전도 모드에서 사용합니다. 핀치의 armband 일치·가중치·단독 테스트는 제거했습니다.
