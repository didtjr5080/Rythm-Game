# 매 게임 시작 전 핀치 보정

EXTRACTED: 현재 시작 전 보정은 [Leap만 측정](pinch-leap-only.md)한다. armband는 핀치 보정에 사용하지 않는다. 이 문서 하단의 armband 관련 추가 기록은 이전 버전 이력이다.

EXTRACTED: 핀치 모드 선택 → 열린 손·검지·중지·약지·소지 핀치 측정 → 보정 완료·게임 시작 순서다. 설정 화면의 보정 버튼은 제거했다. 기존 저장 프로필이 있어도 새 측정 없이 시작할 수 없다. 다시 플레이할 때에도 보정을 진행한다.

EXTRACTED: 각 동작은 기존과 같은 1초 준비·3초 측정 방식이며, 다섯 동작 모두 최소 25개의 유효 프레임을 확보해야 완료 버튼이 활성화된다. 기존 임계값 계산의 동작 구분 검증과 파일 저장이 성공한 후에만 보정 창이 승인되고 게임 화면을 생성한다. 취소·창 닫기·측정 또는 저장 실패 시 게임을 시작하지 않는다. 보정용 Leap 연결을 닫은 다음 게임용 연결을 생성한다.

EXTRACTED: 근전도 모드는 Leap 보정을 요구하지 않으며 기존 시작 전 3초 안정값 측정을 유지한다. 변경 소스는 `app/ui/main_window.py`, `settings_screen.py`, `leap_calibration_dialog.py`, `game_selection_screen.py`다. `app/main.py`와 `legacy_web/`는 수정하지 않았다.

EXTRACTED: 회귀 검사는 `docs/check_pre_game_calibration.py`에 있다. 취소 시 게임 미생성, 매 시작·재시도 보정, 근전도 경로 분리, 저장 프로필로 우회 불가, 새 측정 후 저장·승인·입력 해제를 검증한다.

EXTRACTED: 관련 소스 검사 총 59개 통과. 기존 화면 검사도 새 보정 절차에 맞추어 갱신했다.

EXTRACTED: 새 EXE 자체 검사 15항목 통과(`ok=true`). 보고서는 배포 폴더의 `self-test.json`과 `release/self-test-pre-game-calibration-2026.11.18.json`이다. 기존 설정과 핀치 프로필을 복사했으며 이전 빌드는 유지했다. 자체 검사는 실장치에서 보정을 수행하는 검사는 아니다.

AMBIGUOUS: 실제 Leap 장치에서 연속 보정·게임 전환 확인은 남아 있다.

새 빌드: `dist_windows_pre_game_calibration_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`.

[흐름 도식](../diagrams/pre-game-calibration.md)은 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
EXTRACTED: 최신 핀치 보정은 armband도 함께 측정하며 두 센서가 같은 핀치일 때만 입력됩니다. [현재 보정·판정 안내](pinch-armband-intent.md)를 먼저 확인하세요.
