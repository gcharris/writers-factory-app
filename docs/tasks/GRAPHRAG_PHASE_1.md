# GraphRAG Phase 1: Foundation

**Parent Spec**: `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md`
**Status**: Ready for Implementation
**Priority**: High - Unblocks all subsequent phases

---

## Goal

Implement the foundational infrastructure for GraphRAG:
1. Query classification system
2. Token-aware context assembly
3. Working → Manuscript file workflow

---

## Deliverables

### 1. QueryClassifier Service

**File**: `backend/services/query_classifier.py`

Implement the `QueryClassifier` class as specified in the main plan (Part 3.1).

**Key Requirements**:
- 8 query types: `CHARACTER_LOOKUP`, `CHARACTER_DEEP`, `PLOT_STATUS`, `RELATIONSHIP`, `WORLD_RULES`, `WRITING_TECHNIQUE`, `SCENE_CONTEXT`, `CONTRADICTION_CHECK`, `HYBRID`
- Pattern-based classification with regex
- Entity extraction from known graph entities
- Keyword extraction (stopword removal)
- Returns `ClassifiedQuery` dataclass with: `query_type`, `entities`, `keywords`, `sources`, `confidence`, `requires_semantic`

**Integration**:
- Add `get_query_classifier()` singleton function
- Classifier loads known entities from `KnowledgeGraphService` on init
- Call `update_entities()` after graph changes

**Testing**:
```python
# Example test cases
classifier = QueryClassifier(known_entities={"Mickey", "Noni", "Bar"})

# Should classify as CHARACTER_LOOKUP
result = classifier.classify("Who is Mickey?")
assert result.query_type == QueryType.CHARACTER_LOOKUP
assert "mickey" in [e.lower() for e in result.entities]

# Should classify as RELATIONSHIP
result = classifier.classify("How does Mickey feel about Noni?")
assert result.query_type == QueryType.RELATIONSHIP
assert len(result.entities) == 2

# Should classify as WRITING_TECHNIQUE
result = classifier.classify("How should I write compressed prose?")
assert result.query_type == QueryType.WRITING_TECHNIQUE
assert "notebooklm" in result.sources
```

---

### 2. ContextAssembler Service

**File**: `backend/services/context_assembler.py`

Implement the `ContextAssembler` class as specified in the main plan (Part 3.2).

**Key Requirements**:
- Token counting via `tiktoken` (`cl100k_base` encoding)
- Model-specific budgets (see `CONTEXT_BUDGETS` dict)
- Priority-based assembly:
  1. Character core (Fatal Flaw, The Lie, Arc) - NEVER truncate
  2. Active scaffold
  3. Relevant relationships
  4. Beat context
  5. World rules (filtered by keywords)
  6. Recent KB decisions
  7. NotebookLM results (lowest priority, truncate if needed)
- Debug metadata comment showing included sections and token count

**Dependency**:
- Add `tiktoken` to `requirements.txt`:
  ```
  tiktoken>=0.5.0
  ```

**Integration**:
- Add `get_context_assembler(model: str)` factory function
- Returns assembler configured for specific model's token budget

**Testing**:
```python
assembler = ContextAssembler(model='deepseek-chat')  # 8000 token budget

# Should prioritize character core
result = assembler.assemble(
    classified_query=ClassifiedQuery(
        query_type=QueryType.CHARACTER_DEEP,
        entities=["Mickey"],
        keywords=["betrayal", "reaction"],
        sources=["graph", "story_bible"],
        confidence=0.9,
        requires_semantic=True
    ),
    graph_context={"characters": {"Mickey": {"description": "..."}}},
    story_bible_context={"characters": {"Mickey": {"fatal_flaw": "Trust issues"}}},
    kb_context=[],
    notebooklm_results="Long writing guidance text..." * 1000  # Very long
)

# NotebookLM should be truncated, character core preserved
assert "Trust issues" in result
assert "[... truncated for length]" in result
```

---

### 3. ManuscriptService

**File**: `backend/services/manuscript_service.py`

Implement the `ManuscriptService` class as specified in the main plan (Part 1.3).

**Key Requirements**:
- Manage `content/Working/` and `content/Manuscript/` directories
- Track metadata in `.working_meta.json` and `.manuscript_meta.json`
- `promote_to_manuscript(working_file, target_path, trigger_extraction=True)`:
  - Copy file from Working to Manuscript (preserving Working copy)
  - Update metadata
  - Trigger graph extraction via ConsolidatorService
- `get_working_files()` - List working files with metadata
- `get_manuscript_structure()` - Hierarchical structure for file tree

**Integration**:
- Add `get_manuscript_service()` singleton
- Wire to ConsolidatorService for extraction trigger

**Directory Creation**:
- On first init, create `content/Working/` and `content/Manuscript/` if they don't exist

---

### 4. API Endpoints

**File**: `backend/api.py` (modify)

Add the following endpoints:

