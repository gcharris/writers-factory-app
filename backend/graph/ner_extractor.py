"""
Fast NER-based extraction using spaCy.
Fallback for when LLM extraction is too slow/expensive.
"""

import logging
from typing import List, Optional

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from .schema import Node

logger = logging.getLogger(__name__)


class NERExtractor:
    """Fast entity extraction using spaCy NER."""

    def __init__(self):
        """Initialize spaCy model."""
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_lg")

        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.warning("en_core_web_lg not found, trying en_core_web_sm...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.error("No spaCy model found. Run: python -m spacy download en_core_web_sm")
                raise

    def extract_nodes(self, scene_content: str, scene_id: str) -> List[Node]:
        """
        Extract entities using spaCy NER and return them as Node objects.

        Args:
            scene_content: The text content of the scene.
            scene_id: An identifier for the source scene.

        Returns:
            A list of new, unsaved Node objects.
        """
        doc = self.nlp(scene_content)

        nodes = []
        seen_names = set()

        for ent in doc.ents:
            # Skip duplicates within the same text
            if ent.text.lower() in seen_names:
                continue
            seen_names.add(ent.text.lower())

            # Map spaCy types to our node types
            node_type = self._map_spacy_type(ent.label_)
            if not node_type:
                continue

            # Get context sentence for description
            description = self._get_entity_context(ent, doc)

            node = Node(
                name=ent.text,
                node_type=node_type,
                description=description,
                content=f"Extracted from scene: {scene_id}"
            )
            nodes.append(node)

        logger.info(f"NER extracted {len(nodes)} potential nodes from scene {scene_id}")
        return nodes

    def _map_spacy_type(self, spacy_label: str) -> Optional[str]:
        """Map spaCy entity labels to our node type strings."""
        # This mapping is based on the old EntityType enum
        mapping = {
            'PERSON': "character",
            'GPE': "location",  # Geopolitical entity
            'LOC': "location",
            'FAC': "location",  # Facility
            'ORG': "organization",
            'EVENT': "event",
            'PRODUCT': "object",
            'WORK_OF_ART': "object",
            'CONCEPT': "concept",
            'THEME': "theme"
        }
        return mapping.get(spacy_label)

    def _get_entity_context(self, ent, doc) -> str:
        """Extract context sentence for entity description."""
        # Find the sentence containing this entity
        for sent in doc.sents:
            if ent.start >= sent.start and ent.end <= sent.end:
                # Return the sentence as context
                return sent.text.strip()
        return "Extracted from scene context."