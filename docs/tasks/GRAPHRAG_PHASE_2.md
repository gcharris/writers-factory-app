# GraphRAG Phase 2: Semantic Search & Embeddings

**Parent Spec**: `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md`
**Status**: Ready for Implementation
**Priority**: High - Enables semantic retrieval
**Depends On**: Phase 1 (Complete)

---

## Goal

Implement semantic search capabilities for the knowledge graph:
1. Embedding service with Ollama-first strategy
2. Graph node embedding storage and indexing
3. Knowledge router orchestrating the full retrieval pipeline

---

## Deliverables

### 1. EmbeddingService

**File**: `backend/services/embedding_service.py`

Implement multi-provider embedding service with Ollama-first strategy.

**Key Requirements**:
- `EmbeddingProvider` abstract base class
- `OllamaEmbedding` provider with auto-detection:
  - Check for `nomic-embed-text` first (preferred)
  - Fall back to `llama3.2:3b` (already installed per CLAUDE.md)
  - Last resort: any available Ollama model
- `OpenAIEmbedding` provider (optional, for quality boost)
- `EmbeddingService` unified interface with:
  - `embed(text)` - Single text embedding
  - `embed_batch(texts)` - Batch embedding
  - `cosine_similarity(a, b)` - Similarity calculation
  - `find_similar(query, candidates, top_k)` - Search

**Code Template** (from main spec Part 2.1):

```python
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import httpx
import asyncio
import logging

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass


class OllamaEmbedding(EmbeddingProvider):
    """Ollama-based embeddings with automatic model detection."""

    def __init__(self, model: str = "auto", base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._model = model
        self._detected_model: Optional[str] = None

    async def _detect_best_model(self) -> str:
        """Detect best available Ollama embedding model."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            if "nomic-embed-text" in model_names:
                return "nomic-embed-text"
            if "nomic-embed-text:latest" in model_names:
                return "nomic-embed-text:latest"
            if "llama3.2:3b" in model_names:
                logger.info("Using llama3.2:3b for embeddings (nomic-embed-text not found)")
                return "llama3.2:3b"
            if models:
                logger.warning(f"Using {models[0]['name']} for embeddings")
                return models[0]["name"]

            raise RuntimeError("No Ollama models available")
        except Exception as e:
            logger.error(f"Model detection failed: {e}")
            return "llama3.2:3b"

    async def _get_model(self) -> str:
        if self._model != "auto":
            return self._model
        if self._detected_model is None:
            self._detected_model = await self._detect_best_model()
        return self._detected_model

    async def embed(self, text: str) -> List[float]:
        model = await self._get_model()
        response = await self.client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "prompt": text}
        )
        response.raise_for_status()
        return response.json()["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)
```

**Testing**:
```python
# Test embedding service
service = EmbeddingService(provider="ollama")
emb = await service.embed("Mickey is the protagonist")
print(f"Embedding dimension: {len(emb)}")

# Test similarity
emb1 = await service.embed("Mickey is brave")
emb2 = await service.embed("The protagonist shows courage")
emb3 = await service.embed("The weather is sunny")
print(f"Similar: {service.cosine_similarity(emb1, emb2):.3f}")  # Should be high
print(f"Different: {service.cosine_similarity(emb1, emb3):.3f}")  # Should be low
```

---

### 2. Schema Updates

**File**: `backend/graph/schema.py` (modify)

Add embedding columns to Node model:

```python
class Node(Base):
    __tablename__ = "nodes"

    # ... existing columns ...

    # NEW: Embedding storage
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    embedding_model = Column(String, nullable=True)  # Track which model
    embedding_updated_at = Column(DateTime, nullable=True)
```

**Migration**: After modifying schema, run:
```bash
# If using alembic
alembic revision --autogenerate -m "Add embedding columns"
alembic upgrade head

# Or recreate dev database
rm backend/graph.db
# Reingest content
```

---

### 3. EmbeddingIndexService

**File**: `backend/services/embedding_index_service.py`

Manage embedding lifecycle for graph nodes.

**Key Requirements**:
- `index_node(node_id)` - Generate and store embedding for single node
- `reindex_all(batch_size=50)` - Re-index all nodes (use after provider change)
- `semantic_search(query, node_types, top_k)` - Search nodes by similarity

**Code Template** (from main spec Part 2.3):

