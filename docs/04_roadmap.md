# Implementation Roadmap (V4.1 Updated)

## Phase 1: The Foundation (✅ Done)
**Goal:** Core App Infrastructure.
1.  **Setup:** Tauri + Svelte + Python Backend.
2.  **Graph Engine:** NetworkX + SQLite implemented.
3.  **UI:** Editor, Graph Panel, Agent Panel built.
4.  **Tournament:** Basic drafting logic functional.

## Phase 2: The Oracle (✅ Done)
**Goal:** NotebookLM Integration.
1.  **MCP:** Bridge connected via `notebooklm-mcp`.
2.  **Integration:** App can query research notebooks.
3.  **Verification:** Proven to work with live Google NotebookLM accounts.

## Phase 3: The Metabolism (🚧 Current Focus)
**Goal:** Stateful Session & Memory Digestion.
1.  **Session Manager:** Stop "fire-and-forget". Build SQLite session logging.
2.  **Consolidator Agent:** Local Llama 3.2 script to parse saved text into graph nodes.
3.  **Conflict Resolution:** Logic to detect when new text contradicts old graph facts.

## Phase 4: The Immune System (Planned)
**Goal:** Story Health & Versioning.
1.  **Health Service:** Automated checks for Dropped Threads, Timeline Errors, and Character Absences.
2.  **Version Control:** Graph snapshotting ("Time Travel") and Branching ("What If" scenarios).
3.  **Procedural Memory:** Vectorizing user preferences ("Style Learning").

## Phase 5: Polish & Release
1.  **Packaging:** Build `.dmg` / `.exe` installers.
2.  **Optimizations:** Lazy loading for large graphs.
3.  **Plugins:** External agent registry.
