Graphify Usage

This document explains how to generate a project structure graph for this repository.

Purpose

Graphify is used only for structure visualization and documentation support.

It must not change the implemented game.

Install

python -m venv .venv

Windows PowerShell:

.venv\Scripts\activate
pip install graphifyy

Git Bash:

source .venv/Scripts/activate
pip install graphifyy

Run

graphify .

Output

Expected output:

graphify-out/
├── graph.json
├── GRAPH_REPORT.md
└── graph.html

Notes
Check graphify --help because available commands may differ by installed version.
Use .graphifyignore to exclude runtime data and large files.
Do not upload private patient data or secret keys.

TODO
If the graphify command is not found, install graphifyy in the active environment and retry.
If graphify reports a missing LLM API key, pass --backend or set the required API key env var.
If the OpenAI backend returns a 429 insufficient_quota error, verify billing or use a different backend.

OpenAI Example

Set the API key and run Graphify with the OpenAI backend:

PowerShell:

$env:OPENAI_API_KEY = "<your-api-key>"
graphify . --backend openai

Gemini Example

Set the API key and run Graphify with the Gemini backend:

PowerShell:

$env:GEMINI_API_KEY = "<your-api-key>"
graphify . --backend gemini
