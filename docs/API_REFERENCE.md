# Writers Factory API Reference

> Complete reference for all backend API endpoints.

**Base URL:** `http://localhost:8000`
**Total Endpoints:** 168
**Last Updated:** December 5, 2025

---

## Table of Contents

- [System & Manager](#system--manager)
- [File Management](#file-management)
- [Knowledge Graph](#knowledge-graph)
  - [Ingestion & Export](#ingestion--export)
  - [Semantic Search & Embeddings](#semantic-search--embeddings)
  - [Narrative Extraction](#narrative-extraction)
  - [Node & Relationship Management](#node--relationship-management)
  - [Analysis (GraphRAG)](#analysis-graphrag)
- [Verification Service](#verification-service)
- [Session Management](#session-management)
- [Consolidator](#consolidator)
- [Health Dashboard](#health-dashboard)
- [NotebookLM Integration](#notebooklm-integration)
- [Story Bible System](#story-bible-system)
- [The Foreman](#the-foreman)
- [Voice Calibration](#voice-calibration)
- [Director Mode](#director-mode)
  - [Scaffold Generation](#scaffold-generation)
  - [Scene Writing](#scene-writing)
  - [Scene Analysis](#scene-analysis)
  - [Scene Enhancement](#scene-enhancement)
- [Settings & Configuration](#settings--configuration)
- [API Key Management](#api-key-management)
- [Model Orchestrator](#model-orchestrator)
- [Tournament System](#tournament-system)
- [Squad System](#squad-system)
- [Usage Tracking](#usage-tracking)
- [Key Provisioning](#key-provisioning)
- [System & Hardware](#system--hardware)
- [Workspace Management](#workspace-management)
- [Manuscript & Knowledge Query](#manuscript--knowledge-query)

---

## System & Manager

### `GET /agents`
List all configured AI agents from `agents.yaml`.

### `GET /manager/status`
Health check for the Manager agent.

---

## File Management

### `GET /files/{filepath}`
Read a file by path.

### `PUT /files/{filepath}`
Save content to a file.

---

## Knowledge Graph

### Ingestion & Export

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest` | POST | Legacy ingestion endpoint |
| `/graph/ingest` | POST | Full graph ingestion from content folder |
| `/graph/ingest/test` | POST | Quick test: Ingest 2 files only |
| `/graph/view` | GET | Get current graph state (nodes, edges) |
| `/graph/stats` | GET | Get graph statistics |
| `/graph/export` | GET | Export full knowledge graph |

### Semantic Search & Embeddings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/semantic-search` | POST | Semantic search across graph nodes |
| `/graph/ego-network/{entity_name}` | GET | Get k-hop subgraph around entity |
| `/graph/reindex-embeddings` | POST | Regenerate embeddings for all nodes |
| `/graph/embedding-status` | GET | Get embedding index status |
| `/graph/knowledge-query` | POST | Query with full RAG pipeline |

### Narrative Extraction

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/extract-narrative` | POST | Extract narrative elements from text |
| `/graph/edge-types` | GET | Get available narrative edge types (17 types) |
| `/graph/extract-from-file` | POST | Extract narrative from a file |

**Narrative Edge Types:**
`MOTIVATES`, `HINDERS`, `FORESHADOWS`, `CALLBACKS`, `CHALLENGES`, `SUPPORTS`, `REVEALS`, `CONCEALS`, `TRANSFORMS`, `PARALLELS`, `CONTRASTS`, `ESCALATES`, `RESOLVES`, `COMPLICATES`, `ENABLES`, `PREVENTS`, `SYMBOLIZES`

### Node & Relationship Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/nodes/{node_id}` | GET | Get single node details |
| `/graph/nodes/{node_id}` | PUT | Update node properties |
| `/graph/relationships` | POST | Create a new relationship |
| `/graph/relationships/{edge_id}` | PUT | Update a relationship |
| `/graph/relationships/{edge_id}` | DELETE | Delete a relationship |

### Analysis (GraphRAG)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/analysis/communities` | GET | Detect character communities (Louvain) |
| `/graph/analysis/bridges` | GET | Find bridge characters |
| `/graph/analysis/tension` | GET | Calculate narrative tension |
| `/graph/analysis/pacing` | GET | Analyze narrative pacing |
| `/graph/analysis/summary` | GET | Get narrative structure summary |

### Settings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings/graph` | GET | Get graph settings |
| `/settings/graph` | PUT | Update graph settings |

---

## Verification Service

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verification/run` | POST | Run verification checks on content |
| `/verification/notifications` | GET | Get pending verification notifications |
| `/verification/run-all` | POST | Run all verification tiers |

**Verification Tiers:**
- **FAST**: Dead character check, anti-pattern scan, POV consistency
- **MEDIUM**: Flaw challenge, beat alignment, timeline coherence
- **SLOW**: Full voice authenticity, semantic consistency

---

## Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/session/new` | POST | Create a new chat session |
| `/session/{session_id}/message` | POST | Log a message to session |
| `/session/{session_id}/history` | GET | Get session chat history |
| `/session/{session_id}/stats` | GET | Get session statistics |
| `/sessions/active` | GET | List active sessions |
| `/session/{session_id}/rename` | POST | Rename a session |
| `/session/{session_id}/uncommitted` | GET | Get uncommitted events for Consolidator |
| `/session/commit` | POST | Mark events as digested |

---

## Consolidator

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/consolidate/{session_id}` | POST | Digest session into knowledge graph |
| `/graph/consolidate` | POST | Digest all uncommitted events |
| `/graph/conflicts` | GET | View detected conflicts |

---

## Health Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health/status` | GET | Combined health endpoint |
| `/health/check` | POST | Run health checks on manuscript |
| `/health/report/{report_id}` | GET | Retrieve stored health report |
| `/health/export` | POST | Export health report (markdown/JSON) |
| `/health/trends/{metric}` | GET | Get historical trend data |
| `/health/reports` | GET | List all health reports |
| `/health/export/{report_id}` | GET | Export specific report |
| `/health/theme/override` | POST | Manually override theme score |
| `/health/theme/overrides` | GET | Get all theme overrides |

**7 Health Checks:**
1. Timeline Consistency
2. Theme Resonance
3. Fatal Flaw Challenge
4. Cast Function
5. Pacing Analysis
6. Beat Alignment
7. Symbolic Layering

---

## NotebookLM Integration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/notebooklm/status` | GET | Check MCP server availability |
| `/notebooklm/auth` | GET | Trigger authentication flow |
| `/notebooklm/notebooks` | GET | List configured notebooks |
| `/notebooklm/query` | POST | Query a notebook |
| `/notebooklm/character-profile` | POST | Extract character profile |
| `/notebooklm/world-building` | POST | Extract world-building info |
| `/notebooklm/context` | POST | Get context for entity |

---

## Story Bible System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/story-bible/status` | GET | Get Story Bible validation status |
| `/story-bible/scaffold` | POST | Create Story Bible scaffolding |
| `/story-bible/protagonist` | GET | Get parsed protagonist data |
| `/story-bible/beat-sheet` | GET | Get parsed beat sheet data |
| `/story-bible/ensure-structure` | POST | Ensure directory structure exists |
| `/story-bible/can-execute` | GET | Check if ready for Phase 3 |
| `/story-bible/smart-scaffold` | POST | AI-powered generation from NotebookLM |

---

## The Foreman

The intelligent creative writing partner powered by Ollama.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/foreman/start` | POST | Initialize new project |
| `/foreman/chat` | POST | Chat with the Foreman |
| `/foreman/notebook` | POST | Register NotebookLM notebook |
| `/foreman/status` | GET | Get Foreman status |
| `/foreman/flush-kb` | POST | Flush KB entries |
| `/foreman/reset` | POST | Reset the Foreman |
| `/foreman/mode` | GET | Get current Foreman mode |
| `/foreman/mode/voice-calibration` | POST | Advance to Voice Calibration |
| `/foreman/mode/director` | POST | Advance to Director mode |
| `/foreman/debug/force-mode` | POST | [DEBUG] Force change mode |
| `/foreman/debug/modes` | GET | [DEBUG] List all modes |
| `/foreman/stage` | GET | Get current writing stage |
| `/foreman/stage` | POST | Manually change stage |
| `/foreman/stage` | DELETE | Reset stage to auto-detection |

**Foreman Modes:** `ARCHITECT`, `VOICE_CALIBRATION`, `DIRECTOR`, `EDITOR`

---

## Voice Calibration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/voice-calibration/agents` | GET | Get available tournament agents |
| `/voice-calibration/tournament/start` | POST | Start voice tournament |
| `/voice-calibration/tournament/{id}/status` | GET | Get tournament status |
| `/voice-calibration/tournament/{id}/variants` | GET | Get tournament variants |
| `/voice-calibration/tournament/{id}/select` | POST | Select winning variant |
| `/voice-calibration/generate-bundle/{project_id}` | POST | Generate Voice Bundle |
| `/voice-calibration/{project_id}` | GET | Get voice calibration for project |

**Tournament Strategies:** `ACTION_EMPHASIS`, `CHARACTER_DEPTH`, `DIALOGUE_FOCUS`, `BRAINSTORMING`, `BALANCED`

---

## Director Mode

### Scaffold Generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/director/scaffold/draft-summary` | POST | Generate draft summary (Stage 1) |
| `/director/scaffold/enrich` | POST | Fetch enrichment from NotebookLM |
| `/director/scaffold/generate` | POST | Generate full scaffold (Stage 2) |

### Scene Writing

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/director/scene/structure-variants` | POST | Generate 5 structure variants |
| `/director/scene/generate-variants` | POST | Run multi-model tournament (15 variants) |
| `/director/scene/create-hybrid` | POST | Create hybrid from multiple variants |
| `/director/scene/quick-generate` | POST | Quick single-model generation |

### Scene Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/director/scene/analyze` | POST | Full 5-category analysis (100-point rubric) |
| `/director/scene/compare` | POST | Compare multiple scene variants |
| `/director/scene/detect-patterns` | POST | Detect anti-patterns only |
| `/director/scene/analyze-metaphors` | POST | Analyze metaphor usage only |

**100-Point Rubric:**
| Category | Points |
|----------|--------|
| Voice Authenticity | 30 |
| Character Consistency | 20 |
| Metaphor Discipline | 20 |
| Anti-Pattern Compliance | 15 |
| Phase Appropriateness | 15 |

### Scene Enhancement

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/director/scene/enhance` | POST | Auto-select enhancement mode |
| `/director/scene/action-prompt` | POST | Generate surgical fixes |
| `/director/scene/apply-fixes` | POST | Apply fixes from action prompt |
| `/director/scene/six-pass` | POST | Run 6-pass enhancement |

**Enhancement Modes:**
- **Action Prompt** (85+ score): Surgical line-by-line fixes
- **6-Pass Enhancement** (70-84): Full polish pipeline

---

## Settings & Configuration

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings/{key}` | GET | Get a setting value |
| `/settings` | POST | Set a setting value |
| `/settings/{key}` | DELETE | Reset setting to default |
| `/settings/category/{category}` | GET | Get all settings in category |
| `/settings/category/{category}` | PUT | Update settings in category |
| `/settings/project/{project_id}/overrides` | GET | Get project overrides |
| `/settings/export` | GET | Export settings as YAML |
| `/settings/import` | POST | Import settings |
| `/settings/defaults` | GET | Get all default values |

**Categories:** `foreman`, `scoring`, `voice`, `enhancement`, `health_checks`, `tournament`, `squad`, `graph`

---

## API Key Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api-keys/test` | POST | Test an API key |
| `/api-keys/status` | GET | Get status of all API keys |

**Supported Providers:** `google`/`gemini`, `openai`, `anthropic`, `deepseek`, `qwen`, `xai`/`grok`, `mistral`

---

## Model Orchestrator

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orchestrator/capabilities` | GET | Get model capabilities registry |
| `/orchestrator/estimate-cost` | POST | Estimate monthly cost for tier |
| `/orchestrator/recommendations/{task_type}` | GET | Get model recommendations |
| `/orchestrator/current-spend` | GET | Get current month spending |

**Quality Tiers:** `Budget`, `Balanced`, `Premium`

---

## Tournament System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tournament/structure/create` | POST | Create structure variant tournament |
| `/tournament/scene/create` | POST | Create scene variant tournament |
| `/tournament/{id}/run` | POST | Run tournament round |
| `/tournament/{id}/results` | GET | Get tournament results |
| `/tournament/{id}/variants` | GET | Get tournament variants |
| `/tournament/{id}/consensus` | GET | Get consensus analysis |
| `/tournament/{id}/select-winner` | POST | Select tournament winner |
| `/tournament/{id}/hybrid` | POST | Create hybrid from variants |
| `/tournaments` | GET | List tournaments |
| `/tournament/{id}` | GET | Get tournament details |

---

## Squad System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/squad/available` | GET | Get available squads |
| `/squad/apply` | POST | Apply squad configuration |
| `/squad/active` | GET | Get active squad |
| `/squad/tournament-models` | GET | Get tournament models |
| `/squad/tournament-models` | POST | Set tournament models |
| `/squad/tournament-models/custom` | DELETE | Clear custom models |
| `/squad/estimate-cost` | POST | Estimate tournament cost |
| `/squad/voice-recommendation` | GET | Get voice recommendation |
| `/squad/voice-recommendation` | POST | Generate voice recommendation |
| `/squad/genre-recommendation` | POST | Get genre-based recommendation |
| `/squad/course-mode` | POST | Toggle course mode |

**Squad Presets:** `starter`, `hybrid`, `pro`, `local`

---

## Usage Tracking

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/usage/record` | POST | Record API usage |
| `/usage/summary` | GET | Get monthly usage summary |
| `/usage/thresholds` | GET | Check cost thresholds |
| `/usage/thresholds/dismiss` | POST | Dismiss threshold notification |
| `/usage/recent` | GET | Get recent usage records |
| `/usage/daily` | GET | Get daily cost breakdown |

---

## Key Provisioning

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/keys/provision` | POST | Provision API keys from server |
| `/keys/status` | GET | Get key provisioning status |
| `/keys/providers` | GET | Get available providers |
| `/keys/clear` | DELETE | Clear all provisioned keys |

---

## System & Hardware

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/system/hardware` | GET | Detect system hardware |
| `/system/local-models` | GET | Get recommended local models |
| `/system/ollama/pull` | POST | Start pulling Ollama model |
| `/system/ollama/pull-status` | GET | Get Ollama pull status |
| `/system/workspace/default` | GET | Get default workspace path |
| `/system/workspace/validate` | POST | Validate workspace path |

---

## Workspace Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/workspace/init` | POST | Initialize workspace |
| `/workspace/status` | GET | Get workspace status |

---

## Manuscript & Knowledge Query

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/manuscript/working` | GET | List working files |
| `/manuscript/structure` | GET | Get manuscript structure |
| `/manuscript/promote` | POST | Promote working file to manuscript |
| `/knowledge/query` | POST | Query with auto-classification |

---

## Metabolism

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/metabolism/consolidate-kb` | POST | Consolidate Foreman KB to graph |
| `/metabolism/consolidate-kb/{project_id}` | POST | Consolidate KB for project |

---

## Mentions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mentions/search` | GET | Search for @mentionable entities |

---

## Project & Tournament (Legacy)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/project/init` | POST | Initialize student project |
| `/graph/context/{scene_id}` | GET | Get scaffold data for scene |
| `/tournament/run` | POST | Run scene drafting tournament |
| `/scene/save` | POST | Save scene and ingest data |

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
- `501` - Not Implemented

---

## Endpoint Count by Category

| Category | Count |
|----------|-------|
| Knowledge Graph | 23 |
| Director Mode | 16 |
| Tournament System | 10 |
| Session Management | 8 |
| Health Dashboard | 9 |
| The Foreman | 14 |
| Voice Calibration | 7 |
| Settings | 9 |
| Squad System | 11 |
| Story Bible | 7 |
| NotebookLM | 7 |
| Usage Tracking | 6 |
| System/Hardware | 6 |
| Verification | 3 |
| Other | 32 |
| **Total** | **168** |

---

*Generated for Writers Factory v2.0 - December 2025*
