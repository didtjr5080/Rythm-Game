# 핀치에서 armband 연동 제거

EXTRACTED: 아래는 기존 배포 기록이다. 현재 작업 트리는 핀치 입력에 armband를 사용하지 않으면서 공유 EMG 연결은 유지한다. 아래의 '핀치 진입 시 연결 종료' 설명과 당시 검사는 이전 동작이다. [현재 연결·음악 검증](music-session-review.md)을 참고한다.

EXTRACTED: 핀치 게임은 다시 Leap Motion만 사용한다. armband 신호 수집·핀치 의도 분류·두 센서 일치 검사·70/30 가중 합산·점수 HUD·armband 단독 테스트 체크박스를 제거했다. 관련 분류 및 합산 모듈도 삭제했다. 별도의 EMG 리듬·유지 모드는 OYMotion 입력과 기존 긴 노트 규칙을 유지한다.

EXTRACTED: 게임 선택 → 핀치 선택 → 매번 열린 손과 네 핀치를 Leap으로 보정 → 저장 성공 후 시작 순서다. 재시도에도 새 보정이 필요하다. 각 동작은 기존처럼 1초 준비 후 3초 측정하고 최소 25개 유효 Leap 프레임을 요구한다. 취소 또는 측정·저장 실패 시 시작하지 않는다. armband 연결·보정·패턴 분리 조건은 요구하지 않는다.

EXTRACTED: 핀치 진입 시 메뉴에서 유지하던 공유 EMG 연결은 종료한다. 보정 창과 핀치 GameWidget은 EMG reader를 요청하지 않는다. 입력은 기존 Leap 핀치 분류의 레인·손 추적 유효성만 사용한다. 기준선 핀치 유지 득점, 손을 펴지 않는 직접 핀치 전환, 네 레인, MIDDLE 다음 RING 제한과 연속 MISS 10회 종료는 유지한다.

EXTRACTED: 핀치 HUD에서 EMG·합산 점수를 제거하고 Leap 핀치 상태만 표시한다. 새 세션의 armband 의도·합산 점수 필드도 제거했으며 입력 출처는 `leap_only`다. 이전 세션 데이터와 배포 폴더는 삭제하지 않는다. 수동 EMG 보정과 카메라 입력을 되살리지 않았다.

EXTRACTED: 관련 소스 검사 65개 통과. `docs/check_leap_only_pinch.py`는 Leap 보정에서 armband 연결을 요청하지 않음, 단독 테스트 옵션 제거, 핀치 진입 시 이전 EMG 스트림 종료, EMG reader 없이 실제 GameWidget의 Leap 득점·손 소실 시 미득점·HUD 렌더링을 검증한다. 기존 EMG 시작 전 3초 안정값·+0.01·긴 노트와 핀치 종료 규칙 검사도 통과했다.

새 실행 폴더: `dist_windows_pinch_leap_only_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`. `_internal` 포함 폴더 전체를 사용한다.

EXTRACTED: 새 EXE 자체 검사 16항목 통과(`ok=true`, `pinch_input_source=leap_only`, `gameplay_emg_enabled=false`). 새 PYZ에서도 제거한 `pinch_intent`·`weighted_pinch` 모듈이 없고 별도 근전도용 `oymotion_reader`가 유지된 것을 확인했다. 기존 설정·Leap 프로필을 복사했다. 보고서는 배포 폴더의 `self-test.json` 및 `release/self-test-pinch-leap-only-2026.11.18.json`이다.

변경 소스: `app/ui/main_window.py`, `game_selection_screen.py`, `leap_calibration_dialog.py`, `game_widget.py`, `settings_screen.py`, `app/input/input_fusion.py`, `leap_tracker.py`, `emg_session.py`, `oymotion_reader.py`, `oymotion_activity.py`, `app/analytics/session_logger.py`, `app/diagnostics.py` 및 관련 검사. `app/input/pinch_intent.py`, `weighted_pinch.py`와 제거된 기능 전용 검사 세 개는 삭제했다.

AMBIGUOUS: 새 빌드에서 실제 Leap 장치의 보정·플레이 확인은 남아 있다. 자동 검사는 모의 센서 입력을 사용한다.

[Mermaid 흐름](../diagrams/pinch-leap-only.md)은 Mermaid 지원 Markdown 미리보기로 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
