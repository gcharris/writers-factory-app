# GraphRAG: The Living Brain of Writers Factory

**From Context Flatness to Narrative Intelligence**

---

## The Problem We Solved

### Context Flatness in Traditional RAG

When we first built Writers Factory, we used standard Retrieval-Augmented Generation (RAG) - the industry standard approach where you embed text chunks and retrieve them by semantic similarity.

It worked. But it had a fundamental flaw.

When a writer asked "What happens next?", the system retrieved passages that were *lexically* similar to the query. It missed crucial *causal* links that are semantically distant but narratively connected:

- A gun mentioned in Act 1 that must fire in Act 3
- A character's fatal flaw that should affect their decision in Chapter 12
- A world rule established early that constrains possibilities later

The LLM would "hallucinate" continuity, reinventing facts or dropping subplots because it couldn't "see" the structural relationships between story elements.

### The Insight: Stories Have Physics

The breakthrough came from recognizing that novels aren't just collections of text - they have **narrative physics**:

- **Characters have goals** that motivate their actions
- **Obstacles hinder** those goals, creating conflict
- **Events cause** other events in chains
- **Earlier scenes foreshadow** later payoffs
- **Later scenes callback** to earlier setups

Standard RAG treats stories as bags of words. GraphRAG treats them as systems of relationships.

---

## The Architecture

### From Chunks to Subgraphs

Instead of retrieving isolated text chunks, GraphRAG retrieves **connected subgraphs**.

When the Foreman queries the system, we traverse the graph to find not just the target node (e.g., "Character A") but its neighbors:

```
Character A → HAS_GOAL → Escape → BLOCKED_BY → Guard B
                ↓
            HAS_FLAW → Trust Issues → CHALLENGES → In Scene 7
```

The LLM receives a "pre-connected puzzle" ensuring every generated sentence honors the existing web of relationships.

### The Five Phases

We implemented GraphRAG in five distinct phases, each building on the previous:

| Phase | Name | Focus |
|-------|------|-------|
| **Phase 1** | Foundation | Schema, NetworkX integration, ego graphs |
| **Phase 2** | Semantic Search | Embeddings, cosine similarity, vector queries |
| **Phase 3** | Narrative Extraction | Story-physics edges, LLM-based extraction |
| **Phase 4** | Tiered Verification | Fast/Medium/Slow consistency checks |
| **Phase 5** | Analysis & Enhancement | Community detection, tension calculation |

---

## Phase 1: Foundation

### The Problem

We needed a graph structure that could:
- Store narrative entities (characters, locations, events, themes)
- Capture relationships between them
- Integrate with our existing SQLite/NetworkX stack
- Support efficient traversal queries

### The Solution

**Schema Extension** (`backend/graph/schema.py`):
```python
# Added embedding storage for semantic search
embedding = Column(JSON, nullable=True)
embedding_model = Column(String, nullable=True)
embedding_updated_at = Column(DateTime, nullable=True)
```

**Core Methods** (`backend/graph/graph_service.py`):
- `to_networkx()` - Convert SQLite graph to NetworkX for algorithms
- `ego_graph(entity, radius)` - Get k-hop neighborhood around an entity
- `get_nodes_by_type()` - Filter by CHARACTER, LOCATION, etc.
- `get_edges_by_type()` - Filter by MOTIVATES, HINDERS, etc.

### The Result

The knowledge graph became queryable in relationship terms, not just keyword terms.

---

## Phase 2: Semantic Search

### The Problem

Even with a graph, we needed to find relevant context quickly. If a writer asks about "the confrontation at the bridge", we need to find graph nodes semantically related to that concept.

### The Solution

**Multi-Provider Embedding Service** (`backend/services/embedding_service.py`):

```python
class EmbeddingService:
    """
    Providers:
    - Ollama (nomic-embed-text, llama3.2:3b fallback)
    - OpenAI (text-embedding-3-small)
    - Cohere (embed-english-v3.0)
    """
```

The service auto-detects the best available Ollama model, falling back gracefully when dedicated embedding models aren't installed.

**Index Management** (`backend/services/embedding_index_service.py`):
- Automatic embedding of new nodes
- Background reindexing
- Stale embedding detection

