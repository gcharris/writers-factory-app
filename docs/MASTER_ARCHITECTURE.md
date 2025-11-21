1. ### **Writers Factory Desktop: Master Architecture Document**

   

   **Version:** 1.0 (Consolidated) **Date:** 2025-11-21 **Status:** Active Development (Phase 2 Complete, Phase 3 Pending)

   ------

   

   #### **1. Vision & Philosophy**

   

   - **Core Concept:** A local-first, AI-powered IDE for novelists that moves beyond simple text generation to deep, structural collaboration.
   - **Key Differentiators:**
     - **Graph-as-Truth:** The narrative state is maintained in a Knowledge Graph (Entities, Relationships, Truths), not just linear text files. This allows for consistency tracking and dynamic context injection.
     - **Hybrid AI:** Leverages a "Squad" of diverse LLMs (OpenAI, Anthropic, Google, etc.) for different tasks (Drafting, Critiquing, World Building).
     - **Local-First:** All data resides on the user's machine. The backend acts as a local server, ensuring privacy and speed.

   ------

   

   #### **2. System Architecture**

   

   The application follows a **Client-Server** model running entirely on the local machine.

   - **Frontend (The Face):**
     - **Technology:** Tauri v2 (Rust) + SvelteKit + TypeScript.
     - **Role:** Handles the UI, file management (via native OS dialogs), and user interaction.
     - **Key Components:**
       - `FileTree`: Manages project structure and file navigation via native OS calls.
       - `Editor`: The primary writing interface (Monaco integration planned).
       - `AgentPanel`: Interface for managing the AI Squad and running tournaments.
       - `GraphPanel` (Planned): D3.js visualization of the Knowledge Graph.
   - **Backend (The Brain):**
     - **Technology:** Python 3.12 (FastAPI).
     - **Role:** Orchestrates AI logic, manages the Knowledge Graph, and handles heavy computation.
     - **Key Components:**
       - `api.py`: The REST API gateway.
       - `orchestrator.py`: Manages the "Tournament" logic (Drafting -> Judging).
       - `llm_service.py`: The universal adapter for connecting to various LLM providers.
       - `graph_service.py` (Planned): Manages the NetworkX/SQLite graph engine.
       - `ingestor.py` (Planned): Parses Markdown/NotebookLM files into graph nodes.
   - **Data Layer (The Memory):**
     - **File System:** Raw Markdown files for chapters and character sheets (Source of Truth for Text).
     - **SQLite (Planned):** Stores the persistent Knowledge Graph (Nodes & Edges).
     - **NetworkX (Planned):** In-memory graph for fast querying and analysis.

   ------

   

   #### **3. Core Workflows**

   

   **A. The Tournament Pipeline (Current State)**

   1. **Setup:** User selects a "Squad" of agents and provides a prompt/topic.
   2. **Context Injection:** The backend reads the "World Bible" (character sheets, lore) and injects relevant context into the system prompt.
   3. **Drafting:** Selected agents generate scene drafts in parallel.
   4. **Judging:** A designated "Judge" agent (e.g., GPT-4o) evaluates the drafts based on criteria (creativity, voice, etc.) and selects a winner.
   5. **Result:** The winner and full drafts are returned to the frontend editor.

   **B. The Knowledge Graph Loop (Detailed Specification)** This is the "Brain" that keeps the story consistent.

   1. **Ingestion (The Parser):**
      - **Goal:** Convert unstructured text (Markdown files) into structured graph nodes.
      - **Trigger:** Runs on startup or when a file is saved in `content/World Bible`.
      - **Mechanism:** An LLM-based extractor reads the text and identifies:
        - **Entities:** Characters, Locations, Objects.
        - **Relationships:** "Mickey *hates* The Agency", "The Key *opens* The Vault".
        - **Attributes:** "Mickey" -> `status: injured`.
      - **Storage:** Upserts into SQLite `nodes` and `edges` tables.
   2. **Querying (The Context Builder):**
      - **Goal:** Give drafting agents *exact* context, not the whole bible.
      - **Trigger:** When a Tournament starts.
      - **Logic:** The Orchestrator scans the user prompt for keywords (e.g., "Mickey", "Gunfight").
      - **Graph Traversal:** Queries the graph for mentioned nodes + immediate neighbors (Radius=1).
      - **Injection:** Formats relevant node data as a "Context Block" appended to the system prompt.
   3. **Updating (The State Tracker):**
      - **Goal:** Track narrative consequences.
      - **Trigger:** When a user "Locks" or "Finalizes" a scene.
      - **Mechanism:** A background agent ("The Archivist") reads the new scene, diffs it against the graph, and updates states (e.g., changes `Mickey.status` from `healthy` to `injured`).

   **C. NotebookLM Integration (The Bridge)**

   This module acts as the "Importer" for external research.

   1. **Input:** User exports NotebookLM notes (PDF/Doc converted to Markdown).
   2. **Watch Folder:** App watches `content/imports/notebooklm`.
   3. **Processing:**
      - **Normalization:** Cleans up headers and citations.
      - **Tagging:** Identifies `## Source` vs `## Key Insight`.
      - **Graph Ingestion:** Feeds insights directly into the Knowledge Graph (see section 3B.1).
   4. **UI:** Imported notes appear in the Sidebar under "Research," drag-and-drop ready.

   ------

   

   #### **4. Data Schema (Simplified)**

   

   - **Projects:** Configuration and metadata for a novel.
   - **Scenes:** Metadata for each chapter/scene (status, word count).
   - **Nodes:**
     - `id` (String, PK): e.g., "char_mickey"
     - `type` (Enum): 'character', 'location', 'theme', 'thread'
     - `data` (JSON): `{"emotional_state": "happy", "description": "..."}`
   - **Edges:**
     - `source` (FK -> nodes.id)
     - `target` (FK -> nodes.id)
     - `type` (Enum): 'KNOWS', 'LOCATED_IN', 'MENTIONS', 'DEPENDS_ON'
     - `properties` (JSON): `{"strength": 0.8}`

   ------

   

   #### **5. Roadmap Status**

   

   - **Phase 1: The Foundation (✅ Done)**
     - Tauri + Python setup.
     - Basic File System integration (Open/Save).
     - UI Shell (Sidebar, Editor).
   - **Phase 2: The Engine (✅ Done)**
     - Multi-LLM connection.
     - Tournament Orchestration.
     - Basic "Squad Selection" UI.
   - **Phase 3: The Soul (🚧 Next Up)**
     - **Graph Ingestor:** Implementing `graph_service.py` and `ingestor.py`.
     - **Context Engine:** Wiring the graph to the Tournament.
     - **NotebookLM Import:** Building the bridge.
   - **Phase 4: The Polish (Planned)**
     - Visualizing the story structure (D3.js).
     - Agent Customization UI.

