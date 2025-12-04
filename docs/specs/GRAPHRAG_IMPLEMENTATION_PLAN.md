# GraphRAG Enhancement Implementation Plan

**Version**: 1.1
**Status**: Approved for Implementation
**Date**: December 2025
**Authors**: Claude Code (Opus 4.5) + Human collaboration
**Prerequisites**: UNIVERSAL_AGENT_INSTRUCTION_ARCHITECTURE.md, RAG_IMPLEMENTATION.md

---

## Executive Summary

This document specifies the implementation plan for enhancing Writers Factory's knowledge graph with GraphRAG capabilities. The enhancement focuses on **smarter processing** rather than infrastructure changes, building on the existing SQLite + NetworkX + JSON stack.

### Key Decisions (Confirmed)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Database** | Keep SQLite + NetworkX | Sufficient for novel-scale graphs (~500 nodes) |
| **Embeddings** | Ollama-first, cloud optional | Leverages existing infrastructure |
| **Extraction Trigger** | Manuscript promotion + pre-chat | "Working → Manuscript" workflow |
| **Verification** | Tiered (fast/medium/slow) | Balance UX speed with thoroughness |
| **Ontology** | Fixed core + configurable | Settings panel for customization |

---

## Part 0: Integration Matrix

This section clarifies how new components integrate with existing services.

### 0.1 Component Integration Map

| New Component | Existing File | Integration Type | Description |
|---------------|---------------|------------------|-------------|
| `QueryClassifier` | `foreman.py` | **Calls into** | Called before each Foreman chat to classify user intent and route to appropriate knowledge sources |
| `ContextAssembler` | `foreman_kb_service.py` | **Replaces** | Replaces `get_context_for_foreman()` with token-aware, priority-based assembly |
| `ManuscriptService` | `consolidator_service.py` | **Triggers** | Promotion calls `consolidator.extract_from_file()` for graph extraction |
| `NarrativeExtractor` | `ner_extractor.py` | **Extends** | Adds narrative edge types to existing NER extraction; keeps spaCy for entity detection |
| `EmbeddingService` | `graph_service.py` | **Adds to** | Adds `embedding` column to Node schema; adds `semantic_search()` method |
| `EmbeddingIndexService` | `graph_service.py` | **Wraps** | Manages embedding lifecycle; calls graph_service for node CRUD |
| `KnowledgeRouter` | `foreman.py` | **Called by** | Orchestrates query → classification → retrieval → assembly pipeline |
| `VerificationService` | `graph_health_service.py` | **Wraps** | Adds tiered execution around existing health checks |

### 0.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WRITE PATH                                      │
│                                                                              │
│   Working/scene.md                                                           │
│         │                                                                    │
│         ▼ (User: "finalize this scene")                                     │
│   ┌─────────────────┐                                                        │
│   │ ManuscriptService│ ──────────────────────────────────────┐              │
│   └─────────────────┘                                        │              │
│         │                                                    │              │
│         ▼ (promote)                                          ▼              │
│   Manuscript/Act_1/Ch_1/scene.md              ┌─────────────────────────┐   │
│         │                                     │ ConsolidatorService     │   │
│         │                                     │ (extract_from_file)     │   │
│         │                                     └─────────────────────────┘   │
│         │                                                    │              │
│         │                                                    ▼              │
│         │                                     ┌─────────────────────────┐   │
│         │                                     │ NarrativeExtractor      │   │
│         │                                     │ (LLM: llama3.2:3b)      │   │
│         │                                     └─────────────────────────┘   │
│         │                                                    │              │
│         │                                                    ▼              │
│         │                                     ┌─────────────────────────┐   │
│         │                                     │ KnowledgeGraphService   │   │
│         │                                     │ (SQLite + NetworkX)     │   │
│         │                                     └─────────────────────────┘   │
│         │                                                    │              │
│         │                                                    ▼              │
│         │                                     ┌─────────────────────────┐   │
│         │                                     │ EmbeddingIndexService   │   │
│         │                                     │ (index new nodes)       │   │
│         │                                     └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              READ PATH                                       │
│                                                                              │
│   User Query: "How should Mickey react to the betrayal?"                    │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │ QueryClassifier │ ──► QueryType.CHARACTER_DEEP + QueryType.RELATIONSHIP │
│   └─────────────────┘     entities: [Mickey]                                │
│         │                 sources: [graph, story_bible]                      │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │ KnowledgeRouter │                                                        │
│   └─────────────────┘                                                        │
│         │                                                                    │
│         ├──► Graph: ego_graph(Mickey, k=2) + semantic_search("betrayal")   │
│         │                                                                    │
│         ├──► Story Bible: Character/Mickey.md (Fatal Flaw, The Lie)        │
│         │                                                                    │
│         └──► Foreman KB: recent decisions about Mickey                      │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │ContextAssembler │ ──► Token-counted context block                       │
│   └─────────────────┘     (Priority: char_core > relationships > beat)      │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │    Foreman      │ ──► LLM generates response with rich context          │
│   └─────────────────┘                                                        │
│         │                                                                    │
│         ▼                                                                    │
│   ┌─────────────────┐                                                        │
│   │VerificationSvc  │ ──► FAST checks inline, MEDIUM checks background      │
│   └─────────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 0.3 Embedding Model Strategy

**Primary Model**: `nomic-embed-text` via Ollama
- Size: ~274MB download
- RAM: ~1GB during inference
- Dimension: 768
- Quality: Good for semantic similarity

**Fallback Model**: `llama3.2:3b` via Ollama `/api/embeddings`
- Already installed per CLAUDE.md requirements
- Dimension: 3072 (larger)
- Quality: Acceptable, not optimized for embeddings

**Cloud Option**: OpenAI `text-embedding-3-small`
- Dimension: 1536
- Quality: Excellent
- Cost: ~$0.02 per 1M tokens (negligible at novel scale)

**Initialization Logic**:

```python
# In embedding_service.py

async def _detect_best_ollama_model(self) -> str:
    """Detect best available Ollama embedding model."""
    try:
        # Check for dedicated embedding model
        response = await self.client.get(f"{self.base_url}/api/tags")
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]

        # Prefer dedicated embedding model
        if "nomic-embed-text" in model_names:
            return "nomic-embed-text"
        if "nomic-embed-text:latest" in model_names:
            return "nomic-embed-text:latest"

        # Fall back to llama3.2 (required by CLAUDE.md)
        if "llama3.2:3b" in model_names:
            logger.info("Using llama3.2:3b for embeddings (nomic-embed-text not found)")
            return "llama3.2:3b"

        # Last resort: any available model
        if models:
            logger.warning(f"Using {models[0]['name']} for embeddings (not recommended)")
            return models[0]["name"]

        raise RuntimeError("No Ollama models available for embeddings")
    except Exception as e:
        logger.error(f"Failed to detect Ollama models: {e}")
        raise

class OllamaEmbedding(EmbeddingProvider):
    """Ollama-based embeddings with automatic model detection."""

    def __init__(self, model: str = "auto", base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._model = model
        self._detected_model: Optional[str] = None

    async def _get_model(self) -> str:
        """Get model name, detecting if needed."""
        if self._model != "auto":
            return self._model
        if self._detected_model is None:
            self._detected_model = await self._detect_best_ollama_model()
        return self._detected_model
```

### 0.4 Settings Integration Points

New settings under `settings.graph.*`:

| Setting Key | Type | Default | Used By |
|-------------|------|---------|---------|
| `graph.edge_types.MOTIVATES` | boolean | true | NarrativeExtractor |
| `graph.edge_types.HINDERS` | boolean | true | NarrativeExtractor |
| `graph.edge_types.CHALLENGES` | boolean | true | NarrativeExtractor |
| `graph.edge_types.FORESHADOWS` | boolean | true | NarrativeExtractor |
| `graph.edge_types.CALLBACKS` | boolean | true | NarrativeExtractor |
| `graph.edge_types.CAUSES` | boolean | true | NarrativeExtractor |
| `graph.edge_types.CONTRADICTS` | boolean | false | NarrativeExtractor |
| `graph.extraction_triggers.on_manuscript_promote` | boolean | true | ManuscriptService |
| `graph.extraction_triggers.before_foreman_chat` | boolean | true | Foreman |
| `graph.extraction_triggers.periodic_minutes` | integer | 0 | Background task |
| `graph.verification_level` | enum | "standard" | VerificationService |
| `graph.embedding_provider` | enum | "ollama" | EmbeddingService |

