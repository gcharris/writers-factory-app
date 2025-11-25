"""
Tournament Service - Phase 4 Multi-Model Tournament System

Orchestrates multi-model variant tournaments for structure and scene generation.
Automates STEP 2 (Structure Variants) and STEP 3 (Scene Variants) from the
manual workflow with parallel execution and consensus detection.

Key Features:
- Parallel variant generation across multiple models × strategies
- Automatic scoring using SceneAnalyzerService rubric
- Consensus detection to identify high-agreement sections
- Hybrid creator for merging best parts from multiple variants

Integration Points:
- ModelOrchestrator: Tier-based model routing
- SceneAnalyzerService: 5-category scoring
- VoiceCalibrationService: Voice authentication checks
- LLMService: Multi-provider model calls
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any, Dict, List, Optional, Tuple

from backend.models.tournament import (
    Tournament,
    TournamentConfig,
    TournamentRound,
    TournamentStatus,
    TournamentType,
    Variant,
    VariantStrategy,
    ScoreBreakdown,
    ConsensusReport,
    RankedResults,
    HybridSceneConfig,
    AgentConfig,
)
from backend.services.llm_service import LLMService
from backend.services.model_orchestrator import ModelOrchestrator, SelectionCriteria
from backend.services.scene_analyzer_service import (
    SceneAnalyzerService,
    VoiceBundleContext,
    get_scene_analyzer_service,
)
from backend.services.model_capabilities import get_model_capabilities

logger = logging.getLogger(__name__)


# =============================================================================
# Prompt Templates
# =============================================================================

STRUCTURE_VARIANT_PROMPT = """You are a master storyteller creating a structural variant of a scene.

STRATEGY: {strategy_name}
{strategy_description}

SOURCE MATERIAL:
{source_material}

CONTEXT:
{source_context}

{voice_instructions}

Generate a structural outline/variant that reimagines this scene with the {strategy_name} approach.
Include:
1. Scene opening beat
2. Rising action beats (2-3)
3. Turning point/climax beat
4. Resolution/transition beat

For each beat, provide:
- What happens (2-3 sentences)
- Emotional register
- Key sensory detail

Write the structural variant now. Do not include preamble or meta-commentary."""

SCENE_VARIANT_PROMPT = """You are a master prose writer creating a scene variant.

STRATEGY: {strategy_name}
{strategy_description}

SOURCE MATERIAL:
{source_material}

CONTEXT:
{source_context}

{voice_instructions}

Write a full scene using the {strategy_name} approach. Requirements:
- Maintain consistent POV throughout
- Show, don't tell - embed emotion in action
- Use sensory grounding for setting
- Avoid AI anti-patterns: "crucial", "tapestry", "nestled", "in the heart of"
- Target 500-800 words

Write the scene now. Do not include any preamble or explanation - just the creative writing."""

HYBRID_MERGE_PROMPT = """You are an expert editor merging the best elements from multiple scene variants.

VARIANTS TO MERGE:
{variants_text}

MERGE INSTRUCTIONS:
{merge_instructions}

TARGET:
- Create a cohesive scene that combines the strongest paragraphs from each variant
- Maintain consistent voice and POV throughout
- Smooth transitions between merged sections
- Target word count: {target_word_count} words

PRESERVE FROM PRIMARY VARIANT ({primary_variant_id}):
- Overall voice and tone
- POV consistency
- Opening and closing beats

