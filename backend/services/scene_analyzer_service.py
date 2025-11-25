"""
Scene Analyzer Service - Phase 3B Director Mode

Evaluates scene drafts against a 5-category, 100-point scoring rubric.
The framework is "vanilla" - it references the writer's Voice Bundle and
Story Bible rather than hard-coded character-specific patterns.

Categories:
- Voice Authenticity (30 pts): Authenticity, Purpose, Fusion tests
- Character Consistency (20 pts): Psychology, Capability, Relationship
- Metaphor Discipline (20 pts): Domain rotation, Simile elimination, Transformation
- Anti-Pattern Compliance (15 pts): Zero-tolerance (-2), Formulaic (-1)
- Phase Appropriateness (15 pts): Voice complexity, Earned language
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.services.llm_service import LLMService
from backend.services.settings_service import settings_service

logger = logging.getLogger(__name__)


# =============================================================================
# Constants (Fallback defaults - overridden by Settings Service)
# =============================================================================

# DEFAULT VALUES - These are used ONLY if Settings Service fails to load
# The actual values come from settings_service.get() which uses 3-tier resolution:
# 1. Project-specific override (from voice_settings.yaml)
# 2. Global user setting
# 3. These defaults

DEFAULT_WEIGHTS = {
    "voice_authenticity": 30,
    "character_consistency": 20,
    "metaphor_discipline": 20,
    "anti_pattern_compliance": 15,
    "phase_appropriateness": 15,
}

# Grade thresholds (currently static, could be made dynamic in future)
GRADE_THRESHOLDS = {
    "A": 92,
    "A-": 85,
    "B+": 80,
    "B": 75,
    "B-": 70,
    "C+": 65,
    "C": 60,
    "D": 0,
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PatternViolation:
    """A detected anti-pattern violation."""
    pattern_name: str
    pattern_type: str  # "zero_tolerance" or "formulaic"
    description: str
    matched_text: str
    line_number: int
    penalty: int

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MetaphorAnalysis:
    """Analysis of metaphor usage in a scene."""
    total_metaphors: int
    domains: Dict[str, int]  # domain_name -> count
    domain_percentages: Dict[str, float]
    saturated_domains: List[str]  # domains over threshold
    simile_count: int
    simile_locations: List[Tuple[int, str]]  # (line_number, text)

    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "simile_locations": [(ln, txt) for ln, txt in self.simile_locations],
        }


@dataclass
class SubcategoryScore:
    """Score for a subcategory with notes."""
    score: int
    max_score: int
    notes: str = ""
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CategoryScore:
    """Score for a main category with subcategories."""
    name: str
    score: int
    max_score: int
    subcategories: Dict[str, SubcategoryScore]

    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "max": self.max_score,
            "subcategories": {k: v.to_dict() for k, v in self.subcategories.items()},
        }


@dataclass
class SceneAnalysisResult:
    """Complete analysis result for a scene."""
    scene_id: str
    total_score: int
    grade: str
    categories: Dict[str, CategoryScore]
    violations: List[PatternViolation]
    metaphor_analysis: Optional[MetaphorAnalysis]
    enhancement_needed: bool
    recommended_mode: str  # "none", "action_prompt", "six_pass", "rewrite"
    action_prompt: Optional[str]  # Generated fix instructions if needed
    analyzed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "total_score": self.total_score,
            "grade": self.grade,
            "categories": {k: v.to_dict() for k, v in self.categories.items()},
            "violations": [v.to_dict() for v in self.violations],
            "metaphor_analysis": self.metaphor_analysis.to_dict() if self.metaphor_analysis else None,
            "enhancement_needed": self.enhancement_needed,
            "recommended_mode": self.recommended_mode,
            "action_prompt": self.action_prompt,
            "analyzed_at": self.analyzed_at,
        }


@dataclass
class VoiceBundleContext:
    """
    Voice Bundle files loaded for analysis.

    The Voice Bundle now includes voice_settings.yaml (Phase 3C) which contains
    structured settings for scoring weights, anti-patterns, and enhancement thresholds.
    """
    gold_standard: str
    anti_patterns: str
    phase_evolution: str
    metaphor_domains: Dict[str, List[str]]  # domain_name -> keywords
    settings: Optional[Dict[str, Any]] = None  # NEW: voice_settings.yaml content

    @classmethod
    def from_directory(cls, voice_bundle_path: Path, load_settings: bool = True) -> "VoiceBundleContext":
        """
        Load Voice Bundle from directory.

        Args:
            voice_bundle_path: Path to voice bundle directory
            load_settings: If True, load voice_settings.yaml (default: True)

        Returns:
            VoiceBundleContext with all voice bundle files loaded
        """
        import yaml

        gold_standard = ""
        anti_patterns = ""
        phase_evolution = ""
        metaphor_domains = {}
        settings = None

        gold_path = voice_bundle_path / "Voice-Gold-Standard.md"
        if gold_path.exists():
            gold_standard = gold_path.read_text()
        else:
            # Try lowercase version (backward compatibility)
            gold_path_lower = voice_bundle_path / "voice_gold_standard.md"
            if gold_path_lower.exists():
                gold_standard = gold_path_lower.read_text()

        anti_path = voice_bundle_path / "Voice-Anti-Pattern-Sheet.md"
        if anti_path.exists():
            anti_patterns = anti_path.read_text()
        else:
            # Try lowercase version (backward compatibility)
            anti_path_lower = voice_bundle_path / "voice_anti_patterns.md"
            if anti_path_lower.exists():
                anti_patterns = anti_path_lower.read_text()

        phase_path = voice_bundle_path / "Phase-Evolution-Guide.md"
        if phase_path.exists():
            phase_evolution = phase_path.read_text()
        else:
            # Try lowercase version (backward compatibility)
            phase_path_lower = voice_bundle_path / "voice_phase_evolution.md"
            if phase_path_lower.exists():
                phase_evolution = phase_path_lower.read_text()

        domains_path = voice_bundle_path / "metaphor_domains.yaml"
        if domains_path.exists():
            with open(domains_path) as f:
                metaphor_domains = yaml.safe_load(f) or {}

        # Load voice_settings.yaml (Phase 3C addition)
        if load_settings:
            settings_path = voice_bundle_path / "voice_settings.yaml"
            if settings_path.exists():
                with open(settings_path) as f:
                    settings = yaml.safe_load(f) or {}
                logger.info(f"Loaded voice_settings.yaml from {voice_bundle_path}")

        return cls(
            gold_standard=gold_standard,
            anti_patterns=anti_patterns,
            phase_evolution=phase_evolution,
            metaphor_domains=metaphor_domains,
            settings=settings,
        )

    def get_project_id(self) -> Optional[str]:
        """
        Extract project_id from voice_settings.yaml.

        Returns:
            Project ID if found in settings, None otherwise
        """
        if self.settings:
            return self.settings.get("project_id")
        return None


@dataclass
class StoryBibleContext:
    """Relevant Story Bible context for analysis."""
    protagonist_name: str
    fatal_flaw: str
    the_lie: str
    theme: str
    current_phase: str  # e.g., "act1", "act2a", "act2b", "act3"
    character_capabilities: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)  # character -> relationship_type


# =============================================================================
# Scene Analyzer Service
# =============================================================================

class SceneAnalyzerService:
    """
    Analyzes scene drafts against the 5-category scoring rubric.

    Uses a combination of:
    - Automated pattern detection (anti-patterns, metaphor domains)
    - LLM-based evaluation (voice authenticity, character consistency)
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        weights: Optional[Dict[str, int]] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize Scene Analyzer with dynamic settings.

        Args:
            llm_service: LLM service for AI-based scoring
            weights: Optional weight overrides (if None, loads from Settings Service)
            project_id: Optional project ID for project-specific settings
        """
        self.llm_service = llm_service or LLMService()
        self.project_id = project_id

        # Load settings dynamically from Settings Service
        self._load_settings()

        # Override weights if explicitly provided
        if weights:
            self.weights = weights

    def _load_settings(self):
        """
        Load dynamic settings from Settings Service.

        This method is called during initialization and loads:
        - Scoring weights
        - Anti-pattern definitions
        - Metaphor discipline thresholds
        """
        try:
            # Load scoring weights
            self.weights = {
                "voice_authenticity": settings_service.get(
                    "scoring.voice_authenticity_weight", self.project_id
                ) or DEFAULT_WEIGHTS["voice_authenticity"],
                "character_consistency": settings_service.get(
                    "scoring.character_consistency_weight", self.project_id
                ) or DEFAULT_WEIGHTS["character_consistency"],
                "metaphor_discipline": settings_service.get(
                    "scoring.metaphor_discipline_weight", self.project_id
                ) or DEFAULT_WEIGHTS["metaphor_discipline"],
                "anti_pattern_compliance": settings_service.get(
                    "scoring.anti_pattern_compliance_weight", self.project_id
                ) or DEFAULT_WEIGHTS["anti_pattern_compliance"],
                "phase_appropriateness": settings_service.get(
                    "scoring.phase_appropriateness_weight", self.project_id
                ) or DEFAULT_WEIGHTS["phase_appropriateness"],
            }

            # Load anti-pattern definitions
            # Note: anti_patterns is a category, not a flat key
            anti_patterns_settings = settings_service.get_category("anti_patterns", self.project_id)

            # Convert flat keys back to nested structure
            anti_patterns_config = {
                "zero_tolerance": {},
                "formulaic": {},
                "custom": []
            }

            for key, value in anti_patterns_settings.items():
                if key.startswith("anti_patterns.zero_tolerance."):
                    pattern_name = key.replace("anti_patterns.zero_tolerance.", "")
                    anti_patterns_config["zero_tolerance"][pattern_name] = value
                elif key.startswith("anti_patterns.formulaic."):
                    pattern_name = key.replace("anti_patterns.formulaic.", "")
                    anti_patterns_config["formulaic"][pattern_name] = value
                elif key == "anti_patterns.custom":
                    anti_patterns_config["custom"] = value if isinstance(value, list) else []

            # Build zero-tolerance patterns dictionary
            zero_tolerance_config = anti_patterns_config.get("zero_tolerance", {})
            self.zero_tolerance_patterns = {}
            for pattern_name, pattern_def in zero_tolerance_config.items():
                if pattern_def.get("enabled", True):
                    # Get pattern from defaults or skip if not found
                    default_pattern = self._get_default_pattern(pattern_name, "zero_tolerance")
                    if default_pattern:
                        self.zero_tolerance_patterns[pattern_name] = {
                            "pattern": default_pattern,
                            "description": pattern_def.get("description", f"Zero-tolerance: {pattern_name}"),
                            "penalty": pattern_def.get("penalty", -2),
                        }

            # Build formulaic patterns dictionary
            formulaic_config = anti_patterns_config.get("formulaic", {})
            self.formulaic_patterns = {}
            for pattern_name, pattern_def in formulaic_config.items():
                if pattern_def.get("enabled", True):
                    default_pattern = self._get_default_pattern(pattern_name, "formulaic")
                    if default_pattern:
                        self.formulaic_patterns[pattern_name] = {
                            "pattern": default_pattern,
                            "description": pattern_def.get("description", f"Formulaic: {pattern_name}"),
                            "penalty": pattern_def.get("penalty", -1),
                        }

            # Add custom patterns
            custom_patterns = anti_patterns_config.get("custom", [])
            for custom in custom_patterns:
                pattern_name = custom.get("pattern_name", custom.get("pattern", "custom"))
                severity = custom.get("severity", "formulaic")

                pattern_dict = {
                    "pattern": custom.get("pattern", ""),
                    "description": custom.get("reason", custom.get("description", "")),
                    "penalty": -2 if severity == "zero_tolerance" else -1,
                }

                if severity == "zero_tolerance":
                    self.zero_tolerance_patterns[pattern_name] = pattern_dict
                else:
                    self.formulaic_patterns[pattern_name] = pattern_dict

            # Compile regex patterns for performance
            self._compiled_zero_tolerance = {
                name: re.compile(info["pattern"], re.IGNORECASE)
                for name, info in self.zero_tolerance_patterns.items()
                if info.get("pattern")
            }
            self._compiled_formulaic = {
                name: re.compile(info["pattern"], re.IGNORECASE)
                for name, info in self.formulaic_patterns.items()
                if info.get("pattern")
            }

            # Load metaphor settings
            self.saturation_threshold = settings_service.get(
                "scoring.saturation_threshold", self.project_id
            ) or 30
            self.simile_tolerance = settings_service.get(
                "scoring.simile_tolerance", self.project_id
            ) or 2

            # Simile detection pattern
            self._simile_pattern = re.compile(
                r"\b(like|as if|as though|resembled|similar to)\b",
                re.IGNORECASE
            )

            logger.info(
                f"Scene Analyzer settings loaded: "
                f"weights={self.weights}, "
                f"zero_tolerance={len(self.zero_tolerance_patterns)}, "
                f"formulaic={len(self.formulaic_patterns)}, "
                f"saturation_threshold={self.saturation_threshold}%"
            )

        except Exception as e:
            logger.error(f"Failed to load settings, using defaults: {e}")
            # Fall back to hard-coded defaults
            self.weights = DEFAULT_WEIGHTS.copy()
            self.zero_tolerance_patterns = self._get_default_zero_tolerance_patterns()
            self.formulaic_patterns = self._get_default_formulaic_patterns()
            self.saturation_threshold = 30
            self.simile_tolerance = 2

            self._compiled_zero_tolerance = {
                name: re.compile(info["pattern"], re.IGNORECASE)
                for name, info in self.zero_tolerance_patterns.items()
            }
            self._compiled_formulaic = {
                name: re.compile(info["pattern"], re.IGNORECASE)
                for name, info in self.formulaic_patterns.items()
            }
            self._simile_pattern = re.compile(
                r"\b(like|as if|as though|resembled|similar to)\b",
                re.IGNORECASE
            )

    def _get_default_pattern(self, pattern_name: str, pattern_type: str) -> Optional[str]:
        """
        Get default regex pattern for a named anti-pattern.

        Args:
            pattern_name: Name of the pattern (e.g., "first_person_italics")
            pattern_type: "zero_tolerance" or "formulaic"

        Returns:
            Regex pattern string or None if not found
        """
        default_patterns = {
            "zero_tolerance": {
                "first_person_italics": r"\*[^*]*\b(we|I)\b[^*]*\*",
                "with_precision": r"\bwith \w+ precision\b",
                "computer_psychology": r"\b(brain|mind|consciousness) (processed|computed|analyzed|calculated)\b",
                "with_obvious_adjective": r"\bwith (obvious|clear|visible|apparent|evident) \w+\b",
                "explaining_to_camera": r"\b(obviously|clearly|evidently|apparently)\b",
                "ai_explaining_character": r"\b(as a|being a|was a) \w+ (meant|required|demanded)\b",
            },
            "formulaic": {
                "adverb_verb": r"\b(walked|moved|spoke|said|looked|turned|stood) (carefully|slowly|quickly|quietly|loudly|suddenly)\b",
                "despite_the": r"\bdespite the \w+\b",
                "atmosphere_seemed": r"\b(air|room|atmosphere|silence) (seemed|was|felt) \w+\b",
                "suddenly": r"\bsuddenly\b",
                "eyes_widened": r"\beyes? widened\b",
                "breath_caught": r"\bbreath caught\b",
                "pulse_quickened": r"\bpulse (quickened|raced|pounded)\b",
            },
        }

        return default_patterns.get(pattern_type, {}).get(pattern_name)

    def _get_default_zero_tolerance_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get default zero-tolerance patterns as fallback."""
        return {
            "first_person_italics": {
                "pattern": r"\*[^*]*\b(we|I)\b[^*]*\*",
                "description": "First-person in italics (breaks POV in 3rd person)",
                "penalty": -2,
            },
            "with_precision": {
                "pattern": r"\bwith \w+ precision\b",
                "description": "'With X precision' cliche",
                "penalty": -2,
            },
            "computer_psychology": {
                "pattern": r"\b(brain|mind|consciousness) (processed|computed|analyzed|calculated)\b",
                "description": "Computer psychology (mechanical, not human)",
                "penalty": -2,
            },
            "with_obvious_adjective": {
                "pattern": r"\bwith (obvious|clear|visible|apparent|evident) \w+\b",
                "description": "'With obvious X' lazy description",
                "penalty": -2,
            },
        }

    def _get_default_formulaic_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get default formulaic patterns as fallback."""
        return {
            "adverb_verb": {
                "pattern": r"\b(walked|moved|spoke|said|looked|turned|stood) (carefully|slowly|quickly|quietly|loudly|suddenly)\b",
                "description": "Weak adverb-verb combination",
                "penalty": -1,
            },
            "despite_the": {
                "pattern": r"\bdespite the \w+\b",
                "description": "Overused 'despite the' transition",
                "penalty": -1,
            },
            "atmosphere_seemed": {
                "pattern": r"\b(air|room|atmosphere|silence) (seemed|was|felt) \w+\b",
                "description": "Vague atmosphere description",
                "penalty": -1,
            },
            "suddenly": {
                "pattern": r"\bsuddenly\b",
                "description": "Overused surprise word",
                "penalty": -1,
            },
        }

    def _parse_json_response(self, response: str) -> dict:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        LLMs often wrap JSON in ```json ... ``` which breaks json.loads().
        This helper strips those wrappers before parsing.
        """
        if not response:
            raise ValueError("Empty response")

        # Strip markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            # Remove opening fence (```json or ```)
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove closing fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        return json.loads(cleaned)

    # -------------------------------------------------------------------------
    # Main Analysis Entry Point
    # -------------------------------------------------------------------------

    async def analyze_scene(
        self,
        scene_id: str,
        scene_content: str,
        voice_bundle: Optional[VoiceBundleContext] = None,
        story_bible: Optional[StoryBibleContext] = None,
        pov_character: str = "protagonist",
        phase: str = "act2",
    ) -> SceneAnalysisResult:
        """
        Analyze a scene and return complete scoring breakdown.

        Args:
            scene_id: Unique identifier for the scene
            scene_content: The full scene text to analyze
            voice_bundle: Voice Bundle context (optional, enhances analysis)
            story_bible: Story Bible context (optional, enhances analysis)
            pov_character: POV character name for voice checks
            phase: Current story phase for phase appropriateness

        Returns:
            SceneAnalysisResult with full breakdown
        """
        logger.info(f"Analyzing scene: {scene_id}")

        # Run automated detection
        violations = self._detect_anti_patterns(scene_content)
        metaphor_analysis = self._analyze_metaphors(scene_content, voice_bundle)

        # Calculate automated scores
        anti_pattern_score = self._calculate_anti_pattern_score(violations)
        metaphor_score = self._calculate_metaphor_score(metaphor_analysis)

        # Run LLM-based evaluation for subjective categories
        voice_score = await self._evaluate_voice_authenticity(
            scene_content, voice_bundle, pov_character
        )
        character_score = await self._evaluate_character_consistency(
            scene_content, story_bible
        )
        phase_score = await self._evaluate_phase_appropriateness(
            scene_content, voice_bundle, phase
        )

        # Build category scores
        categories = {
            "voice_authenticity": voice_score,
            "character_consistency": character_score,
            "metaphor_discipline": metaphor_score,
            "anti_pattern_compliance": anti_pattern_score,
            "phase_appropriateness": phase_score,
        }

        # Calculate total score
        total_score = sum(cat.score for cat in categories.values())

        # Determine grade
        grade = self._calculate_grade(total_score)

        # Determine enhancement mode
        enhancement_needed, recommended_mode = self._determine_enhancement_mode(total_score)

        # Generate action prompt if needed
        action_prompt = None
        if recommended_mode == "action_prompt":
            action_prompt = self._generate_action_prompt(
                violations, metaphor_analysis, categories
            )

        return SceneAnalysisResult(
            scene_id=scene_id,
            total_score=total_score,
            grade=grade,
            categories=categories,
            violations=violations,
            metaphor_analysis=metaphor_analysis,
            enhancement_needed=enhancement_needed,
            recommended_mode=recommended_mode,
            action_prompt=action_prompt,
        )

    # -------------------------------------------------------------------------
    # Automated Pattern Detection
    # -------------------------------------------------------------------------

    def _detect_anti_patterns(self, content: str) -> List[PatternViolation]:
        """Detect all anti-pattern violations in the content."""
        violations = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Check zero-tolerance patterns
            for name, pattern in self._compiled_zero_tolerance.items():
                for match in pattern.finditer(line):
                    violations.append(PatternViolation(
                        pattern_name=name,
                        pattern_type="zero_tolerance",
                        description=ZERO_TOLERANCE_PATTERNS[name]["description"],
                        matched_text=match.group(),
                        line_number=line_num,
                        penalty=ZERO_TOLERANCE_PATTERNS[name]["penalty"],
                    ))

            # Check formulaic patterns
            for name, pattern in self._compiled_formulaic.items():
                for match in pattern.finditer(line):
                    violations.append(PatternViolation(
                        pattern_name=name,
                        pattern_type="formulaic",
                        description=FORMULAIC_PATTERNS[name]["description"],
                        matched_text=match.group(),
                        line_number=line_num,
                        penalty=FORMULAIC_PATTERNS[name]["penalty"],
                    ))

        return violations

    def _analyze_metaphors(
        self,
        content: str,
        voice_bundle: Optional[VoiceBundleContext],
    ) -> MetaphorAnalysis:
        """Analyze metaphor usage and domain distribution."""
        # Get domain keywords from voice bundle or use defaults
        domain_keywords = {}
        if voice_bundle and voice_bundle.metaphor_domains:
            domain_keywords = voice_bundle.metaphor_domains
        else:
            # Default domains for basic analysis
            domain_keywords = {
                "gambling": ["bet", "odds", "gamble", "wager", "poker", "cards", "chips", "dealer", "house"],
                "music": ["rhythm", "tempo", "harmony", "melody", "crescendo", "note", "chord"],
                "cooking": ["simmer", "boil", "recipe", "ingredient", "stew", "bake", "flavor"],
                "architecture": ["foundation", "scaffold", "blueprint", "structure", "framework"],
                "medicine": ["diagnosis", "symptom", "treatment", "surgical", "prescription"],
                "nature": ["storm", "river", "mountain", "forest", "ocean", "seed", "bloom"],
            }

        # Count metaphors by domain
        domain_counts: Dict[str, int] = {domain: 0 for domain in domain_keywords}
        content_lower = content.lower()

        for domain, keywords in domain_keywords.items():
            for keyword in keywords:
                domain_counts[domain] += len(re.findall(rf"\b{keyword}\b", content_lower))

        # Calculate totals and percentages
        total = sum(domain_counts.values())
        if total == 0:
            total = 1  # Avoid division by zero

        percentages = {
            domain: (count / total) * 100
            for domain, count in domain_counts.items()
        }

        # Find saturated domains (using dynamic threshold from settings)
        saturated = [
            domain for domain, pct in percentages.items()
            if pct > self.saturation_threshold and domain_counts[domain] > 0
        ]

        # Count similes
        lines = content.split("\n")
        simile_locations = []
        for line_num, line in enumerate(lines, start=1):
            for match in self._simile_pattern.finditer(line):
                simile_locations.append((line_num, match.group()))

        return MetaphorAnalysis(
            total_metaphors=total,
            domains=domain_counts,
            domain_percentages=percentages,
            saturated_domains=saturated,
            simile_count=len(simile_locations),
            simile_locations=simile_locations,
        )

    # -------------------------------------------------------------------------
    # Score Calculations
    # -------------------------------------------------------------------------

    def _calculate_anti_pattern_score(
        self,
        violations: List[PatternViolation],
    ) -> CategoryScore:
        """Calculate Anti-Pattern Compliance score from violations."""
        # Start with max scores
        zero_tolerance_score = 10
        formulaic_score = 5

        zero_tolerance_violations = []
        formulaic_violations = []

        for v in violations:
            if v.pattern_type == "zero_tolerance":
                zero_tolerance_score = max(0, zero_tolerance_score + v.penalty)
                zero_tolerance_violations.append(f"{v.matched_text} (line {v.line_number})")
            else:
                formulaic_score = max(0, formulaic_score + v.penalty)
                formulaic_violations.append(f"{v.matched_text} (line {v.line_number})")

        return CategoryScore(
            name="anti_pattern_compliance",
            score=zero_tolerance_score + formulaic_score,
            max_score=15,
            subcategories={
                "zero_tolerance": SubcategoryScore(
                    score=zero_tolerance_score,
                    max_score=10,
                    notes=f"{len(zero_tolerance_violations)} violations found",
                    violations=zero_tolerance_violations,
                ),
                "formulaic": SubcategoryScore(
                    score=formulaic_score,
                    max_score=5,
                    notes=f"{len(formulaic_violations)} violations found",
                    violations=formulaic_violations,
                ),
            },
        )

    def _calculate_metaphor_score(
        self,
        analysis: MetaphorAnalysis,
    ) -> CategoryScore:
        """Calculate Metaphor Discipline score from analysis."""
        # Domain rotation (0-10)
        if not analysis.saturated_domains:
            domain_score = 10
            domain_notes = "Good rotation, no domain over 30%"
        elif len(analysis.saturated_domains) == 1:
            pct = analysis.domain_percentages[analysis.saturated_domains[0]]
            if pct <= 35:
                domain_score = 7
                domain_notes = f"{analysis.saturated_domains[0]} at {pct:.0f}% (slightly high)"
            elif pct <= 45:
                domain_score = 4
                domain_notes = f"{analysis.saturated_domains[0]} at {pct:.0f}% (heavy reliance)"
            else:
                domain_score = 0
                domain_notes = f"{analysis.saturated_domains[0]} at {pct:.0f}% (saturation)"
        else:
            domain_score = 4
            domain_notes = f"Multiple saturated domains: {', '.join(analysis.saturated_domains)}"

        # Simile elimination (0-5)
        if analysis.simile_count == 0:
            simile_score = 5
            simile_notes = "Zero similes - all direct metaphors"
        elif analysis.simile_count <= 2:
            simile_score = 3
            simile_notes = f"{analysis.simile_count} similes found"
        elif analysis.simile_count <= 4:
            simile_score = 1
            simile_notes = f"{analysis.simile_count} similes - multiple comparison structures"
        else:
            simile_score = 0
            simile_notes = f"{analysis.simile_count} similes - simile-heavy"

        # Transformation score (placeholder - needs LLM evaluation for accuracy)
        # For now, estimate based on domain diversity
        active_domains = sum(1 for count in analysis.domains.values() if count > 0)
        if active_domains >= 4:
            transform_score = 5
            transform_notes = "Good domain diversity suggests active transformation"
        elif active_domains >= 2:
            transform_score = 3
            transform_notes = "Moderate domain diversity"
        else:
            transform_score = 1
            transform_notes = "Limited domain diversity"

        return CategoryScore(
            name="metaphor_discipline",
            score=domain_score + simile_score + transform_score,
            max_score=20,
            subcategories={
                "domain_rotation": SubcategoryScore(
                    score=domain_score,
                    max_score=10,
                    notes=domain_notes,
                ),
                "simile_elimination": SubcategoryScore(
                    score=simile_score,
                    max_score=5,
                    notes=simile_notes,
                ),
                "transformation": SubcategoryScore(
                    score=transform_score,
                    max_score=5,
                    notes=transform_notes,
                ),
            },
        )

    # -------------------------------------------------------------------------
    # LLM-Based Evaluation
    # -------------------------------------------------------------------------

    async def _evaluate_voice_authenticity(
        self,
        content: str,
        voice_bundle: Optional[VoiceBundleContext],
        pov_character: str,
    ) -> CategoryScore:
        """
        Evaluate Voice Authenticity using LLM.

        Tests:
        - Authenticity Test (10 pts): Character observing vs AI explaining
        - Purpose Test (10 pts): Theme embedded in action
        - Fusion Test (10 pts): Expertise fused with personality
        """
        # Build context for LLM
        gold_standard_context = ""
        if voice_bundle and voice_bundle.gold_standard:
            gold_standard_context = f"\n\nVOICE GOLD STANDARD:\n{voice_bundle.gold_standard[:2000]}"

        prompt = f"""You are a Voice Authenticity Critic evaluating a scene draft.

SCENE TO EVALUATE:
{content[:4000]}
{gold_standard_context}

Evaluate the following three tests. For each, provide a score and brief explanation.

1. AUTHENTICITY TEST (0-10): Does this sound like {pov_character} actively observing and thinking, or does it sound like an AI explaining what {pov_character} is doing?
   - 10: Perfect authentic voice - character observing in real-time
   - 7: Mostly authentic with occasional AI-explaining moments
   - 4: Mix of authentic voice and academic commentary
   - 0: Sounds like AI studying the character from outside

2. PURPOSE TEST (0-10): Is the theme/purpose embedded in the action, or is it stated explicitly?
   - 10: Theme embedded in action, never stated
   - 7: Theme present but occasionally stated rather than shown
   - 4: Generic prose with theme tangential
   - 0: Well-written but doesn't serve any thematic purpose

3. FUSION TEST (0-10): Are the character's expertise/knowledge areas fused with their personality?
   - 10: Technical language seamlessly integrated with character voice
   - 7: Occasional separation between expertise and personality
   - 4: Either technical OR character voice, not fused
   - 0: Academic analysis without character grounding

Respond in JSON format:
{{
    "authenticity": {{"score": N, "notes": "..."}},
    "purpose": {{"score": N, "notes": "..."}},
    "fusion": {{"score": N, "notes": "..."}}
}}"""

        try:
            response = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a voice authenticity critic. Respond only with valid JSON.",
                prompt=prompt,
            )

            # Parse JSON response
            result = self._parse_json_response(response)

            return CategoryScore(
                name="voice_authenticity",
                score=(
                    result["authenticity"]["score"] +
                    result["purpose"]["score"] +
                    result["fusion"]["score"]
                ),
                max_score=30,
                subcategories={
                    "authenticity_test": SubcategoryScore(
                        score=result["authenticity"]["score"],
                        max_score=10,
                        notes=result["authenticity"]["notes"],
                    ),
                    "purpose_test": SubcategoryScore(
                        score=result["purpose"]["score"],
                        max_score=10,
                        notes=result["purpose"]["notes"],
                    ),
                    "fusion_test": SubcategoryScore(
                        score=result["fusion"]["score"],
                        max_score=10,
                        notes=result["fusion"]["notes"],
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Voice authenticity evaluation failed: {e}")
            # Return default middle-range scores on failure
            return CategoryScore(
                name="voice_authenticity",
                score=21,  # 7+7+7
                max_score=30,
                subcategories={
                    "authenticity_test": SubcategoryScore(score=7, max_score=10, notes="Evaluation failed - default score"),
                    "purpose_test": SubcategoryScore(score=7, max_score=10, notes="Evaluation failed - default score"),
                    "fusion_test": SubcategoryScore(score=7, max_score=10, notes="Evaluation failed - default score"),
                },
            )

    async def _evaluate_character_consistency(
        self,
        content: str,
        story_bible: Optional[StoryBibleContext],
    ) -> CategoryScore:
        """
        Evaluate Character Consistency using LLM.

        Tests:
        - Psychology (8 pts): Behavior matches Fatal Flaw/Lie
        - Capability (6 pts): Actions within established limits
        - Relationship (6 pts): Interactions match dynamics
        """
        # Build context
        story_context = ""
        if story_bible:
            story_context = f"""
CHARACTER CONTEXT:
- Protagonist: {story_bible.protagonist_name}
- Fatal Flaw: {story_bible.fatal_flaw}
- The Lie: {story_bible.the_lie}
- Capabilities: {', '.join(story_bible.character_capabilities) if story_bible.character_capabilities else 'Not specified'}
"""

        # Add instruction for handling missing context
        no_context_instruction = ""
        if not story_bible:
            no_context_instruction = """
NOTE: No explicit character bible provided. Evaluate based on what the prose IMPLIES about the character:
- Infer psychological consistency from how the character thinks and acts
- Assess whether actions feel plausible for the implied character type
- If no relationships shown, evaluate potential for relationship dynamics
Score based on internal consistency of what IS shown, not penalize for missing context.
"""

        prompt = f"""You are a Character Consistency Critic evaluating a scene draft.

SCENE TO EVALUATE:
{content[:4000]}
{story_context}
{no_context_instruction}
Evaluate character consistency in three areas:

1. PSYCHOLOGY (0-8): Does character behavior feel internally consistent?
   - 8: Highly consistent psychology throughout - character feels real
   - 6: Mostly consistent, character psychology is clear
   - 3: Some inconsistent behaviors or unclear motivations
   - 0: Character behavior feels random or contradictory

2. CAPABILITY (0-6): Do character actions feel plausible?
   - 6: All actions feel natural and within implied abilities
   - 4: Actions mostly plausible, one stretch
   - 2: Some implausible actions
   - 0: Actions break believability

3. RELATIONSHIP (0-6): Are relationship dynamics (if present) authentic?
   - 6: Rich, authentic interpersonal dynamics
   - 4: Solid relationships, some generic beats
   - 2: Relationships feel flat or forced
   - 0: No relationships or completely inauthentic
   (If solo scene with no relationships: score 4 as neutral)

Respond in JSON format:
{{
    "psychology": {{"score": N, "notes": "..."}},
    "capability": {{"score": N, "notes": "..."}},
    "relationship": {{"score": N, "notes": "..."}}
}}"""

        try:
            response = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a character consistency critic. Respond only with valid JSON.",
                prompt=prompt,
            )

            result = self._parse_json_response(response)

            return CategoryScore(
                name="character_consistency",
                score=(
                    result["psychology"]["score"] +
                    result["capability"]["score"] +
                    result["relationship"]["score"]
                ),
                max_score=20,
                subcategories={
                    "psychology": SubcategoryScore(
                        score=result["psychology"]["score"],
                        max_score=8,
                        notes=result["psychology"]["notes"],
                    ),
                    "capability": SubcategoryScore(
                        score=result["capability"]["score"],
                        max_score=6,
                        notes=result["capability"]["notes"],
                    ),
                    "relationship": SubcategoryScore(
                        score=result["relationship"]["score"],
                        max_score=6,
                        notes=result["relationship"]["notes"],
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Character consistency evaluation failed: {e}")
            return CategoryScore(
                name="character_consistency",
                score=14,  # 6+4+4
                max_score=20,
                subcategories={
                    "psychology": SubcategoryScore(score=6, max_score=8, notes="Evaluation failed - default score"),
                    "capability": SubcategoryScore(score=4, max_score=6, notes="Evaluation failed - default score"),
                    "relationship": SubcategoryScore(score=4, max_score=6, notes="Evaluation failed - default score"),
                },
            )

    async def _evaluate_phase_appropriateness(
        self,
        content: str,
        voice_bundle: Optional[VoiceBundleContext],
        phase: str,
    ) -> CategoryScore:
        """
        Evaluate Phase Appropriateness using LLM.

        Tests:
        - Voice Complexity (8 pts): Matches story phase expectations
        - Earned Language (7 pts): Technical terms justified by experience
        """
        phase_context = ""
        if voice_bundle and voice_bundle.phase_evolution:
            phase_context = f"\n\nPHASE EVOLUTION GUIDE:\n{voice_bundle.phase_evolution[:1500]}"

        prompt = f"""You are a Phase Appropriateness Critic evaluating a scene draft.

SCENE TO EVALUATE:
{content[:4000]}

CURRENT PHASE: {phase}
{phase_context}

Phase expectations:
- Act 1 (Setup): Grounded, relatable voice - reader learning the world
- Act 2A (Fun & Games): Voice can flex into specialty domains
- Act 2B (Bad Guys Close In): Darker, more cynical
- Act 3 (Finale): Full integration of all learned voice elements

Evaluate:

1. VOICE COMPLEXITY (0-8): Is the voice complexity appropriate for this story phase?
   - 8: Perfect alignment with phase expectations
   - 6: Generally correct with minor anachronisms
   - 3: Wrong complexity level for phase
   - 0: Completely inappropriate voice

2. EARNED LANGUAGE (0-7): Is specialized terminology justified by character experience at this point?
   - 7: All technical terms earned through character experience
   - 5: 1-2 slightly premature terms
   - 2: Multiple premature specialized terms
   - 0: Inappropriate academic jargon

Respond in JSON format:
{{
    "voice_complexity": {{"score": N, "notes": "..."}},
    "earned_language": {{"score": N, "notes": "..."}}
}}"""

        try:
            response = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a phase appropriateness critic. Respond only with valid JSON.",
                prompt=prompt,
            )

            result = self._parse_json_response(response)

            return CategoryScore(
                name="phase_appropriateness",
                score=(
                    result["voice_complexity"]["score"] +
                    result["earned_language"]["score"]
                ),
                max_score=15,
                subcategories={
                    "voice_complexity": SubcategoryScore(
                        score=result["voice_complexity"]["score"],
                        max_score=8,
                        notes=result["voice_complexity"]["notes"],
                    ),
                    "earned_language": SubcategoryScore(
                        score=result["earned_language"]["score"],
                        max_score=7,
                        notes=result["earned_language"]["notes"],
                    ),
                },
            )

        except Exception as e:
            logger.error(f"Phase appropriateness evaluation failed: {e}")
            return CategoryScore(
                name="phase_appropriateness",
                score=10,  # 6+4
                max_score=15,
                subcategories={
                    "voice_complexity": SubcategoryScore(score=6, max_score=8, notes="Evaluation failed - default score"),
                    "earned_language": SubcategoryScore(score=4, max_score=7, notes="Evaluation failed - default score"),
                },
            )

    # -------------------------------------------------------------------------
    # Grade and Enhancement Mode
    # -------------------------------------------------------------------------

    def _calculate_grade(self, total_score: int) -> str:
        """Calculate letter grade from total score."""
        for grade, threshold in GRADE_THRESHOLDS.items():
            if total_score >= threshold:
                return grade
        return "F"

    def _determine_enhancement_mode(
        self,
        total_score: int,
    ) -> Tuple[bool, str]:
        """Determine if enhancement is needed and what mode."""
        if total_score >= 92:
            return False, "none"
        elif total_score >= 85:
            return True, "action_prompt"
        elif total_score >= 70:
            return True, "six_pass"
        else:
            return True, "rewrite"

    def _generate_action_prompt(
        self,
        violations: List[PatternViolation],
        metaphor_analysis: MetaphorAnalysis,
        categories: Dict[str, CategoryScore],
    ) -> str:
        """Generate surgical fix instructions for action prompt mode."""
        fixes = []
        fix_num = 1

        # Add violation fixes
        for v in violations[:5]:  # Limit to top 5
            fixes.append(f"{fix_num}. Line {v.line_number}: Replace '{v.matched_text}' - {v.description}")
            fix_num += 1

        # Add metaphor fixes if saturated
        if metaphor_analysis.saturated_domains:
            for domain in metaphor_analysis.saturated_domains[:2]:
                pct = metaphor_analysis.domain_percentages[domain]
                fixes.append(
                    f"{fix_num}. Reduce {domain} metaphors (currently {pct:.0f}%) - "
                    f"replace 2-3 with alternate domains"
                )
                fix_num += 1

        # Add simile fixes
        if metaphor_analysis.simile_count > 2:
            fixes.append(
                f"{fix_num}. Convert {metaphor_analysis.simile_count} similes to direct metaphors"
            )
            fix_num += 1

        if not fixes:
            return "Scene scores well. Optional polish for voice refinement."

        return "Fix the following issues while preserving scene voice:\n\n" + "\n".join(fixes)


# =============================================================================
# Service Singleton
# =============================================================================

_scene_analyzer_service: Optional[SceneAnalyzerService] = None


def get_scene_analyzer_service() -> SceneAnalyzerService:
    """Get or create the SceneAnalyzerService singleton."""
    global _scene_analyzer_service
    if _scene_analyzer_service is None:
        _scene_analyzer_service = SceneAnalyzerService()
    return _scene_analyzer_service
