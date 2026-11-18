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

## 2026-11-18 Leap Motion 4??

EXTRACTED: ??? ???? Orion ?? ??? ABI ????? ??? ???? ??? 4???? ??. EMG ?? ??, ?? ???SDK ?? ?? ??. ??: [?? ??](docs/leap-four-lane.md), [?????](diagrams/leap-four-lane.md). SDK ?? ??, 3? ???? ?????????? ???. ?? ?? ??? ??? EXE ??? TODO.

EXTRACTED: `python -m unittest docs.check_leap_input -v` 3? ??. Qt offscreen ?? ?????? ? ?? Python ??? ?? ??.

## 2026-11-18 Leap 4?? EXE ??

EXTRACTED: ? dist_windows_leap_4lane_2026.11.18 ??? No-Bandpass EXE ??. spec? SDK ???DLL ??, frozen SDK ?? ??, diagnostics 4?? ?? ??. EXE ?? ?? 12?? ??(ok=true, lane_count=4). ?? ??? ??. ?? ?? ??? TODO. [??](docs/leap-four-lane.md).
## 2026-11-18 Leap Motion 전용 입력

EXTRACTED: 근전도 작업 보류, 핀치 모드만 연속 MISS 10회 즉시 종료 추가. PERFECT/GOOD이면 횟수 초기화. 음악 재생 중에도 finish_game으로 종료하고 결과 원인 기록. EMG 동작 유지. 회귀 검사 49개 통과. [문서](docs/leap-miss-limit.md), [Mermaid](diagrams/leap-miss-limit.md). 실제 장치 확인 TODO.

EXTRACTED: `dist_windows_leap_miss10_2026.11.18` 새 EXE 생성, 자체 검사 15항목 통과(`ok=true`, `pinch_consecutive_miss_limit=10`). 기존 설정·핀치 보정 2개 파일 보존. 실행 안내문·검사 보고서 포함, 이전 빌드 유지.

EXTRACTED: 수동 EMG 보정 UI를 제거하고 매 근전도 게임 시작 전 3초 신선한 안정 패킷 평균을 측정한다. 측정 완료 전 음악/노트/점수 정지. 소수 둘째 자리 정수 비교로 안정 기준+0.01부터 활성, 기존 ON/OFF·감소형·재무장 bool 무시. 신호 손실 시 3초 재측정, 핀치 개인별 보정 유지. 회귀 검사 45개 통과. [문서](docs/emg-rest-baseline.md), [Mermaid](diagrams/emg-rest-baseline.md). 실제 센서 확인 TODO.

EXTRACTED: `dist_windows_emg_rest_001_2026.11.18` 최종 EXE 빌드. 메인·결과 화면의 과거 EMG 임계값/보정 표시 제외. 최종 EXE 자체 검사 14항목 통과(`ok=true`, 3초·+0.01). 이전 설정·핀치 보정 2개 파일 보존. 안내문·검사 보고서 포함.

EXTRACTED: EMG 보정/게임 값 차이 재점검. 화면별 포트 재연결·필터 재초기화 구조를 공유 EMGSession으로 변경하고 성공한 자동 보정의 소스·ON/OFF를 즉시 저장한다. 보정값 표시는 소수 두 자리로 통일. 근전도 판정 ±350ms/PERFECT 150ms, 짧은 활성 저하 400ms 회복 허용, 새 보정 ON 35%/OFF 10%. 센서 손실·오래된 데이터 성공 차단 유지. 모의 시리얼 보정→게임의 동일 리더·값·임계값 검사 포함 40개 통과. 실제 장치·사용자 검증 TODO. [문서](docs/emg-assisted-input.md), [Mermaid](diagrams/emg-assisted-input.md).

EXTRACTED: `dist_windows_emg_assisted_2026.11.18` 새 EXE 빌드. 이전 설정·핀치 보정 2개 파일 복사, 이전 폴더 유지. EXE 자체 검사 14항목 통과(`ok=true`, 박자 350ms·활성 저하 400ms). 안내문과 검사 보고서 포함. 기존 EMG 임계값은 보존하므로 약한 수축용 비율 적용은 자동 보정 재실행 필요.

