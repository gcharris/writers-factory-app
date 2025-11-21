# 🏭 Writers Factory Desktop: Master Architecture (Final)

**Version:** 3.0 (Unified) **Date:** 2025-11-21 **Philosophy:** Local-First, Graph-Driven, Context-Aware.

## 1. 🏗️ System Architecture

The application uses a **Sidecar Architecture**: a lightweight Rust/JS frontend coupled with a heavy Python backend and specialized Bridges.

### **A. Frontend (The Face)**

- **Tech Stack:** Tauri v2 (Rust), SvelteKit, TypeScript.
- **State:** `stores.js` syncs with Backend via REST/WebSocket.
- **Components:** `FileTree` (Native FS), `Editor` (Monaco wrapper), `AgentPanel`.

### **B. Backend (The Brain)**

- **Tech Stack:** Python 3.12 (FastAPI).
- **Core Services:**
  - `orchestrator.py`: Manages the Tournament lifecycle.
  - `llm_service.py`: Universal adapter for OpenAI, Anthropic, XAI.
  - `graph_service.py`: Manages NetworkX (Hot) and SQLite (Cold) memory.
- **Security:** API Keys stored in **OS Keychain** (via `keyring`), never in text files.

### **C. The Bridges (External Comms)**

- **Ollama Bridge:** Local inference for fast, zero-cost tasks (Spellcheck, Graph extraction).
- **MCP Bridge (NotebookLM):** A Node.js sidecar that connects to Google's NotebookLM for "Ground Truth" queries.

## 2. 🧠 The Narrative Protocol (Data Structure)

The system enforces a structured "Story Bible" before drafting begins.

### **Phase 1: Foundation (Context Injection)**

- **Artifacts:** `Mindset.md`, `Premise.md`, `Theme.md`, `Voice_Rules.md`.
- **Usage:** These are pre-pended to **every** Agent's system prompt.

### **Phase 2: The Knowledge Graph (Dynamic Memory)**

- **Schema:**
  - **Nodes:** Characters, Locations, Objects.
  - **Edges:** Relationships (LOVES, BETRAYS, OWNED_BY).
  - **State:** Nodes have mutable properties (`status: wounded`).
- **Ingestion:** On startup, the `Ingestor` scans `content/World Bible/` and builds the graph.
- **Sync:** A `watchdog` service monitors file changes and updates the graph in real-time.

### **Phase 3: The Structural Blueprint**

- **Artifacts:** `Beat_Sheet.md`, `Scene_Strategy.md`.
- **Usage:** The Tournament Orchestrator reads the *current beat* to determine the pacing instructions for the agents.

## 3. 🔄 NotebookLM Integration (The Oracle)

*Based on Legacy Phase 9 Research*

Instead of manual exports, we use an **MCP (Model Context Protocol)** Bridge.

### **Architecture**

1. **MCP Server:** A Node.js process (`notebooklm-mcp`) running locally.
2. **Client:** A Python service (`NotebookLMMCPClient`) inside FastAPI.
3. **Workflow:**
   - **Query:** Backend asks: *"What does Mickey fear most?"*
   - **Bridge:** MCP Server queries your specific "Character Notebook" in NotebookLM.
   - **Response:** NotebookLM returns the grounded answer + citations.
   - **Action:** This response is injected into the Tournament context or used to update the Graph.

## 4. 🛠️ Operational Workflows

### **A. The Tournament Pipeline**

1. **Setup:** User selects Squad (e.g., Claude + Grok).
2. **Context Assembly:**
   - Load `Voice_Rules.md`.
   - Query Graph for characters in the scene.
   - (Optional) Query NotebookLM for obscure lore.
3. **Drafting:** Agents generate variations in parallel.
4. **Judging:** GPT-4o selects the winner based on the **Rubric Schema** (Voice adherence, Plot advancement).
5. **Output:** Winner text streams to Editor; Graph updates with new events.

### **B. File System Sync**

- **App -> Disk:** User saves -> writes `.md` file -> updates Graph Node.
- **Disk -> App:** User edits in VS Code -> `watchdog` detects change -> re-ingests to Graph -> UI updates.

## 5. 🗺️ Implementation Roadmap

**Phase 1: The Foundation (✅ Done)**

- Native App Shell, File System, Basic Tournament.

**Phase 2: The Soul (🚧 NEXT)**

- **Step 1:** Build `ingestor.py` to parse the "Story Bible" folders into a basic in-memory Graph.
- **Step 2:** Connect `TournamentOrchestrator` to this Graph (Context Injection).
- **Step 3:** Implement the **MCP Bridge** to connect NotebookLM.

**Phase 3: The Polish**

- Monaco Editor integration.
- Visualization Dashboard.