---

## Part 1: Working Files → Manuscript Architecture

### 1.1 Directory Structure

```
content/
├── Working/                    # NEW: Active drafts, frequent saves
│   ├── Chapter_04_Scene_02.md  # Writer's current work
│   ├── Chapter_04_Scene_03.md
│   └── .working_meta.json      # Tracks working file state
│
├── Manuscript/                 # NEW: Finalized, graph-extracted content
│   ├── Act_1/
│   │   ├── Chapter_01/
│   │   │   ├── Scene_01.md
│   │   │   └── Scene_02.md
│   │   └── Chapter_02/
│   │       └── Scene_01.md
│   └── .manuscript_meta.json   # Tracks extraction state per file
│
├── Story Bible/                # Existing: Structure artifacts
├── Characters/                 # Existing: Character profiles
└── World Bible/                # Existing: World-building
```

### 1.2 File Metadata Schema

```python
# .working_meta.json
{
    "files": {
        "Chapter_04_Scene_02.md": {
            "created_at": "2025-12-04T10:00:00Z",
            "last_saved": "2025-12-04T14:32:00Z",
            "save_count": 47,
            "word_count": 2340,
            "target_location": "Act_2/Chapter_04/Scene_02.md",
            "beat_alignment": "Midpoint",
            "status": "drafting"  # drafting | reviewing | ready_to_promote
        }
    }
}

# .manuscript_meta.json
{
    "files": {
        "Act_2/Chapter_04/Scene_02.md": {
            "promoted_at": "2025-12-04T15:00:00Z",
            "promoted_from": "Working/Chapter_04_Scene_02.md",
            "extraction_status": "complete",
            "extracted_at": "2025-12-04T15:00:05Z",
            "nodes_created": 3,
            "edges_created": 7,
            "word_count": 2340,
            "version": 1
        }
    }
}
```

### 1.3 Promotion Service

```python
# backend/services/manuscript_service.py

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil

class ManuscriptService:
    """
    Manages the Working → Manuscript promotion workflow.

    Responsibilities:
    - Track working file state
    - Promote files to manuscript directory
    - Trigger graph extraction on promotion
    - Maintain version history
    """

    def __init__(self, content_path: Path):
        self.content_path = content_path
        self.working_dir = content_path / "Working"
        self.manuscript_dir = content_path / "Manuscript"
        self._ensure_directories()

    def _ensure_directories(self):
        """Create directories if they don't exist."""
        self.working_dir.mkdir(exist_ok=True)
        self.manuscript_dir.mkdir(exist_ok=True)

    async def promote_to_manuscript(
        self,
        working_file: str,
        target_path: str,
        trigger_extraction: bool = True
    ) -> dict:
        """
        Promote a working file to the manuscript.

        Args:
            working_file: Filename in Working/ directory
            target_path: Relative path in Manuscript/ (e.g., "Act_2/Chapter_04/Scene_02.md")
            trigger_extraction: Whether to run graph extraction immediately

        Returns:
            Promotion result with extraction status
        """
        source = self.working_dir / working_file
        target = self.manuscript_dir / target_path

        if not source.exists():
            raise FileNotFoundError(f"Working file not found: {working_file}")

        # Create target directory structure
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy file (keep working copy for now)
        content = source.read_text(encoding='utf-8')
        target.write_text(content, encoding='utf-8')

        # Update metadata
        await self._update_manuscript_meta(target_path, working_file)

        result = {
            "promoted": True,
            "source": str(source),
            "target": str(target),
            "promoted_at": datetime.now(timezone.utc).isoformat(),
        }

        # Trigger extraction
        if trigger_extraction:
            from backend.services.consolidator_service import get_consolidator
            consolidator = get_consolidator()
            extraction_result = await consolidator.extract_from_file(target)
            result["extraction"] = extraction_result

        return result

    async def get_working_files(self) -> list[dict]:
        """List all files in Working/ with metadata."""
        meta = self._load_working_meta()
        files = []

        for f in self.working_dir.glob("*.md"):
            file_meta = meta.get("files", {}).get(f.name, {})
            files.append({
                "name": f.name,
                "path": str(f),
                "word_count": len(f.read_text().split()),
                **file_meta
            })

        return files

    async def get_manuscript_structure(self) -> dict:
        """Get hierarchical manuscript structure."""
        structure = {"acts": {}}

        for f in self.manuscript_dir.rglob("*.md"):
            rel_path = f.relative_to(self.manuscript_dir)
            parts = rel_path.parts

            # Build nested structure
            current = structure["acts"]
            for part in parts[:-1]:  # All but filename
                if part not in current:
                    current[part] = {"scenes": [], "subdirs": {}}
                current = current[part]["subdirs"]

            # Add file
            parent_key = parts[-2] if len(parts) > 1 else "root"
            if parent_key not in current:
                current[parent_key] = {"scenes": [], "subdirs": {}}
            current[parent_key]["scenes"].append({
                "name": f.stem,
                "path": str(rel_path),
            })

        return structure

    def _load_working_meta(self) -> dict:
        meta_file = self.working_dir / ".working_meta.json"
        if meta_file.exists():
            return json.loads(meta_file.read_text())
        return {"files": {}}

    async def _update_manuscript_meta(self, target_path: str, source_file: str):
        meta_file = self.manuscript_dir / ".manuscript_meta.json"
        meta = json.loads(meta_file.read_text()) if meta_file.exists() else {"files": {}}

        meta["files"][target_path] = {
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "promoted_from": f"Working/{source_file}",
            "extraction_status": "pending",
            "version": meta["files"].get(target_path, {}).get("version", 0) + 1
        }

        meta_file.write_text(json.dumps(meta, indent=2))
```

### 1.4 API Endpoints

```python
# In api.py - New endpoints

@app.post("/manuscript/promote")
async def promote_to_manuscript(request: PromoteRequest):
    """
    Promote a working file to the manuscript.

    Triggers graph extraction automatically.
    """
    service = get_manuscript_service()
    result = await service.promote_to_manuscript(
        working_file=request.working_file,
        target_path=request.target_path,
        trigger_extraction=request.extract
    )
    return result

@app.get("/manuscript/working")
async def list_working_files():
    """List all files in the Working directory."""
    service = get_manuscript_service()
    return {"files": await service.get_working_files()}

@app.get("/manuscript/structure")
async def get_manuscript_structure():
    """Get hierarchical manuscript structure."""
    service = get_manuscript_service()
    return await service.get_manuscript_structure()

@app.post("/manuscript/promote-via-chat")
async def promote_via_agent(request: AgentPromoteRequest):
    """
    Handle agent command: "Let's finalize this scene"

    Parses natural language to identify scene and promote it.
    """
    # Parse the command to identify which scene
    # Could be explicit: "Finalize Chapter 4 Scene 2"
    # Or contextual: "We're done with this scene" (uses active context)
    pass
```

### 1.5 Agent Command Integration

The Foreman should recognize promotion commands:

```python
# In foreman.py - Add to action handlers

PROMOTION_PATTERNS = [
    r"finalize (this )?scene",
    r"save (this )?to manuscript",
    r"we'?re done (with this scene)?",
    r"promote (this )?scene",
    r"move to manuscript",
]

async def _handle_promotion_intent(self, message: str) -> Optional[dict]:
    """
    Detect and handle manuscript promotion requests.

    Returns action result if promotion detected, None otherwise.
    """
    if not any(re.search(p, message.lower()) for p in PROMOTION_PATTERNS):
        return None

    # Get active context (which scene is user working on)
    active_file = self.session_state.get("active_file")
    if not active_file:
        return {
            "type": "clarification_needed",
            "message": "Which scene would you like to finalize? I don't see an active working file."
        }

    # Confirm with user
    return {
        "type": "promotion_confirmation",
        "file": active_file,
        "suggested_target": self._infer_manuscript_path(active_file),
        "message": f"Ready to finalize **{active_file}** and add it to the manuscript. This will update the knowledge graph with any new story facts. Proceed?"
    }
```

