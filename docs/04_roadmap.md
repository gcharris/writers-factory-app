# Implementation Roadmap

## Phase 1: The Great Port (Week 1)
**Goal:** Establish the Graph Engine using existing code.
1.  **Setup:** Init Tauri + Python environment.
2.  **Port:** Copy `graph_service.py`, `models.py`, `ner_extractor.py` from old repo.
3.  **Refactor:** Convert PostgreSQL models to SQLite (using `docs/03_data_schema.md`).
4.  **Verify:** Write a script to ingest a test novel and query the graph.

## Phase 2: The Brain (Week 2)
**Goal:** Connect Gemini 3.0 CLI.
1.  **Bridge:** Implement `backend/bridges/gemini_cli.py` (REST API version).
2.  **Architect:** Use Gemini to write the `Tournament` logic.
3.  **Test:** Run a headless tournament (CLI only) generating 3 drafts.

## Phase 3: The Face (Week 3)
**Goal:** Build the UI.
1.  **Editor:** Integrate Monaco for writing.
2.  **Graph:** Integrate D3.js to visualize `nodes` and `edges`.
3.  **Dashboard:** Create the "Tournament Results" view (Side-by-side diffs).

## Phase 4: Polish (Week 4+)
1.  **Plugins:** Implement the registry system.
2.  **MCP:** Connect NotebookLM.
3.  **Packaging:** Build `.dmg` / `.exe` installers.