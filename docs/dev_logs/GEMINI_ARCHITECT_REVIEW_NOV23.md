# Gemini Architect Review: The Foreman

**Date:** November 23, 2025
**Reviewer:** Gemini Architect (v2)
**Subject:** Phase 2A Implementation Review (The Foreman)

---

## 1. Executive Summary

**Verdict:** 🟢 **EXCELLENT PROGRESS**

The pivot from "Wizard Chatbot" to "Creative Partner" is the correct strategic move. The implementation of `foreman.py` is clean, robust, and well-structured. The `WorkOrder` concept is particularly strong as it gives the agent a "sense of purpose" beyond just reacting to the last message.

The "Creative Partner" insight—that we should *challenge* the user, not just collect answers—is what will differentiate this product from generic AI writing tools.

---

## 2. Decision Guidelines (Architectural Decisions)

### Decision 1: Multi-Notebook Orchestration
**Question:** Manual registration vs. Auto-detection?
**Decision:** **Hybrid / Auto-Bias.**

*   **Reasoning:** Manual registration is tedious and breaks flow. The Foreman should be smart enough to know that a question about "The Gatekeepers" belongs to the *World* notebook, while a question about "Sarcasm" belongs to the *Voice* notebook.
*   **Implementation:**
    *   Keep `register_notebook` for *assigning* roles (e.g., "This notebook is for World").
    *   When a query happens, the Foreman should internally decide which notebook to query.
    *   **Action Item:** Add a `router` step in the `chat` loop. Before calling Ollama for the response, ask: "Does this require external context? If so, which notebook?"

### Decision 2: KB Persistence
**Question:** Memory vs. Files vs. Graph vs. SQLite?
**Decision:** **SQLite (Immediate) + Graph (Async).**

*   **Reasoning:**
    *   *Memory* is too fragile. If the app crashes, we lose the "Creative Partner" context.
    *   *Files* are messy for granular facts.
    *   *Graph* is too rigid for "soft" facts like "User prefers dark themes".
*   **Implementation:**
    *   Use `sessions.db`. Add a table `foreman_kb` (key, value, type, source, timestamp).
    *   The `Foreman` class should write to this DB *immediately* on `save_decision`.
    *   **The Consolidator** (Phase 3) will later scan this table and promote "hard facts" (Character traits, World rules) into the `knowledge_graph.json`. This keeps the graph clean.

### Decision 3: Action System
**Question:** Robust enough?
**Decision:** **Add `suggest_ui_action`.**

*   **Reasoning:** The current actions (`query_notebook`, `write_template`) are backend-focused. We need actions that drive the frontend.
*   **Implementation:**
    *   Add `suggest_ui_action`: e.g., "Open the Protagonist file", "Show the Beat Sheet", "Switch to Director Mode".
    *   This allows the Foreman to control the IDE, making it feel like a true "Foreman".

### Decision 4: Next Focus
**Decision:** **Option D: UI Integration.**

*   **Reasoning:** A backend agent is invisible. We need to get this into the `ChatSidebar.svelte` immediately to test the "feel" of the conversation.
*   **Sequence:**
    1.  **UI Integration:** Wire `POST /foreman/chat` to the frontend.
    2.  **Persistence:** Hook up SQLite for KB.
    3.  **Smart Orchestration:** Make it auto-select notebooks.

---

## 3. Code Level Feedback (`foreman.py`)

1.  **Prompt Management:**
    *   *Current:* `ARCHITECT_SYSTEM_PROMPT` is a string constant in the file.
    *   *Recommendation:* Move prompts to `backend/prompts/foreman/architect.md`. This allows for easier iteration on the "personality" without touching code.

2.  **State Loading:**
    *   The `load_state` method exists but is manual.
    *   *Recommendation:* In `__init__`, if a `project_id` is passed, auto-load the state from SQLite.

3.  **Error Handling in Actions:**
    *   The `_parse_and_execute_actions` block is good, but if an action fails (e.g., NotebookLM times out), the user might not know.
    *   *Recommendation:* If an action fails, the Foreman should self-correct or inform the user in the *next* message (e.g., "I tried to check the notebook, but couldn't reach it. Here's what I think based on what I know...").

---

## 4. The "Metabolism" Connection

The briefing mentions Phase 3 (Metabolism) as a future step. I propose we link Foreman to Metabolism sooner.

*   **Concept:** The Foreman is the *mouth* of the Metabolism.
*   **Flow:**
    1.  Foreman learns a fact -> Writes to `foreman_kb` (SQLite).
    2.  Consolidator (Metabolism) wakes up -> Reads `foreman_kb` -> Updates `knowledge_graph.json`.
    3.  Foreman reads `knowledge_graph.json` for context in future chats.

This loop creates the "Living Brain".

---

*End of Review*
