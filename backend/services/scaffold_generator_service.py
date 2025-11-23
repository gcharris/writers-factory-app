"""
Scaffold Generator Service - Phase 3B Director Mode

Generates strategic briefing documents (scaffolds) for scene writing.
Two-stage process:
1. Draft Summary - Quick preview with enrichment suggestions
2. Full Scaffold - Complete document with optional NotebookLM enrichment

All scaffold generation runs through Ollama (free) - only enrichment
queries use NotebookLM (also free).
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class BeatInfo:
    """Information about a story beat from the Beat Sheet."""
    beat_number: int
    beat_name: str  # e.g., "Catalyst", "Midpoint", "All Is Lost"
    beat_percentage: str  # e.g., "10%", "50%"
    description: str
    beat_type: Optional[str] = None  # e.g., "false_victory", "false_defeat"


@dataclass
class CharacterContext:
    """Character information for scaffold generation."""
    name: str
    role: str  # "protagonist", "antagonist", "supporting"
    fatal_flaw: Optional[str] = None
    the_lie: Optional[str] = None
    arc_state: Optional[str] = None  # Where they are in their arc
    relevant_relationships: Dict[str, str] = field(default_factory=dict)


@dataclass
class ContinuityEntry:
    """A continuity note from previous scenes."""
    scene_id: str
    event: str
    category: str  # "plot", "character", "world", "foreshadow"
    must_callback: bool = False  # If True, this MUST be referenced


@dataclass
class EnrichmentSuggestion:
    """A suggested NotebookLM query for enrichment."""
    notebook_id: str
    notebook_name: str
    suggested_query: str
    reason: str  # Why this might help


@dataclass
class DraftSummary:
    """Stage 1 output - preview before full scaffold generation."""
    scene_id: str
    chapter_number: int
    scene_number: int
    beat_info: BeatInfo
    narrative_summary: str  # Human-readable "what happens"
    available_context: List[str]  # What we already know
    enrichment_suggestions: List[EnrichmentSuggestion]
    ready_to_generate: bool
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "chapter_number": self.chapter_number,
            "scene_number": self.scene_number,
            "beat_info": asdict(self.beat_info),
            "narrative_summary": self.narrative_summary,
            "available_context": self.available_context,
            "enrichment_suggestions": [asdict(s) for s in self.enrichment_suggestions],
            "ready_to_generate": self.ready_to_generate,
            "generated_at": self.generated_at,
        }


@dataclass
class EnrichmentData:
    """Data retrieved from NotebookLM enrichment queries."""
    notebook_id: str
    query: str
    answer: str
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Scaffold:
    """Stage 2 output - the full scaffold document."""
    scene_id: str
    chapter_number: int
    scene_number: int
    title: str

    # Chapter Overview
    target_word_count: str
    phase: str  # e.g., "Act II: Fun & Games"
    voice_state: str  # From Voice Bundle
    core_function: str  # What this scene must accomplish

    # Strategic Context
    conflict_positioning: str
    character_goals: str
    thematic_setup: str
    protagonist_constraint: str

    # Success Criteria
    quality_threshold: float
    voice_requirements: List[str]
    phase_calibration: str

    # Continuity
    callbacks: List[str]  # Previous events to reference
    foreshadowing: List[str]  # Elements to plant

    # Enrichment (if any)
    enrichment_data: List[EnrichmentData] = field(default_factory=list)

    # Metadata
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "enrichment_data": [asdict(e) for e in self.enrichment_data],
        }

    def to_markdown(self) -> str:
        """Generate the scaffold as a markdown document."""
        enrichment_section = ""
        if self.enrichment_data:
            enrichment_section = "\n---\n\n#### Enrichment Notes\n"
            for e in self.enrichment_data:
                enrichment_section += f"\n**From {e.notebook_id}:** {e.query}\n> {e.answer}\n"

        return f"""## SCENE {self.chapter_number}.{self.scene_number}: {self.title.upper()}

**For Writers Factory Scene Writer**

---

