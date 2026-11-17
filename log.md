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

2026-11-17: 전시 작업 지시서 실행. 커서 배경 전파, 설정 저장 시 창 유지, 영상 표시 제어와 세대 폐기, 비동기 준비·저장, 원자 파일과 고유 ID, 계측, 회귀 검사 추가. 실제 전시 장치·DPI·장시간 검증은 docs/exhibition-stability.md 참조.

2026-11-17 후속: 사용자 버튼 깨짐 스크린샷과 설정 상태 흔들림 반영. 커서를 별도 네이티브 투명 창으로 분리하고 설정 카메라 상태·영상 크기 고정 및 중간 갱신 제거. 실제 Windows 125%와 오프스크린 회귀 검사 통과.

2026-11-17 — EXTRACTED: 사용자 승인 범위에서 EMG 활동 신호에 3표본 중앙값·EMA 필터를 적용하고 표시/판정 신호를 통일. 설정 화면에 안정·수축 자동 임계값 보정, 신호 끊김 취소와 실패 시 기존 값 유지 추가. 회귀 검사 17개 통과. docs/emg-auto-calibration.md 및 diagrams/emg-auto-calibration.md 작성, wiki/index.md 갱신. AMBIGUOUS: 실제 장치 출력 종류·GUI 실행·현장 반응은 미검증(PyQt6 미설치). 새 EXE 미빌드.

2026-11-17 — EXTRACTED: Python 3.11 빌드 환경 생성 및 의존성 설치 후 build_windows.ps1 -Version 2026.11.17.3 실행. EMG 회귀 검사 17개와 오프스크린 설정 자동 보정/취소/저장 검증 통과. EXE 자체 검사 11개 항목 통과(ok=true), Windows ZIP·SHA256 생성. docs/emg-auto-calibration.md, docs/windows-release.md, wiki/index.md 갱신. 실제 EMG 장치 반응은 미검증이며 GitHub 업로드는 수행하지 않음.

2026-11-17 — EXTRACTED: 사용자가 SZH-GJD001 사용을 재확인. 판매처 GJD001_code.ino의 500Hz·60–100Hz Butterworth 응답 기준으로 ESP8266 필터 수정, 40ms RMS와 펌웨어 v2 식별 추가. 앱에 v1 업그레이드 안내·v2 RAW 진단 차단과 보정 가드 추가. 회귀 검사 20개 및 Qt 보정 흐름 검사 통과. 사용자 승인 COM3 ESP8266EX 4MB 전체 백업 후 업로드·쓰기 해시·v2 실수신 검증 완료. 새 EXE는 기존 파일 잠금을 피해 dist_windows_szh_v4에 생성, 자체 검사 11개 항목 통과 및 2026.11.17.4 ZIP·SHA256 생성. docs/szh-gjd001-filter.md, 관련 문서·위키·다이어그램 갱신. TODO: 새 EXE에서 실제 안정/수축 자동 보정과 지연 확인.

2026-11-17 — EXTRACTED: 사용자 보정 실패 스크린샷 검토 중 noise/0.55와 고정 60% 해제 규칙 때문에 안정 300/수축 400도 거부하는 계산 문제 확인. 안정 P95·수축 P10 사이에 ON 60%·OFF 20%를 분리 설정하고 OFF 저장·게임 전달·수동 변경 시 해제·상태 초기화 추가. 실패 시 측정값 표시. 회귀 검사 24개와 Windows 2026.11.17.5 EXE 자체 검사 11개 항목 통과. dist_windows_szh_v5에 생성, 펌웨어 변경 없음. docs/emg-calibration-hysteresis.md 신규 및 관련 문서·위키·다이어그램 갱신. AMBIGUOUS: 스크린샷에 두 측정 구간 통계가 없어 실제 실패 원인 확정은 불가. TODO: 새 EXE에서 현장 보정과 실패 통계 확인.

2026-11-17 — EXTRACTED: 사용자 요청으로 별도 No-Bandpass EXE 비교 빌드 추가. ESP8266은 같은 500Hz 표본에서 기존 60–100Hz RMS와 대역통과 우회 DC+RMS를 계산하고 EMG1_BYPASS 확장 메시지로 추가 전송. 기존 EMG1/v2 식별 유지. 신호 선택·보정·설정 저장 및 marker 기반 비교 빌드 기본값 추가. 회귀 검사 27개·비교 EXE 자체 검사 11개 통과(default_emg_signal=unfiltered). 사용자 게임 종료 확인 후 COM3 4MB 전체 백업·업로드·쓰기 해시·양 경로 실수신 검증. 기존 EXE/ZIP 유지, 새 dist_windows_no_bandpass와 2026.11.17.6 ZIP 생성. docs/emg-no-bandpass-comparison.md 및 배포 문서·위키·Mermaid 갱신. TODO: 실제 안정/수축 구간의 두 모드 성능 비교.

2026-11-17 — EXTRACTED: 사용자 요청에 따라 고정 차이 5 조건 제거. 초기 안정 및 반복 이완 구간 MAD/백분위 흔들림과 3회 최약 수축 P10을 비교해 잡음 대비 분리 판정. UI에 힘빼기 2초/수축 2초 3회(12초) 안내·전환 0.5초 제외·구간별 표본 수집 추가. 숫자 입력/설정 저장/실제 GameWidget까지 소수점 ON/OFF 보존(게임 생성 시 정수 변환 제거). 회귀 검사 31개 및 EXE 자체 검사 11개 통과. Windows 2026.11.17.7을 dist_windows_adaptive_calibration에 생성. 펌웨어 변경·업로드 없음. docs/emg-adaptive-calibration.md 신규 및 관련 문서·위키·다이어그램·배포 README 갱신. TODO: 실제 A/B 착용자의 반복 보정과 오입력/누락 검증.

