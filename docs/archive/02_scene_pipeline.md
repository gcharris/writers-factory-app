# Writers Factory Desktop App: Scene Generation Pipeline & Knowledge Graph Integration

## Executive Summary
This document details the **Scene Generation & Agent Orchestration** components. It integrates a multi-agent tournament workflow with a dynamic, graph-centric architecture. The knowledge graph serves as the "story brain," ensuring every draft is informed by the evolving narrative state.

---

## 1. Overview: From Manual Process to Automated Pipeline
The system replaces manual context tracking with automated graph queries.
* **Story Truth = Knowledge Graph:** Files are serialization; the graph is the operational reality.
* **Context:** Agents query the graph to build prompts automatically.
* **Updates:** Every draft updates the graph with new entities and relationships.
* **Transactional Memory:** Every brainstorming session and decision is saved as an artifact.

---

## 2. Architecture: Graph-Centric Scene Generation

### 2.1 Core Components
* **Knowledge Graph Engine (`backend/graph/`):** NetworkX/SQLite runtime.
* **Agent Orchestration (`backend/agents/`):** Registry, Orchestrator, Prompt Builder.
* **Ideation Engine (`backend/agents/ideation.py`):** Handles "Chat-to-Graph" sessions.
* **MCP Integration (`backend/mcp/`):** NotebookLM client and Context Logging.

---

## 3. The Automated Scene Generation Pipeline

### Step 1: Scene Scaffold Generation
**Input:** Scene ID and brief outline.
**Process:** Query graph for characters, emotional states, location, and active threads.
**Output:** A structured `Scaffold` object containing all context needed for drafting.

### Step 1.5: Active Ideation (The Brainstorm Loop)
**Trigger:** User wants to explore options (e.g., "What if he gets hit in the throat?").
**Process:**
1.  **Chat:** User converses with Gemini/Ollama.
2.  **Summarize:** Agent extracts new facts/decisions from the chat.
3.  **Log:** Save full transcript to `workspace/my-novel/development_docs/`.
4.  **Ingest:** Update Graph Nodes immediately (e.g., `Mickey` -> `has_condition` -> `Mute`).

### Step 2: 5× Variation Tournament
**Process:**
1.  Select 5 agents based on config (e.g., 1x Gemini, 2x Claude, 1x GPT, 1x Llama).
2.  Generate 5 distinct drafts in parallel using the Scaffold AND the Ideation results.
3.  Track cost per draft.

### Step 3: Strategic Analysis & Scoring
**Process:** A "Critic Agent" evaluates drafts on:
* **Voice Authenticity (0-10)**
* **Narrative Impact (0-10)**
* **Philosophy Integration (0-10)**
* **Character Alignment (0-10)**
* **Graph Consistency (0-10)**

### Step 4: Selection or Hybridization
**User Action:** Select a winner, or create a hybrid (e.g., "Structure from V1, Dialogue from V3").

### Step 5: Enhancement & Polish
**Process:** Surgical polish pass to tighten compression and sharpen metaphors.

### Step 6: Quality Gate (The "Lock")
**Process:** Automated checks before saving.
* Observer Test (Pass/Fail)
* Voice Score >= 8.5
* Overall Quality >= 9.0

### Step 7: Graph Update & Archive
**Process:**
1.  Extract entities/facts from the final text.
2.  Update Graph Nodes (e.g., "Alice knows Secret X").
3.  Mark threads as "Advanced" or "Resolved".
4.  **Artifact Archival:** Move all `development_docs` related to this scene into the permanent archive for NotebookLM ingestion.

---

## 4. Knowledge Graph Integration Details

### 4.1 Graph Schema
**Nodes:** `Character`, `Scene`, `Beat`, `Thread`, `Research`, `Location`.
**Edges:** `DEPENDS_ON`, `MENTIONS`, `ADVANCES`, `RESOLVES`, `CONTRADICTS`, `INFORMED_BY`.

### 4.2 Key Queries
* `get_character_state_at(character, scene_id)`
* `get_active_threads(scene_id)`
* `score_consistency(graph, draft)`

---

## 5. User Interface Integration
* **Scene Panel:** Shows Scaffold status and Active Threads.
* **Tournament View:** Side-by-side comparison of drafts with scores.
* **Graph Sidebar:** Live context showing character states for the current scene.
* **Ideation Chat:** A dedicated chat window that persists decisions to the Graph.

---

## 6. Implementation Roadmap
*(See `docs/03_roadmap.md` for the project timeline)*

---

## 7. Technical Specifications

### 7.1 Agent Registry Schema
**File:** `agents.yaml`

```yaml
version: "1.0"

agents:
  - id: "ollama-llama-3.2"
    name: "Ollama Llama 3.2"
    provider: "ollama"
    endpoint: "http://localhost:11434"
    model: "llama3.2"
    cost_per_1k_tokens: 0.0
    latency: "fast"
    quality_rating: 7.5
    use_cases: ["brainstorming", "quick_drafts", "character_checks"]
    enabled: true
    
  - id: "claude-sonnet-3-5"
    name: "Claude Sonnet 3.5"
    provider: "anthropic"
    api_key_env: "ANTHROPIC_API_KEY"
    model: "claude-3-5-sonnet-20240620"
    cost_per_1k_tokens: 0.003
    latency: "medium"
    quality_rating: 9.5
    use_cases: ["tournament", "enhancement", "critique"]
    enabled: true
    max_monthly_spend: 50.00  # USD

  - id: "gemini-pro-1-5"
    name: "Gemini 1.5 Pro"
    provider: "google"
    api_key_env: "GEMINI_API_KEY"
    model: "gemini-1.5-pro"
    cost_per_1k_tokens: 0.00125
    latency: "medium"
    quality_rating: 9.2
    use_cases: ["tournament", "reasoning"]
    enabled: true
...

### 7.2 Graph Database Schema (SQLite)
* **Nodes Table:** `id`, `type`, `data` (JSON), `created_at`.
* **Edges Table:** `from_node`, `to_node`, `type`, `properties` (JSON).
* **SceneDrafts Table:** `scene_id`, `version`, `agent_id`, `content`, `scores`, `cost`.
* **SceneMetadata Table:** `scene_id`, `tournament_winner`, `final_scores`, `locked_at`.

---

## 8. Cost Management
* **Tracker:** logs tokens per tournament.
* **Budget Controls:** auto-switches to free agents if monthly budget exceeded.

## 9. Success Metrics
* **Quality:** Average scene score >= 8.5.
* **Efficiency:** Time per scene < 10 mins.
* **Graph:** Context accuracy > 90%.
