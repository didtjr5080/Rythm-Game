# EMG Motion Rhythm

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