2026-11-17 — EXTRACTED: 사용자 요청으로 신호 품질 판단 기준 제거. 초기 안정/반복 이완 및 수축 구간 중앙값으로 ON/OFF를 직접 계산하며 작은 차이·겹침·동일값·감소형·ADC 범위 끝값도 적용. 최소 표본 수 기준 제거(구간 데이터 유무와 숫자 형식 검사는 유지). OFF>ON이면 감소형 활성/이완 판정, 설정 저장·게임 전달 및 DIR 표시 지원. 회귀 검사 33개·EXE 자체 검사 11개 통과, Windows 2026.11.17.8을 dist_windows_direct_calibration에 생성. 펌웨어 변경 없음. docs/emg-direct-calibration.md 신규 및 관련 문서·위키·Mermaid·배포 README 갱신. TODO: 실제 측정값 적용 후 동작 확인. 동일 신호를 서로 다른 동작으로 구분하는 정보가 생긴다고 주장하지 않음.

2026-11-17 — EXTRACTED: 사용자 100% 초과 제보 확인. 기존 InputFusion의 활동값/ON 비율을 MVC로 표시하던 계산·표기 제거. 게임 HUD에 실제 활동값, ACTIVE/REST, ON/OFF 및 UP/DOWN 표시. 보정 계산과 판정 변경 없음. 실행 중 v8의 저장 ON 39.544/OFF 38.552 확인. 실제 설정 파일을 읽어 GameWidget 생성 전후 값·파일 바이트 유지 및 HUD 숫자 표시를 검사, 회귀 검사 34개 통과. v2026.11.17.9 EXE 자체 검사 11개 항목 통과, dist_windows_emg_display에 생성. docs/emg-game-display.md 신규 및 배포 문서·위키·Mermaid·README 갱신. TODO: 새 로컬 실행 폴더에 기존 설정 보존 후 실제 표시값 비교. 실제 신호의 전환 전후 변화까지 해결했다고 주장하지 않음.

2026-11-17 후속 확인 — EXTRACTED: v9 ZIP·SHA256 검증 완료. ZIP 생성 후 기존 v8의 최신 설정을 새 로컬 실행 폴더에 바이트 단위 그대로 복사하고 로드 값 동일성 확인(복사 시점 ON 20.213/OFF 10.967/unfiltered). 기존 v8 설정 파일에는 쓰지 않았으며 사용자 설정은 배포 ZIP에서 제외. 남은 TODO는 실제 화면 간 활동값/ON/OFF 비교.

2026-11-17 — EXTRACTED: 사용자 EMG 해결 확인 후 근전도 핵심 소스 7개 해시를 보존한 채 손 스크롤 변경. 두 손가락 90ms 유지 후 위아래 드래그, 정지 시 반복 이동 없음, 자세 해제 시 오클릭 없이 종료. 두 번 주먹 스크롤 토글 제거, 기존 주먹 클릭과 짧은 두 손가락 전환 유지. 메인·설정·결과·기록 안내/문서/Mermaid/EXE 자체 검사 갱신. 손 커서·결과 목록 회귀 및 EMG 34개 검사, 최신 EXE 자체 검사 11개 항목 통과. 2026.11.17.10을 dist_windows_current에 생성하고 SHA256 검증. 런타임 66개 사본 백업·해시 검증, 최신 폴더에 고유 51파일 이관. 구버전 EXE 폴더 7개·캐시 5개·ZIP/해시 14개·보고서 9개(백업 보존), 총35항목 정리. backups/version-cleanup-20261117에 manifest/정리 결과 보존, git 추적 제외. 최신 EMG 저장값 unfiltered/ON32.462/OFF19.606 유지. 펌웨어/원본 플래시 백업/소스/가상환경 유지. TODO: 실제 카메라에서 두 손가락 인식·드래그 감도 확인.

2026-11-17 — EXTRACTED: 사용자 확인에 따라 손바닥 펴기/주먹이 아닌 실제 손목 젖힘/굽힘을 입력으로 사용하되, 추가 요청대로 손가락 정확히 두 개를 편 상태에서만 검사. 기존 MediaPipe 결과에 종횡비 보정 3D 관절 추가 전달, 손목→손바닥 기울기와 0.4초 안정 중립 비교. 15도 진입/8도 해제·약90ms 확인, 유지 시 위/아래 스크롤, 중립/자세 해제 시 정지. HOLD WRIST/WRIST READY/SCROLL UP/DOWN 안내 및 기존 주먹 클릭 유지. 손목 단위검사7개+EMG검사34개, 기존 손가락·5레인·손커서·결과 목록 검사, v2026.11.17.11 EXE 자체 검사11항목 통과. 핵심 EMG 소스7개 해시 동일. dist_windows_current에 새 버전 교체, 51개 런타임 파일 백업·SHA256 검증·이관(EMG unfiltered/ON32.462/OFF19.606 유지), v10 ZIP/검사/캐시 정리. backups/wrist-scroll-upgrade-20261117에 목록과 이전 자체 검사 보존. 문서·위키·Mermaid·배포 README 갱신. INFERRED: 전완 추적 없는 카메라 기준 손 기울기 추정이므로 손바닥을 카메라로 향하고 팔을 고정해야 함. TODO: 실제 카메라에서 방향·인식·감도 확인.

2026-11-17 ? EXTRACTED: ??? ?? PPT ??? ????? 7? ?? ?? ??. ?? 180???? 120? ??, ??? ??/?? ??, ?? ?? ??? ??, ?? ???Mermaid ??. ?? ?? ?? ??. ZIP/XML/?? ?? ?? ??. TODO: ?? ??, ?? PC?? ?? ??????? 5? ???.
