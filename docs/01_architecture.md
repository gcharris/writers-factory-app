# System Architecture: Writers Factory Desktop

**Version:** 3.0 (Final Desktop Spec)
**Core Philosophy:** Local-First, Graph-Driven, Hybrid AI.

## 1. Executive Summary
Writers Factory Desktop is a specialized IDE for novelists. It abandons the client-server web model in favor of a local, high-performance application where the **Knowledge Graph** is the state engine.

**Key Differentiators:**
1.  **Graph-as-Truth:** The story is stored as a NetworkX graph (relationships, consistency), not just text files.
2.  **Hybrid AI:** Uses Gemini 3.0 CLI (Cloud) for heavy reasoning and Ollama (Local) for fast, zero-cost utility tasks.
3.  **Tournament System:** Inherited from the web platform, running 5-agent competitions to draft scenes.

## 2. Tech Stack
* **Frontend:** Tauri v2 (Rust) + SvelteKit + TypeScript.
* **Backend:** Python 3.12 (running as a sidecar binary).
* **Database:**
    * **Hot:** NetworkX (In-Memory Graph).
    * **Warm:** SQLite (Persistence & Vector Search).
    * **Cold:** JSON/Markdown Exports.
* **AI Bridge:** `gemini_cli.py` (Subprocess wrapper) + `ollama` (REST API).

## 3. Core Components (The "Critical Additions")

### A. Hybrid Graph Storage
To handle 100k+ word novels without lag:
* **Active Memory:** The current scene and its immediate connections (radius=10) are loaded into NetworkX.
* **Backing Store:** Full story history resides in SQLite.
* **Logic:** `backend/graph/hybrid_store.py` handles the hot/warm swapping.

### B. Versioning (Time Travel)
* **Checkpoints:** Every "Lock" action creates a graph snapshot.
* **Diffing:** The system calculates `nodes_added`, `edges_changed`, and `character_arcs_diverged` between snapshots.

### C. Plugin Architecture
Future-proof design allowing custom Python scripts to hook into the graph:
* `register_agent()`: Add new LLM providers.
* `register_query()`: Add custom graph analysis (e.g., "Weather Tracker").
* `register_exporter()`: Add Scrivener/Docx formats.

## 4. Directory Structure

```plaintext
writers-factory-desktop/
├── frontend/                    # Tauri + Svelte
│   ├── src/
│   │   ├── graph-panel/         # D3.js Visualization
│   │   ├── editor/              # Monaco Editor
│   │   └── dashboard/           # Story Health & Tournament UI
│
├── backend/                     # Python Core
│   ├── graph/                   # THE ENGINE (Ported from Web)
│   │   ├── graph_service.py     # NetworkX Logic
│   │   ├── hybrid_store.py      # SQLite Sync
│   │   └── versioning.py        # Time Travel
│   │
│   ├── agents/                  # AI Orchestration
│   │   ├── tournament.py        # Multi-Agent Drafting
│   │   └── scoring.py           # The 7-Dimension Scoring Logic
│   │
│   ├── models/                  # Pydantic/SQLAlchemy Schemas
│   └── bridges/                 # Gemini CLI & Ollama
```