#### Scene Overview
**Scene ID:** {self.scene_id}
**Target Length:** {self.target_word_count} words
**Phase:** {self.phase}
**Voice:** {self.voice_state}
**Core Function:** {self.core_function}

---

#### Strategic Context
- **Conflict Positioning:** {self.conflict_positioning}
- **Character Goals:** {self.character_goals}
- **Thematic Setup:** {self.thematic_setup}
- **Protagonist Constraint:** {self.protagonist_constraint}

---

#### Success Criteria
##### Quality Thresholds
- Overall quality score > {self.quality_threshold}
- Voice authenticity > 8.0 (sounds like character, not AI explaining character)

##### Voice Requirements
{chr(10).join(f'- {req}' for req in self.voice_requirements)}

##### Phase Calibration
{self.phase_calibration}

---

#### Continuity Checklist
**Callbacks (reference these):**
{chr(10).join(f'- {cb}' for cb in self.callbacks) if self.callbacks else '- None required'}

**Foreshadowing (plant these):**
{chr(10).join(f'- {fs}' for fs in self.foreshadowing) if self.foreshadowing else '- None required'}
{enrichment_section}
---

#### Ready for Scene Writer
This scaffold provides sufficient context for scene generation using the
Voice Bundle without requiring access to the full project knowledge base.

**Expected Output:** {self.target_word_count} words maintaining voice consistency

*Generated: {self.generated_at}*
"""


# =============================================================================
# Scaffold Generator Service
# =============================================================================

class ScaffoldGeneratorService:
    """
    Generates strategic scaffolds for scene writing.

    Two-stage process:
    1. generate_draft_summary() - Quick preview with enrichment options
    2. generate_full_scaffold() - Complete document, optionally enriched
    """

    def __init__(
        self,
        ollama_url: str = OLLAMA_BASE_URL,
        model: str = DEFAULT_MODEL,
        notebooklm_client: Optional[Any] = None,
        kb_service: Optional[Any] = None,
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.notebooklm_client = notebooklm_client
        self.kb_service = kb_service

        # Cache for story bible data
        self._story_bible_cache: Dict[str, Any] = {}
        self._voice_bundle_cache: Dict[str, Any] = {}

    # -------------------------------------------------------------------------
    # Stage 1: Draft Summary
    # -------------------------------------------------------------------------

    async def generate_draft_summary(
        self,
        project_id: str,
        chapter_number: int,
        scene_number: int,
        beat_info: BeatInfo,
        characters: List[CharacterContext],
        scene_description: str,
        available_notebooks: Optional[List[Dict[str, str]]] = None,
    ) -> DraftSummary:
        """
        Generate a draft summary with enrichment suggestions.

        This is the checkpoint where the writer can decide to add
        NotebookLM enrichment before generating the full scaffold.

        Args:
            project_id: The project identifier
            chapter_number: Chapter number
            scene_number: Scene number within chapter
            beat_info: The story beat this scene serves
            characters: Characters appearing in this scene
            scene_description: Brief description of what happens
            available_notebooks: List of available NotebookLM notebooks

        Returns:
            DraftSummary with narrative preview and enrichment suggestions
        """
        scene_id = f"ch{chapter_number}-sc{scene_number}"
        logger.info(f"Generating draft summary for {scene_id}")

        # Build context from what we already have
        available_context = self._build_available_context(
            characters, beat_info, scene_description
        )

        # Generate narrative summary via Ollama
        narrative_summary = await self._generate_narrative_summary(
            beat_info, characters, scene_description
        )

        # Generate enrichment suggestions
        enrichment_suggestions = self._generate_enrichment_suggestions(
            characters, scene_description, available_notebooks or []
        )

        return DraftSummary(
            scene_id=scene_id,
            chapter_number=chapter_number,
            scene_number=scene_number,
            beat_info=beat_info,
            narrative_summary=narrative_summary,
            available_context=available_context,
            enrichment_suggestions=enrichment_suggestions,
            ready_to_generate=True,
        )

    def _build_available_context(
        self,
        characters: List[CharacterContext],
        beat_info: BeatInfo,
        scene_description: str,
    ) -> List[str]:
        """Build list of what context we already have."""
        context = []

        # Beat context
        context.append(f"Beat: {beat_info.beat_name} ({beat_info.beat_percentage})")

        # Character context
        for char in characters:
            char_info = f"{char.name} ({char.role})"
            if char.fatal_flaw:
                char_info += f" - Flaw: {char.fatal_flaw}"
            context.append(char_info)

        # Scene basics
        if scene_description:
            context.append(f"Scene premise: {scene_description[:100]}...")

        return context

    async def _generate_narrative_summary(
        self,
        beat_info: BeatInfo,
        characters: List[CharacterContext],
        scene_description: str,
    ) -> str:
        """Generate human-readable narrative summary via Ollama."""
        char_list = ", ".join([c.name for c in characters])
        protagonist = next((c for c in characters if c.role == "protagonist"), None)

        flaw_context = ""
        if protagonist and protagonist.fatal_flaw:
            flaw_context = f"The protagonist's fatal flaw ({protagonist.fatal_flaw}) should be relevant."

        prompt = f"""Summarize this upcoming scene in 2-3 conversational sentences, as if explaining to a writer what they're about to write.

