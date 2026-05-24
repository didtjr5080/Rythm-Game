Agent Rules for Rythm-Game

Purpose

This repository already contains an implemented EMG + hand-tracking rhythm game.

The agent's role is to document, explain, and visualize the existing structure without changing game behavior.

Hard Restrictions

Do not modify:

app/main.py
existing game logic
existing EMG input logic
existing MediaPipe hand-tracking logic
existing note generation logic
existing UI behavior
legacy_web/ source code

Do not add:

Firebase implementation
Firestore implementation
patient database
backend server changes
new gameplay features

Allowed Work

The agent may create or update:

wiki/
docs/
diagrams/
AGENTS.md
log.md
.graphifyignore
README documentation sections only

Required Reading Order

Before answering or documenting, inspect:

README.md
wiki/index.md if it exists
graphify-out/GRAPH_REPORT.md if it exists
Relevant source files

Documentation Rules

When documenting the project:

Separate confirmed facts from inferred interpretation.
Mark claims as:
EXTRACTED: directly verified from source code or README
INFERRED: inferred from multiple files
AMBIGUOUS: uncertain or conflicting
Keep diagrams synchronized with the current code structure.
Do not invent features that are not implemented.

Update Rules

When new documentation is added:

Update wiki/index.md
Update log.md
Add or update Mermaid diagrams if relevant

Output Rule

Every final response must include:

Files created or modified
What was documented
How to view the diagrams
How to run Graphify manually
Remaining TODO