**Knowledge Router** (`backend/services/knowledge_router.py`):
- Classifies queries by type (character, world, theme, plot)
- Routes to appropriate knowledge sources
- Assembles context with token awareness

### The Result

Queries like "How should Marcus react to betrayal?" now retrieve:
1. Marcus's ego graph (2-hop relationships)
2. Semantically similar nodes about betrayal, trust, conflict
3. Relevant Story Bible entries

---

## Phase 3: Narrative Extraction

### The Problem

The graph needed to understand **story physics** - not just that two characters are connected, but *how* they're connected narratively.

### The Solution

**Narrative Ontology** (`backend/graph/narrative_ontology.py`):

17 edge types capturing the mechanics of story:

| Category | Edge Types |
|----------|------------|
| **Goal-Obstacle-Conflict** | MOTIVATES, HINDERS, CAUSES |
| **Character Dynamics** | CHALLENGES, KNOWS, CONTRADICTS |
| **Narrative Threading** | FORESHADOWS, CALLBACKS |
| **Basic Relationships** | LOCATED_IN, OWNS, LOVES, HATES, etc. |

**LLM Extraction** (`backend/graph/narrative_extractor.py`):

```python
NARRATIVE_EXTRACTION_PROMPT = """
Extract from this scene:
- What MOTIVATES characters?
- What HINDERS their goals?
- Is the protagonist's fatal flaw being CHALLENGED?
- What does this FORESHADOW?
- What earlier events does it CALLBACK to?
"""
```

The extractor runs on manuscript promotion - when a scene moves from "working" to "manuscript" status, we extract its narrative structure.

### The Result

The graph now understands that:
- Mickey's pride (fatal flaw) → CHALLENGES → his decision in the warehouse scene
- The locked box in Chapter 1 → FORESHADOWS → the revelation in Chapter 15
- The argument with Sarah → CAUSES → Mickey's isolation in Act 2

---

## Phase 4: Tiered Verification

### The Problem

Narrative consistency checking can be slow (LLM-based analysis) or fast (graph traversal). Different situations call for different approaches.

### The Solution

**Three Verification Tiers** (`backend/services/verification_service.py`):

| Tier | Speed | Checks | Use Case |
|------|-------|--------|----------|
| **FAST** | <500ms | Dead character detection, contradiction edges, missing callbacks | Inline during generation |
| **MEDIUM** | 2-5s | Flaw challenge gaps, beat alignment, timeline consistency | Background after generation |
| **SLOW** | 5-30s | Full LLM semantic analysis | On-demand deep check |

**Example FAST Check**:
```python
def _check_character_status(self, content: str) -> List[VerificationIssue]:
    """Check if dead characters are acting in scenes."""
    death_edges = self.graph.get_edges_by_type("DIES_IN")
    # Cross-reference with characters mentioned in content
```

**Notification System** (`frontend/src/lib/components/VerificationNotification.svelte`):
- Toast notifications for detected issues
- Severity levels (critical, warning, info)
- Actionable suggestions

### The Result

Writers get immediate feedback on narrative consistency without waiting for slow LLM analysis.

---

## Phase 5: Analysis & Enhancement

### The Problem

Beyond verification, we wanted the graph to provide **narrative insights** - understanding story structure at a higher level.

### The Solution

**Graph Analyzer** (`backend/graph/graph_analysis.py`):

**Community Detection**:
```python
def detect_communities(self) -> Dict[str, List[str]]:
    """
    Uses Louvain algorithm to find character clusters.

    Communities often represent:
    - Subplots
    - Character factions
    - Thematic clusters
    """
```

**Bridge Characters**:
```python
def find_bridge_characters(self) -> List[Dict]:
    """
    Identifies characters connecting communities.

    These are often:
    - Protagonists (connect all threads)
    - Plot catalysts (bring groups together)
    - Antagonists (create conflict between groups)
    """
```

**Tension Calculation**:
```python
def calculate_tension(self) -> Dict:
    """
    Tension = f(HINDERS, FORESHADOWS, CONTRADICTS, CHALLENGES)

    Returns score (0-1), level, and actionable recommendations.
    """
```

**Pacing Analysis**:
```python
def analyze_pacing(self) -> Dict:
    """
    Categorizes edges as action/setup/resolution.

    Returns:
    - Pacing type (fast/slow/balanced/concluding)
    - Ratios by category
    - Recommendations
    """
```

