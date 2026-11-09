Project Knowledge Log
2026-05-24

Task

Initialized documentation-only wiki and structure visualization resources.

Files Created

AGENTS.md
.graphifyignore
log.md
wiki/
docs/
diagrams/
graphify-out/

Scope

Documentation and visualization only.

No Code Changes

The following were intentionally not modified:

game logic
EMG input logic
MediaPipe hand tracking logic
note generation logic
PyQt6 UI behavior
legacy_web source code

Notes
EXTRACTED: The project is an implemented rhythm game using EMG input and hand-tracking concepts.
INFERRED: The wiki can support future maintenance and rehabilitation engineering documentation.
AMBIGUOUS: Some future clinical analysis features are not part of the current implemented game.

2026-05-24
Task

Generated Graphify HTML/report outputs and aligned wiki notes with session/result data.

Files Updated

docs/structure-visualization.md
wiki/index.md
wiki/architecture/system-overview.md
wiki/architecture/data-flow.md
wiki/audio/audio-note-generation.md
wiki/data/local-data-layout.md

Notes
EXTRACTED: Graphify cluster-only produced graph.html and GRAPH_REPORT.md.
EXTRACTED: Session logs are saved to app/data/sessions/ as JSON/CSV.
EXTRACTED: Result summaries are saved to app/data/results/ as JSON.

2026-11-07

Task

EXTRACTED: 사용자 요청에 따른 UI·카메라·손가락 판정·전체 곡 재생 변경 사항과 Windows 실행 파일 배포 경로를 문서화했습니다.

Files Updated

README.md, docs/windows-release.md, wiki/index.md, diagrams/game-loop.md, WorkOrder/implementation_report.md

EXTRACTED: 빌드 스크립트는 개인 음원·설정·기록을 제외하고 EXE 자체 검사 후 ZIP과 SHA256을 생성합니다.
AMBIGUOUS: 물리 카메라·시리얼·스피커 조합의 실제 동작은 별도 기기 검증이 필요합니다. 기존 Graphify 그래프는 이번 변경 사항으로 재생성하지 않았습니다.

2026-11-07 — 프로그램 아이콘

EXTRACTED: 사용자 제공 손 엠블럼 PNG를 원본 그대로 추가하고 투명 다중 크기 ICO로 변환했습니다. `app/ui/app_icon.py`, `app/main.py`, `EMG-Motion-Rhythm.spec`에서 Windows 앱 식별자·창·작업 표시줄·EXE 아이콘을 연결했습니다.
EXTRACTED: `build_windows.ps1`의 아이콘 생성 단계와 `app/diagnostics.py`의 리소스 검사를 추가하고 `docs/windows-release.md` 및 `wiki/index.md`에 변환·적용 경로를 정리했습니다. 게임 데이터 흐름의 변경이 없어 기존 Mermaid 다이어그램은 유지합니다.

2026-11-08 — EMG 펌웨어 및 장치 선택

EXTRACTED: 설정에 EMG 장치 검색·선택·USB 식별자 저장·연결 테스트·재연결·원시/처리 신호 선택을 추가했습니다. Nano 및 ESP8266 A0 펌웨어는 컴파일을 통과했습니다. COM5의 칩 식별 결과는 ESP8266EX입니다.
EXTRACTED: 이후 사용자가 A0를 찾고 SZH-GJD001 모델과 3V3 전원을 확인했습니다. COM5 ESP8266EX에 펌웨어를 업로드하고 플래시 해시와 실제 식별·데이터 프레임 수신을 검증했습니다. 기존 플래시 첫 512KiB는 로컬 빌드 폴더에만 백업합니다.
AMBIGUOUS: 실제 보드의 ADC 허용 전압과 근육 수축 시 활성 임계값 검증은 별도 확인이 필요합니다.

2026-11-08 — 노트 이동 속도

EXTRACTED: 요청에 따라 기본 노트 속도를 450에서 360으로 낮췄으며 현재 PC의 소스 실행·배포 EXE 저장 설정에도 360을 적용했습니다. 음악과 판정 시각은 유지합니다. `wiki/game/settings-system.md`와 위키 목차에 설명을 반영했습니다. 입력·게임 흐름의 변화가 없어 기존 다이어그램은 유지합니다.