```python
class EmbeddingIndexService:
    """Maintains embeddings for all graph nodes."""

    def __init__(self, graph_service, embedding_service):
        self.graph = graph_service
        self.embeddings = embedding_service

    async def index_node(self, node_id: int) -> bool:
        """Generate and store embedding for a node."""
        node = self.graph.get_node(node_id)
        if not node:
            return False

        text = f"{node.node_type}: {node.name}. {node.description or ''}"
        embedding = await self.embeddings.embed(text)

        node.embedding = embedding
        node.embedding_model = self.embeddings.provider_name
        node.embedding_updated_at = datetime.now(timezone.utc)
        self.graph.session.commit()
        return True

    async def semantic_search(
        self,
        query: str,
        node_types: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[tuple[Node, float]]:
        """Search graph nodes by semantic similarity."""
        query_embedding = await self.embeddings.embed(query)

        nodes = self.graph.get_all_nodes()
        if node_types:
            nodes = [n for n in nodes if n.node_type in node_types]

        nodes_with_embeddings = [n for n in nodes if n.embedding]

        results = []
        for node in nodes_with_embeddings:
            sim = self.embeddings.cosine_similarity(query_embedding, node.embedding)
            results.append((node, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
```

---

### 4. KnowledgeRouter

**File**: `backend/services/knowledge_router.py`

Orchestrate the full query → classification → retrieval → assembly pipeline.

**Key Requirements**:
- Takes user query and returns assembled context
- Uses QueryClassifier (Phase 1) for routing
- Combines graph traversal + semantic search
- Passes to ContextAssembler (Phase 1) for token-aware assembly

```python
class KnowledgeRouter:
    """
    Orchestrates knowledge retrieval pipeline.

    Query → Classify → Retrieve (graph + semantic + story bible) → Assemble
    """

    def __init__(
        self,
        classifier: QueryClassifier,
        graph_service: KnowledgeGraphService,
        embedding_index: EmbeddingIndexService,
        story_bible: StoryBibleService,
        assembler: ContextAssembler
    ):
        self.classifier = classifier
        self.graph = graph_service
        self.embedding_index = embedding_index
        self.story_bible = story_bible
        self.assembler = assembler

    async def route(self, query: str, model: str = "claude-sonnet-4-5") -> dict:
        """
        Route a query through the full pipeline.

        Returns:
            {
                "context": "assembled context string",
                "classification": ClassifiedQuery,
                "retrieval_sources": [...],
                "token_count": int
            }
        """
        # 1. Classify
        classified = self.classifier.classify(query)

        # 2. Retrieve based on classification
        graph_context = await self._retrieve_from_graph(classified)
        story_bible_context = await self._retrieve_from_story_bible(classified)
        semantic_results = await self._semantic_retrieve(query, classified)

        # 3. Merge semantic results into graph context
        for node, score in semantic_results:
            if node.name not in graph_context.get("characters", {}):
                graph_context.setdefault("semantic_matches", []).append({
                    "name": node.name,
                    "type": node.node_type,
                    "description": node.description,
                    "relevance": score
                })

        # 4. Assemble within token budget
        context = self.assembler.assemble(
            classified_query=classified,
            graph_context=graph_context,
            story_bible_context=story_bible_context,
            kb_context=[],  # Could integrate Foreman KB here
        )

        return {
            "context": context,
            "classification": classified,
            "retrieval_sources": classified.sources,
            "token_count": self.assembler._count_tokens(context)
        }

    async def _retrieve_from_graph(self, classified: ClassifiedQuery) -> dict:
        """Retrieve graph context using k-hop ego network."""
        result = {"characters": {}, "edges": []}

        for entity in classified.entities:
            node = self.graph.find_node_by_name(entity)
            if node:
                # Get k-hop subgraph (ego network)
                import networkx as nx
                G = self.graph.to_networkx()
                if node.name in G:
                    ego = nx.ego_graph(G, node.name, radius=2)
                    result["characters"][entity] = {
                        "description": node.description,
                        "neighbors": list(ego.nodes())
                    }

        return result

    async def _semantic_retrieve(
        self,
        query: str,
        classified: ClassifiedQuery
    ) -> List[tuple]:
        """Semantic search if beneficial for query type."""
        if not classified.requires_semantic:
            return []

        return await self.embedding_index.semantic_search(
            query=query,
            top_k=5
        )
```

---

### 5. Graph Service Updates

**File**: `backend/graph/graph_service.py` (modify)

Add NetworkX integration for ego_graph extraction:

```python
def to_networkx(self) -> nx.DiGraph:
    """Convert graph to NetworkX for advanced algorithms."""
    G = nx.DiGraph()

    for node in self.get_all_nodes():
        G.add_node(node.name, **{
            "type": node.node_type,
            "description": node.description
        })

    for edge in self.get_all_edges():
        source = self.get_node(edge.source_id)
        target = self.get_node(edge.target_id)
        if source and target:
            G.add_edge(source.name, target.name, **{
                "relation": edge.relation_type,
                "description": edge.description
            })

    return G

def ego_graph(self, entity_name: str, radius: int = 2) -> dict:
    """
    Get k-hop ego network around an entity.

    Returns subgraph as dict with nodes and edges.
    """
    import networkx as nx
    G = self.to_networkx()

    if entity_name not in G:
        return {"nodes": [], "edges": []}

    ego = nx.ego_graph(G, entity_name, radius=radius)

    return {
        "center": entity_name,
        "nodes": [{"name": n, **G.nodes[n]} for n in ego.nodes()],
        "edges": [
            {"source": u, "target": v, **G.edges[u, v]}
            for u, v in ego.edges()
        ]
    }
```

---

### 6. API Endpoints

**File**: `backend/api.py` (modify)

Add new endpoints:

```python
@app.post("/graph/semantic-search", summary="Semantic search across graph")
async def semantic_search(
    query: str,
    node_types: Optional[List[str]] = None,
    top_k: int = 10
):
    """
    Search graph nodes by semantic similarity.
    """
    index_service = get_embedding_index_service()
    results = await index_service.semantic_search(
        query=query,
        node_types=node_types,
        top_k=top_k
    )
    return {
        "query": query,
        "results": [
            {"name": node.name, "type": node.node_type, "score": score}
            for node, score in results
        ]
    }


@app.get("/graph/ego-network/{entity_name}", summary="Get k-hop subgraph")
async def get_ego_network(
    entity_name: str,
    radius: int = 2
):
    """
    Get k-hop ego network around an entity.
    """
    graph_service = KnowledgeGraphService()
    return graph_service.ego_graph(entity_name, radius=radius)


@app.post("/graph/reindex-embeddings", summary="Reindex all embeddings")
async def reindex_embeddings():
    """
    Regenerate embeddings for all nodes.
    Use after changing embedding provider.
    """
    index_service = get_embedding_index_service()
    result = await index_service.reindex_all()
    return result
```

---

## Implementation Order

1. **EmbeddingService** - No dependencies, pure async
2. **Schema updates** - Add embedding columns
3. **EmbeddingIndexService** - Depends on both above
4. **Graph service updates** - Add NetworkX methods
5. **KnowledgeRouter** - Orchestrates everything
6. **API endpoints** - Wire it all together

---

## Files Checklist

**Create**:
- [ ] `backend/services/embedding_service.py`
- [ ] `backend/services/embedding_index_service.py`
- [ ] `backend/services/knowledge_router.py`

**Modify**:
- [ ] `backend/graph/schema.py` - Add embedding columns
- [ ] `backend/graph/graph_service.py` - Add ego_graph, to_networkx
- [ ] `backend/api.py` - Add 3 new endpoints

**Optional**:
- [ ] `requirements.txt` - Add numpy if not present

---

## Verification

### Manual Testing

1. **Embedding Service**:
```bash
python3 -c "
import asyncio
from backend.services.embedding_service import get_embedding_service

async def test():
    svc = get_embedding_service()
    emb = await svc.embed('Mickey is the protagonist')
    print(f'Dimension: {len(emb)}')
    print(f'First 5 values: {emb[:5]}')

asyncio.run(test())
"
```

2. **Semantic Search**:
```bash
curl -X POST http://localhost:8000/graph/semantic-search \
  -H "Content-Type: application/json" \
  -d '{"query": "character with trust issues"}'
```

3. **Ego Network**:
```bash
curl http://localhost:8000/graph/ego-network/Mickey?radius=2
```

---

## Success Criteria

- [ ] Embedding service auto-detects Ollama model
- [ ] Embeddings stored in Node.embedding column
- [ ] Semantic search returns relevant nodes (similarity > 0.5)
- [ ] Ego network returns connected subgraph
- [ ] KnowledgeRouter integrates with Phase 1 ContextAssembler
- [ ] All endpoints return expected JSON structure

---

## Notes for Implementing Agent

1. **numpy dependency** - May need to add to requirements.txt for cosine similarity
2. **Ollama must be running** - Test with `curl http://localhost:11434/api/tags`
3. **Initial indexing** - After schema update, run `/graph/reindex-embeddings` once
4. **Token considerations** - Embedding dimension varies by model (768-3072)

---

## Handoff

When complete, provide:
1. Branch name and commit hash
2. List of files created/modified
3. Sample semantic search results
4. Any deviations from spec