EXTRACTED: 사용자 요청으로 게임 시작을 게임 선택으로 바꾸고 EMG 1레인/핀치 4레인 분리. 한 번 분석·생성하여 notes와 emg_notes를 함께 저장하는 v2 채보 추가. EMG 짧은 노트는 새 수축, 긴 노트는 꼬리까지 유지 후 한 번 득점하며 중도 해제/250ms 입력 공백은 MISS. 긴 노트 몸통·꼬리·유지 시간 표시와 결과 모드·긴 노트 성공 수 기록. 기존 EMG 처리 코드는 유지. 이전 채보 로딩·모드별 샘플·장치 독립성 포함 소스 검사 30개 통과. [문서](docs/game-modes.md), [Mermaid](diagrams/game-modes.md). 실제 장치 플레이 TODO.

EXTRACTED: `dist_windows_dual_mode_2026.11.18` 새 EXE 생성. 이전 설정·개인별 보정 2개 파일 복사, 이전 배포 폴더 유지. EXE 자체 검사 13항목 통과(`ok=true`, 두 모드 채보 저장·로딩 및 긴 노트 판정 포함). 실행 폴더에 안내문·검사 보고서 포함.

EXTRACTED: 요청에 따라 EMG 판정 조건·수축 시작 감지를 제외하고 기준선 도착 시 해당 핀치를 유지하면 득점하도록 변경. 게임의 EMG 리더 생성을 중단하고 키보드로 가짜 손 상태를 만드는 경로 제외. 같은 핀치 유지로 연속 노트 각각 득점, 도착 전 조기 득점 방지. 게임 HUD·새 결과 모드 표시 변경, EMG 테스트·보정은 유지. 소스 검사 21개 통과. [문서](docs/pinch-hold-scoring.md), [Mermaid](diagrams/pinch-hold-scoring.md). 실제 장치 플레이 TODO.

EXTRACTED: `dist_windows_leap_pinch_hold_2026.11.18` 새 EXE 생성. 기존 개인별 핀치 보정 파일 검증 후 복사. 자체 검사 11항목 통과(`ok=true`, `gameplay_emg_enabled=false`). 실행 폴더에 안내문·보고서 포함. 이전 빌드 유지.

