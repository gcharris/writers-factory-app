"""
Embedding Index Service for GraphRAG.

Manages embedding lifecycle for graph nodes:
- Index individual nodes
- Reindex all nodes (after provider change)
- Semantic search across nodes

Part of GraphRAG Phase 2 - Semantic Search & Embeddings.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
import logging

from ..graph.schema import Node
from .embedding_service import EmbeddingService, get_embedding_service

logger = logging.getLogger(__name__)


class EmbeddingIndexService:
    """
    Maintains embeddings for all graph nodes.

    Provides:
    - index_node(node_id) - Generate and store embedding for single node
    - index_nodes(node_ids) - Batch index multiple nodes
    - reindex_all(batch_size) - Re-index all nodes
    - semantic_search(query, node_types, top_k) - Search nodes by similarity
    - get_indexing_status() - Check indexing progress
    """

    def __init__(self, graph_service, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize the embedding index service.

        Args:
            graph_service: KnowledgeGraphService instance for node access
            embedding_service: Optional EmbeddingService (creates default if not provided)
        """
        self.graph = graph_service
        self.embeddings = embedding_service or get_embedding_service()
        logger.info(f"EmbeddingIndexService initialized with {self.embeddings.provider_name}")

    def _get_node_text(self, node: Node) -> str:
        """
        Generate text representation of a node for embedding.

        Combines type, name, description, and content into a searchable string.
        """
        parts = [f"{node.node_type}: {node.name}"]

        if node.description:
            parts.append(node.description)

        if node.content:
            # Limit content to avoid embedding overly long texts
            content = node.content[:2000] if len(node.content) > 2000 else node.content
            parts.append(content)

        return ". ".join(parts)

    async def index_node(self, node_id: int) -> bool:
        """
        Generate and store embedding for a single node.

        Args:
            node_id: ID of the node to index

        Returns:
            True if indexing succeeded, False otherwise
        """
        node = self.graph.get_node(node_id)
        if not node:
            logger.warning(f"Cannot index node {node_id}: not found")
            return False

        try:
            text = self._get_node_text(node)
            embedding = await self.embeddings.embed(text)

            node.embedding = embedding
            node.embedding_model = self.embeddings.provider_name
            node.embedding_updated_at = datetime.now(timezone.utc)
            self.graph.session.commit()

            logger.debug(f"Indexed node {node_id} ({node.name})")
            return True

        except Exception as e:
            logger.error(f"Failed to index node {node_id}: {e}")
            return False

    async def index_nodes(self, node_ids: List[int]) -> Dict[str, int]:
        """
        Index multiple nodes.

        Args:
            node_ids: List of node IDs to index

        Returns:
            Dict with 'success' and 'failed' counts
        """
        success = 0
        failed = 0

        for node_id in node_ids:
            if await self.index_node(node_id):
                success += 1
            else:
                failed += 1

        logger.info(f"Indexed {success} nodes, {failed} failed")
        return {"success": success, "failed": failed}

    async def reindex_all(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Re-index all nodes in the graph.

        Use after changing embedding provider or for full refresh.

        Args:
            batch_size: Number of nodes to process at a time

        Returns:
            Dict with indexing statistics
        """
        nodes = self.graph.get_all_nodes()
        total = len(nodes)

        if total == 0:
            logger.warning("No nodes to index")
            return {
                "total": 0,
                "indexed": 0,
                "failed": 0,
                "provider": self.embeddings.provider_name
            }

        logger.info(f"Reindexing {total} nodes with {self.embeddings.provider_name}")

        indexed = 0
        failed = 0

        # Process in batches
        for i in range(0, total, batch_size):
            batch = nodes[i:i + batch_size]

            for node in batch:
                try:
                    text = self._get_node_text(node)
                    embedding = await self.embeddings.embed(text)

                    node.embedding = embedding
                    node.embedding_model = self.embeddings.provider_name
                    node.embedding_updated_at = datetime.now(timezone.utc)
                    indexed += 1

                except Exception as e:
                    logger.error(f"Failed to index node {node.id} ({node.name}): {e}")
                    failed += 1

            # Commit after each batch
            self.graph.session.commit()
            logger.debug(f"Processed batch {i // batch_size + 1} ({indexed}/{total})")

        result = {
            "total": total,
            "indexed": indexed,
            "failed": failed,
            "provider": self.embeddings.provider_name,
            "dimension": self.embeddings.dimension
        }

        logger.info(f"Reindexing complete: {indexed}/{total} nodes indexed")
        return result

    async def semantic_search(
        self,
        query: str,
        node_types: Optional[List[str]] = None,
        top_k: int = 10,
        min_similarity: float = 0.0
    ) -> List[Tuple[Node, float]]:
        """
        Search graph nodes by semantic similarity.

        Args:
            query: Natural language query
            node_types: Optional list of node types to filter (e.g., ['character', 'location'])
            top_k: Maximum number of results to return
            min_similarity: Minimum similarity score (0.0-1.0)

        Returns:
            List of (Node, similarity_score) tuples, sorted by similarity descending
        """
        # Get query embedding
        query_embedding = await self.embeddings.embed(query)

        # Get nodes with embeddings
        nodes = self.graph.get_all_nodes()

        # Filter by type if specified
        if node_types:
            nodes = [n for n in nodes if n.node_type in node_types]

        # Filter to nodes with embeddings
        nodes_with_embeddings = [n for n in nodes if n.embedding]

        if not nodes_with_embeddings:
            logger.warning("No nodes with embeddings found")
            return []

        # Calculate similarities
        results = []
        for node in nodes_with_embeddings:
            similarity = self.embeddings.cosine_similarity(query_embedding, node.embedding)
            if similarity >= min_similarity:
                results.append((node, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)

        logger.debug(f"Semantic search for '{query[:50]}...' returned {len(results[:top_k])} results")
        return results[:top_k]

    async def find_similar_nodes(
        self,
        node_id: int,
        node_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Tuple[Node, float]]:
        """
        Find nodes similar to a given node.

        Args:
            node_id: ID of the reference node
            node_types: Optional list of node types to filter
            top_k: Maximum number of results to return

        Returns:
            List of (Node, similarity_score) tuples, excluding the reference node
        """
        source_node = self.graph.get_node(node_id)
        if not source_node:
            logger.warning(f"Reference node {node_id} not found")
            return []

        if not source_node.embedding:
            # Generate embedding if missing
            await self.index_node(node_id)
            source_node = self.graph.get_node(node_id)
            if not source_node.embedding:
                logger.warning(f"Could not generate embedding for node {node_id}")
                return []

        # Get all nodes with embeddings
        nodes = self.graph.get_all_nodes()
        if node_types:
            nodes = [n for n in nodes if n.node_type in node_types]

        nodes_with_embeddings = [n for n in nodes if n.embedding and n.id != node_id]

        # Calculate similarities
        results = []
        for node in nodes_with_embeddings:
            similarity = self.embeddings.cosine_similarity(source_node.embedding, node.embedding)
            results.append((node, similarity))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_indexing_status(self) -> Dict[str, Any]:
        """
        Get statistics about embedding index status.

        Returns:
            Dict with indexing statistics
        """
        nodes = self.graph.get_all_nodes()
        total = len(nodes)
        indexed = sum(1 for n in nodes if n.embedding)

        # Check for stale embeddings (different provider)
        current_provider = self.embeddings.provider_name
        stale = sum(1 for n in nodes if n.embedding and n.embedding_model != current_provider)

        # Group by type
        by_type = {}
        for node in nodes:
            node_type = node.node_type or "unknown"
            if node_type not in by_type:
                by_type[node_type] = {"total": 0, "indexed": 0}
            by_type[node_type]["total"] += 1
            if node.embedding:
                by_type[node_type]["indexed"] += 1

        return {
            "total_nodes": total,
            "indexed_nodes": indexed,
            "unindexed_nodes": total - indexed,
            "stale_embeddings": stale,
            "coverage_percent": round(indexed / total * 100, 1) if total > 0 else 0,
            "current_provider": current_provider,
            "by_type": by_type
        }

    async def index_unindexed(self, batch_size: int = 50) -> Dict[str, Any]:
        """
        Index only nodes that don't have embeddings.

        Args:
            batch_size: Number of nodes to process at a time

        Returns:
            Dict with indexing statistics
        """
        nodes = self.graph.get_all_nodes()
        unindexed = [n for n in nodes if not n.embedding]

        if not unindexed:
            logger.info("All nodes already indexed")
            return {"total": 0, "indexed": 0, "failed": 0}

        logger.info(f"Indexing {len(unindexed)} unindexed nodes")
        node_ids = [n.id for n in unindexed]
        return await self.index_nodes(node_ids)


# Singleton instance
_index_service: Optional[EmbeddingIndexService] = None


def get_embedding_index_service(graph_service=None) -> EmbeddingIndexService:
    """
    Get or create the singleton EmbeddingIndexService instance.

    Args:
        graph_service: KnowledgeGraphService instance (required on first call)

    Returns:
        EmbeddingIndexService instance
    """
    global _index_service

    if _index_service is None:
        if graph_service is None:
            raise ValueError("graph_service required for first initialization")
        _index_service = EmbeddingIndexService(graph_service)

    return _index_service


def reset_embedding_index_service():
    """Reset the singleton instance (useful for testing)."""
    global _index_service
    _index_service = None