---

## Part 2: Embedding Service

### 2.1 Service Architecture

```python
# backend/services/embedding_service.py

from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import httpx
import asyncio

class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
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

            # Prefer dedicated embedding model
            if "nomic-embed-text" in model_names:
                return "nomic-embed-text"
            if "nomic-embed-text:latest" in model_names:
                return "nomic-embed-text:latest"

            # Fall back to llama3.2 (required by CLAUDE.md)
            if "llama3.2:3b" in model_names:
                logger.info("Using llama3.2:3b for embeddings (nomic-embed-text not found)")
                return "llama3.2:3b"

            # Last resort: any available model
            if models:
                logger.warning(f"Using {models[0]['name']} for embeddings")
                return models[0]["name"]

            raise RuntimeError("No Ollama models available")
        except Exception as e:
            logger.error(f"Model detection failed: {e}")
            return "llama3.2:3b"  # Safe fallback

    async def _get_model(self) -> str:
        """Get model name, detecting if 'auto'."""
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
        # Ollama doesn't have native batch, so we parallelize
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI embeddings (optional, for quality boost)."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )

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


class EmbeddingService:
    """
    Unified embedding service with provider abstraction.

    Default: Ollama (local, free)
    Optional: Cloud providers for quality boost
    """

    def __init__(self, provider: str = "ollama", **kwargs):
        self.provider_name = provider
        self.provider = self._create_provider(provider, **kwargs)
        self._cache: dict[str, List[float]] = {}

    def _create_provider(self, provider: str, **kwargs) -> EmbeddingProvider:
        if provider == "ollama":
            return OllamaEmbedding(
                model=kwargs.get("model", "nomic-embed-text"),
                base_url=kwargs.get("base_url", "http://localhost:11434")
            )
        elif provider == "openai":
            return OpenAIEmbedding(
                api_key=kwargs["api_key"],
                model=kwargs.get("model", "text-embedding-3-small")
            )
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    async def embed(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding with optional caching."""
        cache_key = f"{self.provider_name}:{hash(text)}"

        if use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        embedding = await self.provider.embed(text)

        if use_cache:
            self._cache[cache_key] = embedding

        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return await self.provider.embed_batch(texts)

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        a_np = np.array(a)
        b_np = np.array(b)
        return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))

    async def find_similar(
        self,
        query: str,
        candidates: List[tuple[str, str]],  # [(id, text), ...]
        top_k: int = 5
    ) -> List[tuple[str, float]]:
        """
        Find most similar candidates to query.

        Returns: [(id, similarity_score), ...] sorted by similarity
        """
        query_embedding = await self.embed(query)

        # Embed all candidates
        candidate_texts = [c[1] for c in candidates]
        candidate_embeddings = await self.embed_batch(candidate_texts)

        # Calculate similarities
        similarities = []
        for (cid, _), emb in zip(candidates, candidate_embeddings):
            sim = self.cosine_similarity(query_embedding, emb)
            similarities.append((cid, sim))

        # Sort and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


# Singleton
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        # Load provider preference from settings
        from backend.services.settings_service import get_settings_service
        settings = get_settings_service()
        provider = settings.get("embedding_provider", "ollama")
        _embedding_service = EmbeddingService(provider=provider)
    return _embedding_service
```

### 2.2 Graph Node Embedding Storage

```python
# Update to schema.py

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    node_type = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    source = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, onupdate=lambda: datetime.now(timezone.utc))

    # NEW: Embedding storage
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    embedding_model = Column(String, nullable=True)  # Track which model generated it
    embedding_updated_at = Column(DateTime, nullable=True)
```

### 2.3 Embedding Index Service

```python
# backend/services/embedding_index_service.py

class EmbeddingIndexService:
    """
    Maintains embeddings for all graph nodes.

    Responsibilities:
    - Index new nodes on creation
    - Re-index on description update
    - Semantic search across graph
    """

    def __init__(self, graph_service, embedding_service):
        self.graph = graph_service
        self.embeddings = embedding_service

    async def index_node(self, node_id: int) -> bool:
        """Generate and store embedding for a node."""
        node = self.graph.get_node(node_id)
        if not node:
            return False

        # Create embedding text from node properties
        text = f"{node.node_type}: {node.name}. {node.description or ''}"
        embedding = await self.embeddings.embed(text)

        # Store in database
        node.embedding = embedding
        node.embedding_model = self.embeddings.provider_name
        node.embedding_updated_at = datetime.now(timezone.utc)
        self.graph.session.commit()

        return True

    async def reindex_all(self, batch_size: int = 50) -> dict:
        """Re-index all nodes. Use after changing embedding provider."""
        nodes = self.graph.get_all_nodes()
        indexed = 0
        failed = 0

        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i+batch_size]
            texts = [f"{n.node_type}: {n.name}. {n.description or ''}" for n in batch]

            try:
                embeddings = await self.embeddings.embed_batch(texts)
                for node, emb in zip(batch, embeddings):
                    node.embedding = emb
                    node.embedding_model = self.embeddings.provider_name
                    node.embedding_updated_at = datetime.now(timezone.utc)
                self.graph.session.commit()
                indexed += len(batch)
            except Exception as e:
                logger.error(f"Failed to index batch: {e}")
                failed += len(batch)

        return {"indexed": indexed, "failed": failed, "total": len(nodes)}

    async def semantic_search(
        self,
        query: str,
        node_types: Optional[List[str]] = None,
        top_k: int = 10
    ) -> List[tuple[Node, float]]:
        """
        Search graph nodes by semantic similarity.

        Args:
            query: Natural language query
            node_types: Filter to specific types (CHARACTER, LOCATION, etc.)
            top_k: Number of results to return

        Returns:
            List of (node, similarity_score) tuples
        """
        query_embedding = await self.embeddings.embed(query)

        # Get candidate nodes
        nodes = self.graph.get_all_nodes()
        if node_types:
            nodes = [n for n in nodes if n.node_type in node_types]

        # Filter to nodes with embeddings
        nodes_with_embeddings = [n for n in nodes if n.embedding]

        # Calculate similarities
        results = []
        for node in nodes_with_embeddings:
            sim = self.embeddings.cosine_similarity(query_embedding, node.embedding)
            results.append((node, sim))

        # Sort and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
```

---

## Part 3: Query Classification & Routing

### 3.1 Query Classifier

