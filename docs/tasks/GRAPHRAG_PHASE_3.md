# GraphRAG Phase 3: Narrative Extraction

**Parent Spec**: `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md`
**Status**: Ready for Implementation
**Priority**: High - Enables rich narrative graph
**Depends On**: Phase 1 (Complete), Phase 2 (Embeddings optional but helpful)

---

## Goal

Implement narrative-aware entity and relationship extraction:
1. Narrative ontology with story-specific edge types
2. Enhanced extraction prompts for LLM-based extraction
3. Integration with manuscript promotion workflow

---

## Deliverables

### 1. NarrativeOntology

**File**: `backend/graph/narrative_ontology.py`

Define narrative-specific edge types based on story physics.

**Key Requirements**:
- `NarrativeEdgeType` enum with core story-driving types
- `NarrativeEdge` dataclass with metadata
- Default enabled/disabled state for each type

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class NarrativeEdgeType(Enum):
    """
    Core narrative edge types based on story physics.

    These capture the dramatic relationships that drive plot.
    """
    # Goal-Obstacle-Conflict Triad
    MOTIVATES = "MOTIVATES"      # Goal → Character (what drives them)
    HINDERS = "HINDERS"          # Obstacle → Goal (what blocks progress)
    CAUSES = "CAUSES"            # Event → Event (causality chain)

    # Character Dynamics
    CHALLENGES = "CHALLENGES"    # Scene → Fatal Flaw (when flaw is tested)
    KNOWS = "KNOWS"              # Character → Fact (knowledge state)
    CONTRADICTS = "CONTRADICTS"  # Fact → Fact (conflicts in story logic)

    # Narrative Threading
    FORESHADOWS = "FORESHADOWS"  # Scene → Future Event (setup)
    CALLBACKS = "CALLBACKS"      # Scene → Past Event (payoff)

    # Existing types (for compatibility)
    LOCATED_IN = "LOCATED_IN"
    OWNS = "OWNS"
    PART_OF = "PART_OF"
    HAS_TRAIT = "HAS_TRAIT"
    LOVES = "LOVES"
    HATES = "HATES"

    # Escape hatch for custom types
    CUSTOM = "CUSTOM"


@dataclass
class NarrativeEdge:
    """Enhanced edge with narrative metadata."""
    source: str
    target: str
    edge_type: NarrativeEdgeType
    description: Optional[str] = None
    weight: float = 1.0  # For tension calculations
    scene_id: Optional[str] = None  # Where relationship established
    is_active: bool = True  # Can be "resolved" (obstacle overcome)
    custom_type: Optional[str] = None  # If edge_type is CUSTOM


# Default edge types (can be toggled in settings)
DEFAULT_EDGE_TYPES = {
    NarrativeEdgeType.MOTIVATES: True,
    NarrativeEdgeType.HINDERS: True,
    NarrativeEdgeType.CHALLENGES: True,
    NarrativeEdgeType.CAUSES: True,
    NarrativeEdgeType.FORESHADOWS: True,
    NarrativeEdgeType.CALLBACKS: True,
    NarrativeEdgeType.KNOWS: True,
    NarrativeEdgeType.CONTRADICTS: False,  # Experimental - off by default
}


def get_enabled_edge_types() -> list:
    """Get list of enabled edge types from settings."""
    from backend.services.settings_service import settings_service

    enabled = []
    for edge_type, default in DEFAULT_EDGE_TYPES.items():
        key = f"graph.edge_types.{edge_type.value}"
        if settings_service.get(key, default):
            enabled.append(edge_type)

    return enabled
```

---

### 2. NarrativeExtractor

**File**: `backend/graph/narrative_extractor.py`

LLM-based extraction with narrative-aware prompts.

**Key Requirements**:
- Use Ollama (llama3.2:3b) for extraction
- Include known entities as context to avoid duplicates
- Extract both entities and narrative relationships
- Return structured JSON with flaw challenge and beat alignment

```python
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp

from backend.graph.narrative_ontology import NarrativeEdgeType, get_enabled_edge_types

logger = logging.getLogger(__name__)

