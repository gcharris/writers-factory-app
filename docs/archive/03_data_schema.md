# Database Schema (SQLite)

**Derived from:** Writers Platform Web (PostgreSQL models) adapted for Desktop.

## 1. Core Tables

### `projects`
* `id` (UUID, PK)
* `title` (String)
* `genre` (String)
* `graph_config` (JSON) - Settings for the graph engine.

### `scenes`
* `id` (UUID, PK)
* `project_id` (FK)
* `title` (String)
* `content` (Text) - The actual Markdown content.
* `sequence` (Integer) - Order in the book.
* `status` (Enum) - 'draft', 'analyzed', 'locked'.
* `word_count` (Integer)

### `nodes` (The Knowledge Graph Storage)
* `id` (String, PK) - e.g., "char_alice".
* `type` (Enum) - 'character', 'location', 'theme', 'thread'.
* `data` (JSON) - { "emotional_state": "happy", "description": "..." }.
* `embedding` (Blob) - Vector embedding for semantic search.

### `edges` (Relationships)
* `source` (FK -> nodes.id)
* `target` (FK -> nodes.id)
* `type` (Enum) - 'KNOWS', 'LOCATED_IN', 'MENTIONS', 'DEPENDS_ON'.
* `properties` (JSON) - { "strength": 0.8, "valence": -0.5 }.

## 2. Tournament Tables

### `scene_drafts`
* `id` (UUID, PK)
* `scene_id` (FK)
* `agent_name` (String) - e.g., "Gemini 3.0".
* `content` (Text)
* `scores` (JSON) - { "voice": 8.5, "pacing": 9.0 ... }
* `cost` (Float) - Calculated API cost.

### `analysis_results`
* `id` (UUID, PK)
* `scene_id` (FK)
* `winning_draft_id` (FK)
* `critique_summary` (Text)
* `consistency_report` (JSON) - Output from Consistency Agent.