Scene serves: {beat_info.beat_name} beat ({beat_info.description})
Characters: {char_list}
What happens: {scene_description}
{flaw_context}

Write a friendly, conversational summary. Start with "In this scene..." or "Next up...". Keep it under 100 words."""

        try:
            response = await self._call_ollama(prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            # Fallback to basic summary
            return f"In this scene, {scene_description}. This serves the {beat_info.beat_name} beat."

    def _generate_enrichment_suggestions(
        self,
        characters: List[CharacterContext],
        scene_description: str,
        available_notebooks: List[Dict[str, str]],
    ) -> List[EnrichmentSuggestion]:
        """Generate suggestions for NotebookLM enrichment."""
        suggestions = []

        if not available_notebooks:
            return suggestions

        # Look for character-related notebooks
        for notebook in available_notebooks:
            notebook_id = notebook.get("id", "")
            notebook_name = notebook.get("name", "").lower()

            # Character voice notebooks
            if "voice" in notebook_name or "character" in notebook_name:
                for char in characters:
                    if char.role != "protagonist":  # Supporting characters need voice help
                        suggestions.append(EnrichmentSuggestion(
                            notebook_id=notebook_id,
                            notebook_name=notebook.get("name", ""),
                            suggested_query=f"How does {char.name} typically speak when under pressure?",
                            reason=f"Get voice patterns for {char.name}'s dialogue",
                        ))

            # World-building notebooks
            if "world" in notebook_name or "setting" in notebook_name:
                suggestions.append(EnrichmentSuggestion(
                    notebook_id=notebook_id,
                    notebook_name=notebook.get("name", ""),
                    suggested_query="What sensory details define this location?",
                    reason="Add atmospheric grounding to the scene",
                ))

            # Craft reference notebooks
            if "craft" in notebook_name or "reference" in notebook_name:
                suggestions.append(EnrichmentSuggestion(
                    notebook_id=notebook_id,
                    notebook_name=notebook.get("name", ""),
                    suggested_query="Examples of similar confrontation scenes?",
                    reason="Get structural inspiration from references",
                ))

        return suggestions[:5]  # Limit to 5 suggestions

    # -------------------------------------------------------------------------
    # Stage 2: Full Scaffold
    # -------------------------------------------------------------------------

    async def generate_full_scaffold(
        self,
        project_id: str,
        chapter_number: int,
        scene_number: int,
        title: str,
        beat_info: BeatInfo,
        characters: List[CharacterContext],
        scene_description: str,
        voice_state: str,
        phase: str,
        target_word_count: str = "1500-2000",
        continuity_entries: Optional[List[ContinuityEntry]] = None,
        enrichment_data: Optional[List[EnrichmentData]] = None,
        theme: Optional[str] = None,
    ) -> Scaffold:
        """
        Generate the full scaffold document.

        Args:
            project_id: The project identifier
            chapter_number: Chapter number
            scene_number: Scene number within chapter
            title: Scene title
            beat_info: The story beat this scene serves
            characters: Characters appearing in this scene
            scene_description: Brief description of what happens
            voice_state: Voice description from Voice Bundle
            phase: Story phase (e.g., "Act II: Fun & Games")
            target_word_count: Target word count range
            continuity_entries: Previous events to callback/foreshadow
            enrichment_data: Data from NotebookLM queries (if any)
            theme: Story theme for thematic setup

        Returns:
            Complete Scaffold document
        """
        scene_id = f"ch{chapter_number}-sc{scene_number}"
        logger.info(f"Generating full scaffold for {scene_id}")

        # Find protagonist
        protagonist = next((c for c in characters if c.role == "protagonist"), None)

        # Generate strategic context via Ollama
        strategic_context = await self._generate_strategic_context(
            beat_info, characters, scene_description, theme
        )

        # Build voice requirements
        voice_requirements = self._build_voice_requirements(voice_state, protagonist)

        # Process continuity
        callbacks, foreshadowing = self._process_continuity(continuity_entries or [])

        # Build protagonist constraint
        protagonist_constraint = "None specified"
        if protagonist:
            if protagonist.fatal_flaw:
                protagonist_constraint = f"{protagonist.name}'s {protagonist.fatal_flaw} limits their options"
            if protagonist.the_lie:
                protagonist_constraint += f"; still believes {protagonist.the_lie}"

        return Scaffold(
            scene_id=scene_id,
            chapter_number=chapter_number,
            scene_number=scene_number,
            title=title,
            target_word_count=target_word_count,
            phase=phase,
            voice_state=voice_state,
            core_function=f"Serve {beat_info.beat_name} beat: {beat_info.description}",
            conflict_positioning=strategic_context.get("conflict", scene_description),
            character_goals=strategic_context.get("goals", "Protagonist pursues scene objective"),
            thematic_setup=strategic_context.get("theme", theme or "Theme embedded in action"),
            protagonist_constraint=protagonist_constraint,
            quality_threshold=8.5,
            voice_requirements=voice_requirements,
            phase_calibration=f"Maintain {phase} voice complexity",
            callbacks=callbacks,
            foreshadowing=foreshadowing,
            enrichment_data=enrichment_data or [],
        )

    async def _generate_strategic_context(
        self,
        beat_info: BeatInfo,
        characters: List[CharacterContext],
        scene_description: str,
        theme: Optional[str],
    ) -> Dict[str, str]:
        """Generate strategic context elements via Ollama."""
        protagonist = next((c for c in characters if c.role == "protagonist"), None)
        antagonist = next((c for c in characters if c.role == "antagonist"), None)

        char_context = ""
        if protagonist:
            char_context += f"Protagonist: {protagonist.name}"
            if protagonist.fatal_flaw:
                char_context += f" (Fatal Flaw: {protagonist.fatal_flaw})"
            char_context += "\n"
        if antagonist:
            char_context += f"Antagonist: {antagonist.name}\n"

        prompt = f"""For this scene, provide brief strategic context. Be concise (1-2 sentences each).

