---
layout: default
title: GraphRAG Technical

---


# GraphRAG Implementation (Technical)

**Complete technical reference for the GraphRAG system**

> For conceptual overview and philosophy, see [GraphRAG: The Living Brain](graphrag.md)

---

## Implementation Overview

GraphRAG was implemented in five phases, each building on the previous:

| Phase | Name | Focus |
|-------|------|-------|
| **Phase 1** | Foundation | Schema, NetworkX, ego graphs |
| **Phase 2** | Semantic Search | Embeddings, similarity |
| **Phase 3** | Narrative Extraction | Story-physics edges, LLM extraction |
| **Phase 4** | Tiered Verification | Fast/Medium/Slow checks |
| **Phase 5** | Analysis & Enhancement | Community detection, tension |

---

## Phase 1: Foundation

### Schema Extension

**File**: `backend/graph/schema.py`

Added embedding storage columns to the Node model:

```python
# Phase 2: Embedding storage for semantic search
embedding = Column(JSON, nullable=True)
embedding_model = Column(String, nullable=True)
embedding_updated_at = Column(DateTime, nullable=True)
```

### Core Graph Methods

**File**: `backend/graph/graph_service.py`

```python
def to_networkx(self) -> nx.DiGraph:
    """Convert SQLite graph to NetworkX for algorithms."""

def ego_graph(self, entity_name: str, radius: int = 2) -> dict:
    """Get k-hop neighborhood around an entity."""

def get_nodes_by_type(self, node_type: str) -> List[Node]:
    """Filter nodes by type (CHARACTER, LOCATION, etc.)."""

def get_edges_by_type(self, relation_type: str) -> List[Edge]:
    """Filter edges by relation type (MOTIVATES, HINDERS, etc.)."""

def get_all_nodes(self) -> List[Node]:
    """Return all nodes in the graph."""

def get_all_edges(self) -> List[Edge]:
    """Return all edges in the graph."""
```

---

## Phase 2: Semantic Search

### Embedding Service

**File**: `backend/services/embedding_service.py`

Multi-provider embedding with automatic model detection:

```python
class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]: ...

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]: ...


class OllamaEmbedding(EmbeddingProvider):
    """Ollama-based embeddings with automatic model detection."""

    EMBEDDING_MODELS = [
        "nomic-embed-text",
        "mxbai-embed-large",
        "all-minilm",
    ]

    FALLBACK_MODELS = [
        "llama3.2:3b",
        "mistral:7b",
    ]


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI text-embedding-3-small/large."""


class CohereEmbedding(EmbeddingProvider):
    """Cohere embed-english-v3.0."""
```

**Usage**:
```python
from backend.services.embedding_service import get_embedding_service

service = get_embedding_service(provider="ollama")
embedding = await service.embed("Character description text")
similarity = service.cosine_similarity(embedding_a, embedding_b)
```

### Embedding Index Service

**File**: `backend/services/embedding_index_service.py`

Manages embedding lifecycle:

```python
class EmbeddingIndexService:
    async def index_node(self, node: Node) -> bool:
        """Generate and store embedding for a node."""

    async def reindex_all(self) -> Dict[str, int]:
        """Rebuild all embeddings."""

    async def get_stale_nodes(self) -> List[Node]:
        """Find nodes needing reindexing."""
```

### Knowledge Router

**File**: `backend/services/knowledge_router.py`

Query classification and context assembly:

```python
class KnowledgeRouter:
    async def route_query(self, query: str) -> RoutedContext:
        """
        Classify query → Retrieve from graph → Assemble context.

        Returns token-counted context block with priorities.
        """
```

---

## Phase 3: Narrative Extraction

### Narrative Ontology

**File**: `backend/graph/narrative_ontology.py`

17 edge types for story physics:

```python
class NarrativeEdgeType(Enum):
    # Goal-Obstacle-Conflict
    MOTIVATES = "MOTIVATES"
    HINDERS = "HINDERS"
    CAUSES = "CAUSES"

    # Character Dynamics
    CHALLENGES = "CHALLENGES"
    KNOWS = "KNOWS"
    CONTRADICTS = "CONTRADICTS"

    # Narrative Threading
    FORESHADOWS = "FORESHADOWS"
    CALLBACKS = "CALLBACKS"

    # Basic Relationships
    LOCATED_IN = "LOCATED_IN"
    OWNS = "OWNS"
    PART_OF = "PART_OF"
    HAS_TRAIT = "HAS_TRAIT"
    LOVES = "LOVES"
    HATES = "HATES"
    ALLIES_WITH = "ALLIES_WITH"
    CONFLICTS_WITH = "CONFLICTS_WITH"
    REVEALS = "REVEALS"
    CUSTOM = "CUSTOM"
```

### Narrative Extractor

**File**: `backend/graph/narrative_extractor.py`

