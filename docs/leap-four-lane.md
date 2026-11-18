# Leap Motion 4레인 핀치 입력

EXTRACTED: 이 문서는 웹캠 미리보기를 유지하던 중간 버전 기록입니다. 이후 [Leap 전용 입력](leap-only.md)에서 웹캠과 MediaPipe 사용을 제외했습니다.

EXTRACTED: 2026-11-18 사용자 요청에 따라 게임 입력을 4레인으로 변경했다. `app/main.py`, EMG 처리, MediaPipe 구현, `legacy_web/`는 수정하지 않았다.

EXTRACTED: `Orion_4_1_Pinch_Lab_Fix_v3/orion_leapc.py`의 SDK ABI 검사·ctypes 연결과 `leap_pinch_lab.py`의 분류기를 프로젝트 안으로 가져왔다. 참고 프로젝트 자체는 수정하지 않았다.

| 오른손 동작 | 화면 레인 |
| --- | --- |
| 엄지 + 검지 | 1 |
| 엄지 + 중지 | 2 |
| 엄지 + 약지 | 3 |
| 엄지 + 소지 | 4 |
| 핀치 없음 / 추적 손실 | 선택 없음 |

EXTRACTED: 기본 SDK 경로는 `C:\EMG-Motion-Rhythm\LeapSDK`이며 `LEAPSDK_INSTALL_LOCATION` 환경변수로 바꿀 수 있다. Windows 64비트 Python과 Orion 추적 서비스가 필요하다. SDK 헤더와 DLL은 실행 시 외부 경로에서 읽는다.

EXTRACTED: 핀치 분류는 손바닥 너비 대비 거리 0.36, 후보 거리 차이 0.065, 약 90ms 안정화, 해제 배율 1.28을 사용한다. 기존 실험의 개인별 보정 파일은 자동으로 가져오지 않는다. 오른손만 선택한다.

EXTRACTED: 전용 스레드가 SDK를 폴링하며 게임은 최신 결과만 읽는다. 250ms보다 오래된 결과와 종료된 입력은 레인 선택에서 제외한다. 핀치는 레인을 선택하고 기존 EMG 수축이 노트를 판정한다. 숫자 1~4는 손 미감지 시 수동 입력이다.

EXTRACTED: 웹캠/MediaPipe 세션은 기존 메뉴 탐색·카메라 미리보기 용도로 유지된다. 게임 레인 선택에는 Leap 입력을 전달한다. 게임 화면의 웹캠 영상은 Leap IR 영상이 아니다.

EXTRACTED: 새 노트 생성은 기존 생성기에 `LANE_COUNT=4`를 전달한다. 기존 채보는 파일을 덮어쓰지 않고 로딩 시 `lane % 4`를 적용하므로 이전 5번 레인은 1번 레인으로 표시된다. 기존 3→5레인 확장 처리는 제거했다.

## 실행과 검증

```powershell
.venv311\Scripts\python.exe app/main.py
.venv311\Scripts\python.exe -m unittest docs.check_leap_input -v
```

EXTRACTED: 로컬 SDK의 ABI 검사와 DLL 로딩은 통과했다. 3초 폴링에서는 `connected=False`, `device=False`, `frames=0`이었다.

AMBIGUOUS: 서비스 미실행·장치 연결 상태 중 어떤 원인인지는 이번 확인으로 구분하지 못했다. 실제 손으로 네 가지 핀치와 EMG 동시 판정을 확인해야 한다. 기존 EXE는 다시 빌드하기 전까지 이 변경을 포함하지 않는다.

다이어그램: [Mermaid 입력 흐름](../diagrams/leap-four-lane.md). Mermaid를 지원하는 Markdown 미리보기에서 연다.

Graphify 수동 실행: `pip install graphifyy`, `graphify --help`, `graphify .`. 기존 생성 보고서는 이번 변경으로 갱신하지 않았다.

EXTRACTED: ?? ?? 3?(? ?????, ?? ?????? ?? ??, ?? ????? ?? ??)? ????. Qt offscreen?? ??? ??? ??? ?? ???4?? ??????? Python ??? ??? ????.

## 2026-11-18 ? EXE ??

EXTRACTED: `dist_windows_leap_4lane_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`? ????. ?? ?? ??? ???? ???. `_internal`? ??? ?? ??? ????.

EXTRACTED: `EMG-Motion-Rhythm.spec`? SDK ??? DLL? ????, `orion_leapc.py`? frozen ???? ?? SDK? ?? ????. `app/diagnostics.py`? ?? ??? 4???? ???? SDK ABI?DLL ??? ? ????? ?? ??? ????.

EXTRACTED: ? EXE? `--self-test` ?? `ok=true`, `lane_count=4`, `default_emg_signal=unfiltered`, 12? ???? ??. ???? `release/self-test-leap-4lane-2026.11.18.json`? ?? ??? `self-test.json`? ??. ?? ??? `README-LEAP-4LANE.txt`? ????.

EXTRACTED: ?? ??:

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_leap_4lane_2026.11.18 --workpath build/leap_4lane_2026.11.18 EMG-Motion-Rhythm.spec
```

AMBIGUOUS: ?? Leap ??? ??? ??+EMG ???? ?? ???? ???. Orion ?? ???? ?? ?? ? ???? ??.
