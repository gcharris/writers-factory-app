# NotebookLM Integration Research

**Source:** `writers-platform` Repository (Legacy)
**Status in Legacy:** Phase 9 Completed (Core + Copilot Integration)
**Date of Original Implementation:** Jan 2025

## 1. Executive Summary

The integration allows writers to "plug in" their external NotebookLM research into the Writers Factory. The system treats NotebookLM as a read-only oracle for "ground truth" about characters, world-building, and themes.

**Core Concept:**
*   **Input:** User provides URLs for specific NotebookLM notebooks (e.g., "Character Research", "World Bible").
*   **Mechanism:** An **MCP (Model Context Protocol) Server** acts as the bridge between the Python backend and Google's NotebookLM.
*   **Output:** Agents and Copilots automatically query these notebooks to ground their suggestions in the user's established research.

## 2. Architecture

### A. The MCP Bridge
The system uses the Model Context Protocol (MCP) to standardize the connection.
*   **Server:** A Node.js based MCP server (`notebooklm-mcp`) running locally.
*   **Client:** A Python singleton service (`NotebookLMMCPClient`) in the FastAPI backend that manages the subprocess and sends JSON-RPC 2.0 requests.

### B. Data Model
The `projects` table was extended to store notebook associations:
```sql
ALTER TABLE projects
ADD COLUMN notebooklm_notebooks JSONB DEFAULT '{}', -- {"character": "url", "world": "url"}
ADD COLUMN notebooklm_config JSONB DEFAULT '{"enabled": false}';
```

### C. Knowledge Graph Integration
Entities extracted from NotebookLM are treated specially in the Knowledge Graph:
*   **Source Type:** `notebooklm` (distinct from `user_created` or `extracted`).
*   **Properties:** `notebooklm_sources` (list of citations/sources returned by the notebook).
*   **Visualization:** Often rendered in a distinct color (e.g., Purple) to show "Research-backed" nodes.

## 3. User Workflow

1.  **Pre-Platform Setup:**
    *   Writer creates notebooks in NotebookLM (e.g., "Project Orion - Characters").
    *   Writer uploads PDFs, YouTube videos, and notes to NotebookLM.

2.  **Configuration:**
    *   In the App, user pastes the URL for their "Character Notebook", "World Notebook", etc.

3.  **Active Writing (Copilot):**
    *   User types: *"Mickey entered the [Location]..."*
    *   **Context Manager:** Detects [Location] is an entity.
    *   **Router:** Checks if [Location] exists in the Graph. If not, it checks if the "World Notebook" has info.
    *   **Query:** Backend sends `query_notebook("Describe [Location] based on research")`.
    *   **Suggestion:** Copilot suggests: *"Mickey entered the [Location], noticing the [Detail from Research]..."*

4.  **Extraction (Graph Building):**
    *   User can explicitly click "Extract Profile" for a character.
    *   System scrapes the notebook for Backstory, Voice, and Relationships.
    *   System inserts these as Nodes in the Graph.

## 4. Implementation Details (Legacy Code)

### MCP Configuration (`backend/mcp_config.json`)
```json
{
  "mcpServers": {
    "notebooklm": {
      "command": "node",
      "args": ["external/notebooklm-mcp/index.js"],
      "env": {
        "NOTEBOOKLM_API_KEY": "${NOTEBOOKLM_API_KEY}"
      }
    }
  }
}
```

### Python Client (`backend/app/services/notebooklm/mcp_client.py`)
A singleton class was used to manage the connection to avoid spawning multiple Node processes.
*   `list_notebooks()`: Fetches available notebooks.
*   `query_notebook(id, query)`: Sends a natural language question.
*   `extract_character_profile(id, name)`: Specialized prompt to structured JSON.

## 5. Migration Strategy for `writers-factory-app`

To bring this feature to the current app, we need to:

1.  **Install MCP Server:** Clone `notebooklm-mcp` into `backend/external/`.
2.  **Port the Client:** Copy/Adapt `NotebookLMMCPClient` to `backend/services/`.
3.  **Update Data Model:** Ensure our SQLite schema supports storing these config values (likely in the `Project` model or a dedicated config file).
4.  **Frontend UI:** Add the "Connect Notebooks" panel to the Agent/Project settings.

---
*Research compiled from `writers-platform/KNOWLEDGE_GRAPH_PHASE_9_NOTEBOOKLM_MCP.md`.*