Beat: {beat_info.beat_name} - {beat_info.description}
{char_context}
Scene: {scene_description}
Theme: {theme or 'Not specified'}

Respond in JSON format:
{{
    "conflict": "What's the core conflict in this scene?",
    "goals": "What does the protagonist want in this scene?",
    "theme": "How does this scene serve the theme?"
}}"""

        try:
            response = await self._call_ollama(prompt)
            # Try to parse JSON from response
            # Handle potential markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response.strip())
        except Exception as e:
            logger.error(f"Strategic context generation failed: {e}")
            return {
                "conflict": scene_description,
                "goals": "Pursue scene objective",
                "theme": theme or "Theme embedded in action",
            }

    def _build_voice_requirements(
        self,
        voice_state: str,
        protagonist: Optional[CharacterContext],
    ) -> List[str]:
        """Build voice requirements list."""
        requirements = [
            f"Maintain {voice_state}",
            "Character observing, not AI explaining character",
        ]

        if protagonist:
            if protagonist.fatal_flaw:
                requirements.append(f"Show {protagonist.fatal_flaw} through behavior, not exposition")
            requirements.append(f"Authentic {protagonist.name} internal voice")

        requirements.append("Metaphor domains rotated (no single domain > 30%)")

        return requirements

    def _process_continuity(
        self,
        entries: List[ContinuityEntry],
    ) -> Tuple[List[str], List[str]]:
        """Process continuity entries into callbacks and foreshadowing."""
        callbacks = []
        foreshadowing = []

        for entry in entries:
            if entry.category == "foreshadow":
                foreshadowing.append(entry.event)
            elif entry.must_callback or entry.category in ["plot", "character"]:
                callbacks.append(f"{entry.scene_id}: {entry.event}")

        return callbacks, foreshadowing

    # -------------------------------------------------------------------------
    # NotebookLM Enrichment
    # -------------------------------------------------------------------------

    async def fetch_enrichment(
        self,
        notebook_id: str,
        query: str,
    ) -> EnrichmentData:
        """
        Fetch enrichment data from NotebookLM.

        Args:
            notebook_id: The notebook to query
            query: The question to ask

        Returns:
            EnrichmentData with the answer
        """
        if not self.notebooklm_client:
            raise ValueError("NotebookLM client not configured")

        try:
            answer = await self.notebooklm_client.query_notebook(notebook_id, query)
            return EnrichmentData(
                notebook_id=notebook_id,
                query=query,
                answer=answer,
            )
        except Exception as e:
            logger.error(f"NotebookLM query failed: {e}")
            return EnrichmentData(
                notebook_id=notebook_id,
                query=query,
                answer=f"[Query failed: {str(e)}]",
            )

    # -------------------------------------------------------------------------
    # Ollama Communication
    # -------------------------------------------------------------------------

    async def _call_ollama(self, prompt: str, system: str = None) -> str:
        """Make a request to Ollama."""
        if system is None:
            system = "You are a helpful writing assistant. Be concise and direct."

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")

    # -------------------------------------------------------------------------
    # KB Integration
    # -------------------------------------------------------------------------

    async def get_continuity_from_kb(
        self,
        project_id: str,
        max_entries: int = 10,
    ) -> List[ContinuityEntry]:
        """
        Retrieve continuity entries from the Knowledge Base.

        Args:
            project_id: The project identifier
            max_entries: Maximum entries to retrieve

        Returns:
            List of ContinuityEntry objects
        """
        if not self.kb_service:
            return []

        try:
            # Get recent scene entries from KB
            entries = await self.kb_service.get_entries_by_category(
                project_id, "continuity", limit=max_entries
            )

            return [
                ContinuityEntry(
                    scene_id=e.get("scene_id", "unknown"),
                    event=e.get("event", e.get("value", "")),
                    category=e.get("subcategory", "plot"),
                    must_callback=e.get("must_callback", False),
                )
                for e in entries
            ]
        except Exception as e:
            logger.error(f"Failed to get continuity from KB: {e}")
            return []


# =============================================================================
# Service Singleton
# =============================================================================

_scaffold_generator_service: Optional[ScaffoldGeneratorService] = None


def get_scaffold_generator_service(
    notebooklm_client: Optional[Any] = None,
    kb_service: Optional[Any] = None,
) -> ScaffoldGeneratorService:
    """Get or create the ScaffoldGeneratorService singleton."""
    global _scaffold_generator_service
    if _scaffold_generator_service is None:
        _scaffold_generator_service = ScaffoldGeneratorService(
            notebooklm_client=notebooklm_client,
            kb_service=kb_service,
        )
    return _scaffold_generator_service