```python
# Manuscript endpoints
@app.get("/manuscript/working")
async def list_working_files() -> dict:
    """List all files in Working/ directory with metadata."""

@app.get("/manuscript/structure")
async def get_manuscript_structure() -> dict:
    """Get hierarchical manuscript structure for file tree."""

@app.post("/manuscript/promote")
async def promote_to_manuscript(request: PromoteRequest) -> dict:
    """
    Promote a working file to the manuscript.

    Request body:
    {
        "working_file": "Chapter_04_Scene_02.md",
        "target_path": "Act_2/Chapter_04/Scene_02.md",
        "extract": true
    }
    """

# Knowledge query endpoint
@app.post("/knowledge/query")
async def knowledge_query(request: QueryRequest) -> dict:
    """
    Query with automatic classification and routing.

    Request body:
    {
        "query": "How should Mickey react to the betrayal?",
        "model": "claude-sonnet-4-5"
    }

    Response:
    {
        "context": "... assembled context ...",
        "metadata": {
            "query_type": "character_deep",
            "sources": ["graph", "story_bible"],
            "entities": ["Mickey"],
            "tokens_used": 4532
        }
    }
    """
```

**Pydantic Models**:
```python
class PromoteRequest(BaseModel):
    working_file: str
    target_path: str
    extract: bool = True

class QueryRequest(BaseModel):
    query: str
    model: str = "claude-sonnet-4-5"
```

---

### 5. Frontend Store (Optional - can defer)

**File**: `frontend/src/lib/stores.js` (modify)

Add manuscript store:

```javascript
// Manuscript store
export const manuscriptStore = writable({
    working_files: [],
    structure: {},
    loading: false
});

export async function loadWorkingFiles() {
    manuscriptStore.update(s => ({ ...s, loading: true }));
    const response = await fetch('/api/manuscript/working');
    const data = await response.json();
    manuscriptStore.update(s => ({
        ...s,
        working_files: data.files,
        loading: false
    }));
}

export async function promoteFile(workingFile, targetPath) {
    const response = await fetch('/api/manuscript/promote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            working_file: workingFile,
            target_path: targetPath,
            extract: true
        })
    });
    return response.json();
}
```

---

## Implementation Order

1. **QueryClassifier** - No dependencies, pure logic
2. **ContextAssembler** - Depends on tiktoken only
3. **ManuscriptService** - Depends on ConsolidatorService (existing)
4. **API Endpoints** - Wire everything together
5. **Frontend Store** - Optional, can defer to UI phase

---

## Files Checklist

**Create**:
- [ ] `backend/services/query_classifier.py`
- [ ] `backend/services/context_assembler.py`
- [ ] `backend/services/manuscript_service.py`

**Modify**:
- [ ] `backend/api.py` - Add 4 new endpoints
- [ ] `requirements.txt` - Add tiktoken
- [ ] `frontend/src/lib/stores.js` - Add manuscript store (optional)

---

## Verification

### Manual Testing

1. **Query Classification**:
   ```bash
   # Start backend
   cd backend && uvicorn api:app --reload --port 8000

   # Test classification
   curl -X POST http://localhost:8000/knowledge/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Who is Mickey?", "model": "claude-sonnet-4-5"}'
   ```

2. **Manuscript Promotion**:
   ```bash
   # Create a test working file
   echo "# Test Scene" > content/Working/test_scene.md

   # List working files
   curl http://localhost:8000/manuscript/working

   # Promote to manuscript
   curl -X POST http://localhost:8000/manuscript/promote \
     -H "Content-Type: application/json" \
     -d '{"working_file": "test_scene.md", "target_path": "Act_1/Chapter_01/Scene_01.md"}'

   # Check manuscript structure
   curl http://localhost:8000/manuscript/structure
   ```

3. **Token Counting**:
   ```bash
   # Test with a model that has small budget (DeepSeek: 8000 tokens)
   curl -X POST http://localhost:8000/knowledge/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Tell me everything about Mickey", "model": "deepseek-chat"}'

   # Response should show tokens_used < 8000
   ```

### Type Checking

```bash
cd frontend && npm run check
```

---

## Success Criteria

- [ ] QueryClassifier correctly classifies all 8 query types
- [ ] ContextAssembler respects token budgets per model
- [ ] Character core info is never truncated
- [ ] Working → Manuscript promotion creates correct directory structure
- [ ] Promotion triggers graph extraction (check logs for extraction activity)
- [ ] All new endpoints return expected JSON structure
- [ ] No TypeScript errors in frontend

---

## Notes for Implementing Agent

1. **Copy code from main spec** - The `GRAPHRAG_IMPLEMENTATION_PLAN.md` has complete code for all services. Copy and adapt as needed.

2. **Don't forget tiktoken** - Add to requirements.txt before testing ContextAssembler.

3. **Test with existing graph** - The knowledge graph should have some entities already. Use those for classifier testing.

4. **ConsolidatorService integration** - The `extract_from_file()` method may need to be added to ConsolidatorService. Check if it exists; if not, create a simple version that calls the existing extraction logic.

5. **Error handling** - Add try/except around extraction in ManuscriptService so promotion succeeds even if extraction fails (log the error).

---

## Handoff

When complete, provide:
1. Branch name and commit hash
2. List of files created/modified
3. Any deviations from spec
4. Known issues or TODOs for Phase 2
