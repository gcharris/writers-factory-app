Excellent. Now I have a complete picture. Let me give you a comprehensive analysis.



------

# Master Architecture V4.1 Review & Next Steps

## Current State Assessment

### What's Built and Working (Phases 1 & 2) ✅

| Component                   | Status       | Notes                                              |
| --------------------------- | ------------ | -------------------------------------------------- |
| **Tauri + SvelteKit Shell** | ✅ Solid      | 3-panel layout, file tree, editor working          |
| **FastAPI Backend**         | ✅ Solid      | REST API on port 8000, CORS configured             |
| **Knowledge Graph**         | ✅ Functional | NetworkX + SQLite dual-layer, CRUD operations work |
| **Agent Registry**          | ✅ Functional | 8 agents configured, cost tracking enabled         |
| **Tournament System**       | ⚠️ Mock       | Structure exists, but scoring is randomized        |
| **NotebookLM Oracle**       | ✅ Working    | MCP bridge verified today                          |
| **NER Extraction**          | ✅ Functional | spaCy-based entity extraction                      |
| **Multi-LLM Gateway**       | ✅ Functional | 10+ providers supported                            |

### What's Missing (Phase 3: The Metabolism) 🚧

| Component               | Current State | Gap                                            |
| ----------------------- | ------------- | ---------------------------------------------- |
| **SessionManager**      | ❌ None        | Sessions are request-scoped, no persistence    |
| **Session Compaction**  | ❌ None        | No recursive summarization                     |
| **Consolidator Agent**  | ❌ None        | No background digestion worker                 |
| **Conflict Resolution** | ❌ None        | No "Mickey loves rain vs hates rain" detection |
| **HealthService**       | ❌ None        | No dropped thread/timeline detection           |
| **VersionControl**      | ❌ None        | No graph snapshots or branching                |
| **Health Dashboard UI** | ❌ None        | No frontend panel for warnings                 |

------

## Architecture Analysis

### Strengths

1. **Solid Foundation**: The dual-layer graph (NetworkX for analysis, SQLite for persistence) is well-designed for the use case.
2. **Clean Separation**: Backend services are modular (`llm_service.py`, `graph_service.py`, `notebooklm_service.py`).
3. **Multi-Agent Ready**: The registry + orchestrator pattern supports the tournament concept well.
4. **Oracle Integration**: NotebookLM as "Ground Truth" source is now working - this is critical for the Consolidator to "phone a friend" when conflicts arise.

### Gaps to Address

1. **Fire-and-Forget Problem**: Currently, when you chat with an agent, that context is lost after the response. The architecture document calls this out explicitly - you need the "Workbench" (session log) before building the "Filing Cabinet" (memory).
2. **No Background Workers**: Python's `asyncio` is in place but not used for background tasks. The Consolidator needs to run asynchronously after saves.
3. **Tournament Scoring is Fake**: The `DraftCritic` returns mock scores. For the system to learn "procedural memory" (why did this draft win?), the critic needs real evaluation.
4. **Frontend State is Ephemeral**: Svelte stores reset on page refresh. No persistence layer for active session context.

------

## Recommended Implementation Order

Based on the architecture and what exists, here's the optimal build sequence:



### Step 1: SessionManager (SQLite)

**Priority: CRITICAL - Everything else depends on this**



```
backend/services/session_service.py (new file)
```

**What to build:**



- SQLite table: `session_events` (session_id, timestamp, role, content, metadata)
- API endpoints: `POST /session/start`, `POST /session/message`, `GET /session/{id}`
- Frontend store update: persist `session_id` and reload on refresh

**Why first:** Without session persistence, there's nothing to consolidate. This unlocks everything else.

 

**Estimated scope:** ~200 lines Python + schema migration + 2 Svelte components



------

### Step 2: Session Compaction

**Priority: HIGH - Prevents context bloat**

 

**What to build:**



