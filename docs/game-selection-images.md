# 이미지 중심 게임 선택 화면

EXTRACTED: 2026.11.18.8부터 핀치+암밴드 상위 모드(`pinch_extension`)는 새 첨부 원본을 `app/assets/game_modes/pinch_extension.png`로 사용한다. 1447×1087 PNG를 편집·재생성하지 않고 그대로 복사했다. SHA256은 `f552c351e31421d0e201fa69fdf5256a5fe18ddcbeeb4095e270d6ab1252848e`다. 기존 근전도·기본 핀치 이미지와 프로필 해금 규칙은 유지한다. 잠긴 카드는 기존처럼 흐리게 표시하고, 해금된 카드는 원본 색으로 보인다. 아래 두 카드 설명은 이전 기록이다.

EXTRACTED: 카드 렌더러의 KeepAspectRatio와 중앙 배치를 유지해 원본을 자르거나 늘이지 않는다. 실제 세 카드 화면과 원본 바이트 일치, 전체120개 회귀 검사가 통과했다. 현재 소스 렌더 미리보기는 `WorkOrder/game_selection_image_preview.png`다. 패키지의 기존 app/assets 포함 규칙으로 EXE에도 넣는다.

EXTRACTED: 2026.11.18.8 EXE자체23항목 통과. ZIP안의 `pinch_extension.png`도 원본과 바이트가 동일하다. 사용자 데이터71파일을 직전7에서 복사·해시 검증했고, 최신8·직전7만 유지하도록 구버전6과 캐시·ZIP/해시를 정리했다. 삭제 전 구버전 데이터66항목은 `backups/build-prune-20261118-v8`에 검증 백업했다. 검증 보고서는 `release/image-2026.11.18.8-*.json`이다.

EXTRACTED: 사용자의 최종 배치 확인에 따라 암밴드 팔 이미지는 근전도 리듬·유지 게임, 핀치 손 이미지는 핀치 리듬 게임에 넣었다. 이미지 원본을 편집하지 않고 `app/assets/game_modes/emg_rhythm_hold.png`, `pinch_rhythm.png`로 복사했다.

EXTRACTED: 게임별 설명, 선택 곡 이름, 샘플 곡 표시, 하단 노트 생성 안내문, 영문 패널 제목과 별도의 선택 버튼을 제거했다. 카드에는 해당 이미지와 게임 이름만 표시한다. 화면 상단 게임 선택 제목과 뒤로 이동은 유지한다. 이미지 카드 전체가 클릭 가능한 QPushButton이며 Tab·키보드 선택도 기본 버튼 동작을 사용한다.

EXTRACTED: `app/ui/game_selection_screen.py`의 GameModeCard는 원본 비율을 유지하여 이미지를 맞추고 카드 아래에 이름을 그린다. 잘라내거나 늘이지 않는다. 이미지 경로는 기존 앱 아이콘과 같은 패키지 상대 경로 방식이다. 기존 PyInstaller spec의 `app/assets` 포함 규칙으로 두 이미지도 EXE 배포 폴더에 포함된다.

EXTRACTED: 숨겨진 창 렌더링으로 1280×720·800×600과 Windows 한글 폰트를 확인했다. 두 이미지 로드·모드 버튼 연결·설명 레이블 제거도 확인했으며 기존 관련 검사 65개가 통과했다. 화면 미리보기는 [PNG](game-selection-images-preview.png)다. 레이아웃만 변경했으며 Leap 전용 핀치 및 별도 근전도 게임의 입력·보정·채보·판정 규칙은 유지한다.

새 실행 폴더: `dist_windows_image_selection_2026.11.18/EMG-Motion-Rhythm-No-Bandpass`. `_internal`을 포함한 전체 폴더를 사용한다.

EXTRACTED: 새 EXE 자체 검사 16항목 통과(`ok=true`). 두 PNG의 배포 포함과 원본 해시 일치를 확인했고 기존 설정·Leap 프로필을 복사했다. 보고서는 배포 폴더의 `self-test.json` 및 `release/self-test-image-selection-2026.11.18.json`이다. 이전 배포 폴더는 보존했다.

[Mermaid 선택 흐름](../diagrams/game-selection-images.md)은 Mermaid 지원 Markdown 미리보기에서 확인한다. Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 출력은 갱신하지 않았다.

AMBIGUOUS: 실제 장치를 연결한 새 빌드 플레이 검증은 남아 있다. 이번 변경의 주 검증은 카드 렌더링·이미지 포함·게임 모드 연결이다.