### The Result

The Foreman can now tell writers:
- "Your tension is low - the protagonist's flaw hasn't been challenged in 3 scenes"
- "Character A is a bridge between your two main subplots"
- "Your pacing is setup-heavy - consider accelerating toward payoffs"

---

## API Reference

### Graph Analysis Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/analysis/communities` | GET | Detect character communities |
| `/graph/analysis/bridges` | GET | Find bridge characters |
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

### Narrative Extraction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/extract-narrative` | POST | Extract from text |
| `/graph/extract-from-file` | POST | Extract from file |
| `/graph/edge-types` | GET | List available edge types |

### Verification Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/verification/run` | POST | Run checks by tier |
| `/verification/run-all` | POST | Run all tiers |
| `/verification/notifications` | GET | Get pending notifications |

---

## Settings

Graph behavior is configurable via the settings service:

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

---

## The Philosophy

### From Passive to Active

Standard RAG is passive - it waits for queries and returns matches.

GraphRAG is active:
- It **infers** implied information (if Character A is in the Forest, and the Forest contains Wolves, danger exists)
- It **predicts** plot requirements (a gun in Act 1 must fire in Act 3)
- It **enforces** consistency (a dead character can't act in later scenes)

### Structure Before Freedom

This aligns with Writers Factory's core philosophy. The graph enforces structural integrity so the creative LLM can focus on prose, voice, and artistry.

The writer provides vision. The graph provides memory. The LLM provides speed.

---

## For Students

### Engineering Lessons

This implementation demonstrates several software engineering principles:

1. **Incremental Enhancement**: We built in phases, each adding capability without breaking existing function
2. **Graceful Degradation**: If embeddings aren't available, graph traversal still works
3. **Separation of Concerns**: Extraction, storage, retrieval, and analysis are independent services
4. **Configuration Over Code**: Edge types and verification levels are settings, not hardcoded

### The Creative-Technical Balance

GraphRAG is infrastructure for creativity. It doesn't constrain the writer - it amplifies their vision by ensuring consistency at scale.

This is the core thesis of the course: **We are not just writing a novel; we are engineering a synthetic cognitive system.**

---

## Implementation Details

### Branch: `nifty-antonelli`

All GraphRAG code was implemented in a single development session across 5 phases:

| Commit | Phase | Lines Added |
|--------|-------|-------------|
| `7a598a6` | Phase 2 | ~600 |
| `ecb0601` | Phase 3 | ~500 |
| `05b23fa` | Phase 4 | ~700 |
| `bad6586` | Phase 5 | ~730 |

### Files Created

```
backend/
├── graph/
│   ├── graph_analysis.py      # Community detection, tension, pacing
│   ├── narrative_extractor.py # LLM-based extraction
│   └── narrative_ontology.py  # Edge type definitions
├── services/
│   ├── embedding_service.py   # Multi-provider embeddings
│   ├── embedding_index_service.py
│   ├── knowledge_router.py    # Query classification & routing
│   └── verification_service.py # Tiered consistency checks

frontend/
└── src/lib/
    ├── components/
    │   └── VerificationNotification.svelte
    └── stores.js  # Verification store section
```

### Testing

All Python files pass syntax verification:
```bash
python3 -m py_compile backend/graph/*.py
python3 -m py_compile backend/services/*.py
python3 -m py_compile backend/api.py
```

---

## What's Next

### Not Yet Implemented

- Frontend tension indicator component
- Settings UI for graph configuration
- WebSocket for real-time tension updates
- Embedding dimension normalization for provider switching

### Future Possibilities

- Voice consistency analysis via embeddings
- Automated pacing recommendations
- Visual graph explorer component
- Multi-novel universe graphs

---

## Conclusion

GraphRAG transforms Writers Factory from a text completion tool into a **narrative operating system**.

The graph doesn't just remember your story - it understands its structure. It ensures that every scene honors the web of relationships you've built. It catches contradictions before they become plot holes. It calculates tension and suggests pacing adjustments.

This is what we mean by "engineering creativity" - using software architecture to amplify human vision, not replace it.

---

*Implementation: December 2025*
*Authors: Claude Code (Opus 4.5) + Human collaboration*
*Course: AI and the One-Week Novel - Skoltech ISP 2026*
