# Handoff: Complete Assistant Panel Redesign Backend Integration

## Context

The **Assistant Panel Redesign (Muse/Scribe)** frontend is 100% complete with all 8 chat components implemented and working beautifully. However, **3 backend endpoints are missing** that prevent full feature integration.

**Current Status**: 81% complete overall
- ✅ Phase 1 (Core Chat Liberation): 100% complete
- ✅ Phase 2 (Enhanced Input Bar): 100% complete
- ⚠️ Phase 3 (Stage Auto-Detection): 50% complete (frontend done, backend missing)
- ✅ Phase 4 (Status Bar): 100% complete

---

## Your Mission

Implement the **3 missing backend endpoints** to complete Phase 3 and verify Phase 4 integration:

### 1. `GET /foreman/stage` - Stage Detection Endpoint

**Location**: `backend/api.py`

**Purpose**: Auto-detect current writing stage based on project state

**Expected Response**:
```json
{
  "current": "voice",
  "completed": ["conception"],
  "progress": {
    "conception": 100,
    "voice": 45,
    "execution": 0,
    "polish": 0
  },
  "can_change": true
}
```

**Detection Logic** (implement in new function in `backend/api.py` or `backend/agents/foreman.py`):

```python
async def detect_current_stage():
    """
    Auto-detect writing stage based on:
    - Story Bible completion → conception
    - Voice reference existence → voice
    - Draft files → execution
    - High completion % → polish
    """
    # Use existing StoryBibleService to check completion
    story_bible_status = await story_bible_service.get_status()

    # Check for voice reference files in content/
    voice_reference_exists = check_voice_reference()  # Look for VoiceReference.md or similar

    # Check for draft chapters
    drafts_exist = check_draft_files()  # Look in content/ for Chapter*.md files

    # Calculate progress percentages
    conception_progress = story_bible_status.completion_percentage

    # Determine current stage
    if conception_progress < 100:
        current = "conception"
        completed = []
    elif not voice_reference_exists:
        current = "voice"
        completed = ["conception"]
    elif drafts_exist:
        # Check if high completion suggests polish stage
        if conception_progress == 100 and voice_reference_exists:
            current = "execution"  # or "polish" based on draft count
            completed = ["conception", "voice"]
        else:
            current = "execution"
            completed = ["conception", "voice"]
    else:
        current = "execution"
        completed = ["conception", "voice"]

    return {
        "current": current,
        "completed": completed,
        "progress": {
            "conception": conception_progress,
            "voice": 50 if voice_reference_exists else 0,
            "execution": calculate_execution_progress(),
            "polish": 0
        },
        "can_change": True
    }
```

**Endpoint Implementation**:
```python
@app.get("/foreman/stage")
async def get_foreman_stage():
    """Get current writing stage with auto-detection"""
    stage_info = await detect_current_stage()
    return stage_info
```

---

### 2. `POST /foreman/stage` - Manual Stage Change

**Location**: `backend/api.py`

**Purpose**: Allow user to manually override stage focus

**Request Body**:
```json
{
  "stage": "conception"  // One of: conception, voice, execution, polish
}
```

**Response**:
```json
{
  "success": true,
  "message": "Focus changed to Conception stage",
  "current": "conception"
}
```

**Implementation**:
```python
from pydantic import BaseModel

class StageChangeRequest(BaseModel):
    stage: str  # conception, voice, execution, polish

@app.post("/foreman/stage")
async def change_foreman_stage(request: StageChangeRequest):
    """Manually change writing stage focus"""
    valid_stages = ["conception", "voice", "execution", "polish"]

    if request.stage not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {valid_stages}")

    # Store stage preference (you can add to FormanKBService or settings)
    # For now, just acknowledge the change
    stage_names = {
        "conception": "Conception",
        "voice": "Voice",
        "execution": "Execution",
        "polish": "Polish"
    }

    return {
        "success": True,
        "message": f"Focus changed to {stage_names[request.stage]} stage",
        "current": request.stage
    }
```

---

### 3. `GET /mentions/search` - Knowledge Graph Search for Mentions

**Location**: `backend/api.py`

**Purpose**: Search Knowledge Graph for @mentionable entities (characters, locations, files)

**Query Parameters**:
- `q` (required): Search query
- `limit` (optional): Max results (default: 10)

**Expected Response**:
```json
{
  "results": [
    {
      "type": "character",
      "name": "Maya",
      "id": "char_maya",
      "file": "Characters/Maya.md"
    },
    {
      "type": "file",
      "name": "Chapter 3 - May Day",
      "id": "file_ch3",
      "path": "Chapters/Chapter3.md"
    },
    {
      "type": "location",
      "name": "The Lab",
      "id": "loc_lab",
      "file": "World Bible/Locations/TheLab.md"
    }
  ]
}
```

