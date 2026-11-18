# 연속 MISS 제한과 근전도 유지 노트

EXTRACTED: 2026.11.18.6에서 추가한 [핀치+신전 상위 모드](pinch-extension-mode.md)도 동일한 연속MISS10종료를 사용한다. 긴 노트 전용 규칙은 기존 근전도 모드에 적용하며 상위 모드는4레인 핀치 채보를 사용한다.

EXTRACTED: 2026-11-18 사용자 정정에 따라 두 게임 모두 **연속 MISS 10회**에 즉시 종료한다. PERFECT/GOOD이 나오면 연속 횟수를 0으로 초기화한다. 누적 MISS가 10회를 넘더라도 연속 10회가 아니면 종료하지 않는다. 10번째 연속 MISS 이후 판정과 음악을 멈추고 `GAME OVER / 10 CONSECUTIVE MISSES`를 표시한다. 이전 누적 MISS 결과 기록 표시는 호환성을 유지한다.

EXTRACTED: 근전도 자동 생성·샘플 채보는 1~4초 유지 노트만 사용한다. 노트 사이 휴식 간격과 박자 정렬을 유지한다. 곡 끝에 1초 이상 유지할 공간이 없으면 해당 노트를 생략하며 짧은 일반 노트로 대체하지 않는다. 이전 혼합 캐시는 자동 재생성 대상이며 파일을 직접 불러오는 경우에도 긴 노트로 다시 구성한다. 핀치 노트 생성과 두 센서 입력은 변경하지 않았다.

EXTRACTED: `docs/check_miss_limit.py`는 두 모드의 연속10회 종료·PERFECT/GOOD 시 초기화·누적10회 초과 후 계속·종료 후 판정 정지·음악 중단과 결과 사유를 검증한다. `docs/check_game_modes.py`는 긴 노트만 생성·기존 혼합 파일 변환·짧은 곡의 일반 노트 대체 금지를 검증한다. 전체92개 검사가 통과했다.

EXTRACTED: 구현은 `app/game/rhythm_game_engine.py`, `app/game/emg_chart.py`, `app/audio/note_generator_adapter.py`, 게임/결과 화면과 자체 검사에 반영했다. [규칙 도식](../diagrams/game-rule-update.md)은 Mermaid 미리보기로 확인한다. Graphify는 `graphify .` 또는 기존 출력에 `graphify update .`로 수동 실행하며 이번에는 실행하지 않았다.

AMBIGUOUS: 물리 센서와 스피커 실기는 별도 확인이 필요하다.

EXTRACTED: 이전 2026.11.18.3은 누적 MISS 기준 빌드이므로 사용자가 정정한 현재 규칙과 다르다. 최신 실행 파일과 검증 결과는 [배포 안내](windows-release.md)의 2026.11.18.4를 따른다.

EXTRACTED: 정정한 EXE의 자체검사19항목과 ZIP 검증이 통과했고 기존 사용자 데이터54파일을 해시 검증해 보존했다. 누적 MISS19회이면서 연속 MISS10회인 종료 경로를 두 모드 모두 EXE 검사에서 확인했다.