```python
# backend/services/query_classifier.py

from enum import Enum
from dataclasses import dataclass
import re
from typing import List, Set, Optional

class QueryType(Enum):
    CHARACTER_LOOKUP = "character_lookup"      # "Who is Mickey?"
    CHARACTER_DEEP = "character_deep"          # "What's Mickey's fatal flaw?"
    PLOT_STATUS = "plot_status"                # "Where are we in the beat sheet?"
    RELATIONSHIP = "relationship"              # "How does Mickey feel about Noni?"
    WORLD_RULES = "world_rules"                # "How does the magic system work?"
    WRITING_TECHNIQUE = "writing_technique"    # "How do I write compressed prose?"
    SCENE_CONTEXT = "scene_context"            # "What happened in the previous scene?"
    CONTRADICTION_CHECK = "contradiction"      # "Does this contradict anything?"
    HYBRID = "hybrid"                          # Complex queries needing multiple sources

@dataclass
class ClassifiedQuery:
    query_type: QueryType
    entities: List[str]          # Detected entity mentions
    keywords: List[str]          # Extracted keywords for search
    sources: List[str]           # Recommended sources: ['graph', 'story_bible', 'notebooklm', 'manuscript']
    confidence: float            # 0.0-1.0 classification confidence
    requires_semantic: bool      # Whether semantic search is beneficial

class QueryClassifier:
    """
    Classifies user queries to determine optimal routing strategy.

    Uses pattern matching + entity detection.
    Falls back to HYBRID for ambiguous queries.
    """

    def __init__(self, known_entities: Set[str]):
        self.known_entities = {e.lower() for e in known_entities}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for classification."""
        self.patterns = {
            QueryType.CHARACTER_LOOKUP: [
                r"who is (\w+)",
                r"tell me about (\w+)",
                r"what do (we|I) know about (\w+)",
            ],
            QueryType.CHARACTER_DEEP: [
                r"(\w+)'?s? (fatal )?flaw",
                r"(\w+)'?s? (the )?lie",
                r"(\w+)'?s? arc",
                r"(\w+)'?s? true character",
                r"(\w+)'?s? motivation",
            ],
            QueryType.PLOT_STATUS: [
                r"what beat",
                r"where (are we|is the story)",
                r"beat sheet",
                r"plot progress",
                r"current scene",
                r"what happens next",
            ],
            QueryType.RELATIONSHIP: [
                r"relationship between",
                r"how does (\w+) feel about (\w+)",
                r"(\w+) and (\w+)",
                r"connection between",
            ],
            QueryType.WORLD_RULES: [
                r"how does .* work",
                r"rules? (of|for)",
                r"world.?building",
                r"magic system",
                r"can .* do",
            ],
            QueryType.WRITING_TECHNIQUE: [
                r"how (do|should) I write",
                r"writing (advice|tips|technique)",
                r"voice",
                r"prose style",
                r"show.?don'?t.?tell",
            ],
            QueryType.SCENE_CONTEXT: [
                r"previous scene",
                r"last scene",
                r"what happened (before|earlier)",
                r"recap",
            ],
            QueryType.CONTRADICTION_CHECK: [
                r"contradict",
                r"consistent",
                r"conflict with",
                r"does this work",
                r"make sense",
            ],
        }

    def classify(self, query: str) -> ClassifiedQuery:
        """Classify a query and determine routing strategy."""
        query_lower = query.lower()
        entities = self._extract_entities(query)
        keywords = self._extract_keywords(query)

        # Try pattern matching
        for query_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return ClassifiedQuery(
                        query_type=query_type,
                        entities=entities,
                        keywords=keywords,
                        sources=self._sources_for_type(query_type),
                        confidence=0.9,
                        requires_semantic=query_type in (
                            QueryType.CHARACTER_DEEP,
                            QueryType.WORLD_RULES,
                            QueryType.HYBRID
                        )
                    )

        # Entity-based classification
        if entities:
            if len(entities) > 1:
                return ClassifiedQuery(
                    query_type=QueryType.RELATIONSHIP,
                    entities=entities,
                    keywords=keywords,
                    sources=['graph'],
                    confidence=0.7,
                    requires_semantic=False
                )
            else:
                return ClassifiedQuery(
                    query_type=QueryType.CHARACTER_LOOKUP,
                    entities=entities,
                    keywords=keywords,
                    sources=['graph', 'story_bible'],
                    confidence=0.6,
                    requires_semantic=True
                )

        # Fallback to hybrid
        return ClassifiedQuery(
            query_type=QueryType.HYBRID,
            entities=entities,
            keywords=keywords,
            sources=['graph', 'story_bible', 'notebooklm'],
            confidence=0.4,
            requires_semantic=True
        )

    def _extract_entities(self, query: str) -> List[str]:
        """Find known entities mentioned in query."""
        found = []
        query_lower = query.lower()
        for entity in self.known_entities:
            if entity in query_lower:
                found.append(entity)
        return found

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords."""
        stopwords = {
            'is', 'the', 'a', 'an', 'how', 'what', 'who', 'where', 'when',
            'do', 'does', 'did', 'can', 'could', 'would', 'should', 'will',
            'about', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by',
            'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their',
            'me', 'you', 'we', 'they', 'it', 'i', 'he', 'she'
        }
        words = re.findall(r'\w+', query.lower())
        return [w for w in words if w not in stopwords and len(w) > 2]

    def _sources_for_type(self, query_type: QueryType) -> List[str]:
        """Determine appropriate sources for query type."""
        mapping = {
            QueryType.CHARACTER_LOOKUP: ['graph', 'story_bible'],
            QueryType.CHARACTER_DEEP: ['story_bible', 'graph'],
            QueryType.PLOT_STATUS: ['story_bible'],
            QueryType.RELATIONSHIP: ['graph'],
            QueryType.WORLD_RULES: ['story_bible', 'notebooklm'],
            QueryType.WRITING_TECHNIQUE: ['notebooklm'],
            QueryType.SCENE_CONTEXT: ['manuscript', 'graph'],
            QueryType.CONTRADICTION_CHECK: ['graph'],
            QueryType.HYBRID: ['graph', 'story_bible', 'notebooklm'],
        }
        return mapping.get(query_type, ['graph'])

    def update_entities(self, entities: Set[str]):
        """Update known entities (call after graph changes)."""
        self.known_entities = {e.lower() for e in entities}
```

### 3.2 Context Assembler with Token Management

