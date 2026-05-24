Structure Visualization

Mermaid diagrams in the diagrams/ folder are rendered automatically on GitHub.
If you view these files locally, ensure your Markdown viewer supports Mermaid.

Diagrams Folder

diagrams/
- system-overview.md
- data-flow.md
- input-flow.md
- game-loop.md
- file-structure.md

Graphify Output

graphify-out/graph.html can be opened directly in a browser for a clickable structure view.
graphify-out/GRAPH_REPORT.md provides a textual summary of the extracted graph.
On Windows PowerShell:

Set-Location D:\Develop\Rythm-Game\rhythm-note-generator
Start-Process .\graphify-out\graph.html

Roles

Mermaid diagrams provide curated, human-readable structure views.
Graphify output provides an auto-generated snapshot of the repository structure.