NARRATIVE_EXTRACTION_PROMPT = """You are analyzing a scene from a novel to extract narrative structure.

SCENE CONTENT:
{scene_content}

EXISTING CHARACTERS: {known_characters}
EXISTING LOCATIONS: {known_locations}
CURRENT BEAT: {current_beat}

Extract the following from this scene:

1. NEW ENTITIES (only if not already known):
   - Characters introduced
   - Locations mentioned
   - Objects of significance
   - Events that occur

2. NARRATIVE RELATIONSHIPS:
   For each relationship, identify:
   - Source entity
   - Relationship type (from: {enabled_types})
   - Target entity
   - Brief description

Focus especially on:
- What MOTIVATES characters in this scene?
- What HINDERS their goals?
- Is the protagonist's fatal flaw being CHALLENGED?
- What does this scene FORESHADOW for later?
- What earlier events does it CALLBACK to?

Return as JSON:
{{
  "entities": [
    {{"id": "entity_name", "type": "CHARACTER|LOCATION|OBJECT|EVENT", "description": "..."}}
  ],
  "relationships": [
    {{"source": "...", "type": "MOTIVATES|HINDERS|...", "target": "...", "description": "..."}}
  ],
  "flaw_challenge": {{
    "challenged": true/false,
    "description": "How the flaw was challenged (if applicable)"
  }},
  "beat_alignment": {{
    "aligned": true/false,
    "expected_beat": "{current_beat}",
    "actual_function": "What this scene actually accomplishes"
  }}
}}

Be precise. Only extract what is explicitly present or strongly implied."""


class NarrativeExtractor:
    """
    Extracts narrative structure from scenes.

    Uses LLM (Ollama Llama 3.2) for intelligent extraction
    with narrative-aware prompts.
    """

    def __init__(self, graph_service):
        self.graph = graph_service
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "llama3.2:3b"

    async def _query_ollama(self, prompt: str) -> str:
        """Query Ollama for extraction."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.1}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.ollama_url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("message", {}).get("content", "{}")
                else:
                    logger.error(f"Ollama error: {response.status}")
                    return "{}"

    async def extract_from_scene(
        self,
        scene_content: str,
        scene_id: str,
        current_beat: str = "Unknown"
    ) -> dict:
        """
        Extract narrative elements from a scene.

        Args:
            scene_content: The scene text
            scene_id: Identifier for the scene
            current_beat: Expected beat alignment (e.g., "Midpoint")

        Returns:
            Structured extraction result
        """
        # Gather existing context
        known_characters = self._get_known_entities("CHARACTER")
        known_locations = self._get_known_entities("LOCATION")
        enabled_types = [t.value for t in get_enabled_edge_types()]

        prompt = NARRATIVE_EXTRACTION_PROMPT.format(
            scene_content=scene_content[:6000],  # Truncate for context
            known_characters=", ".join(known_characters) or "None yet",
            known_locations=", ".join(known_locations) or "None yet",
            current_beat=current_beat,
            enabled_types=", ".join(enabled_types)
        )

        response = await self._query_ollama(prompt)

        try:
            result = json.loads(response)
            result["scene_id"] = scene_id
            result["extracted_at"] = datetime.now(timezone.utc).isoformat()
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse: {response[:200]}")
            return {"error": "Extraction failed", "raw": response}

    def _get_known_entities(self, entity_type: str) -> List[str]:
        """Get known entities of a type from the graph."""
        try:
            nodes = self.graph.get_nodes_by_type(entity_type)
            return [n.name for n in nodes] if nodes else []
        except Exception:
            return []

    async def merge_to_graph(self, extraction: dict) -> dict:
        """
        Merge extraction results into the knowledge graph.

        Returns:
            Merge statistics
        """
        stats = {"nodes_created": 0, "edges_created": 0, "conflicts": []}
        scene_id = extraction.get("scene_id", "unknown")

        # Create new entities
        for entity in extraction.get("entities", []):
            entity_id = entity.get("id", "").strip()
            if not entity_id:
                continue

            existing = self.graph.find_node_by_name(entity_id)
            if not existing:
                self.graph.add_node(
                    name=entity_id,
                    node_type=entity.get("type", "UNKNOWN"),
                    description=entity.get("description"),
                    source=f"scene:{scene_id}"
                )
                stats["nodes_created"] += 1

        # Create relationships
        for rel in extraction.get("relationships", []):
            try:
                edge_type = NarrativeEdgeType[rel.get("type", "CUSTOM")]
            except KeyError:
                edge_type = NarrativeEdgeType.CUSTOM

            # Flag contradictions for review
            if edge_type == NarrativeEdgeType.CONTRADICTS:
                stats["conflicts"].append(rel)
                continue

            source_node = self.graph.find_node_by_name(rel.get("source", ""))
            target_node = self.graph.find_node_by_name(rel.get("target", ""))

            if source_node and target_node:
                self.graph.add_edge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation_type=edge_type.value,
                    description=rel.get("description")
                )
                stats["edges_created"] += 1

        return stats


# Factory function
def get_narrative_extractor():
    """Get NarrativeExtractor instance."""
    from backend.graph.graph_service import KnowledgeGraphService
    return NarrativeExtractor(KnowledgeGraphService())
```

---

### 3. Consolidator Service Updates

**File**: `backend/services/consolidator_service.py` (modify)

Add method to extract from file content using NarrativeExtractor:

```python
# Add to ConsolidatorService class

async def extract_from_file(
    self,
    filepath: str,
    current_beat: str = "Unknown"
) -> Dict[str, Any]:
    """
    Extract narrative elements from a file.

    Called by ManuscriptService after promotion.

    Args:
        filepath: Path to the file to extract from
        current_beat: Expected beat alignment

    Returns:
        Extraction result with merge stats
    """
    from backend.graph.narrative_extractor import get_narrative_extractor

    # Read file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        return {"status": "error", "error": str(e)}

    if not content.strip():
        return {"status": "skipped", "reason": "empty_file"}

    # Extract using NarrativeExtractor
    extractor = get_narrative_extractor()
    scene_id = os.path.basename(filepath)

    extraction = await extractor.extract_from_scene(
        scene_content=content,
        scene_id=scene_id,
        current_beat=current_beat
    )

    if extraction.get("error"):
        return {"status": "error", "error": extraction.get("error")}

    # Merge to graph
    merge_stats = await extractor.merge_to_graph(extraction)

    # Also index embeddings if available
    try:
        from backend.services.embedding_index_service import get_embedding_index_service
        index_service = get_embedding_index_service()
        # Index newly created nodes
        # (Implementation depends on Phase 2 completion)
    except ImportError:
        pass  # Phase 2 not implemented yet

    return {
        "status": "success",
        "scene_id": scene_id,
        "entities_found": len(extraction.get("entities", [])),
        "relationships_found": len(extraction.get("relationships", [])),
        "nodes_created": merge_stats["nodes_created"],
        "edges_created": merge_stats["edges_created"],
        "conflicts": merge_stats["conflicts"],
        "flaw_challenged": extraction.get("flaw_challenge", {}).get("challenged", False),
        "beat_aligned": extraction.get("beat_alignment", {}).get("aligned", True)
    }
```

---

### 4. Ingestor Updates

**File**: `backend/ingestor.py` (modify)

Update extraction prompts to use narrative ontology:

```python
# Replace or augment existing EXTRACTION_PROMPT

NARRATIVE_INGESTION_PROMPT = """You are a Literary Data Analyst extracting story structure.