Write the merged scene now. Output only the final scene text."""


# =============================================================================
# Tournament Service
# =============================================================================

class TournamentService:
    """
    Orchestrates multi-model variant tournaments.

    Manages the full tournament lifecycle:
    1. Create tournament with configuration
    2. Run rounds with parallel variant generation
    3. Score variants automatically
    4. Detect consensus across variants
    5. Create hybrid scenes from selected variants
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        orchestrator: Optional[ModelOrchestrator] = None,
        scene_analyzer: Optional[SceneAnalyzerService] = None,
    ):
        """
        Initialize Tournament Service with dependencies.

        Args:
            llm_service: LLM service for model calls
            orchestrator: Model orchestrator for selection
            scene_analyzer: Scene analyzer for scoring
        """
        self.llm_service = llm_service or LLMService()
        self.orchestrator = orchestrator or ModelOrchestrator()
        self.scene_analyzer = scene_analyzer or get_scene_analyzer_service()

        # In-memory tournament storage (would be database in production)
        self._tournaments: Dict[str, Tournament] = {}

        logger.info("TournamentService initialized")

    # =========================================================================
    # Tournament Lifecycle
    # =========================================================================

    def create_tournament(self, config: TournamentConfig) -> Tournament:
        """
        Create a new tournament with the given configuration.

        Args:
            config: Tournament configuration

        Returns:
            Created Tournament object
        """
        tournament_id = f"tournament_{config.project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        tournament = Tournament(
            id=tournament_id,
            tournament_type=config.tournament_type,
            project_id=config.project_id,
            config=config,
            status=TournamentStatus.PENDING,
        )

        self._tournaments[tournament_id] = tournament
        logger.info(f"Created tournament: {tournament_id} (type: {config.tournament_type.value})")

        return tournament

    async def run_round(
        self,
        tournament_id: str,
        round_number: int = 1,
    ) -> TournamentRound:
        """
        Run a tournament round - generate variants from all agents.

        Args:
            tournament_id: ID of the tournament
            round_number: Round number (default: 1)

        Returns:
            TournamentRound with generated variants
        """
        tournament = self.get_tournament(tournament_id)
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")

        # Update status
        tournament.status = TournamentStatus.RUNNING
        tournament.started_at = datetime.now(timezone.utc).isoformat()

        # Create round
        round_ = TournamentRound(
            round_number=round_number,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        try:
            # Load voice bundle if specified
            voice_context = None
            if tournament.config.voice_bundle_path:
                voice_bundle_path = Path(tournament.config.voice_bundle_path)
                if voice_bundle_path.exists():
                    voice_context = VoiceBundleContext.from_directory(voice_bundle_path)

            # Generate variants in parallel
            if tournament.config.parallel_execution:
                variants = await self._generate_variants_parallel(tournament, voice_context)
            else:
                variants = await self._generate_variants_sequential(tournament, voice_context)

            round_.variants = variants

            # Auto-score if enabled
            if tournament.config.auto_score:
                tournament.status = TournamentStatus.SCORING
                await self._score_variants(round_, voice_context)

            # Calculate consensus
            round_.consensus_score = self._calculate_consensus_score(round_.variants)

            round_.completed_at = datetime.now(timezone.utc).isoformat()
            tournament.rounds.append(round_)

            # Update tournament totals
            tournament.total_cost_usd = sum(v.cost_usd for v in tournament.all_variants)
            tournament.total_tokens_input = sum(v.token_count_input for v in tournament.all_variants)
            tournament.total_tokens_output = sum(v.token_count_output for v in tournament.all_variants)

            tournament.status = TournamentStatus.AWAITING_SELECTION

            logger.info(
                f"Round {round_number} complete: {len(variants)} variants, "
                f"consensus score: {round_.consensus_score:.1f}"
            )

        except Exception as e:
            tournament.status = TournamentStatus.FAILED
            tournament.error_message = str(e)
            logger.error(f"Tournament round failed: {e}")
            raise

        return round_

    async def _generate_variants_parallel(
        self,
        tournament: Tournament,
        voice_context: Optional[VoiceBundleContext],
    ) -> List[Variant]:
        """
        Generate all variants in parallel.

        Creates tasks for each (agent × strategy) combination and runs
        them concurrently using asyncio.gather.
        """
        tasks = []
        config = tournament.config

        for agent in config.agents:
            if not agent.enabled:
                continue

            for strategy in config.strategies[:config.max_variants_per_agent]:
                tasks.append(
                    self._generate_single_variant(
                        tournament=tournament,
                        agent=agent,
                        strategy=strategy,
                        voice_context=voice_context,
                    )
                )

        logger.info(f"Starting parallel generation of {len(tasks)} variants")

        # Run all generation tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful variants
        variants = []
        for result in results:
            if isinstance(result, Variant):
                variants.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Variant generation failed: {result}")

        logger.info(f"Generated {len(variants)} variants successfully")
        return variants

    async def _generate_variants_sequential(
        self,
        tournament: Tournament,
        voice_context: Optional[VoiceBundleContext],
    ) -> List[Variant]:
        """
        Generate variants sequentially (for debugging or rate limiting).
        """
        variants = []
        config = tournament.config

        for agent in config.agents:
            if not agent.enabled:
                continue

            for strategy in config.strategies[:config.max_variants_per_agent]:
                try:
                    variant = await self._generate_single_variant(
                        tournament=tournament,
                        agent=agent,
                        strategy=strategy,
                        voice_context=voice_context,
                    )
                    variants.append(variant)
                except Exception as e:
                    logger.error(f"Failed to generate variant from {agent.agent_id}/{strategy.value}: {e}")

        return variants

    async def _generate_single_variant(
        self,
        tournament: Tournament,
        agent: AgentConfig,
        strategy: VariantStrategy,
        voice_context: Optional[VoiceBundleContext],
    ) -> Variant:
        """
        Generate a single variant from one agent with one strategy.
        """
        variant_id = f"{tournament.id}_{agent.agent_id}_{strategy.value}_{uuid.uuid4().hex[:6]}"
        config = tournament.config

        # Build prompt based on tournament type
        if config.tournament_type == TournamentType.STRUCTURE_VARIANT:
            prompt = self._build_structure_prompt(config, strategy, voice_context)
        else:
            prompt = self._build_scene_prompt(config, strategy, voice_context)

        # Time the generation
        start_time = datetime.now()

        try:
            response = await self.llm_service.generate_response(
                provider=agent.provider,
                model=agent.model,
                system_role="You are a master storyteller. Write creative, authentic prose.",
                prompt=prompt,
            )

            generation_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            # Check for error response
            if response.startswith("Error"):
                raise Exception(response)

            # Estimate costs
            model_caps = get_model_capabilities(agent.model)
            input_tokens = len(prompt) // 4  # Rough estimate
            output_tokens = len(response) // 4

            cost = 0.0
            if model_caps:
                cost = (
                    (input_tokens / 1_000_000) * model_caps.cost_per_1m_input +
                    (output_tokens / 1_000_000) * model_caps.cost_per_1m_output
                )

            return Variant(
                id=variant_id,
                agent_id=agent.agent_id,
                strategy=strategy,
                content=response,
                generation_time_ms=generation_time_ms,
                token_count_input=input_tokens,
                token_count_output=output_tokens,
                cost_usd=cost,
            )

        except Exception as e:
            logger.error(f"Generation failed for {agent.agent_id}/{strategy.value}: {e}")
            raise

    def _build_structure_prompt(
        self,
        config: TournamentConfig,
        strategy: VariantStrategy,
        voice_context: Optional[VoiceBundleContext],
    ) -> str:
        """Build prompt for structure variant generation."""
        voice_instructions = ""
        if voice_context and voice_context.gold_standard:
            voice_instructions = f"""VOICE REFERENCE:
{voice_context.gold_standard[:1000]}

Match this voice quality and style."""

        return STRUCTURE_VARIANT_PROMPT.format(
            strategy_name=strategy.value.upper(),
            strategy_description=strategy.description,
            source_material=config.source_material,
            source_context=config.source_context,
            voice_instructions=voice_instructions,
        )

    def _build_scene_prompt(
        self,
        config: TournamentConfig,
        strategy: VariantStrategy,
        voice_context: Optional[VoiceBundleContext],
    ) -> str:
        """Build prompt for scene variant generation."""
        voice_instructions = ""
        if voice_context and voice_context.gold_standard:
            voice_instructions = f"""VOICE REFERENCE:
{voice_context.gold_standard[:1500]}

Anti-Patterns to Avoid:
{voice_context.anti_patterns[:500] if voice_context.anti_patterns else "Standard AI anti-patterns"}

Match this voice quality and style while avoiding the anti-patterns."""

        return SCENE_VARIANT_PROMPT.format(
            strategy_name=strategy.value.upper(),
            strategy_description=strategy.description,
            source_material=config.source_material,
            source_context=config.source_context,
            voice_instructions=voice_instructions,
        )

    # =========================================================================
    # Scoring
    # =========================================================================

    async def _score_variants(
        self,
        round_: TournamentRound,
        voice_context: Optional[VoiceBundleContext],
    ):
        """
        Score all variants in a round using SceneAnalyzerService.
        """
        logger.info(f"Scoring {len(round_.variants)} variants...")

        # Score variants in parallel
        tasks = [
            self._score_single_variant(variant, voice_context)
            for variant in round_.variants
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for variant, result in zip(round_.variants, results):
            if isinstance(result, ScoreBreakdown):
                variant.scores = result
            elif isinstance(result, Exception):
                logger.error(f"Scoring failed for {variant.id}: {result}")
                # Assign default score
                variant.scores = ScoreBreakdown(total_score=50, grade="C")

    async def _score_single_variant(
        self,
        variant: Variant,
        voice_context: Optional[VoiceBundleContext],
    ) -> ScoreBreakdown:
        """
        Score a single variant using the scene analyzer.
        """
        try:
            result = await self.scene_analyzer.analyze_scene(
                scene_id=variant.id,
                scene_content=variant.content,
                voice_bundle=voice_context,
                pov_character="protagonist",  # Could be configurable
                phase="act2",  # Could be configurable
            )

            return ScoreBreakdown(
                total_score=result.total_score,
                grade=result.grade,
                voice_authenticity=result.categories["voice_authenticity"].score,
                character_consistency=result.categories["character_consistency"].score,
                metaphor_discipline=result.categories["metaphor_discipline"].score,
                anti_pattern_compliance=result.categories["anti_pattern_compliance"].score,
                phase_appropriateness=result.categories["phase_appropriateness"].score,
                word_count=len(variant.content.split()),
                violation_count=len(result.violations),
                notes=result.action_prompt or "",
            )

        except Exception as e:
            logger.error(f"Scoring error for {variant.id}: {e}")
            raise

    def aggregate_scores(self, variants: List[Variant]) -> RankedResults:
        """
        Aggregate and rank variant scores.

        Args:
            variants: List of scored variants

        Returns:
            RankedResults with rankings and statistics
        """
        # Get scores
        scored_variants = [v for v in variants if v.scores]
        if not scored_variants:
            return RankedResults(
                tournament_id="",
                round_number=0,
                ranked_variants=[],
                top_tier=[],
                mid_tier=[],
                bottom_tier=[],
                average_score=0,
                median_score=0,
                score_std_dev=0,
            )

        scores = [v.scores.total_score for v in scored_variants]

        # Sort by score
        sorted_variants = sorted(
            scored_variants,
            key=lambda v: v.scores.total_score,
            reverse=True
        )

        # Create ranked list
        ranked = []
        for rank, variant in enumerate(sorted_variants, 1):
            ranked.append({
                "variant_id": variant.id,
                "rank": rank,
                "score": variant.scores.total_score,
                "grade": variant.scores.grade,
                "agent_id": variant.agent_id,
                "strategy": variant.strategy.value,
            })

        # Calculate tier thresholds
        n = len(sorted_variants)
        top_n = max(1, n // 5)  # Top 20%
        bottom_n = max(1, n // 5)  # Bottom 20%

        top_tier = [v.id for v in sorted_variants[:top_n]]
        bottom_tier = [v.id for v in sorted_variants[-bottom_n:]]
        mid_tier = [v.id for v in sorted_variants[top_n:-bottom_n] if n > 2]

        return RankedResults(
            tournament_id=sorted_variants[0].id.split("_")[0] if sorted_variants else "",
            round_number=1,
            ranked_variants=ranked,
            top_tier=top_tier,
            mid_tier=mid_tier,
            bottom_tier=bottom_tier,
            average_score=mean(scores),
            median_score=median(scores),
            score_std_dev=stdev(scores) if len(scores) > 1 else 0,
        )

    # =========================================================================
    # Consensus Detection
    # =========================================================================

    def detect_consensus(self, variants: List[Variant]) -> ConsensusReport:
        """
        Detect consensus/agreement across variants.

        Analyzes where variants agree (high confidence) and diverge
        (areas needing human review).

        Args:
            variants: List of variants to analyze

        Returns:
            ConsensusReport with agreement metrics
        """
        if not variants:
            return ConsensusReport(
                tournament_id="",
                round_number=0,
                overall_consensus=0,
                high_agreement_sections=[],
                divergent_sections=[],
                variant_alignments={},
                recommendation="No variants to analyze",
            )

        tournament_id = variants[0].id.rsplit("_", 2)[0]

        # Calculate score variance for consensus
        scored = [v for v in variants if v.scores]
        if not scored:
            return ConsensusReport(
                tournament_id=tournament_id,
                round_number=1,
                overall_consensus=50,
                high_agreement_sections=[],
                divergent_sections=[],
                variant_alignments={v.id: 0.5 for v in variants},
                recommendation="Variants not yet scored. Score variants first for consensus analysis.",
            )

        scores = [v.scores.total_score for v in scored]
        avg_score = mean(scores)
        score_spread = max(scores) - min(scores)

        # Consensus score: inverse of spread (closer scores = higher consensus)
        # Max spread of 100 maps to 0 consensus, spread of 0 maps to 100 consensus
        overall_consensus = max(0, 100 - score_spread)

        # Calculate per-variant alignment (how close to average)
        variant_alignments = {}
        for variant in scored:
            deviation = abs(variant.scores.total_score - avg_score)
            alignment = 1.0 - (deviation / 50)  # Normalize to 0-1
            variant_alignments[variant.id] = max(0, min(1, alignment))

        # Identify high-agreement and divergent sections
        high_agreement = []
        divergent = []

        # Analyze category agreement
        category_scores = {
            "voice_authenticity": [],
            "character_consistency": [],
            "metaphor_discipline": [],
            "anti_pattern_compliance": [],
            "phase_appropriateness": [],
        }

        for variant in scored:
            category_scores["voice_authenticity"].append(variant.scores.voice_authenticity)
            category_scores["character_consistency"].append(variant.scores.character_consistency)
            category_scores["metaphor_discipline"].append(variant.scores.metaphor_discipline)
            category_scores["anti_pattern_compliance"].append(variant.scores.anti_pattern_compliance)
            category_scores["phase_appropriateness"].append(variant.scores.phase_appropriateness)

        for category, cat_scores in category_scores.items():
            cat_spread = max(cat_scores) - min(cat_scores)
            if cat_spread <= 5:
                high_agreement.append(category)
            elif cat_spread >= 10:
                divergent.append(category)

        # Generate recommendation
        if overall_consensus >= 80:
            recommendation = "High consensus across variants. Top-ranked variant is a safe choice."
        elif overall_consensus >= 60:
            recommendation = "Moderate consensus. Review top 3 variants for final selection."
        elif overall_consensus >= 40:
            recommendation = "Mixed consensus. Consider hybrid approach combining best elements."
        else:
            recommendation = "Low consensus. Manual review recommended before selection."

        if divergent:
            recommendation += f" Pay attention to divergent areas: {', '.join(divergent)}."

        return ConsensusReport(
            tournament_id=tournament_id,
            round_number=1,
            overall_consensus=overall_consensus,
            high_agreement_sections=high_agreement,
            divergent_sections=divergent,
            variant_alignments=variant_alignments,
            recommendation=recommendation,
        )

    def _calculate_consensus_score(self, variants: List[Variant]) -> float:
        """Calculate simple consensus score for a round."""
        report = self.detect_consensus(variants)
        return report.overall_consensus

    # =========================================================================
    # Hybrid Creator
    # =========================================================================

    async def create_hybrid(
        self,
        config: HybridSceneConfig,
    ) -> str:
        """
        Create a hybrid scene by merging selected variants.

        Uses LLM to intelligently merge the best paragraphs from
        multiple variants into a cohesive final scene.

        Args:
            config: Hybrid creation configuration

        Returns:
            Merged scene content
        """
        tournament = self.get_tournament(config.tournament_id)
        if not tournament:
            raise ValueError(f"Tournament {config.tournament_id} not found")

        # Get selected variants
        selected_variants = []
        for variant_id in config.selected_variant_ids:
            variant = tournament.get_variant_by_id(variant_id)
            if variant:
                selected_variants.append(variant)

        if len(selected_variants) < 2:
            raise ValueError("Need at least 2 variants for hybrid creation")

        # Build merge prompt
        variants_text = ""
        for i, variant in enumerate(selected_variants, 1):
            variants_text += f"""
--- VARIANT {i} (ID: {variant.id}, Agent: {variant.agent_id}, Strategy: {variant.strategy.value}) ---
Score: {variant.scores.total_score if variant.scores else 'N/A'}

{variant.content}

"""

        primary_id = config.preserve_voice_from or selected_variants[0].id
        merge_instructions = f"""
Merge Strategy: {config.merge_strategy}
- Preserve voice from: {primary_id}
- Maintain pacing: {"Yes" if config.maintain_pacing else "No"}
- Smooth transitions: {"Yes" if config.smooth_transitions else "No"}
"""

        target_word_count = config.target_word_count or 600

        prompt = HYBRID_MERGE_PROMPT.format(
            variants_text=variants_text,
            merge_instructions=merge_instructions,
            target_word_count=target_word_count,
            primary_variant_id=primary_id,
        )

        # Use premium model for hybrid creation
        criteria = SelectionCriteria(
            task_type="creative_writing",
            quality_tier="premium",
        )
        model_id = self.orchestrator.select_model(criteria)
        model_caps = get_model_capabilities(model_id)

        provider = model_caps.provider if model_caps else "anthropic"
        model = model_id

        logger.info(f"Creating hybrid using {model}")

        try:
            hybrid_content = await self.llm_service.generate_response(
                provider=provider,
                model=model,
                system_role="You are an expert editor creating a cohesive scene from multiple variants.",
                prompt=prompt,
            )

            # Store hybrid in tournament
            tournament.hybrid_content = hybrid_content

            # Mark selected variants
            for variant in selected_variants:
                variant.selected_for_hybrid = True

            logger.info(f"Created hybrid scene: {len(hybrid_content.split())} words")
            return hybrid_content

        except Exception as e:
            logger.error(f"Hybrid creation failed: {e}")
            raise

    # =========================================================================
    # Tournament Management
    # =========================================================================

    def get_tournament(self, tournament_id: str) -> Optional[Tournament]:
        """Get tournament by ID."""
        return self._tournaments.get(tournament_id)

    def get_tournament_results(self, tournament_id: str) -> Dict[str, Any]:
        """Get formatted tournament results."""
        tournament = self.get_tournament(tournament_id)
        if not tournament:
            return {"error": f"Tournament {tournament_id} not found"}

        # Get ranked results
        ranked = self.aggregate_scores(tournament.all_variants)
        consensus = self.detect_consensus(tournament.all_variants)

        return {
            "tournament": tournament.to_dict(),
            "ranked_results": ranked.to_dict(),
            "consensus_report": consensus.to_dict(),
            "summary": {
                "total_variants": len(tournament.all_variants),
                "total_cost": tournament.total_cost_usd,
                "top_variant_id": ranked.ranked_variants[0]["variant_id"] if ranked.ranked_variants else None,
                "top_score": ranked.ranked_variants[0]["score"] if ranked.ranked_variants else None,
                "consensus_score": consensus.overall_consensus,
            },
        }

    def select_winner(
        self,
        tournament_id: str,
        winner_variant_id: str,
    ) -> Tournament:
        """
        Select the winning variant for a tournament.

        Args:
            tournament_id: Tournament ID
            winner_variant_id: ID of the winning variant

        Returns:
            Updated Tournament
        """
        tournament = self.get_tournament(tournament_id)
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")

        variant = tournament.get_variant_by_id(winner_variant_id)
        if not variant:
            raise ValueError(f"Variant {winner_variant_id} not found")

        tournament.winner_variant_id = winner_variant_id
        tournament.status = TournamentStatus.COMPLETE
        tournament.completed_at = datetime.now(timezone.utc).isoformat()

        logger.info(f"Tournament {tournament_id} complete. Winner: {winner_variant_id}")
        return tournament

    def list_tournaments(
        self,
        project_id: Optional[str] = None,
        status: Optional[TournamentStatus] = None,
    ) -> List[Tournament]:
        """
        List tournaments with optional filters.

        Args:
            project_id: Filter by project
            status: Filter by status

        Returns:
            List of matching tournaments
        """
        tournaments = list(self._tournaments.values())

        if project_id:
            tournaments = [t for t in tournaments if t.project_id == project_id]

        if status:
            tournaments = [t for t in tournaments if t.status == status]

        return sorted(tournaments, key=lambda t: t.created_at, reverse=True)


# =============================================================================
# Singleton Access
# =============================================================================

_tournament_service: Optional[TournamentService] = None


def get_tournament_service() -> TournamentService:
    """Get or create the TournamentService singleton."""
    global _tournament_service
    if _tournament_service is None:
        _tournament_service = TournamentService()
    return _tournament_service
