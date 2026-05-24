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
