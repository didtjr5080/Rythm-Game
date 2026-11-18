EXTRACTED: Latest 2026.11.18.10 reduces note frequency: pinch/advanced minimum gap 1.8s, EMG minimum rest after holds 1.8s, including existing charts. [GitHub release and Windows download](https://github.com/didtjr5080/Rythm-Game/releases/tag/v2026.11.18.10). Local EXE: `dist_windows_density_20261118_10/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`. [Details](docs/note-density.md). Older release paths below are historical.

EXTRACTED: Current build 2026.11.18.9: webcam mode selection with open-hand movement and fist selection, camera status on selection page, note speed 50-200. EXE: `dist_windows_camera_20261118_9/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`. See [details](docs/camera-selection-speed.md).

# EMG Motion Rhythm

## 최신 로컬 선택 이미지 빌드 — 2026.11.18.8

EXTRACTED: 핀치+암밴드 상위 모드의 선택 카드를 사용자가 첨부한 이미지로 변경했습니다. 프로필 보정 저장·삭제·상위 모드 해금 규칙은 유지합니다. 최신 EXE는 `dist_windows_image_20261118_8/EMG-Motion-Rhythm/EMG-Motion-Rhythm.exe`입니다. 소스120개 검사와 실제 카드 렌더링이 통과했습니다. [이미지 안내](docs/game-selection-images.md), [프로필 사용법](docs/player-profiles.md), [배포 안내](docs/windows-release.md)를 참고하세요. 최신8·직전7만 보관합니다. 아래 경로는 과거 기록이며 파일 존재를 보장하지 않습니다.

EXTRACTED: 2026-11-18 GitHub 전체 구현 소스에는 Leap 전용 4레인 핀치, OYMotion USB armband 근전도 모드, 공유 EMG 세션, 메뉴 전용 MediaPipe 커서와 게임 선택 이미지가 포함됩니다. 음악 과제의 최신 상태는 위 안내와 [다음 과제](docs/NEXT_TASKS.md)를 참고하세요. 개발 실행의 Leap SDK는 별도 설치 후 `LEAPSDK_INSTALL_LOCATION`으로 지정하며 기본 경로는 `C:/EMG-Motion-Rhythm/LeapSDK`입니다. OYMotion 필수 DLL과 배포 고지는 `app/vendor/oymotion/`에 포함됩니다.

EXTRACTED: 최신 버전은 메인·게임 선택·설정·결과에서 웹캠 MediaPipe 손 커서를 사용하고, 게임 시작 전 카메라·손 추론 종료를 확인합니다. 게임은 핀치 Leap 전용 / 근전도 armband 전용입니다. 최신 EXE: `dist_windows_menu_hand_cursor_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [메뉴 손 커서 안내·실제 카메라 검증 제한](docs/menu-hand-cursor.md). 아래 웹캠 비활성 설명은 이전 기록입니다.

EXTRACTED: 최신 게임 선택 화면은 제공받은 이미지와 게임 이름만 표시합니다. 암밴드 이미지는 근전도 게임, 핀치 손 이미지는 핀치 게임입니다. 최신 EXE: `dist_windows_image_selection_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [화면 안내·미리보기](docs/game-selection-images.md). 아래 배포 경로는 이전 기록입니다.

EXTRACTED: 최신 핀치는 **Leap Motion만 사용**합니다. armband 보정·가중 합산·단독 핀치 테스트를 제거했으며 별도 근전도 게임은 유지합니다. 최신 EXE: `dist_windows_pinch_leap_only_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [현재 입력 안내](docs/pinch-leap-only.md). 아래 가중치·armband 핀치 설명은 이전 버전 기록입니다.

EXTRACTED: 최신 일반 핀치는 **Leap 70% + EMG 30% 인식 점수**를 합산합니다. EMG 패턴 유사성만으로 일반 모드 보정을 막지 않으며, armband 단독 테스트는 기존 구분 검사를 유지합니다. 최신 EXE: `dist_windows_weighted_pinch_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [가중 판정 안내](docs/weighted-pinch.md). 아래 배포 경로와 두 센서 일치 필수 설명은 이전 기록입니다.

EXTRACTED: USB 초기화 실패 후 재연결을 수정한 최신 빌드: `dist_windows_armband_reconnect_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. 새 폴더의 포트는 Auto입니다. [현재 USB 장치 상태와 재연결 안내](docs/armband-reconnect.md). 실제 동글 인식 복구는 아직 확인하지 못했습니다.

EXTRACTED: 테스트 시 게임 선택의 **armband만 사용 (Leap 불필요)**를 체크하면 armband로만 다섯 자세를 보정하고 핀치 4레인을 플레이할 수 있습니다. 최신 EXE: `dist_windows_armband_only_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [테스트 사용법](docs/armband-only-test.md). 체크하지 않으면 아래의 두 센서 일치 규칙을 사용합니다.

EXTRACTED: 최신 핀치 게임은 **Leap + OYMotion armband의 핀치가 일치해야 입력**됩니다. 시작 전 열린 손과 네 핀치를 두 센서로 보정합니다. 최신 빌드: `dist_windows_pinch_armband_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. [보정·판정 안내](docs/pinch-armband-intent.md). 아래 배포 기록과 EMG 불필요 설명은 이전 버전 기준입니다.

EXTRACTED: 핀치 보정은 설정 대신 매 게임 시작 직전에 진행합니다. 다섯 동작을 새로 측정하고 저장한 후 시작하며 재시도에도 적용됩니다. 최신 빌드는 `dist_windows_pre_game_calibration_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. [시작 전 보정 안내](docs/pre-game-calibration.md). 아래 배포 경로는 이전 기록입니다.

EXTRACTED: OYMotion USB 8-channel, 12bit, 500Hz build: `dist_windows_oymotion_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`. See [all-channel EMG input and verification](docs/oymotion-emg.md). Older build paths below are historical.

EXTRACTED: 최신 소스는 **게임 선택 → 근전도 리듬·유지(1레인) / 핀치 리듬(4레인)**을 지원합니다. 노트 생성 한 번으로 두 모드 채보를 함께 저장합니다. 근전도 모드에는 박자 수축과 긴 근활성 유지 노트가 있고, 핀치 모드는 기준선에서 해당 핀치를 유지하면 득점합니다. 웹캠·MediaPipe 입력은 사용하지 않습니다. [최신 두 모드 안내](docs/game-modes.md)를 우선 확인하세요. 아래 과거 빌드·입력 안내는 이전 버전 기록입니다.

## 최신 로컬 Windows 버전

EXTRACTED: Leap 핀치 모드의 연속 MISS 10회 종료를 적용한 최신 EXE는 `dist_windows_leap_miss10_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. 근전도 작업은 보류하고 해당 모드는 변경하지 않았습니다. [종료 규칙](docs/leap-miss-limit.md). 아래 경로는 이전 기록입니다.

EXTRACTED: 최신 실행 파일은 `dist_windows_emg_rest_001_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. 근전도 게임 선택 후 3초간 가만히 있으면 시작하며 **안정 기준+0.01부터 활성**으로 인정합니다. 수동 근전도 보정은 사용하지 않습니다. [사용법](docs/emg-rest-baseline.md). 아래 실행 경로는 이전 기록입니다.

EXTRACTED: 최신 근전도 모드는 수동 보정 없이 게임 시작 전 **3초 안정값 측정 → 안정값보다 0.01 이상 높으면 입력** 규칙을 사용합니다. 측정 중 음악과 노트는 시작하지 않습니다. [현재 입력 안내](docs/emg-rest-baseline.md). 아래 ON/OFF·수동 보정 설명은 이전 기록입니다.

EXTRACTED: 보정·게임의 EMG 연결/필터 공유와 넓어진 입력 범위를 적용한 최신 EXE는 `dist_windows_emg_assisted_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. EMG 박자 ±350ms, 유지 중 400ms 이내 활성 회복을 허용합니다. 약한 수축용 새 ON/OFF 기준은 자동 보정을 다시 하면 적용되며 성공값은 자동 저장됩니다. [사용법·검증](docs/emg-assisted-input.md). 아래 경로는 이전 빌드 기록입니다.

EXTRACTED: 두 게임 모드를 지원하는 최신 EXE는 `dist_windows_dual_mode_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. **노트 생성 → 게임 선택 → 근전도 또는 핀치** 순서로 이용합니다. 기존 설정·개인별 보정값을 새 폴더에 복사했습니다. [두 모드 사용법](docs/game-modes.md). 아래 경로는 이전 빌드 기록입니다.

EXTRACTED: EMG 없이 핀치 유지로 판정하는 최신 EXE는 `dist_windows_leap_pinch_hold_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. 이전 개인별 보정 파일을 검증 후 새 폴더에 복사했습니다. [판정·사용 안내](docs/pinch-hold-scoring.md). 아래 경로는 이전 빌드 기록입니다.

EXTRACTED: 연속 핀치 즉시 전환을 반영한 최신 EXE는 `dist_windows_leap_direct_pinch_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. 명확한 새 핀치는 손을 펼치지 않고 전환합니다. 이전 개인별 보정 빌드의 보정 파일을 검증 후 새 실행 폴더에 복사했습니다. [상세](docs/leap-personal-calibration.md#손을-펼치지-않는-연속-핀치-전환). 아래 경로는 이전 빌드 기록입니다.

EXTRACTED: 개인별 보정을 포함한 최신 EXE는 `dist_windows_leap_personal_calibration_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. Settings의 **Leap Motion 개인별 핀치 보정**에서 열린 손과 네 핀치를 측정·저장합니다. [사용법](docs/leap-personal-calibration.md). 아래 경로는 이전 빌드 기록입니다.

EXTRACTED: 샘플 게임 레인 제약 재점검 빌드는 `dist_windows_leap_sample_fix_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`입니다. 노래 없이 시작하는 게임과 기존 채보 로딩에도 MIDDLE → RING 금지 제약을 적용합니다. 아래 `dist_windows_current` 경로는 이전 배포 기록입니다.

EXTRACTED: 현재 로컬 실행 파일은 `dist_windows_current/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`, 배포 ZIP은 `release/EMG-Motion-Rhythm-windows-x64-2026.11.17.11.zip`입니다. [두 손가락 손목 기울기 스크롤](docs/hand-cursor.md)과 [버전 정리·백업 위치](docs/version-cleanup.md)를 참고하세요. 근전도 처리·보정은 유지했습니다.

MediaPipe 손 위치 추적과 EMG 근전도 신호를 입력 장치로 활용한 PyQt6 기반 인터랙티브 리듬게임입니다.

## Game Mode

- 손가락 종류와 관계없이 펼친 전체 개수 1~5개가 각각 1~5번 레인을 선택합니다. 주먹은 레인을 선택하지 않습니다.
- 노트가 판정선에 도착할 때 EMG 입력을 발생시킵니다.
- 선택된 레인과 노트 레인이 일치하고 휴식 후 EMG 수축이 확인되면 HIT 판정이 발생합니다. 한 번의 수축은 최대 한 노트만 판정합니다.
- 판정은 PERFECT, GOOD, MISS로 구분됩니다.

## Legacy Web Code

- 기존 웹 기반 리듬 노트 생성기 코드는 `legacy_web/`에 보존되어 있습니다.
- 기존 FastAPI 백엔드는 `legacy_web/backend/`에 보존되어 있습니다.
- 기존 웹 프론트엔드는 `legacy_web/frontend/`에 보존되어 있습니다.
- 기존 오디오 분석/노트 생성 아이디어는 PyQt6 앱의 `app/audio/` adapter에서 재사용합니다.

## Install

Python 3.10 또는 3.11을 권장합니다.

```powershell
python -m venv .venv311
.venv311\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
.venv311\Scripts\python.exe app/main.py
```

또는 Windows에서:

```powershell
run.bat
```

## Mock EMG Test

- 설정에서 모의 EMG 입력을 선택하고 웹캠 앞에서 손가락 1~5개를 펼칩니다.
- 모의 입력 모드에서 SPACE 키를 누르면 EMG 입력이 활성화됩니다. 실제 센서 모드에서는 장치가 없을 때 입력을 차단합니다.
- 실제 EMG 센서 없이도 게임 판정이 가능합니다.
- 카메라가 없을 때는 숫자키 1~5로 레인을 선택할 수 있습니다.

## Saved Music

- Start 화면의 Add Song으로 mp3, wav, ogg 파일을 추가하면 `app/data/songs/`에 저장됩니다.
- Saved Music 목록에서 저장된 음악을 선택하고 Load Selected를 누르면 해당 음악으로 게임을 시작할 수 있습니다.
- Generate Notes를 누르면 `app/data/notes/{song_name}_notes.json` 형식으로 노트가 저장됩니다.
- 저장된 노트가 있는 음악은 다음에 Load Selected를 눌렀을 때 자동으로 해당 노트를 불러옵니다.
- 저장된 음악 파일은 `.gitignore`에 의해 git 추적에서 제외됩니다.

## Settings

- Start 화면의 Settings에서 게임 화면 왼쪽 위 HUD 표시를 켜거나 끌 수 있습니다.
- Settings에서 음악 음량을 조절할 수 있습니다.
- Settings에서 판정 텍스트, 카메라 디버그, 카메라 반전, 노트 속도, 판정선 위치, EMG threshold를 조절할 수 있습니다.
- 점수와 콤보는 HUD 표시 여부와 관계없이 게임 화면에 항상 표시됩니다.
- 설정은 `app/data/settings.json`에 저장되며 git 추적에서 제외됩니다.

## Real EMG Input

- `app/input/emg_reader.py`의 `SerialEMGReader`에서 COM 포트와 baudrate를 수정합니다.
- 기본 예시는 `COM3`, `115200`입니다.
- 한 줄에 숫자 하나가 들어오는 serial 데이터 형식을 기본으로 사용합니다.

예:

```text
523
610
230
```

## Notes

- 카메라가 없어도 앱이 죽지 않게 fallback 처리되어 있습니다.
- EMG 센서가 없어도 mock 모드로 실행할 수 있습니다.
- MediaPipe가 설치되지 않았거나 초기화에 실패하면 콘솔에 명확한 메시지를 출력하고 앱은 계속 실행됩니다.

## Knowledge Wiki and Structure Visualization

This repository includes documentation-only resources for understanding the existing EMG Motion Rhythm game.

Folders

wiki/: persistent project wiki
docs/: documentation for Graphify and visualization
diagrams/: Mermaid structure diagrams
graphify-out/: generated Graphify output

Important Rule

These files are for documentation and visualization only.

They must not change the existing game behavior.

Start Reading

wiki/index.md
diagrams/system-overview.md
diagrams/data-flow.md
docs/graphify.md

Generate Structure Graph

pip install graphifyy
graphify .

Check available commands:

graphify --help

## Windows EXE 다운로드와 빌드

- [EMG 장치·펌웨어 설정](docs/emg-device-setup.md): USB 장치 자동 검색·수동 선택·연결 테스트·재연결과 지원 펌웨어를 설명합니다.

- 실행 파일: [GitHub Releases](https://github.com/didtjr5080/Rythm-Game/releases)에서 Windows ZIP을 받고 전체 압축을 해제한 뒤 `EMG-Motion-Rhythm.exe`를 실행하세요. `_internal` 폴더를 함께 유지해야 합니다.
- 직접 빌드: `.venv311/Scripts/python.exe -m pip install -r requirements-build.txt` 후 `powershell -ExecutionPolicy Bypass -File build_windows.ps1`을 실행합니다.
- [Windows 배포 안내](docs/windows-release.md)에 실행 방법, 카메라·고해상도 설정, EXE 자체 검사와 저장 위치를 정리했습니다.
