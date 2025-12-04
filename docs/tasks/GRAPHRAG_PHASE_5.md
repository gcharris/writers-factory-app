# GraphRAG Phase 5: Enhancements

**Parent Spec**: `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md`
**Status**: Ready for Implementation (Optional Enhancements)
**Priority**: Low - Polish and optimization
**Depends On**: Phases 1-4 (All core functionality)

---

## Goal

Implement optional enhancements to the GraphRAG system:
1. Cloud embedding providers (OpenAI, etc.)
2. Community detection for plot clustering
3. Tension calculation based on graph structure
4. Full settings panel integration

---

## Deliverables

### 1. Cloud Embedding Providers

**File**: `backend/services/embedding_service.py` (modify)

Add optional cloud providers for higher quality embeddings.

**OpenAI Provider**:

```python
class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI embeddings (optional, for quality boost)."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small"
    ):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        self._dimension = 1536 if "small" in model else 3072

    async def embed(self, text: str) -> List[float]:
        response = await self.client.post(
            "/embeddings",
            json={"model": self.model, "input": text}
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.post(
            "/embeddings",
            json={"model": self.model, "input": texts}
        )
        response.raise_for_status()
        data = response.json()["data"]
        return [d["embedding"] for d in sorted(data, key=lambda x: x["index"])]

    @property
    def dimension(self) -> int:
        return self._dimension


class AnthropicEmbedding(EmbeddingProvider):
    """Anthropic embeddings (future - Claude embeddings not yet available)."""
    pass  # Placeholder for future


class CohereEmbedding(EmbeddingProvider):
    """Cohere embeddings (alternative cloud option)."""

    def __init__(
        self,
        api_key: str,
        model: str = "embed-english-v3.0"
    ):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.cohere.ai/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )

    async def embed(self, text: str) -> List[float]:
        response = await self.client.post(
            "/embed",
            json={
                "model": self.model,
                "texts": [text],
                "input_type": "search_document"
            }
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.post(
            "/embed",
            json={
                "model": self.model,
                "texts": texts,
                "input_type": "search_document"
            }
        )
        response.raise_for_status()
        return response.json()["embeddings"]
```

**Update EmbeddingService factory**:

```python
def _create_provider(self, provider: str, **kwargs) -> EmbeddingProvider:
    if provider == "ollama":
        return OllamaEmbedding(
            model=kwargs.get("model", "auto"),
            base_url=kwargs.get("base_url", "http://localhost:11434")
        )
    elif provider == "openai":
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required")
        return OpenAIEmbedding(
            api_key=api_key,
            model=kwargs.get("model", "text-embedding-3-small")
        )
    elif provider == "cohere":
        api_key = kwargs.get("api_key") or os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("Cohere API key required")
        return CohereEmbedding(
            api_key=api_key,
            model=kwargs.get("model", "embed-english-v3.0")
        )
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
```

---

### 2. Community Detection

**File**: `backend/graph/graph_analysis.py`

Add community detection for plot clustering and subplot identification.