LLM-based extraction with context awareness:

```python
class NarrativeExtractor:
    def __init__(
        self,
        graph_service: KnowledgeGraphService,
        ollama_url: str = "http://localhost:11434/api/chat",
        model: str = "llama3.2:3b"
    ): ...

    async def extract_from_scene(
        self,
        scene_content: str,
        scene_id: str,
        current_beat: str = "Unknown"
    ) -> Dict[str, Any]:
        """
        Extract entities and relationships from scene text.

        Returns:
        - entities: New characters, locations, objects, events
        - relationships: Narrative edges between entities
        - flaw_challenge: Whether protagonist's flaw was tested
        - beat_alignment: Whether scene matches expected beat
        """

    async def merge_to_graph(self, extraction: Dict) -> Dict[str, Any]:
        """Merge extraction results into the knowledge graph."""
```

**Extraction Prompt**:
```
Extract from this scene:
- What MOTIVATES characters?
- What HINDERS their goals?
- Is the protagonist's fatal flaw being CHALLENGED?
- What does this FORESHADOW?
- What earlier events does it CALLBACK to?
```

---

## Phase 4: Tiered Verification

### Verification Service

**File**: `backend/services/verification_service.py`

Three-tier consistency checking:

```python
class VerificationTier(Enum):
    FAST = "fast"      # <500ms - inline
    MEDIUM = "medium"  # 2-5s - background
    SLOW = "slow"      # 5-30s - on-demand


class VerificationService:
    async def run_fast_checks(
        self, content: str, context: Dict
    ) -> VerificationResult:
        """
        FAST tier checks:
        - Character alive/dead status
        - Known fact contradictions
        - Required callbacks present
        """

    async def run_medium_checks(
        self, content: str, context: Dict
    ) -> VerificationResult:
        """
        MEDIUM tier checks:
        - Flaw challenge gap detection
        - Beat alignment
        - Timeline consistency
        """

    async def run_slow_checks(
        self, content: str, context: Dict
    ) -> VerificationResult:
        """
        SLOW tier checks:
        - Full LLM semantic analysis
        - Delegates to GraphHealthService if available
        """
```

### Scene Writer Integration

**File**: `backend/services/scene_writer_service.py`

Verification integrated into generation:

```python
class SceneWriterService:
    async def verify_scene(
        self,
        content: str,
        scene_context: Optional[Dict] = None,
        run_background: bool = True
    ) -> Dict[str, Any]:
        """Run verification on generated content."""

    async def generate_and_verify(
        self,
        scene_id: str,
        scaffold: Scaffold,
        ...
    ) -> SceneGenerationResult:
        """Generate scene with automatic verification."""
```

### Frontend Notification

**File**: `frontend/src/lib/components/VerificationNotification.svelte`

Toast notifications for verification issues:
- Severity-based styling (critical/warning/info)
- Dismiss individual or all
- Actionable suggestions
- Slide-in animation

**File**: `frontend/src/lib/stores.js`

Verification state management:
```javascript
export const verificationNotifications = writable([]);
export const verificationSettings = persistentWritable('wf_verification_settings', {
  enabled: true,
  autoVerifyOnGenerate: true,
  showNotifications: true,
  minSeverity: 'warning'
});

export function addVerificationNotification(notification) { ... }
export function dismissVerificationNotification(id) { ... }
export function processVerificationResult(result, sceneId) { ... }
```

---

## Phase 5: Analysis & Enhancement

### Graph Analyzer

**File**: `backend/graph/graph_analysis.py`

Advanced narrative analysis:

```python
class GraphAnalyzer:
    def detect_communities(self) -> Dict[str, List[str]]:
        """
        Louvain community detection on character nodes.
        Returns: {"primary_cast": [...], "secondary_cast": [...], ...}
        """

    def find_bridge_characters(self, top_k: int = 5) -> List[Dict]:
        """
        Betweenness centrality to find connecting characters.
        Returns role inference: protagonist/major/supporting/minor
        """

    def calculate_tension(self) -> Dict[str, Any]:
        """
        Tension = weighted sum of:
        - HINDERS edges (weight 2.0)
        - FORESHADOWS edges (weight 1.5)
        - CONTRADICTS edges (weight 3.0)
        - CHALLENGES edges (weight 2.5)

        Returns: score (0-1), level, indicators, recommendation
        """

    def analyze_pacing(self) -> Dict[str, Any]:
        """
        Categorize edges as action/setup/resolution.
        Returns: pacing type, ratios, recommendation
        """

    def get_narrative_summary(self) -> Dict[str, Any]:
        """
        Comprehensive analysis combining all methods.
        """
```

### Settings Integration

**File**: `backend/services/settings_service.py`

Graph configuration schema:

