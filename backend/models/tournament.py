"""
Tournament Models - Phase 4 Multi-Model Tournament System

Data models for structure and scene variant tournaments, enabling parallel
multi-model execution and consensus-based selection.

Tournament Types:
- STRUCTURE_VARIANT: Generate structural variants (STEP 2 from manual workflow)
- SCENE_VARIANT: Generate scene variants (STEP 3 from manual workflow)

Workflow Mapping:
- Manual STEP 2: 5 sequential variants → Automated: 15 parallel (3 models × 5 strategies)
- Manual STEP 3: 5 sequential variants → Automated: 15-25 parallel with consensus detection
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# Enums
# =============================================================================

class TournamentType(Enum):
    """Type of tournament."""
    STRUCTURE_VARIANT = "structure_variant"  # STEP 2: Structure variants
    SCENE_VARIANT = "scene_variant"          # STEP 3: Scene variants


class TournamentStatus(Enum):
    """Status of a tournament."""
    PENDING = "pending"              # Created but not started
    RUNNING = "running"              # Variants being generated
    SCORING = "scoring"              # Variants generated, scoring in progress
    AWAITING_SELECTION = "awaiting_selection"  # Ready for user selection
    COMPLETE = "complete"            # Winner selected, tournament done
    FAILED = "failed"                # Error during execution


class VariantStrategy(Enum):
    """
    Variant generation strategies - same as voice calibration but applied
    to structure/scene generation.

    Each strategy emphasizes different narrative elements, creating diverse
    variants for comparison and selection.
    """
    ACTION = "action"          # Fast pacing, physical detail, external conflict
    CHARACTER = "character"    # Slower pacing, internal landscape, psychology
    DIALOGUE = "dialogue"      # Conversation-centered, conflict through words
    BRAINSTORMING = "brainstorming"  # Idea exploration, divergent thinking
    BALANCED = "balanced"      # Mix of elements, standard structure

    @property
    def description(self) -> str:
        """Get human-readable description for the strategy."""
        descriptions = {
            "action": "Fast pacing, physical detail, external conflict, dialogue in motion",
            "character": "Slower pacing, internal landscape, psychology foregrounded",
            "dialogue": "Conversation-centered, conflict through words, subtext",
            "brainstorming": "Idea exploration, multiple perspectives, experimental approaches",
            "balanced": "Mix of elements, standard structure, reliable execution",
        }
        return descriptions.get(self.value, "")


# =============================================================================
# Configuration Data Classes
# =============================================================================

@dataclass
class AgentConfig:
    """
    Configuration for a participating agent in the tournament.

    Agents are AI models that generate variants. Multiple agents compete
    in parallel, each producing variants across different strategies.
    """
    agent_id: str          # e.g., "claude", "gpt4", "deepseek"
    provider: str          # e.g., "anthropic", "openai", "deepseek"
    model: str             # e.g., "claude-3-5-sonnet-20241022", "gpt-4o"
    quality_tier: str      # "budget" | "balanced" | "premium"
    enabled: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TournamentConfig:
    """
    Configuration for creating a tournament.

    Defines the tournament type, participating agents, strategies to use,
    and source material for variant generation.
    """
    tournament_type: TournamentType
    project_id: str

    # Agents participating in the tournament
    agents: List[AgentConfig]

    # Strategies to apply (default: all 5)
    strategies: List[VariantStrategy] = field(
        default_factory=lambda: list(VariantStrategy)
    )

    # Source material for generation
    source_material: str = ""          # The content to create variants from
    source_context: str = ""           # Additional context (scene brief, chapter summary)
    voice_bundle_path: Optional[str] = None  # Path to voice bundle for voice checks

    # Tournament settings
    max_variants_per_agent: int = 5    # Maximum variants per agent
    parallel_execution: bool = True    # Run all variants in parallel
    auto_score: bool = True            # Automatically score variants

    def to_dict(self) -> Dict:
        return {
            "tournament_type": self.tournament_type.value,
            "project_id": self.project_id,
            "agents": [a.to_dict() for a in self.agents],
            "strategies": [s.value for s in self.strategies],
            "source_material": self.source_material[:500] + "..." if len(self.source_material) > 500 else self.source_material,
            "source_context": self.source_context[:200] + "..." if len(self.source_context) > 200 else self.source_context,
            "voice_bundle_path": self.voice_bundle_path,
            "max_variants_per_agent": self.max_variants_per_agent,
            "parallel_execution": self.parallel_execution,
            "auto_score": self.auto_score,
        }


# =============================================================================
# Score Data Classes
# =============================================================================

@dataclass
class ScoreBreakdown:
    """
    Detailed score breakdown for a variant.

    Uses the same 5-category, 100-point rubric from SceneAnalyzerService:
    - Voice Authenticity (30 pts)
    - Character Consistency (20 pts)
    - Metaphor Discipline (20 pts)
    - Anti-Pattern Compliance (15 pts)
    - Phase Appropriateness (15 pts)
    """
    total_score: int = 0
    grade: str = "D"  # A, A-, B+, B, B-, C+, C, D, F

    # Category scores
    voice_authenticity: int = 0
    character_consistency: int = 0
    metaphor_discipline: int = 0
    anti_pattern_compliance: int = 0
    phase_appropriateness: int = 0

    # Additional metrics
    word_count: int = 0
    violation_count: int = 0
    consensus_alignment: float = 0.0  # 0-1, how much it agrees with other variants

    # Notes from scoring
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_scene_analysis(cls, analysis_result) -> "ScoreBreakdown":
        """
        Create ScoreBreakdown from SceneAnalysisResult.

        This bridges the existing SceneAnalyzerService output to our
        tournament scoring format.
        """
        return cls(
            total_score=analysis_result.total_score,
            grade=analysis_result.grade,
            voice_authenticity=analysis_result.categories.get("voice_authenticity", {}).get("score", 0) if isinstance(analysis_result.categories.get("voice_authenticity"), dict) else analysis_result.categories.get("voice_authenticity").score if hasattr(analysis_result.categories.get("voice_authenticity"), "score") else 0,
            character_consistency=analysis_result.categories.get("character_consistency", {}).get("score", 0) if isinstance(analysis_result.categories.get("character_consistency"), dict) else analysis_result.categories.get("character_consistency").score if hasattr(analysis_result.categories.get("character_consistency"), "score") else 0,
            metaphor_discipline=analysis_result.categories.get("metaphor_discipline", {}).get("score", 0) if isinstance(analysis_result.categories.get("metaphor_discipline"), dict) else analysis_result.categories.get("metaphor_discipline").score if hasattr(analysis_result.categories.get("metaphor_discipline"), "score") else 0,
            anti_pattern_compliance=analysis_result.categories.get("anti_pattern_compliance", {}).get("score", 0) if isinstance(analysis_result.categories.get("anti_pattern_compliance"), dict) else analysis_result.categories.get("anti_pattern_compliance").score if hasattr(analysis_result.categories.get("anti_pattern_compliance"), "score") else 0,
            phase_appropriateness=analysis_result.categories.get("phase_appropriateness", {}).get("score", 0) if isinstance(analysis_result.categories.get("phase_appropriateness"), dict) else analysis_result.categories.get("phase_appropriateness").score if hasattr(analysis_result.categories.get("phase_appropriateness"), "score") else 0,
            violation_count=len(analysis_result.violations),
            notes=analysis_result.action_prompt or "",
        )


# =============================================================================
# Variant Data Class
# =============================================================================

@dataclass
class Variant:
    """
    A single generated variant from an agent.

    Represents one output from one agent using one strategy. A tournament
    generates multiple variants (e.g., 3 agents × 5 strategies = 15 variants).
    """
    id: str                           # Unique variant ID
    agent_id: str                     # Which agent generated this
    strategy: VariantStrategy         # Which strategy was used
    content: str                      # The generated text

    # Scoring
    scores: Optional[ScoreBreakdown] = None

    # Metadata
    generation_time_ms: int = 0       # How long generation took
    token_count_input: int = 0        # Input tokens used
    token_count_output: int = 0       # Output tokens generated
    cost_usd: float = 0.0             # Estimated cost in USD
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Selection tracking
    selected_for_hybrid: bool = False  # Included in hybrid output
    user_rating: Optional[int] = None  # User's 1-5 rating (optional)
    user_notes: str = ""               # User's notes on this variant

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "strategy": self.strategy.value,
            "content": self.content,
            "scores": self.scores.to_dict() if self.scores else None,
            "generation_time_ms": self.generation_time_ms,
            "token_count_input": self.token_count_input,
            "token_count_output": self.token_count_output,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp,
            "selected_for_hybrid": self.selected_for_hybrid,
            "user_rating": self.user_rating,
            "user_notes": self.user_notes,
        }

    @property
    def word_count(self) -> int:
        """Calculate word count of the variant content."""
        return len(self.content.split())


# =============================================================================
# Tournament Round Data Class
# =============================================================================

@dataclass
class TournamentRound:
    """
    A single round of variant generation.

    Most tournaments have one round, but complex tournaments may iterate
    with multiple rounds (e.g., top variants from round 1 compete in round 2).
    """
    round_number: int
    variants: List[Variant] = field(default_factory=list)

    # Round results
    winner_id: Optional[str] = None    # ID of winning variant
    consensus_score: float = 0.0       # 0-100, how much variants agree

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "round_number": self.round_number,
            "variants": [v.to_dict() for v in self.variants],
            "winner_id": self.winner_id,
            "consensus_score": self.consensus_score,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @property
    def variant_count(self) -> int:
        """Get number of variants in this round."""
        return len(self.variants)

    def get_ranked_variants(self) -> List[Variant]:
        """Get variants sorted by total score (descending)."""
        return sorted(
            self.variants,
            key=lambda v: v.scores.total_score if v.scores else 0,
            reverse=True
        )


# =============================================================================
# Tournament Data Class
# =============================================================================

@dataclass
class Tournament:
    """
    Complete tournament tracking structure.

    Tracks the full lifecycle of a tournament from creation through
    variant generation, scoring, selection, and optional hybrid creation.
    """
    id: str                            # Unique tournament ID
    tournament_type: TournamentType
    project_id: str

    # Configuration
    config: TournamentConfig

    # Rounds
    rounds: List[TournamentRound] = field(default_factory=list)

    # Status
    status: TournamentStatus = TournamentStatus.PENDING
    error_message: Optional[str] = None

    # Results
    winner_variant_id: Optional[str] = None
    hybrid_content: Optional[str] = None  # Combined content from selected variants

    # Cost tracking
    total_cost_usd: float = 0.0
    total_tokens_input: int = 0
    total_tokens_output: int = 0

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "tournament_type": self.tournament_type.value,
            "project_id": self.project_id,
            "config": self.config.to_dict(),
            "rounds": [r.to_dict() for r in self.rounds],
            "status": self.status.value,
            "error_message": self.error_message,
            "winner_variant_id": self.winner_variant_id,
            "hybrid_content": self.hybrid_content[:500] + "..." if self.hybrid_content and len(self.hybrid_content) > 500 else self.hybrid_content,
            "total_cost_usd": self.total_cost_usd,
            "total_tokens_input": self.total_tokens_input,
            "total_tokens_output": self.total_tokens_output,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    @property
    def current_round(self) -> Optional[TournamentRound]:
        """Get the most recent round."""
        return self.rounds[-1] if self.rounds else None

    @property
    def all_variants(self) -> List[Variant]:
        """Get all variants across all rounds."""
        variants = []
        for round_ in self.rounds:
            variants.extend(round_.variants)
        return variants

    def get_variant_by_id(self, variant_id: str) -> Optional[Variant]:
        """Find a variant by its ID."""
        for variant in self.all_variants:
            if variant.id == variant_id:
                return variant
        return None


# =============================================================================
# Hybrid Scene Configuration
# =============================================================================

@dataclass
class HybridSceneConfig:
    """
    Configuration for creating a hybrid scene from selected variants.

    The hybrid creator merges the best paragraphs from multiple variants
    into a cohesive final scene.
    """
    tournament_id: str
    selected_variant_ids: List[str]    # Variants to merge

    # Merge preferences
    merge_strategy: str = "paragraph"  # "paragraph" | "section" | "sentence"
    preserve_voice_from: Optional[str] = None  # Variant ID for voice reference

    # Output preferences
    target_word_count: Optional[int] = None
    maintain_pacing: bool = True
    smooth_transitions: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# Result Data Classes
# =============================================================================

@dataclass
class ConsensusReport:
    """
    Report on variant consensus/agreement.

    Identifies where multiple variants agree (high confidence areas) and
    where they diverge (areas needing human review).
    """
    tournament_id: str
    round_number: int

    # Consensus metrics
    overall_consensus: float           # 0-100, overall agreement level
    high_agreement_sections: List[str]  # Sections with strong consensus
    divergent_sections: List[str]      # Sections needing review

    # Per-variant alignment
    variant_alignments: Dict[str, float]  # variant_id -> alignment score

    # Recommendations
    recommendation: str                # Human-readable recommendation

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RankedResults:
    """
    Ranked results from scoring aggregation.

    Provides ordered list of variants by score with tier groupings.
    """
    tournament_id: str
    round_number: int

    # Ranked variants
    ranked_variants: List[Dict[str, Any]]  # {variant_id, rank, score, tier}

    # Tier groupings
    top_tier: List[str]     # Top 20% variant IDs
    mid_tier: List[str]     # Middle 60% variant IDs
    bottom_tier: List[str]  # Bottom 20% variant IDs

    # Statistics
    average_score: float
    median_score: float
    score_std_dev: float

    def to_dict(self) -> Dict:
        return asdict(self)
