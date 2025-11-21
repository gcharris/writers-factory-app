### **Writers Factory Desktop: Master Architecture Document v2.0**



**Status:** Phase 2 Complete. Preparing for Phase 3 (The Soul & The Graph).

------



#### **1. Gap Remediation Strategy**



Here is how we are solving the five critical gaps identified in the audit:

**Gap 1: File System Sync (The "Two-Way Mirror" Problem)**

- **Solution:** A **File Watcher Service** (`watchdog` in Python) that monitors the `content/` directory.
- **Logic:**
  - **App -> Disk:** When you save in the app, it writes to disk AND updates the Graph Node immediately.
  - **Disk -> App:** If you edit a file in VS Code or Obsidian, the Watcher detects the change, triggers a "Re-Ingest" event, and updates the Graph (and UI) automatically.
  - **Conflict Resolution:** "Last Write Wins" timestamp logic to prevent loops.

**Gap 2: Security & API Keys**

- **Solution:** Move keys out of `.env` (which is insecure for distributed apps) and into the **OS Keychain** (Mac Keychain / Windows Credential Manager) using `keyring` library.
- **Usage:** The app prompts for keys on first run, stores them securely in the OS, and retrieves them in memory only when running a tournament. They are never written to plain text files.

**Gap 3: Professional Editor Features**

- **Solution:** Integrate **Monaco Editor** (the engine behind VS Code) instead of a simple `<textarea>`.
- **Features:**
  - Syntax highlighting for Markdown.
  - Mini-map for navigation.
  - **Inline Decorations:** We will use Monaco's API to render "AI Comments" (critiques) as yellow underlines/hover widgets, keeping the text clean.
  - **Split View:** A "Context Pane" (Svelte component) that sits right of the editor to show the Character Sheet for the active scene.

**Gap 4: RAG-Lite Specification**

- **Solution:** A "Hybrid Retrieval" strategy.
  - **Chunking:** Split "World Bible" files by Header (`# Character Name`).
  - **Storage:** Store chunks in SQLite with a simple vector embedding (using `sentence-transformers` locally, no API cost).
  - **Retrieval:**
    1. **Keyword Match:** "Mickey" -> Fetch `Mickey.md`.
    2. **Vector Search:** "Betrayal" -> Fetch chunks semantically related to betrayal.
  - **Context Window:** Top 5 chunks + "Current Scene Scaffold" are injected.

**Gap 5: Narrative Scoring Methodology**

- **Solution:** A "Rubric-Based" Prompting System.
- **Logic:** The Critic Agent isn't just asked "Rate this." It is given a specific **Rubric Schema** (JSON).
  - *Philosophy Integration:* "Does this scene advance the theme of 'Man vs Machine'? Score 1-10. Quote specific lines."
  - *Voice:* "Count the number of street metaphors. If < 2, score < 5."
- **Output:** The agent returns a JSON object `{ "scores": {...}, "reasoning": "..." }` which the UI renders as a scorecard chart.

------



#### **2. Updated System Architecture**



**A. Frontend (Tauri + SvelteKit)**

- **Editor:** Monaco Editor (wrapped in a Svelte component).
- **State:** `stores.js` syncs with the Backend via WebSocket (for real-time graph updates).

**B. Backend (Python FastAPI)**

- **Services:**
  - `file_watcher.py`: The sentry monitoring disk changes.
  - `key_manager.py`: The guard handling OS Keychain access.
  - `graph_service.py`: The brain managing NetworkX + SQLite.
  - `rag_engine.py`: The librarian handling Embeddings + Retrieval.

**C. Data Layer**

- **Graph (SQLite):** Stores Nodes, Edges, and *Vectors*.
- **Files (Markdown):** The "Hard Copy" source of truth.

------



#### **3. Revised Roadmap (Phase 3 Breakdown)**



**Phase 3: The Soul (Context & Security) [IMMEDIATE PRIORITY]**

1. **Secure Key Storage:** Implement `key_manager.py` to migrate keys from `.env` to OS Keychain.
2. **Graph Ingestor (The Reader):** Build the script to parse `content/` into SQLite nodes.
3. **File Watcher:** Implement `watchdog` to auto-update the graph on file save.
4. **RAG-Lite:** Implement basic keyword matching for Context Injection.

**Phase 4: The Professional Editor**

1. **Monaco Integration:** Swap `<textarea>` for Monaco.
2. **Split View:** Build the "Context Sidebar" (Character Sheets).

**Phase 5: The Critic**

1. **Scoring Engine:** Implement the JSON Rubric system for the Judge.