```python
# backend/services/context_assembler.py

import tiktoken
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class ContextBudget:
    max_input: int
    recommended_context: int
    max_context: int

CONTEXT_BUDGETS: Dict[str, ContextBudget] = {
    'claude-sonnet-4-5': ContextBudget(200000, 16000, 32000),
    'claude-opus-4': ContextBudget(200000, 16000, 32000),
    'gpt-4o': ContextBudget(128000, 12000, 24000),
    'gpt-4o-mini': ContextBudget(128000, 12000, 24000),
    'gemini-2.0-flash': ContextBudget(1000000, 16000, 32000),
    'grok-2': ContextBudget(131072, 12000, 24000),
    'deepseek-chat': ContextBudget(64000, 8000, 16000),
    'qwen-plus': ContextBudget(131072, 12000, 24000),
    'mistral-large': ContextBudget(128000, 12000, 24000),
    'llama3.2:3b': ContextBudget(8192, 2000, 4000),
    'mistral:7b': ContextBudget(32768, 6000, 12000),
}

# Priority order for context sections
CONTEXT_PRIORITY = [
    'character_core',       # Fatal Flaw, The Lie, Arc (highest)
    'active_scaffold',      # Current scene's scaffold
    'scene_strategy',       # Goal/Conflict/Outcome
    'relevant_relationships', # Key character relationships
    'beat_context',         # Beat Sheet position
    'world_rules',          # Relevant world constraints
    'recent_decisions',     # From Foreman KB
    'technique_guidance',   # NotebookLM results (lowest)
]

class ContextAssembler:
    """
    Assembles context from multiple sources within token budget.

    Uses priority-based allocation: most important context first,
    truncates or omits lower-priority content if over budget.
    """

    def __init__(self, model: str = 'claude-sonnet-4-5'):
        self.model = model
        self.budget = CONTEXT_BUDGETS.get(model, CONTEXT_BUDGETS['claude-sonnet-4-5'])
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def assemble(
        self,
        classified_query: 'ClassifiedQuery',
        graph_context: Dict,
        story_bible_context: Dict,
        kb_context: List[Dict],
        notebooklm_results: Optional[str] = None,
        active_scaffold: Optional[Dict] = None,
    ) -> str:
        """
        Assemble context block from multiple sources.

        Returns formatted context string within token budget.
        """
        budget = self.budget.recommended_context
        blocks = []
        used_tokens = 0

        # Track what we included for debugging
        included_sections = []

        # 1. Character Core (highest priority) - NEVER truncate
        for entity in classified_query.entities:
            if entity in graph_context.get('characters', {}):
                char_block = self._format_character_core(
                    entity,
                    graph_context['characters'][entity],
                    story_bible_context.get('characters', {}).get(entity)
                )
                tokens = self._count_tokens(char_block)
                blocks.append(char_block)
                used_tokens += tokens
                included_sections.append(f"character_core:{entity}")

        # 2. Active Scaffold (if writing a scene)
        if active_scaffold:
            scaffold_block = self._format_scaffold(active_scaffold)
            tokens = self._count_tokens(scaffold_block)
            if used_tokens + tokens <= budget:
                blocks.append(scaffold_block)
                used_tokens += tokens
                included_sections.append("active_scaffold")

        # 3. Relevant Relationships
        if classified_query.entities and 'edges' in graph_context:
            rel_block = self._format_relationships(
                classified_query.entities,
                graph_context['edges']
            )
            tokens = self._count_tokens(rel_block)
            if used_tokens + tokens <= budget:
                blocks.append(rel_block)
                used_tokens += tokens
                included_sections.append("relationships")

        # 4. Beat Context
        if 'beat_sheet' in story_bible_context:
            beat_block = self._format_beat_context(story_bible_context['beat_sheet'])
            tokens = self._count_tokens(beat_block)
            if used_tokens + tokens <= budget:
                blocks.append(beat_block)
                used_tokens += tokens
                included_sections.append("beat_context")

        # 5. World Rules (filtered by relevance)
        if 'world_rules' in story_bible_context:
            world_block = self._format_world_rules(
                story_bible_context['world_rules'],
                classified_query.keywords
            )
            if world_block:
                tokens = self._count_tokens(world_block)
                if used_tokens + tokens <= budget:
                    blocks.append(world_block)
                    used_tokens += tokens
                    included_sections.append("world_rules")

        # 6. Recent KB Decisions
        if kb_context:
            remaining = budget - used_tokens
            kb_block = self._format_kb_context(kb_context, remaining)
            blocks.append(kb_block)
            used_tokens += self._count_tokens(kb_block)
            included_sections.append("kb_context")

        # 7. NotebookLM Results (lowest priority, fill remaining space)
        if notebooklm_results:
            remaining = budget - used_tokens
            if remaining > 200:  # Only include if meaningful space left
                nlm_block = self._truncate_to_tokens(
                    f"## Writing Guidance\n\n{notebooklm_results}",
                    remaining
                )
                blocks.append(nlm_block)
                included_sections.append("notebooklm")

        # Add metadata comment for debugging
        context = "\n\n---\n\n".join(blocks)
        metadata = f"<!-- Context: {', '.join(included_sections)} | {used_tokens} tokens -->\n\n"

        return metadata + context

    def _format_character_core(
        self,
        name: str,
        graph_data: Dict,
        story_bible_data: Optional[Dict]
    ) -> str:
        """Format essential character info."""
        parts = [f"## Character: {name}"]

        if graph_data.get('description'):
            parts.append(f"**Summary**: {graph_data['description']}")

        if story_bible_data:
            if story_bible_data.get('fatal_flaw'):
                parts.append(f"**Fatal Flaw**: {story_bible_data['fatal_flaw']}")
            if story_bible_data.get('the_lie'):
                parts.append(f"**The Lie**: {story_bible_data['the_lie']}")
            if story_bible_data.get('arc'):
                parts.append(f"**Arc**: {story_bible_data['arc']}")

        return "\n".join(parts)

    def _format_scaffold(self, scaffold: Dict) -> str:
        """Format active scene scaffold."""
        return f"""## Active Scene Scaffold

**Scene**: {scaffold.get('title', 'Untitled')}
**Beat Alignment**: {scaffold.get('beat_alignment', 'Not specified')}
**POV**: {scaffold.get('pov_character', 'Not specified')}
**Goal**: {scaffold.get('scene_goal', 'Not specified')}
**Constraint**: {scaffold.get('protagonist_constraint', 'None')}
**Callbacks**: {', '.join(scaffold.get('callbacks', [])) or 'None'}
**Foreshadowing**: {', '.join(scaffold.get('foreshadowing', [])) or 'None'}"""

    def _format_relationships(self, entities: List[str], edges: List[Dict]) -> str:
        """Format relevant relationships."""
        parts = ["## Relationships"]

        for edge in edges:
            if edge['source'].lower() in [e.lower() for e in entities] or \
               edge['target'].lower() in [e.lower() for e in entities]:
                parts.append(f"- {edge['source']} --[{edge['relation']}]--> {edge['target']}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _format_beat_context(self, beat_sheet: Dict) -> str:
        """Format beat sheet status."""
        current = beat_sheet.get('current_beat', 1)
        beats = beat_sheet.get('beats', {})
        current_beat = beats.get(str(current), {})

        return f"""## Beat Sheet Status

**Current Beat**: {current} - {current_beat.get('name', 'Unknown')}
**Description**: {current_beat.get('description', 'Not defined')}
**Progress**: Beat {current} of 15"""

    def _format_world_rules(self, rules: Dict, keywords: List[str]) -> str:
        """Format world rules, prioritizing keyword-relevant ones."""
        parts = ["## World Rules"]

        for rule_name, rule_content in rules.items():
            if any(kw in rule_name.lower() or kw in str(rule_content).lower() for kw in keywords):
                parts.append(f"**{rule_name}**: {rule_content}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _format_kb_context(self, entries: List[Dict], max_tokens: int) -> str:
        """Format KB entries within token limit."""
        parts = ["## Recent Decisions"]
        tokens_used = self._count_tokens(parts[0])

        for entry in entries:
            line = f"- [{entry['category']}] {entry['key']}: {entry['value']}"
            line_tokens = self._count_tokens(line)

            if tokens_used + line_tokens > max_tokens:
                break

            parts.append(line)
            tokens_used += line_tokens

        return "\n".join(parts)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        tokens = self.encoder.encode(text)
        if len(tokens) <= max_tokens:
            return text
        truncated = self.encoder.decode(tokens[:max_tokens - 20])
        return truncated + "\n\n[... truncated for length]"
```

---

## Part 4: Narrative Edge Types & Extraction

### 4.1 Narrative Ontology

```python
# backend/graph/narrative_ontology.py

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
    scene_id: Optional[str] = None  # Where this relationship was established
    is_active: bool = True  # Can be "resolved" (e.g., obstacle overcome)
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
    NarrativeEdgeType.CONTRADICTS: False,  # Experimental
}
```

### 4.2 Enhanced Extraction Prompts

```python
# backend/graph/narrative_extractor.py

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
   - Relationship type (from: MOTIVATES, HINDERS, CHALLENGES, CAUSES, FORESHADOWS, CALLBACKS, KNOWS)
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

    def __init__(self, llm_service, graph_service):
        self.llm = llm_service
        self.graph = graph_service

    async def extract_from_scene(
        self,
        scene_content: str,
        scene_id: str,
        current_beat: str
    ) -> dict:
        """
        Extract narrative elements from a scene.

        Returns structured extraction result.
        """
        # Gather existing context
        known_characters = [n.name for n in self.graph.get_nodes_by_type("CHARACTER")]
        known_locations = [n.name for n in self.graph.get_nodes_by_type("LOCATION")]

        prompt = NARRATIVE_EXTRACTION_PROMPT.format(
            scene_content=scene_content,
            known_characters=", ".join(known_characters) or "None yet",
            known_locations=", ".join(known_locations) or "None yet",
            current_beat=current_beat
        )

        response = await self.llm.query(
            prompt=prompt,
            model="llama3.2:3b",
            temperature=0.1,  # Low temperature for consistency
            response_format="json"
        )

        try:
            result = json.loads(response)
            result["scene_id"] = scene_id
            result["extracted_at"] = datetime.now(timezone.utc).isoformat()
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse extraction result: {response}")
            return {"error": "Extraction failed", "raw": response}

    async def merge_to_graph(self, extraction: dict) -> dict:
        """
        Merge extraction results into the knowledge graph.

        Returns merge statistics.
        """
        stats = {"nodes_created": 0, "edges_created": 0, "conflicts": []}
        scene_id = extraction.get("scene_id")

        # Create new entities
        for entity in extraction.get("entities", []):
            existing = self.graph.find_node_by_name(entity["id"])
            if not existing:
                self.graph.add_node(
                    name=entity["id"],
                    node_type=entity["type"],
                    description=entity.get("description"),
                    source=f"scene:{scene_id}"
                )
                stats["nodes_created"] += 1

        # Create relationships
        for rel in extraction.get("relationships", []):
            try:
                edge_type = NarrativeEdgeType[rel["type"]]
            except KeyError:
                edge_type = NarrativeEdgeType.CUSTOM

            # Check for contradictions
            if edge_type == NarrativeEdgeType.CONTRADICTS:
                stats["conflicts"].append(rel)
                continue  # Don't auto-add contradictions

            source_node = self.graph.find_node_by_name(rel["source"])
            target_node = self.graph.find_node_by_name(rel["target"])

            if source_node and target_node:
                self.graph.add_edge(
                    source_id=source_node.id,
                    target_id=target_node.id,
                    relation_type=edge_type.value,
                    description=rel.get("description")
                )
                stats["edges_created"] += 1

        return stats
```

