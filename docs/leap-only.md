# Leap Motion 전용 손 입력

EXTRACTED: 이후 게임 점수 조건에서 EMG를 제외하고 [기준선 핀치 유지 판정](pinch-hold-scoring.md)으로 변경했다. 아래 EMG 판정 설명은 변경 전 기록이다.

EXTRACTED: 개인별 핀치 거리 측정·저장·선택 기능은 [개인별 보정 안내](leap-personal-calibration.md)를 확인한다. 보정 EXE는 기존 샘플 게임 레인 제약을 포함한다.

EXTRACTED: 2026-11-18 요청으로 웹캠 입력과 MediaPipe 손 추적 사용을 중단했다. `USE_CAMERA=False`, `USE_MEDIAPIPE=False`이며 기존 저장 설정에 카메라 활성화가 남아 있어도 실제 입력을 시작하지 않는다. MediaPipe 구현 원본과 EMG 처리, `app/main.py`, `legacy_web/`는 수정하지 않았다.

EXTRACTED: 메인 화면·EMG 보정·게임의 `InputFusion`은 Leap 핀치 결과를 사용한다. 게임은 오른손 엄지+검지/중지/약지/소지를 레인 1/2/3/4로 선택하고 기존 EMG 수축으로 판정한다. 손이 감지되지 않을 때 숫자 1~4 수동 선택은 유지한다.

EXTRACTED: 카메라 미리보기·카메라 선택·반전 설정·게임의 AR 카메라 단축키를 제외했다. 게임에는 웹캠 영상 대신 네 핀치 안내와 Leap 상태를 표시한다. 메인·보정 화면의 가상 손 미리보기도 제거했다.

EXTRACTED: 카메라 기반 메뉴 커서는 연결하지 않는다. 메뉴는 마우스·키보드로 조작한다. Leap 메뉴 커서·클릭·스크롤 기능을 새로 구현하지 않았다.

EXTRACTED: 빌드에서 MediaPipe 패키지·모델을 제외한다. 기존 카메라 관련 모듈은 호환용으로 소스에 남지만 현재 화면에서 웹캠 입력을 열지 않는다. Leap SDK 헤더·DLL은 EXE에 동봉하며 Orion 4.1 서비스 설치와 장치 연결은 별도로 필요하다.

## 검증

### MIDDLE 다음 RING 생성 금지

EXTRACTED: 새 노트 생성·저장 시 `simplify_for_emg()`가 시간순 정렬과 간격 정리를 마친 노트를 기준으로 MIDDLE(2레인, 내부 1) → RING(3레인, 내부 2)을 검사한다. 해당 RING 노트의 레인만 INDEX(1레인, 내부 0)로 바꾸며 노트 시각과 개수를 유지한다. RING → MIDDLE 및 다른 전환은 허용한다.

EXTRACTED: 샘플 채보와 생성 실패 시 대체 채보도 같은 금지 전환이 없도록 변경했다. 이후 샘플 게임 재점검에서 엔진 시작 시에도 제약을 적용하도록 보완했다. 따라서 기존 저장 채보도 게임에 로딩하면 제약이 적용되며 파일 자체는 덮어쓰지 않는다. 핀치 입력 자체의 MIDDLE → RING 전환은 제한하지 않는다.

### 노래 없이 시작하는 샘플 게임 재점검

EXTRACTED: 이전 `dist_windows_leap_only_2026.11.18` EXE의 내장 샘플은 화면 레인 `1,2,3,4,3,2,1,2,4,3,1,4`였다. 직전 `dist_windows_leap_only_no_middle_ring_2026.11.18` EXE는 `1,2,1,4,3,2,1,2,4,3,1,4`로 변경되어 있었다. EXE 내부 Python 아카이브를 읽어 확인했다.

AMBIGUOUS: 사용자가 실행한 EXE 경로는 확인하지 못했으므로 이전 EXE 사용 여부나 현장 발생 원인은 확정하지 않았다.

EXTRACTED: `RhythmGameEngine.__init__()`가 모든 입력 채보를 시간순 정렬한 후 MIDDLE 바로 뒤 RING을 INDEX로 바꾼다. 샘플·기존 채보·직접 전달 채보 모두 같은 검사를 거친다. 노트 수와 판정 시각은 유지한다.

