"""
Knowledge Router for GraphRAG.

Orchestrates the full query → classification → retrieval → assembly pipeline.
Integrates Phase 1 (classifier, assembler) with Phase 2 (embeddings, ego graph).

Part of GraphRAG Phase 2 - Semantic Search & Embeddings.
"""

from dataclasses import asdict
from typing import Dict, List, Any, Optional, TYPE_CHECKING
import logging

import networkx as nx

from .query_classifier import QueryClassifier, ClassifiedQuery, get_query_classifier
from .context_assembler import ContextAssembler, get_context_assembler
from .embedding_index_service import EmbeddingIndexService

if TYPE_CHECKING:
    from ..graph.graph_service import KnowledgeGraphService
    from .story_bible_service import StoryBibleService

logger = logging.getLogger(__name__)


class KnowledgeRouter:
    """
    Orchestrates knowledge retrieval pipeline.

    Query → Classify → Retrieve (graph + semantic + story bible) → Assemble

    Combines:
    - QueryClassifier (Phase 1) for routing decisions
    - Graph traversal via ego_graph for structured data
    - Semantic search for fuzzy matching
    - ContextAssembler (Phase 1) for token-aware output
    """

    def __init__(
        self,
        classifier: QueryClassifier,
        graph_service: 'KnowledgeGraphService',
        embedding_index: EmbeddingIndexService,
        story_bible: Optional['StoryBibleService'],
        assembler: ContextAssembler
    ):
        """
        Initialize the knowledge router.

        Args:
            classifier: QueryClassifier for query analysis
            graph_service: KnowledgeGraphService for graph operations
            embedding_index: EmbeddingIndexService for semantic search
            story_bible: Optional StoryBibleService for structured narrative data
            assembler: ContextAssembler for token-aware context building
        """
        self.classifier = classifier
        self.graph = graph_service
        self.embedding_index = embedding_index
        self.story_bible = story_bible
        self.assembler = assembler
        logger.info("KnowledgeRouter initialized")

    async def route(self, query: str, model: str = "claude-sonnet-4-5") -> Dict[str, Any]:
        """
        Route a query through the full pipeline.

        Args:
            query: Natural language query
            model: Target model for token budget (default claude-sonnet-4-5)

        Returns:
            Dict with:
            - context: Assembled context string
            - classification: ClassifiedQuery details
            - retrieval_sources: Sources that contributed data
            - token_count: Approximate token count
            - semantic_matches: Nodes found via semantic search
            - ego_networks: Subgraphs for matched entities
        """
        # 1. Classify the query
        classified = self.classifier.classify(query)
        logger.debug(f"Query classified as {classified.query_type.value} (confidence: {classified.confidence})")

        # 2. Retrieve from graph (ego networks for entities)
        graph_context = await self._retrieve_from_graph(classified)

        # 3. Retrieve from Story Bible
        story_bible_context = await self._retrieve_from_story_bible(classified)

        # 4. Semantic search (if beneficial for query type)
        semantic_results = await self._semantic_retrieve(query, classified)

        # 5. Merge semantic results into graph context
        for node, score in semantic_results:
            # Avoid duplicates with existing character data
            existing_chars = graph_context.get("characters", {})
            if node.name.lower() not in {k.lower() for k in existing_chars}:
                graph_context.setdefault("semantic_matches", []).append({
                    "name": node.name,
                    "type": node.node_type,
                    "description": node.description,
                    "relevance": round(score, 3)
                })

        # 6. Assemble within token budget
        context = self.assembler.assemble(
            classified_query=classified,
            graph_context=graph_context,
            story_bible_context=story_bible_context,
            kb_context=[],  # Could integrate Foreman KB here in future
        )

        token_count = self.assembler._count_tokens(context)

        return {
            "context": context,
            "classification": {
                "type": classified.query_type.value,
                "entities": classified.entities,
                "keywords": classified.keywords,
                "sources": classified.sources,
                "confidence": classified.confidence,
                "requires_semantic": classified.requires_semantic
            },
            "retrieval_sources": classified.sources,
            "token_count": token_count,
            "semantic_matches": graph_context.get("semantic_matches", []),
            "ego_networks": graph_context.get("ego_networks", {})
        }

    async def _retrieve_from_graph(self, classified: ClassifiedQuery) -> Dict[str, Any]:
        """
        Retrieve graph context using k-hop ego networks.

        For each detected entity, extracts the local subgraph.

        Args:
            classified: The classified query with detected entities

        Returns:
            Dict with 'characters', 'edges', and 'ego_networks' keys
        """
        result = {
            "characters": {},
            "edges": [],
            "ego_networks": {}
        }

        for entity in classified.entities:
            node = self.graph.find_node_by_name(entity)
            if node:
                # Get ego network (2-hop subgraph)
                ego_data = self.graph.ego_graph(node.name, radius=2)

                result["characters"][entity] = {
                    "id": node.id,
                    "description": node.description,
                    "type": node.node_type,
                    "neighbors": [n["name"] for n in ego_data.get("nodes", []) if n["name"] != node.name]
                }

                result["ego_networks"][entity] = ego_data

                # Add edges from ego network
                for edge in ego_data.get("edges", []):
                    edge_info = {
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                        "relation": edge.get("relation")
                    }
                    if edge_info not in result["edges"]:
                        result["edges"].append(edge_info)

        logger.debug(f"Graph retrieval: {len(result['characters'])} characters, {len(result['edges'])} edges")
        return result

    async def _retrieve_from_story_bible(self, classified: ClassifiedQuery) -> Dict[str, Any]:
        """
        Retrieve relevant Story Bible content.

        Args:
            classified: The classified query

        Returns:
            Dict with story bible sections relevant to query
        """
        if not self.story_bible or 'story_bible' not in classified.sources:
            return {}

        result = {}

        try:
            # Get Story Bible status (includes parsed data)
            status = self.story_bible.get_status()

            # Include protagonist data for character queries
            if classified.query_type.value in ('character_lookup', 'character_deep', 'hybrid'):
                if status.protagonist:
                    result["protagonist"] = {
                        "name": status.protagonist.name,
                        "fatal_flaw": status.protagonist.fatal_flaw,
                        "the_lie": status.protagonist.the_lie,
                        "true_character": status.protagonist.true_character,
                        "arc": {
                            "start": status.protagonist.arc_start,
                            "midpoint": status.protagonist.arc_midpoint,
                            "resolution": status.protagonist.arc_resolution
                        }
                    }

                    # Map protagonist to any matching entity
                    for entity in classified.entities:
                        if entity.lower() == status.protagonist.name.lower():
                            result["characters"] = result.get("characters", {})
                            result["characters"][entity] = result["protagonist"]

            # Include beat sheet for plot queries
            if classified.query_type.value in ('plot_status', 'scene_context', 'hybrid'):
                if status.beat_sheet:
                    current = status.beat_sheet.current_beat
                    beats = status.beat_sheet.beats

                    current_beat = beats[current - 1] if current <= len(beats) else None

                    result["beat_sheet"] = {
                        "current_beat": current,
                        "beats": {
                            str(i + 1): {
                                "name": b.name,
                                "description": b.description,
                                "percentage": b.percentage
                            }
                            for i, b in enumerate(beats)
                        }
                    }

                    if current_beat:
                        result["beat_sheet"]["current"] = {
                            "name": current_beat.name,
                            "description": current_beat.description
                        }

            logger.debug(f"Story Bible retrieval: {list(result.keys())}")

        except Exception as e:
            logger.warning(f"Story Bible retrieval failed: {e}")

        return result

    async def _semantic_retrieve(
        self,
        query: str,
        classified: ClassifiedQuery
    ) -> List[tuple]:
        """
        Semantic search if beneficial for query type.

        Args:
            query: Original query text
            classified: The classified query

        Returns:
            List of (Node, similarity_score) tuples
        """
        if not classified.requires_semantic:
            logger.debug("Skipping semantic search (not required for query type)")
            return []

        try:
            results = await self.embedding_index.semantic_search(
                query=query,
                top_k=5,
                min_similarity=0.3  # Only return meaningful matches
            )
            logger.debug(f"Semantic search returned {len(results)} results")
            return results

        except Exception as e:
            logger.warning(f"Semantic search failed: {e}")
            return []

    async def simple_query(self, query: str) -> str:
        """
        Simplified query interface returning just the context string.

        Args:
            query: Natural language query

        Returns:
            Assembled context string
        """
        result = await self.route(query)
        return result["context"]


# Factory function
def create_knowledge_router(
    graph_service: 'KnowledgeGraphService',
    embedding_index: EmbeddingIndexService,
    story_bible: Optional['StoryBibleService'] = None,
    model: str = "claude-sonnet-4-5"
) -> KnowledgeRouter:
    """
    Create a configured KnowledgeRouter.

    Args:
        graph_service: KnowledgeGraphService instance
        embedding_index: EmbeddingIndexService instance
        story_bible: Optional StoryBibleService instance
        model: Target model for context assembly

    Returns:
        Configured KnowledgeRouter
    """
    # Get known entities from graph for classifier
    try:
        nodes = graph_service.get_all_nodes()
        known_entities = {node.name for node in nodes if node.name}
    except Exception:
        known_entities = set()

    classifier = get_query_classifier(known_entities)
    assembler = get_context_assembler(model)

    return KnowledgeRouter(
        classifier=classifier,
        graph_service=graph_service,
        embedding_index=embedding_index,
        story_bible=story_bible,
        assembler=assembler
    )
