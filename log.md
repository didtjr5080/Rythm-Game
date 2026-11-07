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