EXTRACTED: 이전 핀치 해제 범위가 새 후보를 덮어써 연속 전환을 막는 조건을 재현했다. 명확한 새 후보는 즉시 전환하고 모호한 후보에만 기존 유지 조건을 적용하도록 수정. 최초 진입·해제 안정화 유지. 36방향/보정 조합 포함 소스 검사 15개 통과. [상세](docs/leap-personal-calibration.md#손을-펼치지-않는-연속-핀치-전환). 실제 사용자 손 전환 검증 TODO.

EXTRACTED: `dist_windows_leap_direct_pinch_2026.11.18` 새 EXE 생성. 기존 개인별 보정 파일 유효성 검증 후 복사. EXE 자체 검사 11항목 통과(`ok=true`), 보정 12방향 즉시 전환 포함. 이전 실행 폴더 유지.

EXTRACTED: 개인별 Leap 핀치 보정 기능 추가. 설정에서 열린 손+네 핀치를 1초 준비/3초 측정하고 거리 중앙값으로 네 임계값을 계산한다. 로컬 이름별 프로필 저장/선택/기본값 복귀와 다음 게임 적용. 원시 좌표 미저장. 부족 측정·분리 부족·잘못된 보정값 저장 방지. 소스 회귀 검사 12개 통과. [문서](docs/leap-personal-calibration.md), [Mermaid](diagrams/leap-personal-calibration.md). 실제 사용자 손 검증 TODO.

EXTRACTED: `dist_windows_leap_personal_calibration_2026.11.18` 새 EXE 빌드 완료. 자체 검사 10항목 통과(`ok=true`). SDK·안내문·검사 보고서를 실행 폴더에 포함. 이전 빌드 폴더 유지.

EXTRACTED: 노래 없는 게임의 레인 전환 재점검. 구 EXE와 직전 수정 EXE의 내장 샘플 배열을 비교했다. 실행 중 EXE 경로는 미확인. 모든 채보가 엔진 진입 시 MIDDLE → RING 제약을 거치도록 보강. 실제 무곡 GameWidget 순서·렌더링 검사 추가, 소스 검사 8개 통과. 기존 채보 파일은 덮어쓰지 않는다. [상세](docs/leap-only.md#노래-없이-시작하는-샘플-게임-재점검).

EXTRACTED: `dist_windows_leap_sample_fix_2026.11.18` 새 EXE 생성. EXE 자체 검사 9항목 통과. 무곡 게임 실제 레인 `1,2,1,4,3,2,1,2,4,3,1,4` 확인. 보고서 `release/self-test-leap-sample-fix-2026.11.18.json`.

EXTRACTED: 추가 요청으로 새 채보의 MIDDLE → RING 전환을 금지했다. 노트 간격 정리 후 해당 RING을 INDEX로 변경하며 시각·개수 유지. 샘플/대체 채보도 적용. 기존 채보는 재생성 필요. 1,024개 레인 조합을 포함한 테스트 7개 통과. [상세](docs/leap-only.md#middle-다음-ring-생성-금지).

EXTRACTED: `dist_windows_leap_only_no_middle_ring_2026.11.18`에 제약 반영 EXE 생성. 자체 검사 8항목 통과(`ok=true`). 이전 EXE 유지. 실행 폴더에 안내문과 검사 결과 포함.

EXTRACTED: `dist_windows_leap_only_2026.11.18`에 새 EXE 생성 완료. 소스 검사 4개 및 EXE 자체 검사 8항목 통과(`ok=true`, `camera_input_enabled=false`, `lane_count=4`). 실행 폴더에 SDK·안내문·검사 보고서 포함. 이전 빌드 유지.

EXTRACTED: 사용자 요청으로 웹캠·MediaPipe 입력을 비활성화했다. 메인/보정/게임은 Leap 입력을 사용하고 카메라 설정·미리보기·메뉴 커서 연결을 제외했다. 게임은 핀치 4레인과 기존 EMG 판정을 유지한다. 빌드에서 MediaPipe 패키지·모델 제외. [문서](docs/leap-only.md), [Mermaid](diagrams/leap-only.md). 실제 장치 플레이 확인 TODO.


EXTRACTED: 2026-11-18 OYMotion 충전 후 COM4 실장치 수신 재개. 연결 후 약 20초간 9,952개 8채널 프레임, 잘못된 패킷 0개. 기존 구현의 SDK 설정·전체 채널 AC RMS·시작 전 3초 안정 기준+0.01 흐름을 [문서](docs/oymotion-emg.md)와 [Mermaid](diagrams/oymotion-emg.md)에 기록하고 wiki 색인을 갱신. 관련 소스 검사 56개 통과. AMBIGUOUS: 착용 후 수축 구분과 장시간 연결 검증은 TODO.

EXTRACTED: `dist_windows_oymotion_2026.11.18`에 새 EXE 빌드 완료. 기존 핀치 보정·설정 복사, 새 폴더의 EMG 장치는 OYMotion/COM4로 지정. SDK 두 DLL 로딩·ABI 크기·해시 검사 통과, EXE 자체 검사 15항목 통과. 각 보고서를 배포 폴더 및 `release/`에 저장. 이번 재개 작업에서는 기존 게임 동작을 더 수정하지 않았다.
EXTRACTED: 2026-11-18 사용자 요청으로 핀치 보정을 설정에서 매 게임 시작 전으로 이동. 기존 프로필·기본값 사용 우회를 제거하고 새 다섯 동작 측정·검증·저장 후에만 시작. 취소 시 미시작, 재시도에도 보정. EMG 시작 전 3초 안정값 측정 유지. [문서](docs/pre-game-calibration.md), [도식](diagrams/pre-game-calibration.md), wiki 색인 및 회귀 검사 추가.
EXTRACTED: 시작 전 보정 빌드 `dist_windows_pre_game_calibration_2026.11.18` 완료. 관련 소스 검사 59개, EXE 자체 검사 15항목 통과. 기존 설정·프로필 복사 및 이전 빌드 보존. 실제 Leap 측정에서 보정 완료 후 게임 전환은 현장 검증 TODO.
EXTRACTED: 2026-11-18 요청에 따라 열린 손·네 핀치의 Leap/armband 동시 보정과 두 센서 일치 판정을 추가. OYMotion 새 8채널 RMS 특징을 수집하고 게임마다 메모리 분류 모델 생성. 불확실·불일치·장치 변경·신호 소실 시 레인 미인정. HUD 및 세션 기록에 의도·일치 표시. 관련 검사 66개 통과. [문서](docs/pinch-armband-intent.md), [도식](diagrams/pinch-armband-intent.md). 실제 착용 분류 성능은 미검증.
EXTRACTED: `dist_windows_pinch_armband_2026.11.18` 새 EXE 빌드 완료. 소스 검사 최종 67개 및 EXE 자체 검사 16항목 통과(`pinch_requires_sensor_agreement=true`). SDK DLL 해시 일치, 기존 설정·Leap 보정 프로필 복사 확인. 이전 빌드 보존. 실제 착용자의 다섯 자세 분리·동시 보정·게임 판정은 TODO.
EXTRACTED: 2026-11-18 테스트용 armband 단독 핀치 선택 추가. Leap 없이 다섯 자세 보정 후 분류가 직접 4레인 선택. 일반 두 센서 모드와 분리하고 재시도 선택 유지. 세션·결과에 입력 출처 기록. 관련 검사 71개 통과. [문서](docs/armband-only-test.md), [도식](diagrams/armband-only-test.md), wiki·README 갱신. 실제 착용 인식 검증은 TODO.
EXTRACTED: armband 단독 테스트 빌드 `dist_windows_armband_only_2026.11.18` 완료. 소스 검사 71개 및 EXE 자체 검사 17항목 통과(`armband_only_test_enabled=true`). SDK DLL 해시와 기존 설정·프로필 복사 확인, 이전 빌드 보존. 실제 착용 테스트는 TODO.
EXTRACTED: 2026-11-18 사용자 USB 초기화 code 1 오류 조사. 연결된 COM 포트 없음, 과거 FTDI COM4는 Disconnected. 드라이버 등록 존재. Windows 장치 재검색은 Access is denied로 실패. 실패 reader가 같은 설정으로 재사용되는 오류를 수정하고 COM 미감지 안내를 추가. 관련 검사 74개 통과. [문서](docs/armband-reconnect.md), [도식](diagrams/armband-reconnect.md). 실제 동글 인식·수신 복구는 미확인.
EXTRACTED: 재연결 수정 빌드 `dist_windows_armband_reconnect_2026.11.18` 완료. 소스 74개 및 EXE 자체 검사 17항목 통과. 기존 설정·보정 복사 후 새 폴더 포트만 Auto로 지정. 최종 현재 COM 목록은 비어 있어 실수신 복구는 미확인.
EXTRACTED: 후속 사용자 화면의 COM 미감지 재점검. FTDI USB Serial Converter는 IsPresent=FALSE/Disconnected, 기존 상위 Generic USB Hub는 Started. 현재 COM 및 문제 장치 목록 없음. 동글이 현재 열거되지 않는 상태임을 확인했으며 물리 원인은 미확정. 본체 USB에 직접 연결한 상태로 재확인 요청. 게임 코드·EXE는 변경하지 않고 기존 연결 진단 문서만 보강.
INFERRED: 사용자 테스트에서 USB 동글 본체 직결은 정상, 허브 연결은 실패한다고 보고. 기존 USB 상태 관찰과 합쳐 허브 연결 경로 문제로 범위를 좁힘. 본체 직결 후 Refresh EMG Devices → Connect / Test EMG 안내. 구체적 허브 원인은 미확정이며 추가 코드·EXE 변경 없음. 진단 문서와 wiki 색인 보강.
EXTRACTED: 본체 직결도 실패한 후 게임 종료를 확인하고 관리자 RunAs 장치 재검색 수행(종료 코드 0). COM 없음·FTDI Disconnected 지속. 현재 USB Composite Device는 BusReportedDeviceDesc=Leap Motion Controller, VID_F182/PID_0003으로 확인되어 armband FTDI 동글과 구분. AMBIGUOUS: 허브만의 문제라는 이전 추론은 미확정으로 정정. 다른 PC 검사는 불가. 문서·wiki·도식 갱신, 코드·EXE 변경 없음.
EXTRACTED: 사용자 HID 목록의 Bluetooth GATT HID 부모를 직접 조회하여 SPA-NMA1PM으로 확인. 기존 gForcePro+와 별도 장치. 현재 전체 Bluetooth 클래스에서도 gForcePro+ 항목 없음, COM 목록 없음. 진단 문서와 wiki 색인 보강. 코드·EXE 변경 없음.
EXTRACTED: 사용자 재부팅 후 COM4를 직접 조회하여 현재 인식 복구 확인. 보정 화면은 8채널 수신 및 다섯 동작 최소 샘플 수를 충족하나 NONE 인정률 80% 검사에서 실패. 연결 장애와 보정 패턴 분리 오류를 구분하여 문서·wiki에 기록. AMBIGUOUS: 원본 벡터가 없어 겹치는 자세와 원인 미확정. 열린 손 재측정 안내, 코드·임계값·EXE 변경 없음.
EXTRACTED: 2026-11-18 사용자 요청으로 일반 핀치를 Leap 70% + EMG 30% 참고 점수 합산으로 변경. EMG 중첩 패턴의 일반 모드 시작 차단 제거, 단독 테스트 엄격 검사 유지. NONE/불확실/신호 소실 입력 보류. L/E/F 점수 HUD와 세션 기록 추가. 관련 검사 81개 통과. [문서](docs/weighted-pinch.md), [도식](diagrams/weighted-pinch.md). 실제 착용 성능은 미검증.
EXTRACTED: 가중 핀치 빌드 `dist_windows_weighted_pinch_2026.11.18` 완료. 소스 검사 81개 및 EXE 자체 검사 17항목 통과. 보고서에서 가중치 0.7/0.3 및 일치 필수 해제 확인. 설정·Leap 프로필 복사, SDK DLL 해시 일치, 이전 빌드 보존. 실제 착용자의 일반 모드 재보정·판정 확인은 TODO.
EXTRACTED: 2026-11-18 요청에 따라 핀치의 armband 연동 전부 제거. Leap 전용 매 게임 보정·입력 복원, 단독 armband 핀치 옵션과 가중 점수 HUD·모듈 제거. 핀치 진입 시 이전 메뉴 EMG 스트림 종료. 별도 근전도 게임·OYMotion 입력 유지. 관련 검사 65개 통과. [문서](docs/pinch-leap-only.md), [도식](diagrams/pinch-leap-only.md), wiki·README 갱신. 실제 Leap 플레이는 TODO.
EXTRACTED: Leap 전용 핀치 새 빌드 `dist_windows_pinch_leap_only_2026.11.18` 완료. 소스 검사 65개 및 EXE 자체 검사 16항목 통과. PYZ에서 제거한 의도 분류·가중 합산 모듈 부재와 별도 EMG reader 유지 확인. 설정·Leap 프로필 복사, 기존 배포 보존. 실제 Leap 보정·플레이는 TODO.
EXTRACTED: 2026-11-18 사용자 확인에 따라 암밴드 팔→근전도 게임, 핀치 손→핀치 게임 이미지 배치. 게임 선택 설명·곡 정보·하단 안내 제거, 이미지와 이름을 그리는 전체 클릭 카드 적용. 원본 PNG 두 개를 app/assets/game_modes에 복사. 1280/800 너비 렌더링 및 버튼 연결 확인, 기존 검사 65개 통과. [문서·미리보기](docs/game-selection-images.md), [도식](diagrams/game-selection-images.md), wiki·README 갱신. 입력·게임 규칙 변경 없음.
EXTRACTED: 이미지 선택 화면 빌드 `dist_windows_image_selection_2026.11.18` 완료. 소스 회귀 검사 65개 및 EXE 자체 검사 16항목 통과. 두 PNG 배포·해시 일치 및 기존 설정·Leap 프로필 복사 확인. 이전 배포 보존. 실제 센서 플레이는 이번 UI 변경 검증 범위에서 수행하지 않았다.
EXTRACTED: 2026-11-18 메뉴 전용 MediaPipe 손 커서 복원. 메인·게임 선택·설정·결과·저장 결과에서 공유 카메라, 게임 진입은 커서 해제 및 모든 작업자 종료 후에만 진행. 결과·보정 취소 시 메뉴 카메라 복구. 설정 카메라 컨트롤·상태 노출, MediaPipe 모델 패키징 복원. 관련 검사 70개 및 소스 모델 초기화·검은 프레임 추론 통과. AMBIGUOUS: 실제 Camera 0/1은 열기 실패하여 물리 손 커서 검증 미완. [문서](docs/menu-hand-cursor.md), [도식](diagrams/menu-hand-cursor.md).
EXTRACTED: 메뉴 손 커서 빌드 dist_windows_menu_hand_cursor_2026.11.18 완료. 소스 검사 70개 및 EXE 자체 검사 17항목 통과, 필수 MediaPipe 모델 다섯 파일 포함 확인. 배포 EXE에서도 실제 Hands 그래프 초기화·빈 프레임 추론·close 통과. 기존 설정·Leap 프로필 복사 후 새 배포 camera_enabled=True 지정, 이전 배포 보존. 실제 Camera 0/1은 열기 실패하여 손 조작 검증은 TODO.
## 2026-11-18 연결·음악 작업 트리 검증

EXTRACTED: docs/music-session-review.md 및 diagrams/music-session-review.md를 추가하고 wiki/index.md에 연결했다. 핀치 문서의 이전 연결 종료 설명에 이력 표시를 추가하고 흐름도를 현재 공유 연결 유지 동작에 맞췄다. 문서화 전용 지침에 따라 이번 이어서 작업에서 게임 소스 추가 수정이나 EXE 생성은 하지 않았다.

EXTRACTED: 기존 테스트 75개 통과. WorkOrder/verify_full_song.py는 테스트 객체 mode 누락으로 실패했다. 실제 저장 MP3 분석은 208.013초, BPM 126.048, 노트 208개였다. 원본 디코딩 길이 213.773초와 차이가 있어 전처리와 원본 타임라인 동기화 확인을 TODO로 남겼다. 물리 장치 장기 연결·전체 곡 청감 검증·새 배포는 미완료다.


## 2026-11-18 Next tasks and Git documentation update

EXTRACTED: Added docs/NEXT_TASKS.md with priorities and acceptance criteria for audio timelines, the full-song test fixture, real armband persistence, menu camera checks, and a verified EXE build. Included docs/music-session-review.md and diagrams/music-session-review.md as observations of the local working tree, not a release guarantee. This commit excludes game source and other pending edits. TODO: implementation and build require a scope permitting code changes under AGENTS.md. View diagrams with Mermaid Markdown preview; run Graphify manually with graphify .
## 2026-11-18 전체 구현 Git 공유

EXTRACTED: 사용자가 armband·Leap을 포함한 전체 구현 푸시를 명시하여 기존 문서 전용 제한의 이번 작업 예외로 적용했다. app 소스, OYMotion SDK DLL·NOTICE, 게임 선택 이미지, PyInstaller spec, 검사와 관련 문서를 공유 범위에 포함한다. 개인 설정·보정 프로필·사용자 곡·실행 로그·EXE 산출물은 포함하지 않는다. 소스 검사 75개를 재실행하여 통과했다. 새 EXE 빌드와 실제 장치 검증은 수행하지 않았다. 음악 시간축 차이와 전체 곡 검사 fixture 오류는 docs/NEXT_TASKS.md의 미해결 과제로 유지한다.
