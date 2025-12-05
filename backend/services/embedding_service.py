"""
Embedding Service for GraphRAG.

Multi-provider embedding service with Ollama-first strategy.
Supports automatic model detection and fallback.

Part of GraphRAG Phase 2 - Semantic Search & Embeddings.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np
import httpx
import asyncio
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Base class for embedding providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name for tracking."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return the embedding dimension."""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        pass


class OllamaEmbedding(EmbeddingProvider):
    """Ollama-based embeddings with automatic model detection."""

    # Known embedding models in preference order
    EMBEDDING_MODELS = [
        "nomic-embed-text",
        "nomic-embed-text:latest",
        "mxbai-embed-large",
        "all-minilm",
    ]

    # Fallback models that can generate embeddings (less optimal)
    FALLBACK_MODELS = [
        "llama3.2:3b",
        "mistral:7b",
    ]

    # Known dimensions per model
    MODEL_DIMENSIONS = {
        "nomic-embed-text": 768,
        "nomic-embed-text:latest": 768,
        "mxbai-embed-large": 1024,
        "all-minilm": 384,
        "llama3.2:3b": 3072,
        "mistral:7b": 4096,
    }

    def __init__(self, model: str = "auto", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama embedding provider.

        Args:
            model: Model name or "auto" for automatic detection
            base_url: Ollama API base URL
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self._model = model
        self._detected_model: Optional[str] = None
        self._dimension: Optional[int] = None
        logger.info(f"OllamaEmbedding initialized (model={model}, base_url={base_url})")

    @property
    def provider_name(self) -> str:
        return f"ollama:{self._detected_model or self._model}"

    @property
    def dimension(self) -> int:
        if self._dimension:
            return self._dimension
        model = self._detected_model or self._model
        return self.MODEL_DIMENSIONS.get(model, 768)  # Default to 768

    async def _detect_best_model(self) -> str:
        """Detect best available Ollama embedding model."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]

            logger.debug(f"Available Ollama models: {model_names}")

            # Try embedding-specific models first
            for preferred in self.EMBEDDING_MODELS:
                if preferred in model_names:
                    logger.info(f"Using embedding model: {preferred}")
                    return preferred

            # Fall back to general models
            for fallback in self.FALLBACK_MODELS:
                if fallback in model_names:
                    logger.warning(f"Using fallback model for embeddings: {fallback}")
                    return fallback

            # Last resort: use any available model
            if models:
                model = models[0]["name"]
                logger.warning(f"Using first available model for embeddings: {model}")
                return model

            raise RuntimeError("No Ollama models available")
        except httpx.HTTPError as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            # Default fallback
            return "llama3.2:3b"
        except Exception as e:
            logger.error(f"Model detection failed: {e}")
            return "llama3.2:3b"

    async def _get_model(self) -> str:
        """Get the model to use, detecting if necessary."""
        if self._model != "auto":
            return self._model
        if self._detected_model is None:
            self._detected_model = await self._detect_best_model()
        return self._detected_model

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        model = await self._get_model()
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": text}
            )
            response.raise_for_status()
            embedding = response.json().get("embedding", [])

            # Update dimension if we didn't know it
            if embedding and not self._dimension:
                self._dimension = len(embedding)
                logger.info(f"Detected embedding dimension: {self._dimension}")

            return embedding
        except httpx.HTTPError as e:
            logger.error(f"Embedding request failed: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        # Ollama doesn't have native batch support, so we parallelize
        tasks = [self.embed(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class OpenAIEmbedding(EmbeddingProvider):
    """OpenAI-based embeddings (optional, for quality boost)."""

    def __init__(self, model: str = "text-embedding-3-small", api_key: Optional[str] = None):
        """
        Initialize OpenAI embedding provider.

        Args:
            model: OpenAI embedding model name
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        self._model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required (set OPENAI_API_KEY or pass api_key)")

        self.client = httpx.AsyncClient(
            timeout=60.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        # Dimensions by model
        self._dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        logger.info(f"OpenAIEmbedding initialized (model={model})")

    @property
    def provider_name(self) -> str:
        return f"openai:{self._model}"

    @property
    def dimension(self) -> int:
        return self._dimensions.get(self._model, 1536)

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                json={"model": self._model, "input": text}
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except httpx.HTTPError as e:
            logger.error(f"OpenAI embedding request failed: {e}")
            raise RuntimeError(f"Failed to generate embedding: {e}")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch API)."""
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                json={"model": self._model, "input": texts}
            )
            response.raise_for_status()
            data = response.json()
            # Sort by index to ensure correct order
            embeddings = sorted(data["data"], key=lambda x: x["index"])
            return [e["embedding"] for e in embeddings]
        except httpx.HTTPError as e:
            logger.error(f"OpenAI batch embedding request failed: {e}")
            raise RuntimeError(f"Failed to generate embeddings: {e}")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class EmbeddingService:
    """
    Unified embedding service interface.

    Provides:
    - embed(text) - Single text embedding
    - embed_batch(texts) - Batch embedding
    - cosine_similarity(a, b) - Similarity calculation
    - find_similar(query, candidates, top_k) - Search
    """

    def __init__(self, provider: str = "ollama", **kwargs):
        """
        Initialize embedding service with specified provider.

        Args:
            provider: "ollama" or "openai"
            **kwargs: Provider-specific arguments
        """
        if provider == "ollama":
            self._provider = OllamaEmbedding(**kwargs)
        elif provider == "openai":
            self._provider = OpenAIEmbedding(**kwargs)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

        logger.info(f"EmbeddingService initialized with {provider} provider")

    @property
    def provider_name(self) -> str:
        """Return the provider name for tracking."""
        return self._provider.provider_name

    @property
    def dimension(self) -> int:
        """Return the embedding dimension."""
        return self._provider.dimension

    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        return await self._provider.embed(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return await self._provider.embed_batch(texts)

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        """
        Calculate cosine similarity between two embedding vectors.

        Args:
            a: First embedding vector
            b: Second embedding vector

        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if not a or not b:
            return 0.0

        a_arr = np.array(a)
        b_arr = np.array(b)

        dot_product = np.dot(a_arr, b_arr)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))

    async def find_similar(
        self,
        query: str,
        candidates: List[Tuple[str, List[float]]],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find most similar items to query.

        Args:
            query: Query text
            candidates: List of (id, embedding) tuples
            top_k: Number of results to return

        Returns:
            List of (id, similarity_score) tuples, sorted by similarity
        """
        query_embedding = await self.embed(query)

        results = []
        for item_id, item_embedding in candidates:
            similarity = self.cosine_similarity(query_embedding, item_embedding)
            results.append((item_id, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    async def close(self):
        """Close underlying provider connections."""
        await self._provider.close()


# Singleton instance for convenience
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(provider: str = "ollama", **kwargs) -> EmbeddingService:
    """
    Get or create the singleton EmbeddingService instance.

    Args:
        provider: "ollama" or "openai"
        **kwargs: Provider-specific arguments

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService(provider=provider, **kwargs)

    return _embedding_service


def reset_embedding_service():
    """Reset the singleton instance (useful for testing)."""
    global _embedding_service
    _embedding_service = None
