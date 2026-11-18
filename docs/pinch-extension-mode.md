# 핀치 + 신전 상위 리듬 게임

EXTRACTED: 2026.11.18.8에서 선택 카드 이미지를 사용자의 핀치+암밴드 첨부 원본으로 교체했다. [이미지 안내](game-selection-images.md)를 참고한다. 입력·보정·해금 규칙은 변경하지 않았다.

EXTRACTED: 2026.11.18.7부터 [같은 플레이어 프로필의 기본 두 모드 정상 완주](player-profiles.md)가 필요하다. 저장된 핀치·근전도 보정값으로 바로 시작하며, 아래 매번 보정 설명은 이전 기록이다.

EXTRACTED: 2026-11-18 사용자가 선택한 '핀치+신전 동시 확인' 방식으로 세 번째 모드 `pinch_extension`을 추가했다. 기존 두 모드는 유지한다.

| 게임 선택 | 입력 | 채보 | 시작 전 측정 |
| --- | --- | --- | --- |
| 핀치 리듬 게임 | Leap 전용 | 기존 4레인 핀치 | Leap 개인별 보정 |
| 근전도 리듬·유지 게임 | armband 전용 | 1레인 긴 노트 | 3.0초 최저값 |
| 핀치 + 신전 상위 리듬 게임 | Leap와 armband 동시 | 기존 4레인 핀치 | Leap 보정 후3.0초 최저값 |

EXTRACTED: 상위 모드는 해당 레인의 Leap 핀치, 손 추적 유효성, 암밴드 신전 활성과 데이터 신선도가 판정 순간 모두 충족돼야 득점한다. 핀치만, 신전만, 다른 레인, 손 추적 손실, 신호가 오래됐거나 읽기 실패한 경우에는 득점하지 않는다. 기존 핀치와 동일한 판정 시간 창 안에 두 조건이 갖춰지면 한 번만 판정하며 창이 지나면 MISS다. 가중치 합산이나 순서 동작을 사용하지 않는다. 물리 센서 timestamp를 일치시키는 융합이 아니라 동일한 게임 판정 시점의 유효 입력을 함께 확인한다.

EXTRACTED: 게임 선택의 '핀치 + 신전 상위 리듬 게임'을 누르면 메뉴 카메라를 종료하고 Leap 개인별 보정 후 게임 화면에서3.0초를 기록한다. 기록 중 음악·노트·득점은 진행하지 않는다. 최저값 이상(같은 값 포함)이면 신전이다. 완료 후 음악을0부터 시작한다. 암밴드에서 신전이 확인돼도 Leap 레인을0으로 바꾸지 않는다. 현재 EMG값·최저값과 `EXTENSION READY / REQUIRED`를 화면에 표시한다.

EXTRACTED: 두 입력을 동시에 여는 것은 새 모드에서만 적용한다. 기본 핀치는 계속 암밴드를 열지 않고, 기존 근전도 모드는 Leap를 열지 않는다. 새 모드도 기존 공유 EMGSession lease를 사용한다. 두 센서 읽기 경로는 가중 합산하지 않으며, EMG 읽기 예외는 신선하지 않은 입력으로 표시해0값이 최저값 기준을 통과하지 않도록 했다.

EXTRACTED: 연속MISS10회 종료·PERFECT/GOOD 시 연속 횟수 초기화·음악 오류 중단 규칙을 유지한다. 결과는 `input_mode=pinch_extension`, `pinch_input_source=leap_and_emg_extension`으로 저장하고 결과/기록 목록에 상위 모드 이름을 표시한다. 다시하기는 같은 모드를 유지하며 Leap 보정과 EMG측정을 새로 한다. 저장된 핀치 채보를 그대로 사용하므로 세 번째 채보를 별도 생성할 필요가 없다.

EXTRACTED: 기존95+신규9=104개 검사 통과. 새 검사는 동시 조건·신호 손실·시간 창·기존 모드 보존·4레인 채보·연속MISS·새 카드·Leap 보정 수락/취소·3초 지연·실제 최소값 비교·결과 구분·EMG 읽기 오류를 포함한다. source 자체 검사에는 동시 판정과 실제 GameWidget의 두 센서 활성·지연·레인 유지·렌더링 검사도 추가했다.

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.venv311/Scripts/python.exe -m unittest discover -s docs -p 'check_*.py'
```

AMBIGUOUS: 실제 두 센서를 동시에 착용한 상태의 입력 성공률·체감 난이도·장치 지연은 현장 확인이 필요하다. 자동 검사는 모의 입력을 사용한다.

EXTRACTED: `dist_windows_advanced_20261118_6/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`로 빌드했고 EXE자체검사21항목 통과. 세 모드와 동시판정·실제 GameWidget의3초지연/레인보존/렌더링을 EXE에서도 확인했다. ZIP검증 통과, 기존 사용자 데이터60파일 원본보존·해시복사. 파일·보고서는 [배포 안내](windows-release.md)에 기록했다.

EXTRACTED: [상위 모드 흐름도](../diagrams/pinch-extension-mode.md)는 Mermaid 지원 Markdown 미리보기로 확인한다. Graphify는 저장소 루트에서 `graphify .` 또는 `graphify update .`로 수동 실행하며 이번에는 실행하지 않았다.
