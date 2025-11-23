"""
Scene Writer Service - Phase 3B Director Mode

Multi-model scene generation with Voice Bundle injection.
Follows the proven workflow from the Explants Chapter Creation Pipeline:

1. STRUCTURE VARIANTS - 5 different chapter layout approaches
2. SCENE VARIANTS - 5 variations per model using different strategies
3. SCORING - All variants scored by SceneAnalyzerService
4. SELECTION - Human picks winner or hybrid
5. ENHANCEMENT - Selected variant goes through polish pipeline

Key Principle: Creative exploration before commitment.
Generate multiple variants, get feedback, choose the best approach.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.services.llm_service import LLMService
from backend.services.scene_analyzer_service import (
    SceneAnalyzerService,
    get_scene_analyzer_service,
    SceneAnalysisResult,
    VoiceBundleContext,
    StoryBibleContext,
)
from backend.services.scaffold_generator_service import Scaffold

logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

class WritingStrategy(str, Enum):
    """Different creative strategies for scene generation."""
    ACTION = "action"           # More beats, faster pacing, kinetic
    CHARACTER = "character"     # Fewer beats, deeper psychology
    DIALOGUE = "dialogue"       # Conversation-centered scenes
    ATMOSPHERIC = "atmospheric" # Sensory details, mood, setting
    BALANCED = "balanced"       # Mix of action/character/dialogue


# Default models to use for tournament
DEFAULT_TOURNAMENT_MODELS = [
    {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "name": "Claude Sonnet"},
    {"provider": "openai", "model": "gpt-4o", "name": "GPT-4o"},
    {"provider": "deepseek", "model": "deepseek-chat", "name": "DeepSeek"},
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class StructureVariant:
    """A chapter structure variant (layout option)."""
    variant_id: str  # A, B, C, D, E
    beat_count: int
    scene_sequence: List[str]  # Brief description of each scene
    strategic_rationale: str
    pacing: str  # "fast", "medium", "slow"
    focus: str  # "action", "character", "dialogue", etc.

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SceneVariant:
    """A generated scene variant."""
    variant_id: str
    model_name: str
    strategy: WritingStrategy
    content: str
    word_count: int
    generation_time: float  # seconds

    # Scoring (populated after analysis)
    score: Optional[int] = None
    grade: Optional[str] = None
    analysis: Optional[SceneAnalysisResult] = None

    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "variant_id": self.variant_id,
            "model_name": self.model_name,
            "strategy": self.strategy.value,
            "content": self.content,
            "word_count": self.word_count,
            "generation_time": self.generation_time,
            "score": self.score,
            "grade": self.grade,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "generated_at": self.generated_at,
        }


@dataclass
class StructureGenerationResult:
    """Result of structure variant generation."""
    scene_id: str
    beat_description: str
    variants: List[StructureVariant]
    recommendation: Optional[str] = None  # Which variant seems strongest
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "beat_description": self.beat_description,
            "variants": [v.to_dict() for v in self.variants],
            "recommendation": self.recommendation,
            "generated_at": self.generated_at,
        }


@dataclass
class SceneGenerationResult:
    """Result of scene variant generation and scoring."""
    scene_id: str
    scaffold_id: str
    total_variants: int
    variants: List[SceneVariant]

    # Rankings
    winner: Optional[str] = None  # variant_id of highest score
    rankings: List[Dict] = field(default_factory=list)  # sorted by score

    # Metadata
    models_used: List[str] = field(default_factory=list)
    strategies_used: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "scaffold_id": self.scaffold_id,
            "total_variants": self.total_variants,
            "variants": [v.to_dict() for v in self.variants],
            "winner": self.winner,
            "rankings": self.rankings,
            "models_used": self.models_used,
            "strategies_used": self.strategies_used,
            "generated_at": self.generated_at,
        }


@dataclass
class HybridRequest:
    """Request to create a hybrid from multiple variants."""
    scene_id: str
    sources: List[Dict[str, str]]  # [{"variant_id": "A", "section": "opening"}, ...]
    instructions: str  # How to combine them


# =============================================================================
# Scene Writer Service
# =============================================================================

class SceneWriterService:
    """
    Multi-model scene generation with Voice Bundle injection.

    Workflow:
    1. generate_structure_variants() - 5 chapter layout options
    2. [Human selects structure]
    3. generate_scene_variants() - 5 variants per model per strategy
    4. score_all_variants() - Automatic scoring via SceneAnalyzerService
    5. [Human selects winner or hybrid]
    6. create_hybrid() - Combine best elements from multiple variants
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        analyzer_service: Optional[SceneAnalyzerService] = None,
        tournament_models: Optional[List[Dict]] = None,
    ):
        self.llm_service = llm_service or LLMService()
        self.analyzer_service = analyzer_service or get_scene_analyzer_service()
        self.tournament_models = tournament_models or DEFAULT_TOURNAMENT_MODELS

    # -------------------------------------------------------------------------
    # Stage 1: Structure Variants
    # -------------------------------------------------------------------------

    async def generate_structure_variants(
        self,
        scene_id: str,
        beat_description: str,
        scaffold: Optional[Scaffold] = None,
        pov_character: str = "protagonist",
        target_word_count: str = "1500-2000",
    ) -> StructureGenerationResult:
        """
        Generate 5 different structural approaches to a chapter/scene.

        This is Stage 2 of the Chapter Creation Pipeline - creative exploration
        of different ways to structure the scene BEFORE writing prose.

        Args:
            scene_id: Scene identifier (e.g., "ch4-sc1")
            beat_description: What this scene needs to accomplish
            scaffold: Optional scaffold with strategic context
            pov_character: POV character name
            target_word_count: Target word count range

        Returns:
            StructureGenerationResult with 5 layout variants
        """
        logger.info(f"Generating structure variants for {scene_id}")

        scaffold_context = ""
        if scaffold:
            scaffold_context = f"""
SCAFFOLD CONTEXT:
- Core Function: {scaffold.core_function}
- Conflict: {scaffold.conflict_positioning}
- Character Goals: {scaffold.character_goals}
- Phase: {scaffold.phase}
"""

        prompt = f"""Generate 5 different structural approaches to this scene.

SCENE: {scene_id}
BEAT: {beat_description}
POV: {pov_character}
TARGET: {target_word_count} words
{scaffold_context}

For each variant, provide a different creative approach:

VARIANT A: Action-heavy (more beats, faster pacing)
VARIANT B: Character-focused (fewer beats, deeper psychology)
VARIANT C: Dialogue-driven (conversation-centered)
VARIANT D: Atmospheric (sensory details, mood, setting first)
VARIANT E: Balanced (mix of action/character/dialogue)

For each variant, provide:
1. Beat count (2-5 scenes)
2. Scene sequence (brief description of each beat)
3. Strategic rationale (why this structure serves the scene's purpose)
4. Pacing (fast/medium/slow)
5. Focus (what this approach emphasizes)

Respond in JSON format:
{{
    "variants": [
        {{
            "variant_id": "A",
            "beat_count": 4,
            "scene_sequence": ["Beat 1 description", "Beat 2 description", ...],
            "strategic_rationale": "Why this structure works...",
            "pacing": "fast",
            "focus": "action"
        }},
        ...
    ],
    "recommendation": "Which variant seems strongest for this scene and why"
}}"""

        try:
            response = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a story structure expert. Generate creative structural variants. Respond only with valid JSON.",
                prompt=prompt,
            )

            # Parse JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            data = json.loads(response.strip())

            variants = [
                StructureVariant(
                    variant_id=v["variant_id"],
                    beat_count=v["beat_count"],
                    scene_sequence=v["scene_sequence"],
                    strategic_rationale=v["strategic_rationale"],
                    pacing=v["pacing"],
                    focus=v["focus"],
                )
                for v in data["variants"]
            ]

            return StructureGenerationResult(
                scene_id=scene_id,
                beat_description=beat_description,
                variants=variants,
                recommendation=data.get("recommendation"),
            )

        except Exception as e:
            logger.error(f"Structure variant generation failed: {e}")
            # Return default structure on failure
            return StructureGenerationResult(
                scene_id=scene_id,
                beat_description=beat_description,
                variants=[
                    StructureVariant(
                        variant_id="A",
                        beat_count=3,
                        scene_sequence=["Opening", "Conflict", "Resolution"],
                        strategic_rationale="Default three-act structure",
                        pacing="medium",
                        focus="balanced",
                    )
                ],
                recommendation="Default structure due to generation error",
            )

    # -------------------------------------------------------------------------
    # Stage 2: Scene Variants
    # -------------------------------------------------------------------------

    async def generate_scene_variants(
        self,
        scene_id: str,
        scaffold: Scaffold,
        structure_variant: StructureVariant,
        voice_bundle: Optional[VoiceBundleContext] = None,
        story_bible: Optional[StoryBibleContext] = None,
        models: Optional[List[Dict]] = None,
        strategies: Optional[List[WritingStrategy]] = None,
        target_word_count: int = 1500,
    ) -> SceneGenerationResult:
        """
        Generate scene variants using multiple models and strategies.

        Each model generates one variant per strategy, scored by SceneAnalyzerService.

        Args:
            scene_id: Scene identifier
            scaffold: The scaffold with strategic context
            structure_variant: The selected structure layout
            voice_bundle: Voice Bundle for voice injection
            story_bible: Story Bible context
            models: List of models to use (default: tournament models)
            strategies: List of strategies to use (default: all 5)
            target_word_count: Target word count per scene

        Returns:
            SceneGenerationResult with all variants and rankings
        """
        logger.info(f"Generating scene variants for {scene_id}")

        models = models or self.tournament_models
        strategies = strategies or list(WritingStrategy)

        # Build Voice Bundle context for prompt
        voice_context = self._build_voice_context(voice_bundle)

        # Build the base prompt
        base_prompt = self._build_scene_prompt(
            scaffold=scaffold,
            structure_variant=structure_variant,
            voice_context=voice_context,
            target_word_count=target_word_count,
        )

        # Generate variants in parallel
        tasks = []
        for model_config in models:
            for strategy in strategies:
                tasks.append(
                    self._generate_single_variant(
                        scene_id=scene_id,
                        base_prompt=base_prompt,
                        model_config=model_config,
                        strategy=strategy,
                        target_word_count=target_word_count,
                    )
                )

        variants = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_variants = [v for v in variants if isinstance(v, SceneVariant)]

        # Score all variants
        scored_variants = await self._score_variants(
            variants=valid_variants,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
            phase=scaffold.phase,
        )

        # Sort by score
        scored_variants.sort(key=lambda v: v.score or 0, reverse=True)

        # Build rankings
        rankings = [
            {
                "rank": i + 1,
                "variant_id": v.variant_id,
                "model": v.model_name,
                "strategy": v.strategy.value,
                "score": v.score,
                "grade": v.grade,
            }
            for i, v in enumerate(scored_variants)
        ]

        return SceneGenerationResult(
            scene_id=scene_id,
            scaffold_id=scaffold.scene_id,
            total_variants=len(scored_variants),
            variants=scored_variants,
            winner=scored_variants[0].variant_id if scored_variants else None,
            rankings=rankings,
            models_used=[m["name"] for m in models],
            strategies_used=[s.value for s in strategies],
        )

    async def _generate_single_variant(
        self,
        scene_id: str,
        base_prompt: str,
        model_config: Dict,
        strategy: WritingStrategy,
        target_word_count: int,
    ) -> SceneVariant:
        """Generate a single scene variant."""
        import time
        start_time = time.time()

        strategy_instruction = self._get_strategy_instruction(strategy)

        prompt = f"""{base_prompt}

CREATIVE STRATEGY: {strategy.value.upper()}
{strategy_instruction}

Write the complete scene now. Target: {target_word_count} words.
Focus on authentic character voice - the character observing and thinking, NOT AI explaining the character."""

        try:
            content = await self.llm_service.generate_response(
                provider=model_config["provider"],
                model=model_config["model"],
                system_role="You are a skilled fiction writer. Write in the character's authentic voice.",
                prompt=prompt,
            )

            generation_time = time.time() - start_time
            word_count = len(content.split())

            variant_id = f"{model_config['name'][:3].upper()}-{strategy.value[:3].upper()}"

            return SceneVariant(
                variant_id=variant_id,
                model_name=model_config["name"],
                strategy=strategy,
                content=content,
                word_count=word_count,
                generation_time=generation_time,
            )

        except Exception as e:
            logger.error(f"Variant generation failed ({model_config['name']}, {strategy}): {e}")
            raise

    def _build_voice_context(self, voice_bundle: Optional[VoiceBundleContext]) -> str:
        """Build voice context string from Voice Bundle."""
        if not voice_bundle:
            return ""

        sections = []

        if voice_bundle.gold_standard:
            sections.append(f"## VOICE GOLD STANDARD\n{voice_bundle.gold_standard[:2000]}")

        if voice_bundle.anti_patterns:
            sections.append(f"## VOICE ANTI-PATTERNS (AVOID THESE)\n{voice_bundle.anti_patterns[:1500]}")

        if voice_bundle.phase_evolution:
            sections.append(f"## PHASE EVOLUTION\n{voice_bundle.phase_evolution[:1000]}")

        return "\n\n".join(sections)

    def _build_scene_prompt(
        self,
        scaffold: Scaffold,
        structure_variant: StructureVariant,
        voice_context: str,
        target_word_count: int,
    ) -> str:
        """Build the base scene writing prompt."""
        return f"""Write a scene for a novel.

## SCENE CONTEXT
**Scene:** {scaffold.scene_id} - {scaffold.title}
**Phase:** {scaffold.phase}
**Voice State:** {scaffold.voice_state}
**Core Function:** {scaffold.core_function}

## STRATEGIC CONTEXT
- **Conflict:** {scaffold.conflict_positioning}
- **Character Goals:** {scaffold.character_goals}
- **Thematic Setup:** {scaffold.thematic_setup}
- **Protagonist Constraint:** {scaffold.protagonist_constraint}

## STRUCTURE (Selected Layout)
- **Beats:** {structure_variant.beat_count}
- **Sequence:** {' → '.join(structure_variant.scene_sequence)}
- **Pacing:** {structure_variant.pacing}
- **Focus:** {structure_variant.focus}

## CONTINUITY
**Callbacks:** {', '.join(scaffold.callbacks) if scaffold.callbacks else 'None'}
**Foreshadowing:** {', '.join(scaffold.foreshadowing) if scaffold.foreshadowing else 'None'}

{voice_context}

## REQUIREMENTS
- Target: ~{target_word_count} words
- Voice: Character actively observing/thinking, NOT AI explaining character
- Metaphors: Rotate domains, avoid saturation, no similes (use direct transformation)
- Anti-patterns: NO "with [adjective] precision", NO computer psychology, NO passive voice
"""

    def _get_strategy_instruction(self, strategy: WritingStrategy) -> str:
        """Get specific instructions for each writing strategy."""
        instructions = {
            WritingStrategy.ACTION: """
Emphasize kinetic energy and momentum. More beats, faster pacing.
- Open with immediate action or tension
- Quick scene transitions
- Physical movement drives the narrative
- Dialogue is short, punchy
- Internal reflection happens in motion""",

            WritingStrategy.CHARACTER: """
Emphasize psychological depth and internal journey. Fewer beats, deeper exploration.
- Open with internal state or observation
- Longer beats with emotional development
- Focus on what the character FEELS and REALIZES
- Dialogue reveals character rather than plot
- Allow moments of stillness and reflection""",

            WritingStrategy.DIALOGUE: """
Emphasize conversation and verbal conflict. Scene built around exchanges.
- Open with or quickly move to dialogue
- Let characters reveal themselves through speech
- Subtext and what's NOT said matters
- Action serves dialogue, not vice versa
- Internal narration comments on the conversation""",

            WritingStrategy.ATMOSPHERIC: """
Emphasize sensory details, mood, and setting. World-first approach.
- Open with sensory immersion in the space
- Environment reflects and affects character state
- Metaphors drawn from immediate surroundings
- Pacing follows environmental rhythm
- Character perception filtered through place""",

            WritingStrategy.BALANCED: """
Balance action, character, and dialogue. Classic scene structure.
- Mix of movement, reflection, and conversation
- Each element serves the others
- Moderate pacing with variation
- Both external conflict and internal response
- Standard scene arc with clear beats""",
        }
        return instructions.get(strategy, "")

    # -------------------------------------------------------------------------
    # Stage 3: Scoring
    # -------------------------------------------------------------------------

    async def _score_variants(
        self,
        variants: List[SceneVariant],
        voice_bundle: Optional[VoiceBundleContext],
        story_bible: Optional[StoryBibleContext],
        phase: str,
    ) -> List[SceneVariant]:
        """Score all variants using SceneAnalyzerService."""
        logger.info(f"Scoring {len(variants)} variants")

        for variant in variants:
            try:
                analysis = await self.analyzer_service.analyze_scene(
                    scene_id=variant.variant_id,
                    scene_content=variant.content,
                    voice_bundle=voice_bundle,
                    story_bible=story_bible,
                    phase=phase,
                )
                variant.score = analysis.total_score
                variant.grade = analysis.grade
                variant.analysis = analysis
            except Exception as e:
                logger.error(f"Scoring failed for {variant.variant_id}: {e}")
                variant.score = 0
                variant.grade = "F"

        return variants

    # -------------------------------------------------------------------------
    # Stage 4: Hybrid Creation
    # -------------------------------------------------------------------------

    async def create_hybrid(
        self,
        scene_id: str,
        variants: List[SceneVariant],
        hybrid_request: HybridRequest,
        voice_bundle: Optional[VoiceBundleContext] = None,
    ) -> SceneVariant:
        """
        Create a hybrid scene from multiple variant sources.

        Args:
            scene_id: Scene identifier
            variants: List of available variants
            hybrid_request: Instructions for combining variants
            voice_bundle: Voice Bundle for context

        Returns:
            New hybrid SceneVariant
        """
        logger.info(f"Creating hybrid for {scene_id}")

        # Build variant lookup
        variant_lookup = {v.variant_id: v for v in variants}

        # Extract source sections
        source_sections = []
        for source in hybrid_request.sources:
            variant = variant_lookup.get(source["variant_id"])
            if variant:
                source_sections.append(f"""
## Source: {source['variant_id']} ({source.get('section', 'full')})
Score: {variant.score}/100
Model: {variant.model_name}

{variant.content}
""")

        voice_context = self._build_voice_context(voice_bundle) if voice_bundle else ""

        prompt = f"""Create a hybrid scene by combining the best elements from these sources.

{chr(10).join(source_sections)}

## HYBRID INSTRUCTIONS
{hybrid_request.instructions}

{voice_context}

Write the complete hybrid scene, seamlessly combining the best elements.
Maintain consistent voice throughout - the character thinking and observing, not AI explaining.
Fix any anti-patterns (no "with X precision", no similes, no passive voice)."""

        import time
        start_time = time.time()

        try:
            content = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a skilled editor creating a hybrid scene from multiple sources.",
                prompt=prompt,
            )

            generation_time = time.time() - start_time
            word_count = len(content.split())

            return SceneVariant(
                variant_id=f"HYBRID-{scene_id}",
                model_name="Hybrid (Claude)",
                strategy=WritingStrategy.BALANCED,
                content=content,
                word_count=word_count,
                generation_time=generation_time,
            )

        except Exception as e:
            logger.error(f"Hybrid creation failed: {e}")
            raise

    # -------------------------------------------------------------------------
    # Quick Generation (Single Model)
    # -------------------------------------------------------------------------

    async def generate_single_scene(
        self,
        scene_id: str,
        scaffold: Scaffold,
        voice_bundle: Optional[VoiceBundleContext] = None,
        strategy: WritingStrategy = WritingStrategy.BALANCED,
        model: Optional[Dict] = None,
        target_word_count: int = 1500,
    ) -> SceneVariant:
        """
        Quick scene generation with a single model (no tournament).

        Useful for drafts or when speed matters more than variety.
        """
        model = model or self.tournament_models[0]

        # Create minimal structure variant
        structure = StructureVariant(
            variant_id="QUICK",
            beat_count=3,
            scene_sequence=["Opening", "Development", "Conclusion"],
            strategic_rationale="Quick generation structure",
            pacing="medium",
            focus="balanced",
        )

        voice_context = self._build_voice_context(voice_bundle)
        base_prompt = self._build_scene_prompt(
            scaffold=scaffold,
            structure_variant=structure,
            voice_context=voice_context,
            target_word_count=target_word_count,
        )

        return await self._generate_single_variant(
            scene_id=scene_id,
            base_prompt=base_prompt,
            model_config=model,
            strategy=strategy,
            target_word_count=target_word_count,
        )


# =============================================================================
# Service Singleton
# =============================================================================

_scene_writer_service: Optional[SceneWriterService] = None


def get_scene_writer_service() -> SceneWriterService:
    """Get or create the SceneWriterService singleton."""
    global _scene_writer_service
    if _scene_writer_service is None:
        _scene_writer_service = SceneWriterService()
    return _scene_writer_service