---

## Part 5: Tiered Verification System

### 5.1 Verification Tiers

```python
# backend/services/verification_service.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import asyncio

class VerificationTier(Enum):
    FAST = "fast"        # <500ms, always runs inline
    MEDIUM = "medium"    # 2-5s, runs in background
    SLOW = "slow"        # 5-30s, on-demand only

class IssueSeverity(Enum):
    CRITICAL = "critical"    # Blocks output, must fix
    WARNING = "warning"      # Show to user, suggest fix
    INFO = "info"            # Log only, no user notification

@dataclass
class VerificationIssue:
    check_name: str
    severity: IssueSeverity
    message: str
    location: Optional[str] = None  # Scene/line reference
    suggestion: Optional[str] = None
    auto_fixable: bool = False

@dataclass
class VerificationResult:
    tier: VerificationTier
    passed: bool
    issues: List[VerificationIssue]
    duration_ms: float

class VerificationService:
    """
    Tiered verification system for narrative consistency.

    FAST tier (inline, <500ms):
    - Character alive/dead status
    - Known fact contradictions
    - Required callbacks present

    MEDIUM tier (background, 2-5s):
    - Flaw challenge frequency
    - Beat alignment
    - Timeline consistency

    SLOW tier (on-demand):
    - Full LLM semantic analysis
    - Voice consistency
    - Pacing analysis
    """

    def __init__(self, graph_service, health_service):
        self.graph = graph_service
        self.health = health_service

    async def run_fast_checks(
        self,
        content: str,
        scene_context: dict
    ) -> VerificationResult:
        """
        Run fast checks inline. Called after every generation.

        Must complete in <500ms.
        """
        import time
        start = time.time()
        issues = []

        # Check 1: Character status
        dead_characters = self._get_dead_characters()
        for char in dead_characters:
            if char.lower() in content.lower():
                issues.append(VerificationIssue(
                    check_name="character_status",
                    severity=IssueSeverity.CRITICAL,
                    message=f"'{char}' appears in scene but is marked deceased in the graph",
                    suggestion=f"Remove references to {char} or update their status",
                    auto_fixable=False
                ))

        # Check 2: Required callbacks
        required_callbacks = scene_context.get("callbacks", [])
        for callback in required_callbacks:
            if callback.lower() not in content.lower():
                issues.append(VerificationIssue(
                    check_name="missing_callback",
                    severity=IssueSeverity.WARNING,
                    message=f"Expected callback to '{callback}' not found in scene",
                    suggestion=f"Add a reference to '{callback}' to maintain continuity"
                ))

        # Check 3: Known contradictions
        contradictions = self._check_known_contradictions(content, scene_context)
        issues.extend(contradictions)

        duration = (time.time() - start) * 1000

        return VerificationResult(
            tier=VerificationTier.FAST,
            passed=not any(i.severity == IssueSeverity.CRITICAL for i in issues),
            issues=issues,
            duration_ms=duration
        )

    async def run_medium_checks(
        self,
        content: str,
        scene_context: dict
    ) -> VerificationResult:
        """
        Run medium checks in background. Results shown as notifications.
        """
        import time
        start = time.time()
        issues = []

        # Check 1: Flaw challenge frequency (from health service)
        flaw_gap = await self.health.check_flaw_challenge_gap(scene_context.get("scene_id"))
        if flaw_gap and flaw_gap > 10:
            issues.append(VerificationIssue(
                check_name="flaw_challenge_gap",
                severity=IssueSeverity.WARNING,
                message=f"Protagonist's fatal flaw hasn't been challenged in {flaw_gap} scenes",
                suggestion="Consider adding a moment that tests the protagonist's weakness"
            ))

        # Check 2: Beat alignment
        expected_beat = scene_context.get("beat_alignment")
        if expected_beat:
            alignment = await self._check_beat_alignment(content, expected_beat)
            if not alignment["aligned"]:
                issues.append(VerificationIssue(
                    check_name="beat_alignment",
                    severity=IssueSeverity.INFO,
                    message=f"Scene may not align with expected beat: {expected_beat}",
                    suggestion=alignment.get("suggestion")
                ))

        # Check 3: Timeline consistency
        timeline_issues = await self._check_timeline(content, scene_context)
        issues.extend(timeline_issues)

        duration = (time.time() - start) * 1000

        return VerificationResult(
            tier=VerificationTier.MEDIUM,
            passed=not any(i.severity == IssueSeverity.CRITICAL for i in issues),
            issues=issues,
            duration_ms=duration
        )

    async def run_slow_checks(
        self,
        content: str,
        scene_context: dict
    ) -> VerificationResult:
        """
        Run slow checks on-demand only. Full LLM analysis.
        """
        import time
        start = time.time()

        # Delegate to existing health service
        health_report = await self.health.run_full_analysis(
            content=content,
            scene_id=scene_context.get("scene_id")
        )

        issues = self._convert_health_report_to_issues(health_report)
        duration = (time.time() - start) * 1000

        return VerificationResult(
            tier=VerificationTier.SLOW,
            passed=health_report.get("overall_score", 0) >= 0.7,
            issues=issues,
            duration_ms=duration
        )

    def _get_dead_characters(self) -> List[str]:
        """Get list of characters marked as deceased."""
        # Query graph for CHARACTER nodes with status=deceased
        deceased = []
        for node in self.graph.get_nodes_by_type("CHARACTER"):
            status_edges = self.graph.get_edges(source_id=node.id)
            for edge in status_edges:
                if edge.relation_type == "HAS_STATUS" and "dead" in edge.description.lower():
                    deceased.append(node.name)
        return deceased

    def _check_known_contradictions(
        self,
        content: str,
        scene_context: dict
    ) -> List[VerificationIssue]:
        """Check for known contradictions from graph."""
        issues = []

        # Get CONTRADICTS edges
        contradictions = self.graph.get_edges_by_type("CONTRADICTS")
        for c in contradictions:
            source_node = self.graph.get_node(c.source_id)
            target_node = self.graph.get_node(c.target_id)

            # If both facts appear in content, flag it
            if source_node and target_node:
                if (source_node.name.lower() in content.lower() and
                    target_node.name.lower() in content.lower()):
                    issues.append(VerificationIssue(
                        check_name="known_contradiction",
                        severity=IssueSeverity.WARNING,
                        message=f"Scene references both '{source_node.name}' and '{target_node.name}', which are marked as contradictory",
                        suggestion="Review and resolve the contradiction"
                    ))

        return issues

    async def _check_beat_alignment(
        self,
        content: str,
        expected_beat: str
    ) -> dict:
        """Check if content aligns with expected beat."""
        # Simple keyword check for now
        # Could be enhanced with LLM analysis
        beat_keywords = {
            "Opening Image": ["begins", "start", "ordinary"],
            "Catalyst": ["discovers", "learns", "receives"],
            "Midpoint": ["realizes", "victory", "defeat"],
            "Dark Night": ["lowest", "despair", "lost"],
            "Climax": ["confronts", "faces", "final"],
        }

        keywords = beat_keywords.get(expected_beat, [])
        content_lower = content.lower()
        matches = sum(1 for k in keywords if k in content_lower)

        return {
            "aligned": matches > 0,
            "confidence": matches / max(len(keywords), 1),
            "suggestion": f"Consider incorporating elements typical of {expected_beat}"
        }

    async def _check_timeline(
        self,
        content: str,
        scene_context: dict
    ) -> List[VerificationIssue]:
        """Check for timeline inconsistencies."""
        issues = []

        # Get previous scene's time markers
        prev_scene = scene_context.get("previous_scene", {})
        prev_time = prev_scene.get("time_of_day")
        current_time = scene_context.get("time_of_day")

        if prev_time and current_time:
            # Simple check: if previous was "night" and current is "morning", that's fine
            # But "night" → "afternoon" same day might be suspicious
            time_order = ["dawn", "morning", "noon", "afternoon", "evening", "night"]

            try:
                prev_idx = time_order.index(prev_time.lower())
                curr_idx = time_order.index(current_time.lower())

                # If going backwards without scene break, flag it
                if curr_idx < prev_idx and not scene_context.get("day_changed"):
                    issues.append(VerificationIssue(
                        check_name="timeline_regression",
                        severity=IssueSeverity.WARNING,
                        message=f"Time appears to go backwards: {prev_time} → {current_time}",
                        suggestion="Add a day transition or adjust the time of day"
                    ))
            except ValueError:
                pass  # Unknown time markers, skip check

        return issues

    def _convert_health_report_to_issues(
        self,
        health_report: dict
    ) -> List[VerificationIssue]:
        """Convert health service report to verification issues."""
        issues = []

        for check_name, result in health_report.get("checks", {}).items():
            if result.get("score", 1.0) < 0.7:
                issues.append(VerificationIssue(
                    check_name=check_name,
                    severity=IssueSeverity.WARNING if result.get("score", 0) >= 0.5 else IssueSeverity.CRITICAL,
                    message=result.get("message", f"{check_name} check failed"),
                    suggestion=result.get("recommendation")
                ))

        return issues
```