EXTRACTED: 회귀 검사는 실제 MainWindow에서 노래와 채보가 선택되지 않은 상태로 게임 화면에 진입한 뒤 노트 순서와 렌더링을 확인한다. EXE 자체 검사도 노래 없는 실제 GameWidget을 생성하고 `no_song_sample_lanes`에 화면 레인 번호를 기록하도록 보강했다. 소스 검사 8개 통과.

EXTRACTED: 새 빌드는 `dist_windows_leap_sample_fix_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. EXE 자체 검사 9항목 통과(`ok=true`). 무곡 게임 실제 노트 배열은 `1,2,1,4,3,2,1,2,4,3,1,4`로 기록되었다. 보고서는 `release/self-test-leap-sample-fix-2026.11.18.json`과 실행 폴더의 `self-test.json`에 있다. 이전 EXE 대신 이 빌드를 실행한다.

EXTRACTED: `python -m unittest docs.check_lane_transition docs.check_leap_input -v` 7개 통과. 4레인의 길이 5 조합 1,024개, 정렬·간격 정리로 생기는 인접 전환, 생성·저장·대체 경로와 반복 적용 안정성을 검사했다.

EXTRACTED: 전환 제약을 반영한 새 EXE는 `dist_windows_leap_only_no_middle_ring_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. 이전 빌드는 유지한다. 새 채보를 생성하려면 이 EXE를 사용한다.

EXTRACTED: 새 EXE 자체 검사 8항목 통과(`ok=true`). 오디오에서 생성된 노트에도 금지 전환이 없는지 검사했다. 결과는 `release/self-test-leap-no-middle-ring-2026.11.18.json`과 실행 폴더의 `self-test.json`에 저장했다.

EXTRACTED: 새 실행 파일은 `dist_windows_leap_only_2026.11.18/EMG-Motion-Rhythm-No-Bandpass/EMG-Motion-Rhythm-No-Bandpass.exe`이다. 이전 빌드 폴더는 유지했다. `_internal`을 포함한 전체 폴더를 사용한다. 실행 폴더에 `README-LEAP-ONLY.txt`와 `self-test.json`을 포함했다.

EXTRACTED: 소스 검증 4개와 새 EXE 자체 검사 8항목이 통과했다. EXE 보고서는 `release/self-test-leap-only-2026.11.18.json`이며 `ok=true`, `camera_input_enabled=false`, `lane_count=4`다. 동봉 SDK ABI·DLL 로딩과 오디오 분석·노트 생성·EMG 수축 판정도 통과했다. 배포 폴더에 MediaPipe 패키지 디렉터리가 없는 것을 확인했다.

EXTRACTED: 빌드 명령은 다음과 같다.

```powershell
$env:EMG_NO_BANDPASS_BUILD='1'
.venv311/Scripts/python.exe -m PyInstaller --noconfirm --distpath dist_windows_leap_only_2026.11.18 --workpath build/leap_only_2026.11.18 EMG-Motion-Rhythm.spec
```

```powershell
.venv311/Scripts/python.exe -m unittest docs.check_leap_input -v
```

EXTRACTED: 화면 검증은 `cv2.VideoCapture`와 MediaPipe tracker 생성이 호출되면 실패하게 한 상태에서 메인→설정→보정→게임 이동과 렌더링을 확인한다. 설정 카메라 컨트롤 숨김과 MediaPipe 미로딩도 확인한다.

## 다이어그램과 Graphify

[Leap 전용 입력 흐름](../diagrams/leap-only.md)을 Mermaid 지원 Markdown 미리보기에서 연다.

Graphify 수동 실행: `pip install graphifyy` → `graphify --help` → `graphify .`. 기존 Graphify 보고서는 이번 변경을 반영해 재생성하지 않았다.

## 남은 TODO

AMBIGUOUS: 실제 장치가 연결된 상태의 네 핀치 선택·해제·추적 손실 및 EMG 동시 판정은 현장 확인이 필요하다. 자동 검사만으로 실제 장치 플레이를 검증한 것은 아니다.
