# Manager Installation Plan (The "Writer's Cursor")

**Objective:** Install the "Manager" (Integrated Agent) into the Writers Factory Desktop. This component mimics the "Cursor" experience—an always-available, local AI sidebar that has direct access to the user's project files and can perform actions (ideation, graph updates) without latency or cost.

## 1. Architecture Alignment
This plan implements the **"Ideation Engine"** and **"Local Utility"** components described in `docs/02_scene_pipeline.md` and `docs/MASTER_ARCHITECTURE.md`.

*   **Role:** The Manager (Local/Ollama).
*   **Function:** File RAG (Retrieval Augmented Generation), Brainstorming, Graph Updates.
*   **Location:** Persistent Sidebar (Right Pane).

## 2. Implementation Steps

### Step 1: Backend Service (`backend/services/manager_service.py`)
We need a dedicated service to handle local LLM interactions via Ollama.
*   **Dependency:** `ollama` python library.
*   **Class:** `ManagerService`.
*   **Capabilities:**
    *   `chat(message, context)`: Standard chat with memory.
    *   `read_file(path)`: Ability to ingest local file content.
    *   `summarize(text)`: Quick utility for the graph.

### Step 2: API Endpoints (`backend/api.py`)
Expose the Manager to the frontend.
*   `POST /manager/chat`: Send a message to the Manager.
*   `POST /manager/context`: Update the Manager's awareness (e.g., "Focus on Chapter 1").

### Step 3: Frontend UI (`frontend/src/lib/components/ChatSidebar.svelte`)
A new UI component that lives alongside the Editor.
*   **Layout:** Vertical pane on the right side (collapsible).
*   **Features:**
    *   Chat Interface (User/Agent bubbles).
    *   Context Indicator (e.g., "Reading: Chapter 1.md").
    *   Action Buttons (e.g., "Summarize Selection", "Add to Bible").

### Step 4: Integration
*   Update `App.svelte` (or main layout) to include the `ChatSidebar`.
*   Ensure `llm_service.py` can hand off tasks to the Manager if needed (optional for Phase 1).

## 3. Technical Requirements
*   **Ollama:** Must be installed and running locally (`ollama serve`).
*   **Model:** Defaults to `llama3.2` or `mistral` (fast, low resource).
*   **Python Lib:** `pip install ollama`

## 4. Verification
*   User can open the sidebar.
*   User can ask "What is in chapter 1?" (Simulated RAG).
*   Manager responds instantly using local compute.

