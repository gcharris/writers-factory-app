"""
Query Classifier Service for GraphRAG.

Classifies user queries to determine optimal routing strategy for knowledge retrieval.
Uses pattern matching + entity detection to route queries to appropriate sources.

Part of GraphRAG Phase 1 - Foundation.
"""

from enum import Enum
from dataclasses import dataclass
import re
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle."""
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
    """Result of query classification."""
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

    # Stopwords for keyword extraction
    STOPWORDS = {
        'is', 'the', 'a', 'an', 'how', 'what', 'who', 'where', 'when',
        'do', 'does', 'did', 'can', 'could', 'would', 'should', 'will',
        'about', 'with', 'for', 'to', 'of', 'in', 'on', 'at', 'by',
        'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their',
        'me', 'you', 'we', 'they', 'it', 'i', 'he', 'she', 'and', 'or',
        'but', 'if', 'then', 'so', 'just', 'more', 'some', 'any', 'all',
        'been', 'being', 'have', 'has', 'had', 'having', 'get', 'got',
        'are', 'was', 'were', 'am', 'be', 'not', 'no', 'yes'
    }

    def __init__(self, known_entities: Optional[Set[str]] = None):
        """
        Initialize the classifier with known entities from the knowledge graph.

        Args:
            known_entities: Set of entity names (characters, locations, etc.)
        """
        self.known_entities = {e.lower() for e in (known_entities or set())}
        self._compile_patterns()
        logger.info(f"QueryClassifier initialized with {len(self.known_entities)} known entities")

    def _compile_patterns(self):
        """Compile regex patterns for each query type."""
        self.patterns = {
            QueryType.CHARACTER_LOOKUP: [
                r"who is (\w+)",
                r"tell me about (\w+)",
                r"what do (we|I) know about (\w+)",
                r"describe (\w+)",
                r"who('?s| is) (\w+)",
            ],
            QueryType.CHARACTER_DEEP: [
                r"(\w+)'?s? (fatal )?flaw",
                r"(\w+)'?s? (the )?lie",
                r"(\w+)'?s? arc",
                r"(\w+)'?s? true character",
                r"(\w+)'?s? motivation",
                r"(\w+)'?s? goal",
                r"(\w+)'?s? want",
                r"(\w+)'?s? need",
                r"what drives (\w+)",
                r"what motivates (\w+)",
            ],
            QueryType.PLOT_STATUS: [
                r"what beat",
                r"where (are we|is the story)",
                r"beat sheet",
                r"plot progress",
                r"current (scene|beat|act)",
                r"what happens next",
                r"story progress",
                r"where in the story",
            ],
            QueryType.RELATIONSHIP: [
                r"relationship between",
                r"how does (\w+) feel about (\w+)",
                r"(\w+) and (\w+)",
                r"connection between",
                r"(\w+)'?s? relationship",
                r"what('?s| is) between (\w+) and (\w+)",
                r"dynamic between",
            ],
            QueryType.WORLD_RULES: [
                r"how does .* work",
                r"rules? (of|for)",
                r"world.?building",
                r"magic system",
                r"can .* do",
                r"laws? of",
                r"physics of",
                r"how .* works",
            ],
            QueryType.WRITING_TECHNIQUE: [
                r"how (do|should) (i|we) write",
                r"writing (advice|tips|technique)",
                r"voice",
                r"prose style",
                r"show.?don'?t.?tell",
                r"craft",
                r"technique",
                r"style guide",
                r"how to (write|describe|convey)",
                r"compressed prose",
            ],
            QueryType.SCENE_CONTEXT: [
                r"previous scene",
                r"last scene",
                r"what happened (before|earlier)",
                r"recap",
                r"earlier in",
                r"before this",
                r"in the last",
                r"what just happened",
            ],
            QueryType.CONTRADICTION_CHECK: [
                r"contradict",
                r"consistent",
                r"conflict with",
                r"does this (work|make sense)",
                r"continuity",
                r"plot hole",
                r"inconsistent",
                r"doesn'?t match",
            ],
        }

    def classify(self, query: str) -> ClassifiedQuery:
        """
        Classify a query and determine routing strategy.

        Args:
            query: The user's natural language query

        Returns:
            ClassifiedQuery with type, entities, keywords, sources, confidence
        """
        query_lower = query.lower().strip()
        entities = self._extract_entities(query)
        keywords = self._extract_keywords(query)

        # Try pattern matching first (highest confidence)
        for query_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    result = ClassifiedQuery(
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
                    logger.debug(f"Query classified as {query_type.value} (pattern match)")
                    return result

        # Entity-based classification (medium confidence)
        if entities:
            if len(entities) > 1:
                result = ClassifiedQuery(
                    query_type=QueryType.RELATIONSHIP,
                    entities=entities,
                    keywords=keywords,
                    sources=['graph'],
                    confidence=0.7,
                    requires_semantic=False
                )
                logger.debug(f"Query classified as RELATIONSHIP (multiple entities)")
                return result
            else:
                result = ClassifiedQuery(
                    query_type=QueryType.CHARACTER_LOOKUP,
                    entities=entities,
                    keywords=keywords,
                    sources=['graph', 'story_bible'],
                    confidence=0.6,
                    requires_semantic=True
                )
                logger.debug(f"Query classified as CHARACTER_LOOKUP (single entity)")
                return result

        # Fallback to hybrid (low confidence)
        result = ClassifiedQuery(
            query_type=QueryType.HYBRID,
            entities=entities,
            keywords=keywords,
            sources=['graph', 'story_bible', 'notebooklm'],
            confidence=0.4,
            requires_semantic=True
        )
        logger.debug(f"Query classified as HYBRID (fallback)")
        return result

    def _extract_entities(self, query: str) -> List[str]:
        """
        Find known entities mentioned in the query.

        Args:
            query: The user's query

        Returns:
            List of entity names found in the query
        """
        found = []
        query_lower = query.lower()

        for entity in self.known_entities:
            # Use word boundary matching to avoid partial matches
            pattern = r'\b' + re.escape(entity) + r'\b'
            if re.search(pattern, query_lower):
                found.append(entity)

        return found

    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract meaningful keywords for search.

        Args:
            query: The user's query

        Returns:
            List of keywords (stopwords removed, min length 3)
        """
        words = re.findall(r'\w+', query.lower())
        keywords = [w for w in words if w not in self.STOPWORDS and len(w) > 2]
        return keywords

    def _sources_for_type(self, query_type: QueryType) -> List[str]:
        """
        Determine appropriate data sources for a query type.

        Args:
            query_type: The classified query type

        Returns:
            List of source names to query
        """
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
        """
        Update known entities (call after graph changes).

        Args:
            entities: New set of entity names
        """
        old_count = len(self.known_entities)
        self.known_entities = {e.lower() for e in entities}
        logger.info(f"Updated known entities: {old_count} -> {len(self.known_entities)}")


# Singleton instance
_classifier_instance: Optional[QueryClassifier] = None


def get_query_classifier(known_entities: Optional[Set[str]] = None) -> QueryClassifier:
    """
    Get or create the singleton QueryClassifier instance.

    Args:
        known_entities: Optional set of entities to initialize with

    Returns:
        QueryClassifier instance
    """
    global _classifier_instance

    if _classifier_instance is None:
        _classifier_instance = QueryClassifier(known_entities or set())
    elif known_entities:
        _classifier_instance.update_entities(known_entities)

    return _classifier_instance


def reset_classifier():
    """Reset the singleton instance (useful for testing)."""
    global _classifier_instance
    _classifier_instance = None