2026-11-08 — 느린 노트 속도 EXE 배포

EXTRACTED: 노트 기본 속도 360을 포함하는 `v2026.11.08.2` 빌드 설정·릴리즈 노트·배포 안내를 준비하고 EXE 자체 검사 결과에 기본 속도를 기록하도록 했습니다. 기존 사용자 설정이 기본값보다 우선한다는 점도 문서화했습니다. 데이터 흐름은 바뀌지 않아 기존 다이어그램을 유지합니다.
EXTRACTED: 재빌드한 EXE 자체 검사가 통과했으며 검사 결과의 `default_note_speed`가 360임을 확인했습니다.

2026-11-08 — 음악 목록 표시 개선

EXTRACTED: `app/ui/start_screen.py`에서 목록 높이 제한을 없애고 행을 압축했으며 곡 수·긴 제목 툴팁을 추가했습니다. `app/ui/dashboard.py`에는 로비용 소형 곡 분석 요약을 적용했습니다. 20곡으로 1280×720의 7곡, 1440×900의 14곡, 1920×1080의 20곡 표시와 선택·불러오기를 확인했습니다. 배포 문서와 위키에 변경 내용을 정리했습니다. 데이터 흐름이 바뀌지 않아 기존 다이어그램은 유지합니다.

2026-11-08 — MediaPipe 한글 경로·배포 호환성

EXTRACTED: 한글 경로의 모델 로딩 실패를 재현하고 영문 모델 경로 확보·모델 캐시 복구를 추가했습니다. C++ 런타임 사본과 로딩 순서를 보완하고 카메라 테스트 및 게임 화면에 대체 인식과 초기화 오류를 표시했습니다. `WorkOrder/verify_mediapipe_portability.py`와 기존 손가락·UI 검증을 통과했습니다. 관련 문서·위키·입력 다이어그램을 갱신했습니다.
INFERRED: 사용자의 다른 PC 문제와 같은 원인일 가능성이 있으나 그 PC의 오류 로그로 확정하지 않았습니다.
EXTRACTED: `docs/emg-device-setup.md`, `wiki/index.md`, `diagrams/input-flow.md`에 확인된 사실과 남은 확인 사항을 분리해 기록했습니다.


2026-11-08 ? EXTRACTED: five-lane finger-count mapping, strict serial input without keyboard fallback, rest-to-arm and single-hit contraction handling. Added docs/five-lane-input.md and regression checks; synchronized input-flow diagram. Hardware contraction accuracy remains to be verified.
2026-11-08 — EXTRACTED: 사용자 실기 테스트 완료. 새 설치의 기본 EMG 신호를 envelope, 임계값을 12로 확인·통일하고 v2026.11.08.5 EXE 자체 검사에 기본값 검증을 추가했습니다. 기존 사용자 설정은 유지합니다.

2026-11-09 ? EXTRACTED: camera/inference moved off GUI across live screens; bounded latest result with expiry; duplicate conversions cached; visible-note binary search and judgment cursor. Added performance documentation, input diagram and slow-worker lifecycle regression tests. Physical camera FPS remains unverified because camera 0 was unavailable.

2026-11-09 ? EXTRACTED: app-local hand cursor on main/settings only, using shared native video results. Added fold click with double-fold disambiguation, scroll-mode toggle, circular feedback, popup selection and focus/tracking/page guards. Updated hand-cursor docs/diagram, packaged checks, regression tests and release notes. Physical hand sensitivity remains to be verified.

2026-11-09 ? EXTRACTED: confirmed two Windows native access-violation reports for the hand-cursor release; stack memory contains camera-library addresses. Added shared camera leases, serialized native teardown/open, deferred hand page transitions, cancellation guards and local runtime fault logs. Added 20-round-trip regression. INFERRED: overlapping graph lifecycle implicated; physical camera was unavailable in this environment.

2026-11-09 ? EXTRACTED: result and saved-result screens now acquire the shared navigation camera and attach the app-local hand cursor. Fold-click replay/return, record selection/scroll/refresh and camera reuse verified. Preserved disabled cursor in gameplay/calibration. Fixed empty-history placeholder lifetime during repeated refresh.