**Implementation**:
```python
@app.get("/mentions/search")
async def search_mentions(q: str, limit: int = 10):
    """
    Search Knowledge Graph for mentionable entities

    Returns characters, locations, themes, and files matching query
    """
    results = []

    # Search Knowledge Graph nodes
    try:
        # Get all nodes from graph
        graph_data = knowledge_graph_service.get_graph_data()

        query_lower = q.lower()

        # Search character nodes
        for node in graph_data.get("nodes", []):
            if query_lower in node["label"].lower():
                node_type = node["node_type"].lower()

                result = {
                    "type": node_type,
                    "name": node["label"],
                    "id": f"{node_type}_{node['id']}",
                    "file": node.get("file_path", "")
                }
                results.append(result)

        # Also search content directory files
        content_dir = Path("content")
        if content_dir.exists():
            for file_path in content_dir.rglob("*.md"):
                file_name = file_path.stem
                if query_lower in file_name.lower():
                    results.append({
                        "type": "file",
                        "name": file_name,
                        "id": f"file_{file_path.stem}",
                        "path": str(file_path.relative_to(content_dir.parent))
                    })

        # Limit results
        results = results[:limit]

    except Exception as e:
        logger.error(f"Error searching mentions: {e}")
        results = []

    return {"results": results}
```

---

### 4. VERIFY: `/foreman/chat` Context Handling

**Task**: Check if the existing `POST /foreman/chat` endpoint accepts and processes a `context` array.

**Expected Request Format** (from spec):
```json
{
  "message": "Help me with @Maya's arc",
  "context": [
    { "type": "file", "path": "Chapters/Chapter3.md" },
    { "type": "mention", "id": "char_maya" },
    { "type": "attachment", "content": "...", "filename": "research.pdf" }
  ],
  "agent": "default",
  "include_open_file": true
}
```

**If NOT implemented**:
Update the `ForemanChatRequest` Pydantic model and `foreman_chat()` function to:
1. Accept optional `context` array
2. Read context files before sending to Foreman
3. Include context in the prompt sent to LLM

---

## Files You'll Modify

1. **`backend/api.py`**:
   - Add 3 new endpoints (lines ~88+)
   - Add Pydantic models for requests
   - Verify/update `/foreman/chat` endpoint

2. **`backend/agents/foreman.py`** (optional):
   - Add stage detection logic if it fits better here
   - Update chat handler to use context

3. **`backend/services/story_bible_service.py`** (reference only):
   - Already has `get_status()` method - use it for conception progress

---

## Testing Checklist

After implementing, test these scenarios:

### Stage Detection:
```bash
# Should return current stage based on Story Bible completion
curl http://localhost:8000/foreman/stage
```

### Manual Stage Change:
```bash
# Should allow changing focus to voice stage
curl -X POST http://localhost:8000/foreman/stage \
  -H "Content-Type: application/json" \
  -d '{"stage": "voice"}'
```

### Mention Search:
```bash
# Should return Knowledge Graph entities matching "maya"
curl "http://localhost:8000/mentions/search?q=maya&limit=10"
```

### Context in Chat:
```bash
# Should accept context array and include in prompt
curl -X POST http://localhost:8000/foreman/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Help with character arc",
    "context": [{"type": "file", "path": "content/Characters/Protagonist.md"}]
  }'
```

---

## Expected Outcome

After your work:
- ✅ StageDropdown shows **real** project progress with accurate checkmarks
- ✅ Users can manually change stage focus via dropdown
- ✅ MentionPicker searches **Knowledge Graph** for real entities
- ✅ Context items (files, mentions, attachments) are sent to backend
- ✅ Assistant Panel Redesign: **100% complete**

---

## Reference Documentation

- **Task Spec**: `docs/tasks/ASSISTANT_PANEL_REDESIGN.md` (lines 296-395 for Phase 3)
- **API Reference**: `docs/API_REFERENCE.md`
- **Story Bible Service**: `backend/services/story_bible_service.py`
- **Knowledge Graph Service**: `backend/services/graph_service.py`
- **Existing Foreman Endpoints**: Search `backend/api.py` for `@app.post("/foreman/`

---

## Notes

- The frontend is **already wired** to call these endpoints - just implement them and everything will connect
- Use existing services (StoryBibleService, KnowledgeGraphService) - don't reinvent
- Follow existing API patterns in `api.py` for consistency
- Add proper error handling and logging
- The user is already running the app - test with `curl` or frontend UI after implementing

Good luck! You're finishing the last 19% to make this feature 100% complete. 🚀