- Background task in `session_service.py` using `asyncio.create_task()`
- Trigger: Every 20 messages OR 15 min inactivity
- Strategy: Call Llama 3.2 to summarize older messages, keep recent 5 verbatim
- Store compacted summary as special `session_event` type

**Why second:** Long ideation sessions will blow up context windows. Compaction keeps costs down.

 

**Estimated scope:** ~100 lines Python



------

### Step 3: Consolidator Agent (The Liver)

**Priority: HIGH - Core differentiator**



```
backend/agents/specialists/consolidator.py (new file)
```

**What to build:**



- Llama 3.2 agent in JSON mode
- ETL pipeline:
  1. **Extract**: Parse committed text for entities/facts
  2. **Recall**: Query graph for existing knowledge
  3. **Conflict Check**: Compare new vs old facts
  4. **Resolve**: Auto-discard low-confidence, flag conflicts for user
  5. **Update**: Write verified facts to graph
- Integration point: Hook into `POST /scene/save` endpoint

**Architecture decision:** Use the existing `manager_service.py` pattern (Ollama) but with structured JSON output.

 

**Why third:** This is the "digestive system" that makes the graph actually useful over time.

 

**Estimated scope:** ~300 lines Python + prompt engineering



------

### Step 4: HealthService (The Doctor)

**Priority: MEDIUM - Quality of life**



```
backend/services/health_service.py (new file)
```

**What to build:**



- **Dropped Threads**: Query graph for plot nodes introduced >N scenes ago with no resolution edge
- **Character Absences**: Query for character nodes not referenced in recent N scenes
- **Timeline Errors**: Analyze event nodes for causality violations
- Background task that runs after every save
- API endpoint: `GET /health/warnings`

**Why fourth:** Requires a populated graph to be useful. After Consolidator is running, there's data to check.

 

**Estimated scope:** ~200 lines Python + graph queries



------

### Step 5: VersionControl (Time Travel)

**Priority: MEDIUM - Safety net**

 

**What to build:**



- SQLite table: `graph_snapshots` (version_id, timestamp, serialized_graph)
- Auto-snapshot on chapter boundaries
- API endpoints: `GET /versions`, `POST /versions/restore/{id}`, `POST /versions/branch`
- Diff visualization (compare two versions)

**Why fifth:** Less urgent than the core memory pipeline, but valuable for "what if" experiments.

 

**Estimated scope:** ~150 lines Python + UI component



------

### Step 6: Health Dashboard UI

**Priority: LOW - Polish**

 

**What to build:**



- New Svelte component: `HealthDashboard.svelte`
- Display: Digestion status, warnings list, conflict queue
- Actions: Resolve conflict, dismiss warning, view diff

**Why last:** Needs all backend services to exist first.

 

**Estimated scope:** ~200 lines Svelte



------

## Quick Wins (Can Do Now)

1. **Fix Tournament Scoring**: Replace mock random scores in `DraftCritic` with actual LLM evaluation calls. The structure is there, just needs real implementation.
2. **Add Session ID to Frontend**: Even without full persistence, passing a `session_id` through the chat flow prepares for Step 1.
3. **Create Schema Migration**: Add `session_events` and `graph_snapshots` tables now, even if empty.

------

## Summary

| Phase                   | Status    | Next Action               |
| ----------------------- | --------- | ------------------------- |
| Phase 1 (Foundation)    | ✅ Done    | -                         |
| Phase 2 (Oracle)        | ✅ Done    | -                         |
| Phase 3 (Metabolism)    | 🚧 0%      | Start with SessionManager |
| Phase 4 (Immune System) | ⏳ Planned | After Phase 3             |
| Phase 5 (Polish)        | ⏳ Planned | Last                      |

**My recommendation:** Start with **SessionManager** (Step 1). It's ~200 lines of code, uses patterns you already have (SQLite + FastAPI), and unblocks everything else. Once sessions persist, the Consolidator has something to digest.

 

Would you like me to start implementing the SessionManager, or would you prefer a more detailed design spec first?