### 5.2 Verification UX Integration

```python
# backend/services/scene_writer_service.py (updated)

class SceneWriterService:
    """Updated to integrate tiered verification."""

    async def generate_scene(
        self,
        scaffold: dict,
        strategy: str,
        run_verification: bool = True
    ) -> dict:
        """
        Generate scene with optional inline verification.
        """
        # Generate the scene content
        content = await self._generate_content(scaffold, strategy)

        result = {
            "content": content,
            "strategy": strategy,
            "scaffold_id": scaffold.get("scaffold_id"),
            "verification": None
        }

        if run_verification:
            # Run FAST checks inline
            verification_service = get_verification_service()
            fast_result = await verification_service.run_fast_checks(
                content=content,
                scene_context=scaffold
            )

            result["verification"] = {
                "fast": {
                    "passed": fast_result.passed,
                    "issues": [asdict(i) for i in fast_result.issues],
                    "duration_ms": fast_result.duration_ms
                }
            }

            # If FAST checks pass, queue MEDIUM checks in background
            if fast_result.passed:
                asyncio.create_task(self._run_background_verification(
                    content, scaffold
                ))

            # If FAST checks fail with CRITICAL, optionally auto-fix
            if not fast_result.passed:
                critical_issues = [i for i in fast_result.issues
                                   if i.severity == IssueSeverity.CRITICAL]
                result["critical_issues"] = [asdict(i) for i in critical_issues]
                result["requires_revision"] = True

        return result

    async def _run_background_verification(
        self,
        content: str,
        scene_context: dict
    ):
        """Run MEDIUM checks in background, emit results via WebSocket."""
        verification_service = get_verification_service()
        medium_result = await verification_service.run_medium_checks(
            content=content,
            scene_context=scene_context
        )

        if medium_result.issues:
            # Emit notification to frontend
            await self._emit_verification_notification(
                scene_id=scene_context.get("scaffold_id"),
                issues=medium_result.issues
            )
```

### 5.3 Frontend Notification Component

```svelte
<!-- frontend/src/lib/components/VerificationNotification.svelte -->

<script>
    import { onMount } from 'svelte';
    import { verificationStore } from '$lib/stores';

    let notifications = [];

    verificationStore.subscribe(value => {
        notifications = value.pending_notifications;
    });

    function dismissNotification(id) {
        verificationStore.dismiss(id);
    }

    function severityColor(severity) {
        switch(severity) {
            case 'critical': return 'bg-red-100 border-red-500 text-red-800';
            case 'warning': return 'bg-yellow-100 border-yellow-500 text-yellow-800';
            case 'info': return 'bg-blue-100 border-blue-500 text-blue-800';
            default: return 'bg-gray-100 border-gray-500 text-gray-800';
        }
    }
</script>

<div class="fixed bottom-4 right-4 space-y-2 z-50">
    {#each notifications as notif (notif.id)}
        <div class="p-3 rounded-lg border-l-4 shadow-lg max-w-sm {severityColor(notif.severity)}">
            <div class="flex justify-between items-start">
                <div>
                    <p class="font-semibold text-sm">{notif.check_name}</p>
                    <p class="text-sm mt-1">{notif.message}</p>
                    {#if notif.suggestion}
                        <p class="text-xs mt-2 opacity-80">💡 {notif.suggestion}</p>
                    {/if}
                </div>
                <button
                    on:click={() => dismissNotification(notif.id)}
                    class="ml-2 text-gray-500 hover:text-gray-700"
                >
                    ✕
                </button>
            </div>
        </div>
    {/each}
</div>
```

---

## Part 6: Settings Panel Integration

### 6.1 Graph Settings Schema

```python
# backend/services/settings_service.py (additions)

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
            "CONTRADICTS": {"type": "boolean", "default": False},
        }
    },
    "custom_edge_types": {
        "type": "array",
        "items": {"type": "string"},
        "default": [],
        "description": "User-defined edge types"
    },
    "extraction_triggers": {
        "type": "object",
        "properties": {
            "on_manuscript_promote": {"type": "boolean", "default": True},
            "before_foreman_chat": {"type": "boolean", "default": True},
            "periodic_minutes": {"type": "integer", "default": 0, "description": "0 = disabled"}
        }
    },
    "verification_level": {
        "type": "string",
        "enum": ["minimal", "standard", "thorough"],
        "default": "standard",
        "description": "How thorough verification checks should be"
    },
    "embedding_provider": {
        "type": "string",
        "enum": ["ollama", "openai", "none"],
        "default": "ollama",
        "description": "Provider for semantic embeddings"
    }
}
```

### 6.2 Settings Panel Component