```python
import networkx as nx
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """
    Advanced graph analysis for narrative structure.

    Uses NetworkX algorithms to detect:
    - Character communities (plot threads)
    - Key bridge characters
    - Narrative tension points
    """

    def __init__(self, graph_service):
        self.graph = graph_service

    def detect_communities(self) -> Dict[str, List[str]]:
        """
        Detect character communities using Louvain algorithm.

        Communities often represent:
        - Subplots
        - Character factions
        - Thematic clusters
        """
        G = self.graph.to_networkx()

        # Filter to character nodes only
        character_nodes = [n for n, d in G.nodes(data=True)
                         if d.get("type") == "CHARACTER"]
        H = G.subgraph(character_nodes).copy()

        if len(H.nodes()) < 2:
            return {"main": list(H.nodes())}

        try:
            # Louvain community detection
            from networkx.algorithms.community import louvain_communities
            communities = louvain_communities(H.to_undirected())

            result = {}
            for i, community in enumerate(communities):
                result[f"community_{i}"] = list(community)

            return result
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return {"main": list(H.nodes())}

    def find_bridge_characters(self) -> List[Dict[str, Any]]:
        """
        Find characters that bridge multiple communities.

        These are often:
        - Protagonists (connect all threads)
        - Plot catalysts (bring groups together)
        - Antagonists (create conflict between groups)
        """
        G = self.graph.to_networkx()

        bridges = []
        try:
            # Betweenness centrality identifies bridge nodes
            centrality = nx.betweenness_centrality(G)

            for node, score in sorted(centrality.items(), key=lambda x: -x[1])[:5]:
                node_data = G.nodes[node]
                if node_data.get("type") == "CHARACTER":
                    bridges.append({
                        "name": node,
                        "centrality": score,
                        "type": node_data.get("type"),
                        "description": node_data.get("description")
                    })
        except Exception as e:
            logger.warning(f"Bridge detection failed: {e}")

        return bridges

    def calculate_tension(self) -> Dict[str, Any]:
        """
        Calculate narrative tension based on graph structure.

        Tension indicators:
        - Number of active HINDERS edges
        - Unresolved FORESHADOWS
        - CONTRADICTS edges
        - Conflict density between communities
        """
        G = self.graph.to_networkx()

        # Count tension-creating edges
        hinders_count = sum(1 for _, _, d in G.edges(data=True)
                          if d.get("relation") == "HINDERS")
        foreshadows_count = sum(1 for _, _, d in G.edges(data=True)
                               if d.get("relation") == "FORESHADOWS")
        contradicts_count = sum(1 for _, _, d in G.edges(data=True)
                               if d.get("relation") == "CONTRADICTS")

        # Calculate tension score (simplified)
        total_edges = G.number_of_edges() or 1
        tension_score = (hinders_count * 2 + foreshadows_count + contradicts_count * 3) / total_edges

        # Normalize to 0-1 range
        tension_score = min(tension_score, 1.0)

        return {
            "tension_score": round(tension_score, 2),
            "level": "high" if tension_score > 0.6 else "medium" if tension_score > 0.3 else "low",
            "indicators": {
                "active_obstacles": hinders_count,
                "unresolved_foreshadowing": foreshadows_count,
                "contradictions": contradicts_count
            },
            "total_edges": total_edges
        }

    def get_narrative_summary(self) -> Dict[str, Any]:
        """
        Generate a narrative structure summary.
        """
        communities = self.detect_communities()
        bridges = self.find_bridge_characters()
        tension = self.calculate_tension()

        return {
            "communities": communities,
            "community_count": len(communities),
            "bridge_characters": bridges,
            "tension": tension,
            "graph_stats": {
                "total_nodes": self.graph.get_node_count(),
                "total_edges": self.graph.get_edge_count(),
                "character_count": len(self.graph.get_nodes_by_type("CHARACTER")),
                "location_count": len(self.graph.get_nodes_by_type("LOCATION"))
            }
        }


# Factory function
def get_graph_analyzer():
    from backend.graph.graph_service import KnowledgeGraphService
    return GraphAnalyzer(KnowledgeGraphService())
```

---

### 3. Settings Panel Integration

**File**: `backend/services/settings_service.py` (modify)

Add graph-specific settings schema:

```python
# Add to settings schema

GRAPH_SETTINGS_SCHEMA = {
    "edge_types": {
        "type": "object",
        "description": "Enable/disable narrative edge types",
        "properties": {
            "MOTIVATES": {"type": "boolean", "default": True},
            "HINDERS": {"type": "boolean", "default": True},
            "CHALLENGES": {"type": "boolean", "default": True},
            "CAUSES": {"type": "boolean", "default": True},
            "FORESHADOWS": {"type": "boolean", "default": True},
            "CALLBACKS": {"type": "boolean", "default": True},
            "KNOWS": {"type": "boolean", "default": True},
            "CONTRADICTS": {"type": "boolean", "default": False}
        }
    },
    "extraction_triggers": {
        "type": "object",
        "description": "When to trigger graph extraction",
        "properties": {
            "on_manuscript_promote": {"type": "boolean", "default": True},
            "before_foreman_chat": {"type": "boolean", "default": True},
            "periodic_minutes": {"type": "integer", "default": 0, "min": 0, "max": 60}
        }
    },
    "verification_level": {
        "type": "string",
        "enum": ["minimal", "standard", "thorough"],
        "default": "standard",
        "description": "Level of verification to run"
    },
    "embedding_provider": {
        "type": "string",
        "enum": ["ollama", "openai", "cohere"],
        "default": "ollama",
        "description": "Embedding service provider"
    }
}


# Add getter methods
def get_graph_settings() -> Dict[str, Any]:
    """Get all graph-related settings."""
    return {
        "edge_types": {
            edge_type: settings_service.get(f"graph.edge_types.{edge_type}", default)
            for edge_type, default in {
                "MOTIVATES": True, "HINDERS": True, "CHALLENGES": True,
                "CAUSES": True, "FORESHADOWS": True, "CALLBACKS": True,
                "KNOWS": True, "CONTRADICTS": False
            }.items()
        },
        "extraction_triggers": {
            "on_manuscript_promote": settings_service.get(
                "graph.extraction_triggers.on_manuscript_promote", True
            ),
            "before_foreman_chat": settings_service.get(
                "graph.extraction_triggers.before_foreman_chat", True
            ),
            "periodic_minutes": settings_service.get(
                "graph.extraction_triggers.periodic_minutes", 0
            )
        },
        "verification_level": settings_service.get(
            "graph.verification_level", "standard"
        ),
        "embedding_provider": settings_service.get(
            "graph.embedding_provider", "ollama"
        )
    }
```

---

### 4. API Endpoints

**File**: `backend/api.py` (modify)

Add analysis and settings endpoints:

```python
@app.get("/graph/analysis/communities", summary="Detect character communities")
async def get_communities():
    """
    Detect character communities (subplots/factions).
    """
    from backend.graph.graph_analysis import get_graph_analyzer
    analyzer = get_graph_analyzer()
    return analyzer.detect_communities()


@app.get("/graph/analysis/bridges", summary="Find bridge characters")
async def get_bridge_characters():
    """
    Find characters that connect multiple communities.
    """
    from backend.graph.graph_analysis import get_graph_analyzer
    analyzer = get_graph_analyzer()
    return {"bridge_characters": analyzer.find_bridge_characters()}


@app.get("/graph/analysis/tension", summary="Calculate narrative tension")
async def get_tension():
    """
    Calculate current narrative tension based on graph structure.
    """
    from backend.graph.graph_analysis import get_graph_analyzer
    analyzer = get_graph_analyzer()
    return analyzer.calculate_tension()


@app.get("/graph/analysis/summary", summary="Get narrative structure summary")
async def get_narrative_summary():
    """
    Get full narrative structure analysis.
    """
    from backend.graph.graph_analysis import get_graph_analyzer
    analyzer = get_graph_analyzer()
    return analyzer.get_narrative_summary()


@app.get("/settings/graph", summary="Get graph settings")
async def get_graph_settings():
    """
    Get all graph-related settings.
    """
    from backend.services.settings_service import get_graph_settings
    return get_graph_settings()


@app.put("/settings/graph", summary="Update graph settings")
async def update_graph_settings(settings: dict):
    """
    Update graph-related settings.
    """
    from backend.services.settings_service import settings_service

    updated = {}
    for key, value in settings.items():
        full_key = f"graph.{key}" if not key.startswith("graph.") else key
        settings_service.set(full_key, value)
        updated[key] = value

    return {"updated": updated}
```

---

### 5. Frontend Settings Component Updates

**File**: `frontend/src/lib/components/SettingsGraph.svelte` (modify if exists)

Add cloud provider configuration:

