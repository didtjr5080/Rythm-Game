# 메뉴에서만 MediaPipe 손 커서 사용

EXTRACTED: 메인(StartScreen), 게임 선택(GameSelectionScreen), 설정(SettingsScreen), 결과(ResultScreen), 저장 결과 목록(ResultsBrowserScreen)에서 웹캠과 MediaPipe 손 커서를 사용한다. 이미지 게임 선택 카드와 게임별 입력 규칙은 유지한다.

## 화면별 수명

EXTRACTED: MainWindow는 위 메뉴 화면에 공유 VideoSession lease와 HandCursorController를 연결한다. 메뉴 사이를 이동할 때 짧은 idle 기간 안에 같은 작업자를 재사용한다. 커서는 MediaPipe가 확인한 신선한 손 데이터만 받으며 OpenCV 근사 추정으로는 조작하지 않는다.

EXTRACTED: 게임 진입 시 커서 타이머·오버레이를 분리하고 메뉴 lease·설정 미리보기를 닫은 뒤 VideoSession.stop을 호출한다. is_stopped로 현재 및 종료 중인 모든 작업자의 실제 스레드 종료를 확인한다. 아직 종료 중이면 GUI를 막지 않고 30ms 타이머로 다시 확인하며, 마지막 시작 요청과 현재 화면이 여전히 유효할 때만 진행한다. 마우스 release 처리 중 화면 교체도 지연하여 손 클릭 직후 위젯 파괴를 피한다.

EXTRACTED: 카메라 및 MediaPipe Hands close가 완료된 다음 Leap 보정 또는 게임을 생성한다. GameWidget은 use_camera=False이며 커서나 VideoSession을 취득하지 않는다. 핀치 게임은 Leap, 근전도 게임은 armband를 사용한다. 결과·메인 등으로 돌아오면 메뉴용 카메라와 커서를 다시 연결한다. Leap 보정을 취소하면 원래 메뉴의 카메라를 다시 켠다.

EXTRACTED: 네이티브 DLL 충돌 방지를 위한 MediaPipe 사전 로딩은 기존 런타임 훅을 사용한다. 게임 중에도 Python 모듈이나 DLL은 메모리에 남아 있을 수 있지만, 카메라 캡처·MediaPipe 손 추론 그래프·커서 폴링은 종료되어 있다. 모듈을 강제로 언로드하지 않는다.

## 조작과 설정

EXTRACTED: 기존 FoldGestures·WristTilt와 HandCursorController를 재사용한다. 손을 펴서 이동하고 한 번 접어 주먹 상태를 유지하면 클릭한다. 두 손가락 상태에서 손목 기울이기로 스크롤하고 중립 자세에서 멈춘다. 손 상실, 오래된 프레임, 앱 비활성화, 모달 창, Esc에서는 조작을 중단한다. OS 전역 마우스 커서를 움직이거나 다른 앱을 클릭하지 않는다.

EXTRACTED: 설정에 메뉴 손 커서 사용, 카메라 번호·해상도·좌우 반전과 실시간 카메라/MediaPipe 상태를 표시한다. 변경은 저장 후 적용한다. 새 배포 설정은 메뉴 웹캠 사용을 켜 두며 사용자가 끌 수 있다. 카메라가 열리지 않거나 손 추적이 실패해도 기존 마우스로 조작할 수 있다.

## 검증과 제한

EXTRACTED: 관련 회귀 검사 70개 통과. docs/check_menu_camera.py는 다섯 메뉴 화면의 연결·공유, 작업자 종료 전 게임 미생성, 종료 후 게임의 카메라 미사용, 결과의 재연결, 보정 취소 시 복구, 카메라 OFF 설정, 이미지 카드의 손 클릭 release 후 화면 전환을 검증한다. 센서와 카메라 수명은 모의 객체로 검사한다.

EXTRACTED: 소스 환경의 MediaPipe 0.10.21 실제 Hands 그래프 초기화·검은 프레임 추론·close는 통과했다. 실제 Camera 0/1 점검은 둘 다 UNAVAILABLE로 끝났고 각 작업자는 정상 종료됐다. 관찰 보고서는 build/menu-camera-live-check.json, build/menu-camera-1-live-check.json에 있다. 카메라 영상은 저장하지 않았다.

AMBIGUOUS: 실제 웹캠 손 이동·주먹 클릭의 성공은 아직 확인하지 못했다. 카메라 번호, 다른 카메라 앱의 점유, 물리적 가림/비활성화 및 Windows의 데스크톱 앱 카메라 접근 설정을 확인해야 한다. 어느 원인인지는 이번 점검에서 확정하지 못했다. 기존 WorkOrder 수동 스크립트의 일부 후반 통합 검사는 과거 bio.camera_source 및 게임 중 카메라 유지 구조를 전제하므로 현재 수명 검사는 새 회귀 검사로 대체한다. 기존 제스처 및 배타적 카메라 종료 핵심 구간은 별도 실행에서 통과했다.

## 배포

새 실행 폴더: dist_windows_menu_hand_cursor_2026.11.18/EMG-Motion-Rhythm-No-Bandpass. 기존 설정·Leap 보정 파일은 복사하되 새 폴더의 camera_enabled는 True로 설정한다. 이전 폴더는 보존한다.

EXTRACTED: PyInstaller에서 MediaPipe 전체 제외를 해제하고 modules 데이터(모델·그래프)를 포함한다. app/main.py나 legacy_web/는 변경하지 않는다. 변경 코드는 app/config.py, app/settings.py, app/ui/main_window.py, game_widget.py, settings_screen.py, app/input/video_session.py, app/diagnostics.py와 spec 및 관련 검사다.

EXTRACTED: 새 EXE 자체 검사 17항목 통과(`ok=true`, `menu_camera_enabled=true`, `gameplay_camera_enabled=false`, `mediapipe_version=0.10.21`). 패키지 안의 필수 모델·그래프 다섯 파일과 실제 MediaPipe 초기화·검은 프레임 처리·close를 확인했다. 보고서는 배포 폴더의 self-test.json 및 release/self-test-menu-hand-cursor-2026.11.18.json이다. 이 검사는 웹캠 접근을 하지 않으며 실제 Camera 0/1 열기 실패를 해결했다는 뜻은 아니다.

[현재 수명 Mermaid](../diagrams/menu-hand-cursor.md)는 Mermaid 지원 Markdown 미리보기에서 연다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.