```svelte
<!-- frontend/src/lib/components/settings/GraphSettings.svelte -->

<script>
    import { settingsStore } from '$lib/stores';
    import Toggle from '../ui/Toggle.svelte';
    import Select from '../ui/Select.svelte';

    let settings = {};

    settingsStore.subscribe(value => {
        settings = value.graph || {};
    });

    function updateSetting(path, value) {
        settingsStore.update(current => {
            // Deep update the setting
            const keys = path.split('.');
            let obj = current;
            for (let i = 0; i < keys.length - 1; i++) {
                obj = obj[keys[i]] = obj[keys[i]] || {};
            }
            obj[keys[keys.length - 1]] = value;
            return current;
        });
    }

    const edgeTypes = [
        { key: 'MOTIVATES', label: 'MOTIVATES', desc: 'Character → Goal' },
        { key: 'HINDERS', label: 'HINDERS', desc: 'Obstacle → Goal' },
        { key: 'CHALLENGES', label: 'CHALLENGES', desc: 'Scene → Fatal Flaw' },
        { key: 'FORESHADOWS', label: 'FORESHADOWS', desc: 'Scene → Future Event' },
        { key: 'CALLBACKS', label: 'CALLBACKS', desc: 'Scene → Past Event' },
        { key: 'CAUSES', label: 'CAUSES', desc: 'Event → Event' },
        { key: 'CONTRADICTS', label: 'CONTRADICTS', desc: 'Fact → Fact (experimental)' },
    ];

    const verificationLevels = [
        { value: 'minimal', label: 'Minimal - Critical contradictions only' },
        { value: 'standard', label: 'Standard - Fast checks + background medium' },
        { value: 'thorough', label: 'Thorough - All checks, may slow generation' },
    ];
</script>

<div class="space-y-6">
    <section>
        <h3 class="text-lg font-semibold mb-3">Narrative Edge Types</h3>
        <p class="text-sm text-gray-600 mb-4">
            Control which relationship types are extracted from your scenes.
        </p>

        <div class="space-y-2">
            {#each edgeTypes as et}
                <div class="flex items-center justify-between py-2 border-b">
                    <div>
                        <span class="font-mono text-sm">{et.label}</span>
                        <span class="text-gray-500 text-sm ml-2">- {et.desc}</span>
                    </div>
                    <Toggle
                        checked={settings.edge_types?.[et.key] ?? true}
                        on:change={(e) => updateSetting(`edge_types.${et.key}`, e.detail)}
                    />
                </div>
            {/each}
        </div>
    </section>

    <section>
        <h3 class="text-lg font-semibold mb-3">Extraction Behavior</h3>

        <div class="space-y-3">
            <div class="flex items-center justify-between">
                <span>Extract on manuscript promotion</span>
                <Toggle
                    checked={settings.extraction_triggers?.on_manuscript_promote ?? true}
                    on:change={(e) => updateSetting('extraction_triggers.on_manuscript_promote', e.detail)}
                />
            </div>
            <div class="flex items-center justify-between">
                <span>Extract before Foreman chat</span>
                <Toggle
                    checked={settings.extraction_triggers?.before_foreman_chat ?? true}
                    on:change={(e) => updateSetting('extraction_triggers.before_foreman_chat', e.detail)}
                />
            </div>
        </div>
    </section>

    <section>
        <h3 class="text-lg font-semibold mb-3">Verification Level</h3>

        <Select
            value={settings.verification_level || 'standard'}
            options={verificationLevels}
            on:change={(e) => updateSetting('verification_level', e.detail)}
        />

        <div class="mt-3 p-3 bg-gray-50 rounded text-sm">
            {#if settings.verification_level === 'minimal'}
                <p><strong>Minimal:</strong> Only checks for critical issues like dead characters appearing or known contradictions. Fastest, no generation delay.</p>
            {:else if settings.verification_level === 'thorough'}
                <p><strong>Thorough:</strong> Runs all checks including LLM-powered analysis. May add 5-10 seconds to generation.</p>
            {:else}
                <p><strong>Standard:</strong> Fast checks run inline (~500ms). Medium checks run in background with notifications.</p>
            {/if}
        </div>
    </section>

    <section>
        <h3 class="text-lg font-semibold mb-3">Embedding Provider</h3>

        <Select
            value={settings.embedding_provider || 'ollama'}
            options={[
                { value: 'ollama', label: 'Ollama (Local, Free)' },
                { value: 'openai', label: 'OpenAI (Cloud, Best Quality)' },
                { value: 'none', label: 'Disabled' },
            ]}
            on:change={(e) => updateSetting('embedding_provider', e.detail)}
        />

        <p class="text-sm text-gray-500 mt-2">
            Embeddings enable semantic search across your knowledge graph.
        </p>
    </section>
</div>
```

---

## Part 7: Implementation Phases

### Phase 1: Foundation (Week 1)

**Files to Create:**
- `backend/services/query_classifier.py`
- `backend/services/context_assembler.py`
- `backend/services/manuscript_service.py`

**Files to Modify:**
- `backend/api.py` - Add new endpoints
- `frontend/src/lib/stores.js` - Add manuscript store

**Deliverables:**
- [ ] QueryClassifier with 8 query types
- [ ] ContextAssembler with tiktoken token counting
- [ ] Working → Manuscript directory structure
- [ ] Promote endpoint and basic UI

**Unblocks:** Phase 2 (retrieval needs classification), Phase 3 (extraction needs manuscript structure)

---

### Phase 2: Retrieval (Week 2)

**Files to Create:**
- `backend/services/embedding_service.py`
- `backend/services/embedding_index_service.py`
- `backend/services/knowledge_router.py`

**Files to Modify:**
- `backend/graph/schema.py` - Add embedding columns
- `backend/graph/graph_service.py` - Add ego_graph method
- `backend/services/foreman_kb_service.py` - Integrate with router

**Deliverables:**
- [ ] Ollama embedding integration
- [ ] K-hop ego network extraction (`nx.ego_graph`)
- [ ] Semantic search across graph nodes
- [ ] KnowledgeRouter orchestrating classification → retrieval → assembly

**Unblocks:** Phase 4 (verification needs context), Phase 5 (semantic search enhances all features)

---

### Phase 3: Extraction (Week 2-3)

**Files to Create:**
- `backend/graph/narrative_ontology.py`
- `backend/graph/narrative_extractor.py`

**Files to Modify:**
- `backend/services/consolidator_service.py` - Use narrative extractor
- `backend/ingestor.py` - Use narrative prompts

**Deliverables:**
- [ ] NarrativeEdgeType enum with 8 core types
- [ ] Updated extraction prompts for MOTIVATES, HINDERS, CHALLENGES, etc.
- [ ] Extraction triggered on manuscript promotion
- [ ] Extraction triggered before Foreman chat (if recent edits)

**Unblocks:** Phase 4 (verification uses narrative edges)

---

### Phase 4: Verification (Week 3-4)

**Files to Create:**
- `backend/services/verification_service.py`
- `frontend/src/lib/components/VerificationNotification.svelte`
- `frontend/src/lib/stores/verificationStore.js`

**Files to Modify:**
- `backend/services/scene_writer_service.py` - Integrate verification
- `backend/agents/foreman.py` - Add promotion intent detection

**Deliverables:**
- [ ] VerificationService with 3 tiers (fast/medium/slow)
- [ ] Fast checks: character status, callbacks, contradictions
- [ ] Medium checks: flaw challenge, beat alignment, timeline
- [ ] Background notification system for medium check results
- [ ] Settings integration for verification level

**Unblocks:** Full GraphRAG workflow complete

---

### Phase 5: Enhancement (Week 4+)

**Files to Modify:**
- `backend/services/embedding_service.py` - Add cloud providers
- `backend/graph/graph_service.py` - Add community detection
- Various settings panel additions

**Deliverables:**
- [ ] Optional OpenAI/cloud embeddings
- [ ] Community detection for plot clustering
- [ ] Tension calculation based on graph structure
- [ ] Full settings panel for graph configuration

---

## Part 8: API Endpoint Summary

### New Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/manuscript/working` | GET | List working files |
| `/manuscript/structure` | GET | Get manuscript hierarchy |
| `/manuscript/promote` | POST | Promote working file to manuscript |
| `/manuscript/promote-via-chat` | POST | Natural language promotion |
| `/knowledge/query` | POST | Query with classification + routing |
| `/knowledge/entities` | GET | List known entities |
| `/graph/semantic-search` | POST | Embedding-based search |
| `/graph/ego-network` | GET | K-hop subgraph extraction |
| `/graph/reindex-embeddings` | POST | Reindex all node embeddings |
| `/verification/run` | POST | Run verification checks |
| `/verification/issues` | GET | Get pending issues |

---

## Part 9: Success Criteria

### Functional Requirements

- [ ] Queries automatically route to best knowledge source
- [ ] Context assembled within model token budgets
- [ ] Character core info (Fatal Flaw, The Lie) always prioritized
- [ ] Working → Manuscript promotion triggers extraction
- [ ] Narrative edge types (MOTIVATES, HINDERS, etc.) extracted
- [ ] Fast verification checks run inline (<500ms)
- [ ] Medium checks run in background with notifications
- [ ] Settings panel allows customization of all graph features

### Performance Requirements

- [ ] Query classification: <50ms
- [ ] Context assembly: <200ms
- [ ] Fast verification: <500ms
- [ ] Embedding generation: <2s per node (Ollama)
- [ ] Semantic search (100 nodes): <500ms

### UX Requirements

- [ ] Clear indication of verification issues (toast notifications)
- [ ] Manuscript structure visible in file tree
- [ ] Promotion confirmation dialog
- [ ] Settings panel for all configurable options

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 2025 | Initial approved plan |
| 1.1 | Dec 2025 | Added Part 0: Integration Matrix with data flow diagrams, embedding model fallback strategy, and settings integration points |

---

*End of Document*
