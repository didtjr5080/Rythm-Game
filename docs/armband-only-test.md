# Armband 단독 핀치 테스트

EXTRACTED: 이 테스트 옵션은 이후 사용자 요청으로 제거했다. 최신 핀치는 [Leap 전용](pinch-leap-only.md)이며 아래는 과거 구현 기록이다.

EXTRACTED: 게임 선택 화면의 핀치 블록에서 **테스트: armband만 사용 (Leap 불필요)**를 체크한 뒤 핀치 게임을 선택한다. 체크하지 않으면 기존 Leap + armband 일치 규칙을 사용한다. 테스트 모드는 핀치 4레인 채보를 그대로 사용한다.

EXTRACTED: OYMotion과 COM 포트는 기존 Settings에서 선택한다. 시작 전 열린 손(NONE)과 네 핀치(INDEX, MIDDLE, RING, PINKY)를 각각 1초 준비·3초 유지 방식으로 새로 보정한다. 테스트 보정에서는 Leap 추적기를 만들거나 Leap 프로필을 읽고 저장하지 않는다. 각 동작의 새 armband RMS 특징이 최소 25개 필요하며, 기존 다섯 자세 패턴 분리 검사에 통과해야 시작한다. 모델은 메모리에만 유지한다.

EXTRACTED: armband 분류 INDEX/MIDDLE/RING/PINKY가 각각 1/2/3/4번 레인을 선택한다. NONE·불확실·장치 불일치·신호 소실·미보정 상태는 레인을 선택하지 않는다. 두 핀치 사이에 손을 펼칠 필요가 없다. 판정선의 핀치 유지 득점과 연속 MISS 10회 종료는 기존 핀치 규칙을 사용한다.

EXTRACTED: 다시 플레이하면 armband 단독 선택을 유지하면서 다시 보정한다. 게임 선택에서 체크를 해제하고 시작하면 일반 두 센서 모드로 돌아간다. 근전도 리듬·유지 모드는 변경하지 않는다. HUD에는 ARMBAND ONLY / TEST를 표시하고 세션·결과에는 `pinch_input_source=armband_only_test`를 기록한다.

EXTRACTED: 내부 판정 커널의 `hand_visible`은 이 테스트 모드에서 유효한 armband 핀치 입력의 존재를 뜻한다. 실제 광학 손 추적을 뜻하지 않는다. 실제 Leap 핀치 필드는 비워 두고 입력 출처를 함께 기록한다.

EXTRACTED: 관련 소스 검사 71개 통과. `docs/check_armband_only.py`는 Leap 없는 보정·프로필 미접근, 네 레인 득점, 펼친 손·끊긴 신호의 미입력, Leap 없는 GameWidget 렌더링 및 득점, 재시도 모드 유지와 일반 모드 복귀를 검증한다. 실제 착용 신호 대신 합성 신호를 사용한다.

AMBIGUOUS: 실제 착용자의 네 핀치 구분 정확도와 장시간 착용 변화는 미검증이다. 서로 구분되지 않는 패턴은 보정 단계에서 재측정을 요구한다. 이 테스트로 실제 착용 보정·플레이를 확인해야 한다.

새 실행 폴더: `dist_windows_armband_only_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`. `_internal`을 포함한 폴더 전체를 사용한다.

EXTRACTED: 새 EXE 자체 검사 17항목 통과(`ok=true`, `armband_only_test_enabled=true`). SDK DLL 해시 일치와 기존 설정·프로필 복사를 확인했다. 보고서는 배포 폴더의 `self-test.json`과 `release/self-test-armband-only-2026.11.18.json`이다. 자체 검사는 합성 신호 기준이다.

변경 소스: `app/ui/game_selection_screen.py`, `main_window.py`, `leap_calibration_dialog.py`, `game_widget.py`, `app/input/input_fusion.py`, `app/analytics/session_logger.py`, `app/diagnostics.py`.

[Mermaid 도식](../diagrams/armband-only-test.md)은 Mermaid 지원 Markdown 미리보기에서 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