```python
"graph": {
    "edge_types": {
        "MOTIVATES": True,
        "HINDERS": True,
        "CHALLENGES": True,
        "FORESHADOWS": True,
        "CALLBACKS": True,
        "CONTRADICTS": False,  # Experimental
    },
    "extraction_triggers": {
        "on_manuscript_promote": True,
        "before_foreman_chat": True,
        "periodic_minutes": 0,
    },
    "verification_level": "standard",  # minimal | standard | thorough
    "embedding_provider": "ollama",    # ollama | openai | cohere | none
}
```

Validation rules added:
```python
"graph.verification_level": {"type": str, "choices": ["minimal", "standard", "thorough"]},
"graph.embedding_provider": {"type": str, "choices": ["ollama", "openai", "cohere", "none"]},
"graph.extraction_triggers.periodic_minutes": {"type": int, "min": 0, "max": 60},
```

---

## API Reference

### Graph Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/analysis/communities` | GET | Detect character communities |
| `/graph/analysis/bridges?top_k=5` | GET | Find bridge characters |
| `/graph/analysis/tension` | GET | Calculate narrative tension |
| `/graph/analysis/pacing` | GET | Analyze pacing |
| `/graph/analysis/summary` | GET | Comprehensive analysis |

### Semantic Search Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/semantic-search` | POST | Search by semantic similarity |
| `/graph/ego-network/{entity}` | GET | Get k-hop neighborhood |
| `/graph/reindex-embeddings` | POST | Rebuild embedding index |
| `/graph/embedding-status` | GET | Check index health |
| `/graph/knowledge-query` | POST | Full GraphRAG pipeline |

### Narrative Extraction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/extract-narrative` | POST | Extract from text |
| `/graph/extract-from-file` | POST | Extract from file path |
| `/graph/edge-types` | GET | List available edge types |

### Verification Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verification/run` | POST | Run checks by tier |
| `/verification/run-all` | POST | Run all tiers |
| `/verification/notifications` | GET | Get pending notifications |

### Settings Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/settings/graph` | GET | Get all graph settings |
| `/settings/graph` | PUT | Update graph settings |

---

## File Structure

```
backend/
├── graph/
│   ├── schema.py              # SQLAlchemy models (Node, Edge)
│   ├── graph_service.py       # Core graph operations
│   ├── graph_analysis.py      # Community detection, tension, pacing
│   ├── narrative_ontology.py  # Edge type definitions
│   └── narrative_extractor.py # LLM-based extraction
├── services/
│   ├── embedding_service.py        # Multi-provider embeddings
│   ├── embedding_index_service.py  # Embedding lifecycle
│   ├── knowledge_router.py         # Query classification & routing
│   ├── verification_service.py     # Tiered consistency checks
│   ├── scene_writer_service.py     # Generation with verification
│   └── settings_service.py         # Graph settings schema
└── api.py                          # All endpoints

frontend/
└── src/lib/
    ├── components/
    │   └── VerificationNotification.svelte
    └── stores.js  # Verification store section
```

---

## Testing

All Python files pass syntax verification:

```bash
python3 -m py_compile backend/graph/schema.py
python3 -m py_compile backend/graph/graph_service.py
python3 -m py_compile backend/graph/graph_analysis.py
python3 -m py_compile backend/graph/narrative_ontology.py
python3 -m py_compile backend/graph/narrative_extractor.py
python3 -m py_compile backend/services/embedding_service.py
python3 -m py_compile backend/services/embedding_index_service.py
python3 -m py_compile backend/services/knowledge_router.py
python3 -m py_compile backend/services/verification_service.py
python3 -m py_compile backend/api.py
```

### Manual Testing

**Community detection**:
```bash
curl http://localhost:8000/graph/analysis/communities
```

**Tension calculation**:
```bash
curl http://localhost:8000/graph/analysis/tension
```

**Full verification**:
```bash
curl -X POST http://localhost:8000/verification/run-all \
  -H "Content-Type: application/json" \
  -d '{"content": "Scene text here...", "tier": "fast"}'
```

---

## Dependencies

**Python** (requirements.txt):
- `numpy>=1.24.0` - Cosine similarity calculations
- `networkx` - Graph algorithms (already in project)
- `httpx` - Async HTTP for Ollama/OpenAI/Cohere
- `aiohttp` - Async HTTP for LLM extraction

**Environment Variables**:
- `OPENAI_API_KEY` - For OpenAI embeddings (optional)
- `COHERE_API_KEY` - For Cohere embeddings (optional)

---

## Future Work

### Not Yet Implemented
- Frontend tension indicator component
- Settings UI for graph configuration (SettingsGraph.svelte)
- WebSocket for real-time tension updates
- Embedding dimension normalization for provider switching

### Deferred
- `frontend/src/routes/+page.svelte` - VerificationNotification integration
- `backend/ingestor.py` - Narrative prompt updates

---

*Implementation: December 2025*