```svelte
<!-- Add to existing SettingsGraph.svelte -->

<script>
    // ... existing code ...

    // Embedding provider options
    const embeddingProviders = [
        { value: 'ollama', label: 'Ollama (Local)', cost: 'Free' },
        { value: 'openai', label: 'OpenAI', cost: '~$0.02/1M tokens' },
        { value: 'cohere', label: 'Cohere', cost: '~$0.10/1M tokens' }
    ];

    let selectedProvider = 'ollama';
</script>

<!-- Add embedding provider section -->
<div class="setting-group">
    <h4>Embedding Provider</h4>
    <p class="text-sm text-gray-500 mb-2">
        Choose where to generate text embeddings for semantic search.
    </p>

    <select
        bind:value={selectedProvider}
        on:change={() => updateSetting('embedding_provider', selectedProvider)}
        class="select select-bordered w-full"
    >
        {#each embeddingProviders as provider}
            <option value={provider.value}>
                {provider.label} ({provider.cost})
            </option>
        {/each}
    </select>

    {#if selectedProvider !== 'ollama'}
        <div class="alert alert-warning mt-2">
            <span>⚠️ Cloud providers require API keys configured in Settings → Keys</span>
        </div>
    {/if}
</div>

<!-- Add tension indicator -->
<div class="setting-group mt-4">
    <h4>Narrative Tension</h4>
    <div class="flex items-center gap-2">
        <div class="w-full bg-gray-200 rounded-full h-4">
            <div
                class="h-4 rounded-full transition-all"
                class:bg-green-500={tensionLevel === 'low'}
                class:bg-yellow-500={tensionLevel === 'medium'}
                class:bg-red-500={tensionLevel === 'high'}
                style="width: {tensionScore * 100}%"
            ></div>
        </div>
        <span class="text-sm font-medium capitalize">{tensionLevel}</span>
    </div>
    <p class="text-xs text-gray-500 mt-1">
        Based on active obstacles, unresolved foreshadowing, and contradictions
    </p>
</div>
```

---

## Implementation Order

1. **Cloud embedding providers** - Extend embedding_service.py
2. **Graph analysis** - New graph_analysis.py
3. **Settings schema updates** - Extend settings_service.py
4. **API endpoints** - Wire everything
5. **Frontend updates** - Settings panel enhancements

---

## Files Checklist

**Create**:
- [ ] `backend/graph/graph_analysis.py`

**Modify**:
- [ ] `backend/services/embedding_service.py` - Add cloud providers
- [ ] `backend/services/settings_service.py` - Add graph settings schema
- [ ] `backend/api.py` - Add 6 new endpoints
- [ ] `frontend/src/lib/components/SettingsGraph.svelte` - Add provider selection

---

## Verification

### Manual Testing

1. **Community detection**:
```bash
curl http://localhost:8000/graph/analysis/communities
```

2. **Tension calculation**:
```bash
curl http://localhost:8000/graph/analysis/tension
```

3. **Full summary**:
```bash
curl http://localhost:8000/graph/analysis/summary
```

4. **Change embedding provider**:
```bash
curl -X PUT http://localhost:8000/settings/graph \
  -H "Content-Type: application/json" \
  -d '{"embedding_provider": "openai"}'
```

---

## Success Criteria

- [ ] Cloud embedding providers work with API keys
- [ ] Community detection identifies character groups
- [ ] Bridge characters are correctly identified
- [ ] Tension score reflects graph structure
- [ ] Settings persist across restarts
- [ ] Frontend displays tension indicator

---

## Notes for Implementing Agent

1. **Louvain algorithm** - Requires NetworkX 2.6+
2. **API keys** - Cloud providers need keys in .env
3. **Dimension mismatch** - Different providers have different embedding dimensions; may need reindexing when switching
4. **Cost awareness** - Cloud embeddings cost money; default to Ollama

---

## Future Enhancements (Not in Scope)

- WebSocket for real-time tension updates
- Embedding dimension normalization for provider switching
- Voice consistency analysis (requires reference samples)
- Automated pacing recommendations
- Visual graph explorer component

---

## Handoff

When complete, provide:
1. Branch name and commit hash
2. List of files created/modified
3. Sample community detection and tension calculation
4. Any deviations from spec