Analyze this text and extract:

1. ENTITIES - Only explicit mentions:
   - CHARACTER: Named people/beings
   - LOCATION: Named places
   - OBJECT: Significant named items
   - EVENT: Named plot events

2. RELATIONSHIPS - Using these types:
   - MOTIVATES: What drives a character
   - HINDERS: What blocks a goal
   - CHALLENGES: Tests a character's weakness
   - FORESHADOWS: Sets up future events
   - CALLBACKS: References past events
   - CAUSES: Event leads to event
   - KNOWS: Character knows a fact
   - LOCATED_IN: Person/thing in a place
   - OWNS: Possession
   - LOVES/HATES: Strong feelings

Return ONLY valid JSON:
{{
  "nodes": [
    {{"id": "ExactName", "type": "CHARACTER", "desc": "Brief description"}}
  ],
  "edges": [
    {{"source": "id1", "target": "id2", "relation": "MOTIVATES", "desc": "context"}}
  ]
}}

TEXT TO ANALYZE:
{text}
"""
```

---

### 5. ManuscriptService Integration

**File**: `backend/services/manuscript_service.py` (modify)

Update `_trigger_extraction` to use NarrativeExtractor:

```python
async def _trigger_extraction(self, filepath: str) -> Dict[str, Any]:
    """
    Trigger narrative extraction for a promoted file.
    """
    try:
        from backend.services.consolidator_service import get_consolidator_service

        consolidator = get_consolidator_service()

        # Get current beat from story bible if available
        current_beat = await self._get_current_beat()

        result = await consolidator.extract_from_file(
            filepath=filepath,
            current_beat=current_beat
        )

        return result

    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {"status": "error", "error": str(e)}

async def _get_current_beat(self) -> str:
    """Get current beat from story bible."""
    try:
        from backend.services.story_bible_service import StoryBibleService
        svc = StoryBibleService()
        beat_data = svc.parse_beat_sheet()
        current = beat_data.get("current_beat", 1)
        beats = beat_data.get("beats", {})
        beat_info = beats.get(str(current), {})
        return beat_info.get("name", "Unknown")
    except Exception:
        return "Unknown"
```

---

### 6. API Endpoints

**File**: `backend/api.py` (modify)

Add extraction endpoint:

```python
@app.post("/graph/extract-narrative", summary="Extract narrative from text")
async def extract_narrative(
    content: str,
    scene_id: str = "manual",
    current_beat: str = "Unknown"
):
    """
    Extract narrative elements from provided text.

    Useful for testing extraction or manual ingestion.
    """
    from backend.graph.narrative_extractor import get_narrative_extractor

    extractor = get_narrative_extractor()
    extraction = await extractor.extract_from_scene(
        scene_content=content,
        scene_id=scene_id,
        current_beat=current_beat
    )

    if extraction.get("error"):
        raise HTTPException(status_code=500, detail=extraction["error"])

    merge_stats = await extractor.merge_to_graph(extraction)

    return {
        "extraction": extraction,
        "merge_stats": merge_stats
    }


@app.get("/graph/edge-types", summary="Get available edge types")
async def get_edge_types():
    """
    Get list of narrative edge types and their enabled status.
    """
    from backend.graph.narrative_ontology import NarrativeEdgeType, DEFAULT_EDGE_TYPES

    return {
        "edge_types": [
            {
                "name": t.value,
                "enabled": DEFAULT_EDGE_TYPES.get(t, True),
                "description": {
                    "MOTIVATES": "What drives a character",
                    "HINDERS": "What blocks a goal",
                    "CHALLENGES": "Tests a character's weakness",
                    "CAUSES": "Event leads to event",
                    "FORESHADOWS": "Sets up future events",
                    "CALLBACKS": "References past events",
                    "KNOWS": "Character knows a fact",
                    "CONTRADICTS": "Conflicting facts",
                }.get(t.value, "")
            }
            for t in NarrativeEdgeType
            if t != NarrativeEdgeType.CUSTOM
        ]
    }
```

---

## Implementation Order

1. **NarrativeOntology** - Pure definitions, no dependencies
2. **NarrativeExtractor** - Depends on ontology
3. **Consolidator updates** - Add `extract_from_file()`
4. **ManuscriptService updates** - Use new extraction
5. **Ingestor updates** - Optional, can use old prompts
6. **API endpoints** - Wire everything

---

## Files Checklist

**Create**:
- [ ] `backend/graph/narrative_ontology.py`
- [ ] `backend/graph/narrative_extractor.py`

**Modify**:
- [ ] `backend/services/consolidator_service.py` - Add `extract_from_file()`
- [ ] `backend/services/manuscript_service.py` - Update `_trigger_extraction()`
- [ ] `backend/ingestor.py` - Optional: update prompts
- [ ] `backend/api.py` - Add 2 new endpoints

---

## Verification

### Manual Testing

1. **Extract from text**:
```bash
curl -X POST http://localhost:8000/graph/extract-narrative \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Mickey watched Noni leave, knowing his trust issues had pushed her away again.",
    "scene_id": "test_scene",
    "current_beat": "Midpoint"
  }'
```

Expected response includes:
- Entities: Mickey (CHARACTER), Noni (CHARACTER)
- Relationships: CHALLENGES (trust issues → Mickey), HINDERS (trust issues → relationship)
- flaw_challenge.challenged: true

2. **Check edge types**:
```bash
curl http://localhost:8000/graph/edge-types
```

3. **Promote and verify extraction**:
```bash
# Create test file
echo "Mickey confronted his fear at last." > content/Working/test.md

# Promote
curl -X POST http://localhost:8000/manuscript/promote \
  -H "Content-Type: application/json" \
  -d '{"working_file": "test.md", "target_path": "test.md"}'

# Check graph for new edges
curl http://localhost:8000/graph/stats
```

---

## Success Criteria

- [ ] NarrativeEdgeType enum covers core story physics
- [ ] Extraction correctly identifies CHALLENGES to fatal flaw
- [ ] FORESHADOWS and CALLBACKS are detected
- [ ] Known entities are not duplicated
- [ ] Manuscript promotion triggers narrative extraction
- [ ] Contradictions are flagged but not auto-added

---

## Notes for Implementing Agent

1. **Ollama must be running** - Extractor uses llama3.2:3b
2. **Prompt length** - Scene content is truncated to 6000 chars
3. **Graph service methods** - May need `find_node_by_name()` and `get_nodes_by_type()`
4. **Settings integration** - Edge type toggles read from settings_service

---

## Handoff

When complete, provide:
1. Branch name and commit hash
2. List of files created/modified
3. Sample extraction showing narrative edge types
4. Any deviations from spec
