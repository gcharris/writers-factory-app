# Writers Factory API Reference

> Complete reference for all backend API endpoints.

**Base URL:** `http://localhost:8000`

---

## Table of Contents

- [System](#system)
- [The Foreman](#the-foreman)
- [File Management](#file-management)
- [Knowledge Graph](#knowledge-graph)
- [Session Management](#session-management)
- [Consolidator](#consolidator)
- [Health Dashboard](#health-dashboard)
- [NotebookLM Integration](#notebooklm-integration)
- [Story Bible System](#story-bible-system)
- [Project & Tournament](#project--tournament)

---

## System

### `GET /agents`
List all configured AI agents.

**Response:**
```json
{
  "agents": [
    {"id": "drafter-1", "enabled": true, "use_cases": ["tournament"]},
    {"id": "critic-1", "enabled": true, "use_cases": ["evaluation"]}
  ]
}
```

### `GET /manager/status`
Health check for the Manager agent.

**Response:**
```json
{"status": "online"}
```

---

## The Foreman

The Foreman is the intelligent creative writing partner powered by Ollama (Llama 3.2). These endpoints manage the Foreman's lifecycle and conversation.

> **Full Documentation:** See [BACKEND_SERVICES.md](BACKEND_SERVICES.md#1-the-foreman-intelligent-creative-partner) and [specs/STORY_BIBLE_ARCHITECT.md](specs/STORY_BIBLE_ARCHITECT.md)

### `POST /foreman/start`
Initialize a new project with the Foreman.

**Request Body:**
```json
{
  "project_title": "Big Brain",
  "protagonist_name": "Mickey Bardot"
}
```

**Response:**
```json
{
  "status": "started",
  "work_order": {
    "project_title": "Big Brain",
    "protagonist_name": "Mickey Bardot",
    "mode": "architect",
    "templates": [
      {"name": "Protagonist", "status": "not_started", "required_fields": ["fatal_flaw", "the_lie", "arc_start", "arc_resolution"]},
      {"name": "Beat Sheet", "status": "not_started", "required_fields": ["beat_1", "beat_2", "...", "beat_15", "midpoint_type"]},
      {"name": "Theme", "status": "not_started", "required_fields": ["central_theme", "theme_statement"]},
      {"name": "World Rules", "status": "not_started", "required_fields": ["fundamental_rules"]}
    ],
    "notebooks": {},
    "completion_percentage": 0.0,
    "is_complete": false,
    "created_at": "2025-11-23T08:17:19.799329+00:00"
  },
  "message": "Project 'Big Brain' initialized. Ready to build Story Bible."
}
```

### `POST /foreman/chat`
Send a message to the Foreman and get a response.

The Foreman will:
- Consider the work order status
- Apply craft knowledge (Fatal Flaw, The Lie, 15-beat structure)
- Query NotebookLM notebooks if needed
- Challenge weak structural choices
- Track decisions in Knowledge Base

**Request Body:**
```json
{
  "message": "Mickey's fatal flaw is his intellectual arrogance - he believes he can solve any problem with pure logic."
}
```

**Response:**
```json
{
  "response": "That's a strong Fatal Flaw! Intellectual arrogance creates rich story potential...",
  "actions": [
    {"action": "save_decision", "category": "character", "key": "mickey_fatal_flaw", "result": "saved"}
  ],
  "work_order": {
    "completion_percentage": 12.5,
    "templates": [...]
  },
  "kb_entries_pending": 1
}
```

### `POST /foreman/notebook`
Register a NotebookLM notebook for the Foreman to use.

**Request Body:**
```json
{
  "notebook_id": "abc123xyz",
  "role": "world"
}
```

**Role Options:**
- `"world"` - World-building, setting, factions
- `"voice"` - Character voice, dialogue style
- `"craft"` - Narrative techniques, reference works

**Response:**
```json
{
  "status": "registered",
  "notebook_id": "abc123xyz",
  "role": "world"
}
```

### `GET /foreman/status`
Get current Foreman state without making a chat request.

**Response:**
```json
{
  "active": true,
  "mode": "architect",
  "work_order": {...},
  "conversation_length": 4,
  "kb_entries_pending": 2
}
```

### `POST /foreman/flush-kb`
Flush pending Knowledge Base entries and return them for persistence.

**Response:**
```json
{
  "flushed_count": 3,
  "entries": [
    {"category": "character", "key": "mickey_fatal_flaw", "value": "...", "timestamp": "..."},
    {"category": "constraint", "key": "no_personal_trauma", "value": "...", "timestamp": "..."}
  ]
}
```

### `POST /foreman/reset`
Reset the Foreman to start a new project.

**Response:**
```json
{
  "status": "reset",
  "message": "Foreman reset. Ready for new project."
}
```

---

## File Management

### `GET /files/{filepath}`
Read a file by path.

**Parameters:**
- `filepath` (path): Full path to the file

**Response:**
```json
{"content": "File contents here..."}
```

### `PUT /files/{filepath}`
Save content to a file.

**Request Body:**
```json
{"content": "New file contents"}
```

**Response:**
```json
{"status": "success", "message": "File saved"}
```

---

## Knowledge Graph

### `POST /graph/ingest`
Trigger full graph ingestion from content folder.

Uses **LOCAL Llama 3.2 via Ollama** (zero cost).

**Parameters:**
- `max_files` (query, optional): Limit files to process

**Response:**
```json
{
  "status": "Ingestion complete",
  "engine": "ollama/llama3.2",
  "nodes_extracted": 42,
  "edges_extracted": 18,
  "metadata": {}
}
```

### `POST /graph/ingest/test`
Quick test: Ingest just 2 files to verify the pipeline.

**Response:**
```json
{
  "status": "Test ingestion complete",
  "nodes_extracted": 5,
  "edges_extracted": 2,
  "files_processed": 2
}
```

### `GET /graph/view`
Returns the current state of the knowledge graph.

**Response:**
```json
{
  "status": "ok",
  "nodes": [{"id": 1, "name": "Mickey", "type": "character"}],
  "edges": [{"source": 1, "target": 2, "relation": "KNOWS"}],
  "metadata": {"last_update": "2025-01-15T..."}
}
```

### `GET /graph/context/{scene_id}`
Get ACE scaffold data for a scene.

**Parameters:**
- `scene_id` (path): Integer scene ID

**Response:**
```json
{"scaffold": "# Scene Scaffold\n..."}
```

---

## Session Management

### `POST /session/new`
Create a new chat session.

**Request Body (optional):**
```json
{"scene_id": "1.5.2"}
```

**Response:**
```json
{"session_id": "uuid-here", "scene_id": "1.5.2"}
```

### `POST /session/{session_id}/message`
Log a message to a session.

**Parameters:**
- `session_id` (path): Session UUID

**Request Body:**
```json
{
  "role": "user",
  "content": "Help me revise this scene",
  "scene_id": "1.5.2"
}
```

**Response:**
```json
{"status": "logged", "event_id": 42, "token_count": 15}
```

### `GET /session/{session_id}/history`
Retrieve chat history for a session.

**Parameters:**
- `session_id` (path): Session UUID
- `limit` (query): Max events to return (default: 50)

**Response:**
```json
{
  "session_id": "uuid",
  "events": [
    {"id": 1, "role": "user", "content": "...", "timestamp": "..."}
  ]
}
```

### `GET /session/{session_id}/stats`
Get session statistics for compaction decisions.

**Response:**
```json
{
  "total_events": 42,
  "total_tokens": 5000,
  "uncommitted_count": 3
}
```

### `GET /sessions/active`
List recently active sessions.

**Parameters:**
- `limit` (query): Max sessions (default: 20)

**Response:**
```json
{"sessions": [{"session_id": "...", "last_activity": "..."}]}
```

### `GET /session/{session_id}/uncommitted`
Get events not yet digested by the Consolidator.

### `POST /session/commit`
Mark events as digested by the Consolidator.

**Request Body:**
```json
[1, 2, 3, 4]  // Event IDs
```

---

## Consolidator

### `POST /graph/consolidate/{session_id}`
Digest a specific session into the knowledge graph.

Extracts entities from chat events and merges them using **local Llama 3.2**.

**Parameters:**
- `session_id` (path): Session UUID
- `dry_run` (query): If true, extract but don't save

**Response:**
```json
{
  "session_id": "uuid",
  "entities_extracted": 5,
  "merged_count": 3,
  "conflicts": []
}
```

### `POST /graph/consolidate`
Digest ALL uncommitted events across all sessions.

### `GET /graph/conflicts`
View detected conflicts from consolidation.

**Response:**
```json
{
  "conflicts": [
    {"entity": "Mickey", "field": "age", "old": "35", "new": "40"}
  ],
  "count": 1
}
```

---

## Health Dashboard

### `GET /health/status`
Combined health endpoint for the dashboard.

Returns graph stats, conflicts, and uncommitted events in one call.

**Response:**
```json
{
  "graph_stats": {
    "node_count": 42,
    "edge_count": 18,
    "recent_nodes": [...]
  },
  "conflicts": [...],
  "conflict_count": 0,
  "uncommitted_count": 5,
  "timestamp": "2025-01-15T..."
}
```

---

## NotebookLM Integration

### `GET /notebooklm/status`
Check if NotebookLM MCP server is available.

**Response:**
```json
{"status": "ready"}  // or "offline"
```

### `GET /notebooklm/auth`
Trigger the authentication flow (opens browser for Google login).

**Response:**
```json
{"status": "Auth flow triggered. Check for browser window."}
```

### `GET /notebooklm/notebooks`
List configured notebooks.

**Response:**
```json
{"configured": [{"id": "abc123", "title": "My Novel Research"}]}
```

### `POST /notebooklm/query`
Query a notebook with a question.

**Request Body:**
```json
{
  "query": "What is Mickey's fatal flaw?",
  "notebook_id": "abc123"
}
```

**Response:**
```json
{
  "answer": "Mickey's fatal flaw is...",
  "sources": [{"title": "Character Notes", "page": 3}],
  "notebook_id": "abc123",
  "query": "What is Mickey's fatal flaw?"
}
```

### `POST /notebooklm/character-profile`
Extract a character profile from notebook.

**Request Body:**
```json
{
  "character_name": "Mickey Bardot",
  "notebook_id": "abc123"
}
```

### `POST /notebooklm/world-building`
Extract world-building information.

**Request Body:**
```json
{
  "aspect": "quantum consciousness technology",
  "notebook_id": "abc123"
}
```

### `POST /notebooklm/context`
Get context for a specific entity.

**Request Body:**
```json
{
  "entity_name": "Noni",
  "entity_type": "character",
  "notebook_id": "abc123"
}
```

---

## Story Bible System

> **Phase 2 Implementation** - Enforces "Structure Before Freedom" methodology.

### `GET /story-bible/status`
Run Level 2 Health Checks on Story Bible.

Returns completion status, parsed data, and blocking issues.

**Response:**
```json
{
  "phase2_complete": false,
  "completion_score": 71.4,
  "checks": [
    {"name": "Protagonist file exists", "passed": true, "status": "✓"},
    {"name": "Protagonist has Fatal Flaw defined", "passed": false, "status": "✗"}
  ],
  "protagonist": {
    "name": "Mickey Bardot",
    "fatal_flaw": "",
    "the_lie": "",
    "contradiction_score": 0.3
  },
  "beat_sheet": {
    "title": "Big Brain",
    "completion": 60.0,
    "current_beat": 1
  },
  "blocking_issues": ["Protagonist has Fatal Flaw defined"]
}
```

### `POST /story-bible/scaffold`
Create Story Bible directory structure and template files.

**Request Body:**
```json
{
  "project_title": "Big Brain",
  "protagonist_name": "Mickey Bardot",
  "pre_filled": {
    "protagonist": {"fatal_flaw": "Addiction to escape"},
    "beat_sheet": {"beat_1": "Opening in Vegas casino..."}
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Story Bible scaffolding created for 'Big Brain'",
  "created_files": [
    "content/Characters/Mickey_Bardot.md",
    "content/Story Bible/Structure/Beat_Sheet.md"
  ]
}
```

### `GET /story-bible/protagonist`
Parse and return structured protagonist data.

**Response:**
```json
{
  "status": "ok",
  "protagonist": {
    "name": "Mickey Bardot",
    "true_character": "A con man who secretly craves connection",
    "characterization": "Charming, quick-witted, cynical",
    "fatal_flaw": "Pathological aversion to genuine connection",
    "the_lie": "Believes intimacy is a weakness to exploit",
    "arc": {
      "start": "Creature of the immediate, superficial",
      "midpoint": "Forced radical honesty during transfer",
      "resolution": "Hybrid being who chooses to warn humanity"
    },
    "relationships": [
      {"character": "Noni", "function": "Harmonic anchor, co-conspirator"}
    ],
    "contradiction_score": 0.8,
    "is_valid": true
  }
}
```

### `GET /story-bible/beat-sheet`
Parse and return structured beat sheet data.

**Response:**
```json
{
  "status": "ok",
  "beat_sheet": {
    "title": "Big Brain",
    "current_beat": 5,
    "midpoint_type": "false_victory",
    "theme_stated": "Do you keep your mind, or does someone else run it?",
    "completion_percentage": 100.0,
    "is_valid": true,
    "beats": [
      {"number": 1, "name": "Opening Image", "percentage": "1%", "description": "...", "is_complete": true}
    ]
  }
}
```

### `POST /story-bible/ensure-structure`
Create Story Bible directory structure if it doesn't exist.

**Response:**
```json
{
  "status": "success",
  "directories": {
    "story_bible": "content/Story Bible",
    "characters": "content/Characters",
    "story_structure": "content/Story Bible/Structure"
  },
  "created": ["themes", "research"]
}
```

### `GET /story-bible/can-execute`
Simple boolean check: Can we proceed to Phase 3 (Execution)?

**Response:**
```json
{
  "can_execute": true,
  "completion_score": 85.7,
  "blocking_issues": []
}
```

### `POST /story-bible/smart-scaffold`
**AI-powered Story Bible generation from NotebookLM.**

This is the "AI Scaffolding Agent" that:
1. Queries NotebookLM for protagonist data (Fatal Flaw, The Lie, Arc)
2. Queries NotebookLM for 15-beat structure
3. Queries NotebookLM for themes and world rules
4. Synthesizes responses into Story Bible templates
5. Validates completeness

**Prerequisites:**
- NotebookLM authenticated (`GET /notebooklm/auth`)
- Notebook with uploaded research materials

**Request Body:**
```json
{
  "notebook_id": "abc123",
  "project_title": "Big Brain",
  "protagonist_name": "Mickey Bardot"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Story Bible generated from NotebookLM",
  "workflow": {
    "workflow": "SmartScaffoldWorkflow",
    "success": true,
    "duration_ms": 45000,
    "steps": [
      {"name": "Query Protagonist Data", "status": "completed", "duration_ms": 8000},
      {"name": "Query Beat Sheet", "status": "completed", "duration_ms": 10000},
      {"name": "Synthesize Story Bible", "status": "completed", "duration_ms": 5000}
    ]
  }
}
```

---

## Project & Tournament

### `POST /project/init`
Initialize a new student project with the Setup Wizard.

**Request Body:**
```json
{
  "project_name": "my_novel",
  "voice_sample": "Sample text in the writer's voice...",
  "protagonist_name": "Mickey Bardot"
}
```

### `POST /tournament/run`
Run a scene drafting tournament.

**Request Body:**
```json
{"scaffold": "# ACE Scaffold\n..."}
```

**Response:**
```json
{
  "drafts": [
    {"agent_id": "drafter-1", "text": "...", "score": 8.5},
    {"agent_id": "drafter-2", "text": "...", "score": 7.2}
  ],
  "winner": "drafter-1"
}
```

### `POST /scene/save`
Save the winning text and trigger graph ingestion.

**Request Body:**
```json
{
  "scene_id": 1,
  "winning_text": "# Chapter 1\n\nMickey stood at the edge..."
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error description here"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found
- `500` - Internal Server Error
- `501` - Not Implemented (missing dependency like spaCy)

---

*Generated for Writers Factory v0.1*
