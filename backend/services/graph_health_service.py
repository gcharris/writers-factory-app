"""
Graph Health Service - Macro-Level Structural Validation

Phase 3D: Implements asynchronous health checks for narrative structure,
character arcs, and thematic consistency at chapter/act/manuscript level.

Strategic Decisions (from planning):
1. Full LLM semantic analysis for timeline consistency
2. Hybrid LLM + manual override for theme resonance
3. Auto-trigger after chapter assembly (respects Foreman proactiveness)
4. SQLite persistence for historical tracking (365-day retention)

Architecture:
- Two-Tier Quality System: Scene Analyzer (Tier 1) + Graph Health (Tier 2)
- 7 Health Check Algorithms across 3 categories (Structural, Character, Thematic)
- Configurable via Settings Service (health_checks.* settings)
"""

import logging
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.graph.schema import (
    Chapter, Scene, Beat, FlawChallenge,
    ThemeResonanceOverride, HealthReportHistory,
    Base, engine, SettingsSessionLocal
)
from backend.services.settings_service import settings_service
from backend.services.llm_service import LLMService

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class HealthWarning:
    """Individual health warning from a check."""
    type: str  # PACING_PLATEAU, BEAT_DEVIATION, TIMELINE_ERROR, etc.
    severity: str  # info | warning | error
    message: str
    recommendation: Optional[str] = None
    scenes: List[str] = field(default_factory=list)
    chapters: List[str] = field(default_factory=list)
    characters: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class HealthReport:
    """Complete health report for chapter/act/manuscript."""
    report_id: str
    project_id: str
    scope: str  # chapter | act | manuscript
    chapter_id: Optional[str] = None
    act_number: Optional[int] = None
    overall_score: int = 100  # 0-100
    warnings: List[HealthWarning] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def has_critical_warnings(self) -> bool:
        """Check if report contains any error-level warnings."""
        return any(w.severity == "error" for w in self.warnings)

    def has_warnings(self) -> bool:
        """Check if report contains any warnings at all."""
        return len(self.warnings) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "report_id": self.report_id,
            "project_id": self.project_id,
            "scope": self.scope,
            "chapter_id": self.chapter_id,
            "act_number": self.act_number,
            "overall_score": self.overall_score,
            "warnings": [w.to_dict() for w in self.warnings],
            "timestamp": self.timestamp
        }

    def to_markdown(self) -> str:
        """Generate markdown health report for writer."""
        lines = []

        # Header
        if self.scope == "chapter":
            lines.append(f"# Health Report: Chapter {self.chapter_id}")
        elif self.scope == "act":
            lines.append(f"# Health Report: Act {self.act_number}")
        else:
            lines.append("# Health Report: Full Manuscript")

        lines.append(f"**Overall Score**: {self.overall_score}/100 " +
                    ("(Excellent)" if self.overall_score >= 90 else
                     "(Good)" if self.overall_score >= 80 else
                     "(Fair)" if self.overall_score >= 70 else
                     "(Needs Work)"))
        lines.append(f"**Timestamp**: {self.timestamp}")
        lines.append("")

        if not self.warnings:
            lines.append("## Status: CLEAN")
            lines.append("No structural issues detected. Excellent work!")
            return "\n".join(lines)

        # Group warnings by severity
        errors = [w for w in self.warnings if w.severity == "error"]
        warnings_list = [w for w in self.warnings if w.severity == "warning"]
        info = [w for w in self.warnings if w.severity == "info"]

        # Errors
        if errors:
            lines.append("## 🚨 Critical Issues (Must Fix)")
            lines.append("")
            for w in errors:
                lines.append(f"### {w.type}")
                lines.append(f"**Message**: {w.message}")
                if w.recommendation:
                    lines.append(f"**Recommendation**: {w.recommendation}")
                if w.chapters:
                    lines.append(f"**Chapters**: {', '.join(w.chapters)}")
                lines.append("")

        # Warnings
        if warnings_list:
            lines.append("## ⚠️ Warnings (Should Address)")
            lines.append("")
            for w in warnings_list:
                lines.append(f"### {w.type}")
                lines.append(f"**Message**: {w.message}")
                if w.recommendation:
                    lines.append(f"**Recommendation**: {w.recommendation}")
                if w.chapters:
                    lines.append(f"**Chapters**: {', '.join(w.chapters)}")
                lines.append("")

        # Info
        if info:
            lines.append("## ℹ️ Informational Notes")
            lines.append("")
            for w in info:
                lines.append(f"- **{w.type}**: {w.message}")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Graph Health Service
# =============================================================================

class GraphHealthService:
    """
    Asynchronous macro-level analysis of manuscript structure and health.

    Implements 7 health check algorithms across 3 categories:

    A. Structural Integrity:
       - Pacing Plateau Detection
       - Beat Progress Validation
       - Timeline Consistency (full LLM semantic analysis)

    B. Character Arc Health:
       - Fatal Flaw Challenge Monitoring
       - Cast Function Verification

    C. Thematic Health:
       - Symbolic Layering
       - Theme Resonance (hybrid LLM + manual override)

    Strategic Decisions:
    - Decision 1: Full LLM-powered semantic analysis for timeline
    - Decision 2: Hybrid LLM + manual override for theme resonance
    - Decision 3: Auto-trigger after chapter assembly (via Foreman)
    - Decision 4: SQLite persistence with 365-day retention
    """

    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Graph Health Service.

        Args:
            project_id: Optional project ID for project-specific settings
        """
        self.project_id = project_id
        self.llm_service = LLMService()

        # Load settings from Settings Service
        self._load_settings()

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        logger.info(f"Graph Health Service initialized for project: {project_id}")

    def _load_settings(self):
        """Load dynamic settings from Settings Service."""
        try:
            # Load health check models (Phase 3E: Configurable per-check models)
            self.health_check_model = settings_service.get(
                "health_checks.models.default_model", self.project_id
            ) or "llama3.2"

            # Task-specific model assignments
            self.timeline_consistency_model = settings_service.get(
                "health_checks.models.timeline_consistency", self.project_id
            ) or self.health_check_model

            self.theme_resonance_model = settings_service.get(
                "health_checks.models.theme_resonance", self.project_id
            ) or self.health_check_model

            self.flaw_challenges_model = settings_service.get(
                "health_checks.models.flaw_challenges", self.project_id
            ) or self.health_check_model

            self.cast_function_model = settings_service.get(
                "health_checks.models.cast_function", self.project_id
            ) or self.health_check_model

            self.symbolic_layering_model = settings_service.get(
                "health_checks.models.symbolic_layering", self.project_id
            ) or self.health_check_model

            self.pacing_analysis_model = settings_service.get(
                "health_checks.models.pacing_analysis", self.project_id
            ) or self.health_check_model

            self.beat_progress_model = settings_service.get(
                "health_checks.models.beat_progress", self.project_id
            ) or self.health_check_model

            # Load pacing settings
            self.pacing_plateau_window = settings_service.get(
                "health_checks.pacing.plateau_window", self.project_id
            ) or 3

            self.pacing_plateau_tolerance = settings_service.get(
                "health_checks.pacing.plateau_tolerance", self.project_id
            ) or 1.0

            # Load structure settings
            self.beat_deviation_warning = settings_service.get(
                "health_checks.structure.beat_deviation_warning", self.project_id
            ) or 5

            self.beat_deviation_error = settings_service.get(
                "health_checks.structure.beat_deviation_error", self.project_id
            ) or 10

            # Load character settings
            self.flaw_challenge_frequency = settings_service.get(
                "health_checks.character.flaw_challenge_frequency", self.project_id
            ) or 10

            self.min_cast_appearances = settings_service.get(
                "health_checks.character.min_cast_appearances", self.project_id
            ) or 3

            # Load theme settings
            self.min_symbol_occurrences = settings_service.get(
                "health_checks.theme.min_symbol_occurrences", self.project_id
            ) or 3

            self.min_resonance_score = settings_service.get(
                "health_checks.theme.min_resonance_score", self.project_id
            ) or 6

            self.theme_auto_score = settings_service.get(
                "health_checks.theme.auto_score", self.project_id
            )
            if self.theme_auto_score is None:
                self.theme_auto_score = True

            self.theme_allow_manual_override = settings_service.get(
                "health_checks.theme.allow_manual_override", self.project_id
            )
            if self.theme_allow_manual_override is None:
                self.theme_allow_manual_override = True

            # Load timeline settings
            self.timeline_semantic_analysis = settings_service.get(
                "health_checks.timeline.semantic_analysis", self.project_id
            )
            if self.timeline_semantic_analysis is None:
                self.timeline_semantic_analysis = True

            self.timeline_confidence_threshold = settings_service.get(
                "health_checks.timeline.confidence_threshold", self.project_id
            ) or 0.7

            # Load reporting settings
            self.store_history = settings_service.get(
                "health_checks.reporting.store_history", self.project_id
            )
            if self.store_history is None:
                self.store_history = True

            self.retention_days = settings_service.get(
                "health_checks.reporting.retention_days", self.project_id
            ) or 365

            logger.info(
                f"Health check settings loaded: "
                f"model={self.health_check_model}, "
                f"pacing_window={self.pacing_plateau_window}, "
                f"beat_dev_warn={self.beat_deviation_warning}%"
            )

        except Exception as e:
            logger.error(f"Failed to load health check settings: {e}")
            # Set safe defaults
            self.health_check_model = "llama3.2"
            self.timeline_consistency_model = "llama3.2"
            self.theme_resonance_model = "llama3.2"
            self.flaw_challenges_model = "llama3.2"
            self.cast_function_model = "llama3.2"
            self.symbolic_layering_model = "llama3.2"
            self.pacing_analysis_model = "llama3.2"
            self.beat_progress_model = "llama3.2"
            self.pacing_plateau_window = 3
            self.pacing_plateau_tolerance = 1.0
            self.beat_deviation_warning = 5
            self.beat_deviation_error = 10
            self.flaw_challenge_frequency = 10
            self.min_cast_appearances = 3
            self.min_symbol_occurrences = 3
            self.min_resonance_score = 6
            self.theme_auto_score = True
            self.theme_allow_manual_override = True
            self.timeline_semantic_analysis = True
            self.timeline_confidence_threshold = 0.7
            self.store_history = True
            self.retention_days = 365

    # =========================================================================
    # LLM Query Routing (Phase 3E)
    # =========================================================================

    async def _query_llm(
        self,
        prompt: str,
        system_prompt: str,
        model: str
    ) -> str:
        """
        Query LLM with automatic provider detection (Phase 3E).

        Args:
            prompt: User message
            system_prompt: System context
            model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet", "deepseek-chat")

        Returns:
            LLM response text
        """
        import os
        import httpx

        # Detect provider from model name
        if model.startswith("gpt-"):
            provider = "openai"
        elif model.startswith("claude-"):
            provider = "anthropic"
        elif model.startswith("deepseek-"):
            provider = "deepseek"
        elif model.startswith("qwen-"):
            provider = "qwen"
        elif model.startswith("kimi-"):
            provider = "kimi"
        elif model.startswith("glm-"):
            provider = "zhipu"
        elif model.startswith("hunyuan-"):
            provider = "tencent"
        elif model.startswith("mistral-"):
            provider = "mistral"
        elif model.startswith("grok-"):
            provider = "xai"
        else:
            # Default to Ollama for local models
            return await self._query_ollama(prompt, system_prompt, model)

        # Check if API key is available
        api_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "qwen": "QWEN_API_KEY",
            "kimi": "KIMI_API_KEY",
            "zhipu": "ZHIPU_API_KEY",
            "tencent": "TENCENT_API_KEY",
            "mistral": "MISTRAL_API_KEY",
            "xai": "XAI_API_KEY"
        }

        if not os.getenv(api_key_map.get(provider, "")):
            logger.warning(
                f"{provider.upper()} API key not found, falling back to Ollama"
            )
            return await self._query_ollama(prompt, system_prompt, self.health_check_model)

        try:
            # Use LLMService for cloud providers
            response = await self.llm_service.generate_response(
                provider=provider,
                model=model,
                system_role=system_prompt,
                prompt=prompt
            )

            logger.info(f"🧠 Health check using {model} ({provider})")
            return response

        except Exception as e:
            logger.error(f"Cloud LLM query failed ({provider}/{model}): {e}, falling back to Ollama")
            return await self._query_ollama(prompt, system_prompt, self.health_check_model)

    async def _query_ollama(
        self,
        prompt: str,
        system_prompt: str,
        model: str
    ) -> str:
        """
        Query local Ollama models as fallback.

        Args:
            prompt: User message
            system_prompt: System context
            model: Model name (e.g., "mistral", "llama3.2")

        Returns:
            LLM response text
        """
        import httpx

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()

                logger.debug(f"📋 Health check using {model} (Ollama)")
                return data["message"]["content"]

        except Exception as e:
            logger.error(f"Ollama query failed ({model}): {e}")
            return f"[LLM Query Failed: {str(e)}]"

    # =========================================================================
    # Main Entry Points
    # =========================================================================

    async def run_chapter_health_check(
        self,
        chapter_id: str,
        db: Optional[Session] = None
    ) -> HealthReport:
        """
        Run all health checks for a single chapter.

        Args:
            chapter_id: Chapter identifier (e.g., "chapter_2.5")
            db: Optional database session (creates new if None)

        Returns:
            HealthReport with all warnings
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            # Fetch chapter data
            chapter = db.query(Chapter).filter(
                Chapter.chapter_id == chapter_id
            ).first()

            if not chapter:
                logger.error(f"Chapter not found: {chapter_id}")
                return HealthReport(
                    report_id=str(uuid.uuid4()),
                    project_id=self.project_id or "unknown",
                    scope="chapter",
                    chapter_id=chapter_id,
                    overall_score=0,
                    warnings=[HealthWarning(
                        type="CHAPTER_NOT_FOUND",
                        severity="error",
                        message=f"Chapter {chapter_id} not found in database"
                    )]
                )

            warnings = []

            # Run all applicable checks
            # Note: Some checks require multi-chapter context, so skip for single chapter

            # Structural checks (limited for single chapter)
            warnings.extend(await self._check_beat_progress(db, [chapter]))
            warnings.extend(await self._check_timeline_consistency(db, chapter.scenes))

            # Character checks
            warnings.extend(await self._check_flaw_challenges(db, chapter))
            warnings.extend(await self._check_cast_function(db, chapter))

            # Thematic checks
            warnings.extend(await self._check_theme_resonance(db, chapter))

            # Calculate overall score
            overall_score = self._calculate_health_score(warnings)

            # Create report
            report = HealthReport(
                report_id=str(uuid.uuid4()),
                project_id=self.project_id or chapter.project_id or "unknown",
                scope="chapter",
                chapter_id=chapter_id,
                overall_score=overall_score,
                warnings=warnings
            )

            # Store report if enabled
            if self.store_history:
                self._store_health_report(db, report, chapter.id)

            logger.info(
                f"Chapter health check complete: {chapter_id}, "
                f"score={overall_score}, warnings={len(warnings)}"
            )

            return report

        finally:
            if close_db:
                db.close()

    async def run_act_health_check(
        self,
        act_number: int,
        db: Optional[Session] = None
    ) -> HealthReport:
        """
        Run all health checks for an entire act.

        Args:
            act_number: Act number (1, 2, 3)
            db: Optional database session

        Returns:
            HealthReport with all warnings
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            # Fetch all chapters in act
            chapters = db.query(Chapter).filter(
                Chapter.act == act_number,
                Chapter.project_id == self.project_id
            ).order_by(Chapter.id).all()

            if not chapters:
                logger.warning(f"No chapters found for Act {act_number}")
                return HealthReport(
                    report_id=str(uuid.uuid4()),
                    project_id=self.project_id or "unknown",
                    scope="act",
                    act_number=act_number,
                    overall_score=100,
                    warnings=[]
                )

            warnings = []

            # A. Structural Integrity checks (multi-chapter context)
            warnings.extend(await self._check_pacing_plateaus(db, chapters))
            warnings.extend(await self._check_beat_progress(db, chapters))

            # Collect all scenes from all chapters
            all_scenes = []
            for chapter in chapters:
                all_scenes.extend(chapter.scenes)

            warnings.extend(await self._check_timeline_consistency(db, all_scenes))

            # B. Character Arc Health checks (per chapter)
            for chapter in chapters:
                warnings.extend(await self._check_flaw_challenges(db, chapter))
                warnings.extend(await self._check_cast_function(db, chapter))

            # C. Thematic Health checks (act level for symbolic layering)
            warnings.extend(await self._check_symbolic_layering(db, chapters))
            for chapter in chapters:
                warnings.extend(await self._check_theme_resonance(db, chapter))

            # Calculate overall score
            overall_score = self._calculate_health_score(warnings)

            # Create report
            report = HealthReport(
                report_id=str(uuid.uuid4()),
                project_id=self.project_id or "unknown",
                scope="act",
                act_number=act_number,
                overall_score=overall_score,
                warnings=warnings
            )

            # Store report if enabled
            if self.store_history:
                self._store_health_report(db, report)

            logger.info(
                f"Act health check complete: Act {act_number}, "
                f"score={overall_score}, warnings={len(warnings)}"
            )

            return report

        finally:
            if close_db:
                db.close()

    async def run_full_manuscript_check(
        self,
        db: Optional[Session] = None
    ) -> HealthReport:
        """
        Run comprehensive health check on full manuscript.

        Args:
            db: Optional database session

        Returns:
            HealthReport with all warnings
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            # Fetch all chapters
            chapters = db.query(Chapter).filter(
                Chapter.project_id == self.project_id
            ).order_by(Chapter.id).all()

            if not chapters:
                logger.warning("No chapters found for manuscript health check")
                return HealthReport(
                    report_id=str(uuid.uuid4()),
                    project_id=self.project_id or "unknown",
                    scope="manuscript",
                    overall_score=100,
                    warnings=[]
                )

            warnings = []

            # A. Structural Integrity checks (manuscript level)
            warnings.extend(await self._check_pacing_plateaus(db, chapters))
            warnings.extend(await self._check_beat_progress(db, chapters))

            # Collect all scenes
            all_scenes = []
            for chapter in chapters:
                all_scenes.extend(chapter.scenes)

            warnings.extend(await self._check_timeline_consistency(db, all_scenes))

            # B. Character Arc Health checks (per chapter)
            for chapter in chapters:
                warnings.extend(await self._check_flaw_challenges(db, chapter))
                warnings.extend(await self._check_cast_function(db, chapter))

            # C. Thematic Health checks (manuscript level for symbolic layering)
            warnings.extend(await self._check_symbolic_layering(db, chapters))
            for chapter in chapters:
                warnings.extend(await self._check_theme_resonance(db, chapter))

            # Calculate overall score
            overall_score = self._calculate_health_score(warnings)

            # Create report
            report = HealthReport(
                report_id=str(uuid.uuid4()),
                project_id=self.project_id or "unknown",
                scope="manuscript",
                overall_score=overall_score,
                warnings=warnings
            )

            # Store report if enabled
            if self.store_history:
                self._store_health_report(db, report)

            logger.info(
                f"Manuscript health check complete: "
                f"score={overall_score}, warnings={len(warnings)}"
            )

            return report

        finally:
            if close_db:
                db.close()

    # =========================================================================
    # Health Check Algorithms
    # =========================================================================

    async def _check_pacing_plateaus(
        self,
        db: Session,
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Check A1: Pacing Failure Detection (Phase 3D).

        Detects "tension plateaus" - consecutive chapters with low/flat tension
        that cause reader boredom. Uses LLM to analyze if plateau is intentional
        (calm before storm) or problematic.

        Algorithm:
        1. Extract tension scores for last N chapters (configurable, default 10)
        2. Detect plateaus: 3+ consecutive chapters with <5 point tension variation
        3. Use LLM to analyze if plateau is intentional or problematic
        4. Return warnings for problematic plateaus

        Warning Severity:
        - ERROR if 5+ chapters plateau
        - WARNING if 3-4 chapters

        Args:
            db: Database session
            chapters: List of chapters to analyze (ordered)

        Returns:
            List of health warnings for detected plateaus
        """
        warnings = []

        # Need at least plateau_window chapters to detect a plateau
        if len(chapters) < self.pacing_plateau_window:
            return warnings

        # Extract tension scores, filtering out None values
        tension_data = [
            (ch, ch.avg_tension)
            for ch in chapters
            if ch.avg_tension is not None
        ]

        if len(tension_data) < self.pacing_plateau_window:
            return warnings  # Not enough tension data

        logger.info(f"Pacing plateau check: analyzing {len(tension_data)} chapters with {self.pacing_analysis_model}")

        # Sliding window analysis to detect plateaus
        detected_plateaus = []
        i = 0
        while i < len(tension_data) - self.pacing_plateau_window + 1:
            window_data = tension_data[i:i + self.pacing_plateau_window]
            window_scores = [d[1] for d in window_data]
            window_chapters = [d[0] for d in window_data]

            # Check if tension variation is below threshold (flat pacing)
            min_tension_variation = settings_service.get(
                "health_checks.pacing.min_tension_variation", self.project_id
            ) or 5  # Default: 5 points

            variation = max(window_scores) - min(window_scores)

            if variation < min_tension_variation:
                # Found a potential plateau - extend it as far as possible
                plateau_end = i + self.pacing_plateau_window
                while plateau_end < len(tension_data):
                    extended_scores = [d[1] for d in tension_data[i:plateau_end + 1]]
                    if max(extended_scores) - min(extended_scores) < min_tension_variation:
                        plateau_end += 1
                    else:
                        break

                plateau_chapters = [d[0] for d in tension_data[i:plateau_end]]
                plateau_scores = [d[1] for d in tension_data[i:plateau_end]]

                detected_plateaus.append({
                    "chapters": plateau_chapters,
                    "scores": plateau_scores,
                    "start_index": i,
                    "end_index": plateau_end
                })

                # Skip past this plateau
                i = plateau_end
            else:
                i += 1

        # Analyze each detected plateau with LLM
        for plateau in detected_plateaus:
            chapters_in_plateau = plateau["chapters"]
            scores = plateau["scores"]
            chapter_count = len(chapters_in_plateau)

            # Build chapter summaries for LLM analysis
            chapter_summaries = []
            for ch in chapters_in_plateau[:5]:  # Limit to 5 for context window
                scenes = ch.scenes[:2] if hasattr(ch, 'scenes') else []
                scene_summary = "; ".join([s.summary or "No summary" for s in scenes[:2]])
                chapter_summaries.append(f"- **{ch.chapter_id}** ({ch.title or 'Untitled'}): {scene_summary[:200]}")

            # LLM prompt for plateau analysis
            system_prompt = """You are a narrative pacing expert. Analyze tension plateaus in manuscripts.

A "tension plateau" is when consecutive chapters have similar tension levels with little variation.
Plateaus can be:
- INTENTIONAL: Calm before storm, character development, necessary exposition
- PROBLEMATIC: Reader boredom, pacing issues, lack of conflict escalation

Respond in JSON format:
{
  "is_intentional": true | false,
  "risk_level": "low" | "medium" | "high",
  "reasoning": "Brief explanation",
  "recommendation": "Specific actionable suggestion"
}"""

            plateau_desc = f"{chapter_count} consecutive chapters with tension scores: {', '.join(f'{s:.1f}' for s in scores)}"

            user_prompt = f"""Analyze this tension plateau in a manuscript:

**Plateau Description**: {plateau_desc}
**Average Tension**: {sum(scores) / len(scores):.1f}/10
**Tension Variation**: {max(scores) - min(scores):.1f} points

**Chapter Summaries**:
{chr(10).join(chapter_summaries)}

Questions:
1. Is this plateau intentional (e.g., calm before storm, character development)?
2. Does it risk reader boredom?
3. What's missing to create rising tension?"""

            try:
                response = await self._query_llm(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    model=self.pacing_analysis_model
                )

                # Parse JSON response
                try:
                    result = json.loads(response)
                    is_intentional = result.get("is_intentional", False)
                    risk_level = result.get("risk_level", "medium")
                    recommendation = result.get("recommendation", "Consider escalating tension in upcoming chapters")

                    # Determine severity based on chapter count and LLM analysis
                    if is_intentional and risk_level == "low":
                        # Intentional plateau with low risk - just info
                        severity = "info"
                    elif chapter_count >= 5:
                        # Long plateau - error level
                        severity = "error"
                    else:
                        # Short plateau - warning level
                        severity = "warning"

                    # Only add warning if not intentional or high risk
                    if not is_intentional or risk_level in ["medium", "high"]:
                        avg_tension = sum(scores) / len(scores)
                        warnings.append(HealthWarning(
                            type="PACING_PLATEAU",
                            severity=severity,
                            message=(
                                f"Tension plateau detected: {chapter_count} consecutive chapters "
                                f"({chapters_in_plateau[0].chapter_id} through {chapters_in_plateau[-1].chapter_id}) "
                                f"with similar tension (~{avg_tension:.1f}/10, variation: {max(scores) - min(scores):.1f})"
                            ),
                            recommendation=recommendation,
                            chapters=[ch.chapter_id for ch in chapters_in_plateau],
                            data={
                                "tension_scores": scores,
                                "avg_tension": avg_tension,
                                "variation": max(scores) - min(scores),
                                "chapter_count": chapter_count,
                                "is_intentional": is_intentional,
                                "risk_level": risk_level,
                                "llm_reasoning": result.get("reasoning", "")
                            }
                        ))

                except json.JSONDecodeError:
                    # LLM didn't return valid JSON - fall back to simple warning
                    logger.warning(f"Pacing LLM response not JSON: {response[:100]}")
                    avg_tension = sum(scores) / len(scores)
                    warnings.append(HealthWarning(
                        type="PACING_PLATEAU",
                        severity="error" if chapter_count >= 5 else "warning",
                        message=(
                            f"Flat pacing detected: Chapters "
                            f"{chapters_in_plateau[0].chapter_id} through "
                            f"{chapters_in_plateau[-1].chapter_id} have similar tension "
                            f"({', '.join(f'{t:.1f}' for t in scores[:5])}...)"
                        ),
                        recommendation="Next scene should escalate tension significantly",
                        chapters=[ch.chapter_id for ch in chapters_in_plateau],
                        data={
                            "tension_scores": scores,
                            "avg_tension": avg_tension,
                            "variation": max(scores) - min(scores),
                            "chapter_count": chapter_count
                        }
                    ))

            except Exception as e:
                logger.error(f"Pacing plateau LLM analysis failed: {e}")
                # Fall back to simple warning without LLM analysis
                avg_tension = sum(scores) / len(scores)
                warnings.append(HealthWarning(
                    type="PACING_PLATEAU",
                    severity="error" if chapter_count >= 5 else "warning",
                    message=(
                        f"Flat pacing detected: {chapter_count} chapters with similar tension"
                    ),
                    recommendation="Consider escalating tension in upcoming chapters",
                    chapters=[ch.chapter_id for ch in chapters_in_plateau],
                    data={
                        "tension_scores": scores,
                        "avg_tension": avg_tension,
                        "variation": max(scores) - min(scores),
                        "chapter_count": chapter_count,
                        "llm_error": str(e)
                    }
                ))

        return warnings

    # Save the Cat! 15-Beat Structure with target percentages
    BEAT_TARGETS = {
        1: {"percent": 1, "name": "Opening Image"},
        2: {"percent": 5, "name": "Theme Stated"},
        3: {"percent": 10, "name": "Setup Complete"},
        4: {"percent": 10, "name": "Catalyst"},
        5: {"percent": 20, "name": "Debate"},
        6: {"percent": 20, "name": "Break into Two"},
        7: {"percent": 22, "name": "B Story"},
        8: {"percent": 50, "name": "Fun & Games"},
        9: {"percent": 50, "name": "Midpoint"},
        10: {"percent": 75, "name": "Bad Guys Close In"},
        11: {"percent": 75, "name": "All Is Lost"},
        12: {"percent": 80, "name": "Dark Night of the Soul"},
        13: {"percent": 80, "name": "Break into Three"},
        14: {"percent": 99, "name": "Finale"},
        15: {"percent": 100, "name": "Final Image"}
    }

    async def _check_beat_progress(
        self,
        db: Session,
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Check A2: Beat Progress Validation (Phase 3D).

        Validates manuscript follows 15-beat Save the Cat! structure at correct percentages.

        Algorithm:
        1. Load Beat_Sheet.md from Story Bible (15 beats with target percentages)
        2. Calculate current manuscript completion percentage
        3. Determine which beat should be active at current completion
        4. Query Knowledge Graph for scenes tagged with beat numbers
        5. Check if current scenes align with expected beat
        6. Warn if ahead/behind expected beat progression

        Args:
            db: Database session
            chapters: List of chapters to analyze

        Returns:
            List of health warnings for beat deviations
        """
        warnings = []

        # Calculate total word count and completion percentage
        total_word_count = sum(ch.total_word_count for ch in chapters if ch.total_word_count)

        if total_word_count == 0:
            return warnings  # No word count data yet

        # Get target manuscript length from settings (default: 80,000 words)
        target_word_count = settings_service.get(
            "project.target_word_count", self.project_id
        ) or 80000

        # Calculate manuscript completion percentage
        manuscript_completion = min(100, (total_word_count / target_word_count) * 100)

        # Get tolerance from settings
        beat_tolerance = settings_service.get(
            "health_checks.beat_progress.tolerance", self.project_id
        ) or 10  # Default: 10% deviation allowed

        logger.info(f"Beat progress check: {total_word_count} words ({manuscript_completion:.1f}% complete) with {self.beat_progress_model}")

        # Determine expected beat at current completion
        expected_beat_number = 1
        expected_beat_name = "Opening Image"
        for beat_num in sorted(self.BEAT_TARGETS.keys()):
            beat_info = self.BEAT_TARGETS[beat_num]
            if manuscript_completion >= beat_info["percent"]:
                expected_beat_number = beat_num
                expected_beat_name = beat_info["name"]

        # Fetch beats from database to check actual progress
        beats = db.query(Beat).filter(
            Beat.project_id == self.project_id
        ).order_by(Beat.number).all()

        # If no beats defined, create them from BEAT_TARGETS
        if not beats:
            logger.info("No beats found in database, using default 15-beat structure")
            # Check scenes for beat assignments
            all_scenes = []
            for ch in chapters:
                all_scenes.extend(ch.scenes if hasattr(ch, 'scenes') else [])

            # Find current beat from scene assignments
            current_beat_number = 1
            for scene in all_scenes:
                if hasattr(scene, 'beat_number') and scene.beat_number:
                    current_beat_number = max(current_beat_number, scene.beat_number)

            # Compare expected vs actual beat
            beat_deviation = expected_beat_number - current_beat_number

            if abs(beat_deviation) > 0:
                expected_percent = self.BEAT_TARGETS.get(expected_beat_number, {}).get("percent", 0)
                current_percent = self.BEAT_TARGETS.get(current_beat_number, {}).get("percent", 0)
                deviation_points = abs(expected_percent - current_percent)

                if beat_deviation > 0 and deviation_points > beat_tolerance:
                    # Behind schedule
                    severity = "error" if deviation_points > 20 else "warning"
                    current_beat_name = self.BEAT_TARGETS.get(current_beat_number, {}).get("name", "Unknown")
                    warnings.append(HealthWarning(
                        type="BEAT_PROGRESS_BEHIND",
                        severity=severity,
                        message=(
                            f"Manuscript is {manuscript_completion:.0f}% complete but still in "
                            f"Beat {current_beat_number} ({current_beat_name} at {current_percent}%). "
                            f"Expected to be at Beat {expected_beat_number} ({expected_beat_name} at {expected_percent}%). "
                            f"You're {deviation_points:.0f} points behind."
                        ),
                        recommendation="Consider accelerating plot progression to reach expected beats",
                        data={
                            "manuscript_completion": manuscript_completion,
                            "expected_beat": expected_beat_number,
                            "expected_beat_name": expected_beat_name,
                            "current_beat": current_beat_number,
                            "current_beat_name": current_beat_name,
                            "deviation_points": deviation_points,
                            "behind_ahead": "behind"
                        }
                    ))
                elif beat_deviation < 0 and deviation_points > beat_tolerance:
                    # Ahead of schedule
                    severity = "warning"  # Being ahead is less critical
                    current_beat_name = self.BEAT_TARGETS.get(current_beat_number, {}).get("name", "Unknown")
                    warnings.append(HealthWarning(
                        type="BEAT_PROGRESS_AHEAD",
                        severity=severity,
                        message=(
                            f"Manuscript is {manuscript_completion:.0f}% complete and already at "
                            f"Beat {current_beat_number} ({current_beat_name} at {current_percent}%). "
                            f"Expected to be at Beat {expected_beat_number} ({expected_beat_name} at {expected_percent}%). "
                            f"Pacing may be too fast by {deviation_points:.0f} points."
                        ),
                        recommendation="Consider expanding character development or subplot scenes",
                        data={
                            "manuscript_completion": manuscript_completion,
                            "expected_beat": expected_beat_number,
                            "expected_beat_name": expected_beat_name,
                            "current_beat": current_beat_number,
                            "current_beat_name": current_beat_name,
                            "deviation_points": deviation_points,
                            "behind_ahead": "ahead"
                        }
                    ))
        else:
            # Use database beats
            for beat in beats:
                if beat.actual_percentage is None:
                    continue

                deviation = abs(beat.actual_percentage - beat.target_percentage)

                if deviation > self.beat_deviation_error:
                    warnings.append(HealthWarning(
                        type="BEAT_DEVIATION",
                        severity="error",
                        message=(
                            f"Beat '{beat.name}' is significantly off target: "
                            f"expected {beat.target_percentage}%, "
                            f"actual {beat.actual_percentage:.1f}% "
                            f"(deviation: {deviation:.1f}%)"
                        ),
                        recommendation="Consider restructuring to align with beat sheet",
                        data={
                            "beat_name": beat.name,
                            "beat_number": beat.number,
                            "target_percentage": beat.target_percentage,
                            "actual_percentage": beat.actual_percentage,
                            "deviation": deviation
                        }
                    ))
                elif deviation > self.beat_deviation_warning:
                    warnings.append(HealthWarning(
                        type="BEAT_DEVIATION",
                        severity="warning",
                        message=(
                            f"Beat '{beat.name}' is off target: "
                            f"expected {beat.target_percentage}%, "
                            f"actual {beat.actual_percentage:.1f}% "
                            f"(deviation: {deviation:.1f}%)"
                        ),
                        recommendation="Monitor beat placement in upcoming chapters",
                        data={
                            "beat_name": beat.name,
                            "beat_number": beat.number,
                            "target_percentage": beat.target_percentage,
                            "actual_percentage": beat.actual_percentage,
                            "deviation": deviation
                        }
                    ))

        return warnings

    async def _check_timeline_consistency(
        self,
        db: Session,
        scenes: List[Scene]
    ) -> List[HealthWarning]:
        """
        Check A3: Timeline Consistency (Strategic Decision 1: Full LLM Semantic Analysis).

        Uses LLM to analyze scene pairs for semantic conflicts in:
        - Character locations (teleportation detection)
        - World rules consistency
        - Dropped threads

        Args:
            db: Database session
            scenes: List of scenes to analyze (ordered by timestamp)

        Returns:
            List of health warnings for timeline conflicts
        """
        warnings = []

        if not self.timeline_semantic_analysis:
            return warnings  # Semantic analysis disabled

        if len(scenes) < 2:
            return warnings  # Need at least 2 scenes

        # Sort scenes by timestamp
        sorted_scenes = sorted(scenes, key=lambda s: s.timestamp or "")

        logger.info(f"Timeline consistency check: analyzing {len(sorted_scenes)} scenes with {self.timeline_consistency_model}")

        # Phase 3E: Full LLM semantic analysis with configurable model
        # Analyze consecutive scene pairs for conflicts
        for i in range(len(sorted_scenes) - 1):
            scene_a = sorted_scenes[i]
            scene_b = sorted_scenes[i + 1]

            # Build context for LLM
            context = f"""## Scene {i+1}: {scene_a.scene_id}
**Summary**: {scene_a.summary or "No summary available"}
**Timestamp**: {scene_a.timestamp or "Unknown"}
**Characters Present**: {", ".join(scene_a.characters_present or [])}
**Location**: {scene_a.location or "Unknown"}

## Scene {i+2}: {scene_b.scene_id}
**Summary**: {scene_b.summary or "No summary available"}
**Timestamp**: {scene_b.timestamp or "Unknown"}
**Characters Present**: {", ".join(scene_b.characters_present or [])}
**Location**: {scene_b.location or "Unknown"}
"""

            # LLM prompt for timeline analysis
            system_prompt = """You are a narrative continuity expert. Analyze consecutive scenes for timeline conflicts.

Check for:
1. **Character Teleportation**: Characters appearing in different locations without travel time
2. **World Rules Violations**: Magic systems, physics, or established rules being broken
3. **Dropped Threads**: Important plot elements introduced but not resolved

Respond in JSON format:
{
  "conflicts": [
    {
      "type": "character_teleportation" | "world_rules" | "dropped_thread",
      "severity": "error" | "warning" | "info",
      "description": "Clear description of the conflict",
      "characters": ["character names if relevant"],
      "confidence": 0.0-1.0
    }
  ]
}

Only report conflicts with confidence >= 0.7. If no conflicts, return empty array."""

            user_prompt = f"""Analyze these consecutive scenes for timeline consistency issues:

{context}

Are there any timeline conflicts, character teleportation, or world rule violations?"""

            try:
                # Query LLM with configurable model
                response = await self._query_llm(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    model=self.timeline_consistency_model
                )

                # Parse JSON response
                import json
                try:
                    result = json.loads(response)
                    conflicts = result.get("conflicts", [])

                    for conflict in conflicts:
                        confidence = conflict.get("confidence", 0.0)

                        # Filter by confidence threshold
                        if confidence >= self.timeline_confidence_threshold:
                            warnings.append(HealthWarning(
                                type=conflict.get("type", "TIMELINE_ERROR").upper(),
                                severity=conflict.get("severity", "warning"),
                                message=conflict.get("description", "Timeline consistency issue detected"),
                                recommendation="Review scene transitions and character movements",
                                scenes=[scene_a.scene_id, scene_b.scene_id],
                                characters=conflict.get("characters", []),
                                data={
                                    "confidence": confidence,
                                    "scene_pair": [scene_a.scene_id, scene_b.scene_id]
                                }
                            ))

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse LLM response as JSON: {response[:100]}")

            except Exception as e:
                logger.error(f"Timeline consistency check failed for scenes {scene_a.scene_id}-{scene_b.scene_id}: {e}")

        return warnings

    async def _check_flaw_challenges(
        self,
        db: Session,
        chapter: Chapter
    ) -> List[HealthWarning]:
        """
        Check B1: Fatal Flaw Challenge Monitoring (Phase 3E: Enhanced with LLM).

        Tracks when protagonist's Fatal Flaw was last tested.
        - Primary: Use FlawChallenge database records (explicit tracking)
        - Fallback: Use LLM to detect implicit flaw challenges in scene text

        Args:
            db: Database session
            chapter: Chapter to check

        Returns:
            List of health warnings for flaw challenge gaps
        """
        warnings = []

        # Fetch flaw challenges for this chapter's scenes
        scene_ids = [s.id for s in chapter.scenes]

        if not scene_ids:
            return warnings

        challenges = db.query(FlawChallenge).filter(
            FlawChallenge.scene_id.in_(scene_ids),
            FlawChallenge.project_id == self.project_id
        ).order_by(FlawChallenge.timestamp.desc()).all()

        if challenges:
            # Check most recent challenge from explicit tracking
            most_recent = challenges[0]

            if most_recent.scenes_since_last > self.flaw_challenge_frequency:
                warnings.append(HealthWarning(
                    type="FLAW_CHALLENGE_GAP",
                    severity="warning",
                    message=(
                        f"Protagonist's Fatal Flaw ({most_recent.character_id}) "
                        f"hasn't been challenged in {most_recent.scenes_since_last} scenes"
                    ),
                    recommendation="Create a scene where protagonist must confront their flaw",
                    characters=[most_recent.character_id],
                    data={
                        "character_id": most_recent.character_id,
                        "scenes_since_last": most_recent.scenes_since_last,
                        "last_challenge_type": most_recent.challenge_type,
                        "last_outcome": most_recent.outcome,
                        "source": "explicit_tracking"
                    }
                ))
        else:
            # Phase 3E: No explicit tracking - use LLM to detect implicit challenges
            # This is useful for writers who don't manually track FlawChallenge events
            logger.info(f"Flaw challenge check: No explicit tracking found, using LLM analysis with {self.flaw_challenges_model}")

            # Analyze recent scenes for implicit flaw challenges
            recent_scenes = chapter.scenes[-5:] if len(chapter.scenes) > 5 else chapter.scenes

            if recent_scenes:
                context = "## Recent Scenes:\n\n"
                for scene in recent_scenes:
                    context += f"**{scene.scene_id}**: {scene.summary or 'No summary'}\n\n"

                system_prompt = """You are a character arc analyst. Identify whether the protagonist's Fatal Flaw is being challenged in these scenes.

A Fatal Flaw challenge occurs when:
- The protagonist faces a situation that tests their core weakness
- Their flaw causes them to make mistakes or miss opportunities
- They must choose between their flaw and growth

Respond in JSON format:
{
  "challenges_detected": 0-5,
  "scenes_since_last_challenge": 0-10,
  "severity": "warning" | "info" | null,
  "recommendation": "Brief suggestion if gap is too long",
  "confidence": 0.0-1.0
}

If no challenges detected or gap < 5 scenes, return null severity."""

                user_prompt = f"""Analyze these recent scenes for Fatal Flaw challenges:

{context}

How many flaw challenges are present? Is there a concerning gap?"""

                try:
                    response = await self._query_llm(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        model=self.flaw_challenges_model
                    )

                    import json
                    try:
                        result = json.loads(response)
                        challenges_detected = result.get("challenges_detected", 0)
                        scenes_since_last = result.get("scenes_since_last_challenge", 0)
                        severity = result.get("severity")
                        confidence = result.get("confidence", 0.5)

                        # Only warn if gap exceeds threshold and confidence is decent
                        if severity and scenes_since_last > self.flaw_challenge_frequency and confidence >= 0.6:
                            warnings.append(HealthWarning(
                                type="FLAW_CHALLENGE_GAP",
                                severity=severity,
                                message=(
                                    f"Protagonist's Fatal Flaw hasn't been challenged recently "
                                    f"(~{scenes_since_last} scenes since last challenge, LLM detected)"
                                ),
                                recommendation=result.get("recommendation", "Create a scene where protagonist must confront their flaw"),
                                chapters=[chapter.chapter_id],
                                data={
                                    "challenges_detected": challenges_detected,
                                    "scenes_since_last": scenes_since_last,
                                    "confidence": confidence,
                                    "source": "llm_analysis"
                                }
                            ))

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse flaw challenge response as JSON: {response[:100]}")

                except Exception as e:
                    logger.error(f"Flaw challenge LLM analysis failed: {e}")

        return warnings

    async def _check_cast_function(
        self,
        db: Session,
        chapter: Chapter
    ) -> List[HealthWarning]:
        """
        Check B2: Cast Function Verification.

        Ensures supporting characters serve their narrative function.
        Warns if characters appear too rarely.

        Args:
            db: Database session
            chapter: Chapter to check

        Returns:
            List of health warnings for underutilized characters
        """
        warnings = []

        # Phase 3E: Cast function tracking with configurable model
        # Collect all characters mentioned in this chapter's scenes
        character_appearances = {}

        for scene in chapter.scenes:
            for character in (scene.characters_present or []):
                if character not in character_appearances:
                    character_appearances[character] = []
                character_appearances[character].append(scene.scene_id)

        if not character_appearances:
            return warnings  # No characters tracked yet

        logger.info(f"Cast function check: analyzing {len(character_appearances)} characters in {chapter.chapter_id} with {self.cast_function_model}")

        # Check for underutilized supporting characters
        for character, scenes in character_appearances.items():
            appearance_count = len(scenes)

            # Skip protagonist (appears frequently)
            if appearance_count > 10:
                continue  # Likely protagonist or major character

            # Warn if supporting character appears too rarely
            if appearance_count < self.min_cast_appearances:
                # Use LLM to analyze if character has clear narrative function
                context = f"""## Character: {character}
**Appearances**: {appearance_count} scenes in this chapter
**Scenes**: {", ".join(scenes)}

**Scene Summaries**:
"""

                for scene_id in scenes[:3]:  # Limit to 3 scenes
                    scene = next((s for s in chapter.scenes if s.scene_id == scene_id), None)
                    if scene:
                        context += f"\n- **{scene_id}**: {scene.summary or 'No summary'}"

                system_prompt = """You are a narrative structure analyst. Evaluate whether a supporting character has a clear narrative function.

Analyze:
1. **Narrative Function**: Does the character serve a clear purpose (obstacle, mentor, ally, foil)?
2. **Underutilization**: Given their appearances, are they being used effectively?
3. **Recommendation**: Should they appear more, be developed, or be cut?

Respond in JSON format:
{
  "has_clear_function": true | false,
  "function_type": "obstacle" | "mentor" | "ally" | "foil" | "unclear",
  "is_underutilized": true | false,
  "severity": "warning" | "info",
  "recommendation": "Brief suggestion for improvement",
  "confidence": 0.0-1.0
}"""

                user_prompt = f"""Analyze this supporting character's narrative function:

{context}

Does this character have a clear narrative purpose? Are they underutilized?"""

                try:
                    # Query LLM with configurable model
                    response = await self._query_llm(
                        prompt=user_prompt,
                        system_prompt=system_prompt,
                        model=self.cast_function_model
                    )

                    # Parse JSON response
                    import json
                    try:
                        result = json.loads(response)
                        is_underutilized = result.get("is_underutilized", False)
                        has_clear_function = result.get("has_clear_function", True)
                        confidence = result.get("confidence", 0.5)

                        # Only warn if truly underutilized with decent confidence
                        if is_underutilized and confidence >= 0.6:
                            warnings.append(HealthWarning(
                                type="UNDERUTILIZED_CHARACTER",
                                severity=result.get("severity", "info"),
                                message=(
                                    f"Character '{character}' appears only {appearance_count} times "
                                    f"{'with unclear function' if not has_clear_function else 'and may be underutilized'}"
                                ),
                                recommendation=result.get("recommendation", "Consider giving this character more scenes or a clearer role"),
                                chapters=[chapter.chapter_id],
                                characters=[character],
                                data={
                                    "appearance_count": appearance_count,
                                    "function_type": result.get("function_type", "unclear"),
                                    "has_clear_function": has_clear_function,
                                    "confidence": confidence
                                }
                            ))

                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse cast function response as JSON: {response[:100]}")

                except Exception as e:
                    logger.error(f"Cast function check failed for character {character}: {e}")

        return warnings

    async def _check_symbolic_layering(
        self,
        db: Session,
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Check C1: Symbolic Layering (Phase 3D).

        Ensures symbols recur throughout manuscript with evolving meanings
        (not one-off decorations).

        Algorithm:
        1. Extract symbols from Theme.md in Story Bible
        2. Query Knowledge Graph for symbol mentions across scenes
        3. Use LLM to analyze:
           - Symbol recurrence frequency
           - Whether meaning evolves or stays static
           - Whether symbols appear at thematically important moments
        4. Warn if symbols are absent for too long or lack evolution

        Args:
            db: Database session
            chapters: List of chapters to analyze

        Returns:
            List of health warnings for weak or static symbols
        """
        warnings = []

        if not chapters:
            return warnings

        # Get minimum recurrences from settings
        min_recurrences = settings_service.get(
            "health_checks.symbolic.min_recurrences", self.project_id
        ) or 3  # Default: 3 appearances

        logger.info(f"Symbolic layering check: analyzing {len(chapters)} chapters with {self.symbolic_layering_model}")

        # Collect all scenes and track symbol occurrences by chapter
        all_scenes = []
        chapter_map = {}  # scene_id -> chapter_id mapping
        for ch in chapters:
            scenes = ch.scenes if hasattr(ch, 'scenes') else []
            all_scenes.extend(scenes)
            for scene in scenes:
                chapter_map[scene.scene_id] = ch.chapter_id

        if not all_scenes:
            return warnings

        # Build context for LLM to analyze symbols
        scene_summaries_by_chapter = {}
        for ch in chapters[:20]:  # Limit to first 20 chapters for context
            chapter_scenes = ch.scenes if hasattr(ch, 'scenes') else []
            summaries = []
            for scene in chapter_scenes[:3]:  # Limit to 3 scenes per chapter
                if scene.summary:
                    summaries.append(scene.summary[:300])
            if summaries:
                scene_summaries_by_chapter[ch.chapter_id] = summaries

        # LLM system prompt for symbolic analysis
        system_prompt = """You are a literary symbol analyst. Analyze symbolic layering in manuscripts.

Good symbolic layering means:
- Symbols recur throughout the manuscript (minimum 3 appearances)
- Symbol meaning evolves and deepens over time
- Symbols appear at thematically critical beats (Midpoint, All Is Lost, Finale)

Analyze the provided scene summaries and identify:
1. Key symbols (objects, images, motifs that carry symbolic weight)
2. How often each symbol appears
3. Whether the symbol's meaning evolves or stays static
4. Whether symbols appear at critical structural beats

Respond in JSON format:
{
  "symbols_detected": [
    {
      "symbol": "name of symbol",
      "occurrences": ["chapter_id1", "chapter_id2", ...],
      "recurrence_count": number,
      "recurrence_adequate": true | false,
      "meaning_evolves": true | false,
      "appears_at_critical_beats": true | false,
      "analysis": "Brief analysis of how this symbol is used",
      "recommendation": "Specific suggestion if improvement needed"
    }
  ],
  "overall_symbolic_health": "excellent" | "good" | "fair" | "poor",
  "general_recommendations": ["list of general suggestions"]
}"""

        # Build chapter summaries for analysis
        chapter_content = []
        for ch_id, summaries in scene_summaries_by_chapter.items():
            chapter_content.append(f"**{ch_id}**:\n" + "\n".join(f"  - {s}" for s in summaries))

        user_prompt = f"""Analyze symbolic layering in this manuscript:

**Manuscript Structure**: {len(chapters)} chapters analyzed

**Chapter Summaries**:
{chr(10).join(chapter_content)}

Identify key symbols, their recurrence patterns, and whether their meanings evolve throughout the manuscript.

Critical beats to check for symbol appearance:
- Opening Image (1%)
- Midpoint (50%)
- All Is Lost (75%)
- Final Image (100%)"""

        try:
            response = await self._query_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model=self.symbolic_layering_model
            )

            # Parse JSON response
            try:
                result = json.loads(response)
                symbols = result.get("symbols_detected", [])
                overall_health = result.get("overall_symbolic_health", "fair")

                for symbol_data in symbols:
                    symbol_name = symbol_data.get("symbol", "Unknown")
                    recurrence_count = symbol_data.get("recurrence_count", 0)
                    recurrence_adequate = symbol_data.get("recurrence_adequate", True)
                    meaning_evolves = symbol_data.get("meaning_evolves", True)
                    appears_at_critical = symbol_data.get("appears_at_critical_beats", True)
                    occurrences = symbol_data.get("occurrences", [])
                    recommendation = symbol_data.get("recommendation", "")
                    analysis = symbol_data.get("analysis", "")

                    # Check for inadequate recurrence
                    if not recurrence_adequate:
                        # Find where symbol last appeared
                        last_chapter = occurrences[-1] if occurrences else "early chapters"
                        warnings.append(HealthWarning(
                            type="SYMBOL_INSUFFICIENT_RECURRENCE",
                            severity="warning",
                            message=(
                                f"Symbol '{symbol_name}' appears only {recurrence_count} times "
                                f"(minimum {min_recurrences} recommended). "
                                f"Last seen in {last_chapter}."
                            ),
                            recommendation=recommendation or f"Consider reinforcing '{symbol_name}' in later chapters",
                            chapters=occurrences,
                            data={
                                "symbol": symbol_name,
                                "recurrence_count": recurrence_count,
                                "min_required": min_recurrences,
                                "occurrences": occurrences,
                                "analysis": analysis
                            }
                        ))

                    # Check for static meaning (no evolution)
                    if recurrence_count >= min_recurrences and not meaning_evolves:
                        warnings.append(HealthWarning(
                            type="SYMBOL_STATIC_MEANING",
                            severity="info",
                            message=(
                                f"Symbol '{symbol_name}' recurs {recurrence_count} times "
                                f"but its meaning appears static. "
                                f"Consider deepening its significance through the arc."
                            ),
                            recommendation=recommendation or f"Let '{symbol_name}' gain new layers of meaning at key beats",
                            chapters=occurrences,
                            data={
                                "symbol": symbol_name,
                                "recurrence_count": recurrence_count,
                                "meaning_evolves": False,
                                "analysis": analysis
                            }
                        ))

                    # Check for missing critical beats
                    if recurrence_count >= min_recurrences and not appears_at_critical:
                        warnings.append(HealthWarning(
                            type="SYMBOL_MISSING_CRITICAL_BEATS",
                            severity="info",
                            message=(
                                f"Symbol '{symbol_name}' doesn't appear at critical structural beats "
                                f"(Opening Image, Midpoint, All Is Lost, or Finale). "
                                f"Consider a callback at these moments."
                            ),
                            recommendation=recommendation or f"Add '{symbol_name}' callback at Midpoint or Finale",
                            chapters=occurrences,
                            data={
                                "symbol": symbol_name,
                                "appears_at_critical_beats": False,
                                "occurrences": occurrences,
                                "analysis": analysis
                            }
                        ))

                # Add general warning if overall health is poor
                if overall_health == "poor":
                    general_recs = result.get("general_recommendations", [])
                    warnings.append(HealthWarning(
                        type="SYMBOLIC_LAYERING_WEAK",
                        severity="warning",
                        message=(
                            f"Overall symbolic layering is weak. "
                            f"The manuscript may lack thematic depth from recurring symbols."
                        ),
                        recommendation="; ".join(general_recs[:3]) if general_recs else "Identify 2-3 core symbols and weave them throughout the manuscript",
                        data={
                            "overall_health": overall_health,
                            "symbols_analyzed": len(symbols),
                            "general_recommendations": general_recs
                        }
                    ))

            except json.JSONDecodeError:
                logger.warning(f"Symbolic layering LLM response not JSON: {response[:200]}")
                # Fall back to simple analysis based on response
                if "no symbols" in response.lower() or "lack" in response.lower():
                    warnings.append(HealthWarning(
                        type="SYMBOLIC_LAYERING_UNCLEAR",
                        severity="info",
                        message="Unable to detect clear symbolic patterns in the manuscript",
                        recommendation="Consider establishing key symbols early and recurring them at critical beats",
                        data={
                            "llm_response_summary": response[:500]
                        }
                    ))

        except Exception as e:
            logger.error(f"Symbolic layering check failed: {e}")
            # Return graceful fallback - no warning added to avoid false positives

        return warnings

    async def _check_theme_resonance(
        self,
        db: Session,
        chapter: Chapter
    ) -> List[HealthWarning]:
        """
        Check C2: Theme Resonance (Strategic Decision 2: Hybrid LLM + Manual Override).

        Verifies theme appears at critical structural beats.
        - Uses LLM auto-scoring if enabled
        - Respects manual writer overrides

        Args:
            db: Database session
            chapter: Chapter to check

        Returns:
            List of health warnings for weak or missing themes
        """
        warnings = []

        if not self.theme_auto_score:
            return warnings  # Auto-scoring disabled

        # Phase 3E: Hybrid LLM + manual override implementation
        # Fetch beats that fall within this chapter
        beats = db.query(Beat).filter(
            Beat.project_id == self.project_id,
            Beat.chapter_id == chapter.id
        ).all()

        if not beats:
            return warnings  # No beats in this chapter

        logger.info(f"Theme resonance check: analyzing {len(beats)} beats in {chapter.chapter_id} with {self.theme_resonance_model}")

        # Analyze each beat for theme presence
        for beat in beats:
            # Check for manual override first (Strategic Decision 2)
            if self.theme_allow_manual_override:
                override = db.query(ThemeResonanceOverride).filter(
                    ThemeResonanceOverride.project_id == self.project_id,
                    ThemeResonanceOverride.beat_id == beat.id
                ).first()

                if override and override.manual_score is not None:
                    # Use manual score, skip LLM
                    if override.manual_score < self.min_resonance_score:
                        warnings.append(HealthWarning(
                            type="WEAK_THEME",
                            severity="warning",
                            message=(
                                f"Beat '{beat.name}' has low theme resonance: "
                                f"manual score {override.manual_score}/10 "
                                f"(writer override: {override.reason})"
                            ),
                            recommendation="Strengthen thematic elements at this beat",
                            chapters=[chapter.chapter_id],
                            data={
                                "beat_name": beat.name,
                                "manual_score": override.manual_score,
                                "override_reason": override.reason,
                                "is_manual_override": True
                            }
                        ))
                    continue  # Skip LLM scoring

            # LLM auto-scoring for theme resonance
            # Build context from beat and surrounding scenes
            beat_context = f"""## Beat: {beat.name}
**Description**: {beat.description or "No description"}
**Target Position**: {beat.target_percentage}% through manuscript
**Status**: {beat.status}
"""

            # Get scenes near this beat
            nearby_scenes = [s for s in chapter.scenes if s.beat_number == beat.number]

            if nearby_scenes:
                beat_context += "\n### Scenes at this beat:\n"
                for scene in nearby_scenes[:3]:  # Limit to 3 scenes
                    beat_context += f"\n**{scene.scene_id}**: {scene.summary or 'No summary'}\n"

            # LLM prompt for theme scoring
            system_prompt = """You are a literary theme analyst. Evaluate how strongly a story's central theme is expressed at a specific structural beat.

Score theme resonance on a 0-10 scale:
- 10: Theme is explicitly and powerfully expressed
- 7-9: Theme is clearly present and well-integrated
- 4-6: Theme is present but could be stronger
- 1-3: Theme is barely noticeable
- 0: Theme is absent

Respond in JSON format:
{
  "score": 0-10,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of the score",
  "suggestions": "Optional suggestions for strengthening theme presence"
}"""

            user_prompt = f"""Analyze the theme resonance at this beat:

{beat_context}

**Project Theme** (assumed): Identity, transformation, or central dramatic question

Rate how strongly the theme is expressed at this beat (0-10 scale)."""

            try:
                # Query LLM with configurable model
                response = await self._query_llm(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    model=self.theme_resonance_model
                )

                # Parse JSON response
                import json
                try:
                    result = json.loads(response)
                    score = result.get("score", 5)
                    confidence = result.get("confidence", 0.5)
                    reasoning = result.get("reasoning", "")

                    # Store LLM score in override table (for future reference)
                    existing_override = db.query(ThemeResonanceOverride).filter(
                        ThemeResonanceOverride.project_id == self.project_id,
                        ThemeResonanceOverride.beat_id == beat.id
                    ).first()

                    if existing_override:
                        existing_override.llm_score = score
                    else:
                        new_override = ThemeResonanceOverride(
                            project_id=self.project_id,
                            beat_id=beat.id,
                            theme_id="default",  # TODO: Support multiple themes
                            llm_score=score,
                            manual_score=None,
                            reason=reasoning,
                            timestamp=datetime.now(timezone.utc)
                        )
                        db.add(new_override)

                    db.commit()

                    # Check if score is below threshold
                    if score < self.min_resonance_score:
                        warnings.append(HealthWarning(
                            type="WEAK_THEME",
                            severity="warning" if score < 4 else "info",
                            message=(
                                f"Beat '{beat.name}' has low theme resonance: "
                                f"LLM score {score}/10 (confidence: {confidence:.2f})"
                            ),
                            recommendation=result.get("suggestions", "Strengthen thematic elements at this beat"),
                            chapters=[chapter.chapter_id],
                            data={
                                "beat_name": beat.name,
                                "llm_score": score,
                                "confidence": confidence,
                                "reasoning": reasoning,
                                "is_manual_override": False
                            }
                        ))

                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse theme resonance response as JSON: {response[:100]}")

            except Exception as e:
                logger.error(f"Theme resonance check failed for beat {beat.name}: {e}")

        return warnings

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _calculate_health_score(self, warnings: List[HealthWarning]) -> int:
        """
        Calculate overall health score from warnings.

        Score calculation:
        - Start at 100
        - Error: -10 points each
        - Warning: -5 points each
        - Info: -1 point each
        - Minimum score: 0

        Args:
            warnings: List of health warnings

        Returns:
            Overall health score (0-100)
        """
        score = 100

        for warning in warnings:
            if warning.severity == "error":
                score -= 10
            elif warning.severity == "warning":
                score -= 5
            elif warning.severity == "info":
                score -= 1

        return max(0, score)

    def _store_health_report(
        self,
        db: Session,
        report: HealthReport,
        chapter_db_id: Optional[int] = None
    ):
        """
        Store health report in database for historical tracking.

        Strategic Decision 4: SQLite persistence for longitudinal analysis.

        Args:
            db: Database session
            report: Health report to store
            chapter_db_id: Optional chapter database ID (foreign key)
        """
        try:
            # Convert warnings to JSON
            warnings_json = [w.to_dict() for w in report.warnings]

            # Create history entry
            history = HealthReportHistory(
                report_id=report.report_id,
                project_id=report.project_id,
                scope=report.scope,
                chapter_id=chapter_db_id,
                act_number=report.act_number,
                overall_score=report.overall_score,
                warnings=warnings_json,
                timestamp=datetime.now(timezone.utc)
            )

            db.add(history)
            db.commit()

            logger.info(f"Stored health report: {report.report_id}")

            # Cleanup old reports (retention policy)
            self._cleanup_old_reports(db)

        except Exception as e:
            logger.error(f"Failed to store health report: {e}")
            db.rollback()

    def _cleanup_old_reports(self, db: Session):
        """
        Delete health reports older than retention period.

        Args:
            db: Database session
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.retention_days)

            deleted_count = db.query(HealthReportHistory).filter(
                HealthReportHistory.timestamp < cutoff_date,
                HealthReportHistory.project_id == self.project_id
            ).delete()

            if deleted_count > 0:
                db.commit()
                logger.info(f"Cleaned up {deleted_count} old health reports")

        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")
            db.rollback()

    def get_report(self, report_id: str, db: Optional[Session] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieve stored health report by ID.

        Args:
            report_id: Report ID
            db: Optional database session

        Returns:
            Report dictionary or None if not found
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            report = db.query(HealthReportHistory).filter(
                HealthReportHistory.report_id == report_id
            ).first()

            if report:
                return report.to_dict()
            return None

        finally:
            if close_db:
                db.close()

    def get_trend_data(
        self,
        metric: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical trend data for a specific metric.

        Strategic Decision 4: Longitudinal analysis support.

        Supported metrics:
        - pacing_plateaus: Count of pacing warnings
        - beat_deviations: Beat deviation warnings
        - flaw_challenges: Flaw challenge gap warnings
        - theme_resonance: Theme resonance warnings
        - overall_health: Overall health scores

        Args:
            metric: Metric to analyze
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
            db: Optional database session

        Returns:
            List of trend data points
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            query = db.query(HealthReportHistory).filter(
                HealthReportHistory.project_id == self.project_id
            )

            if start_date:
                query = query.filter(HealthReportHistory.timestamp >= start_date)
            if end_date:
                query = query.filter(HealthReportHistory.timestamp <= end_date)

            reports = query.order_by(HealthReportHistory.timestamp).all()

            trend_data = []

            for report in reports:
                if metric == "overall_health":
                    trend_data.append({
                        "chapter_id": report.chapter_id,
                        "act_number": report.act_number,
                        "score": report.overall_score,
                        "timestamp": report.timestamp.isoformat()
                    })
                else:
                    # Count warnings of specific type
                    warning_type_map = {
                        "pacing_plateaus": "PACING_PLATEAU",
                        "beat_deviations": "BEAT_DEVIATION",
                        "flaw_challenges": "FLAW_CHALLENGE_GAP",
                        "theme_resonance": "WEAK_THEME"
                    }

                    target_type = warning_type_map.get(metric)
                    if target_type:
                        count = sum(
                            1 for w in report.warnings
                            if w.get("type") == target_type
                        )

                        trend_data.append({
                            "chapter_id": report.chapter_id,
                            "act_number": report.act_number,
                            f"{metric}_detected": count,
                            "timestamp": report.timestamp.isoformat()
                        })

            return trend_data

        finally:
            if close_db:
                db.close()

    def set_theme_override(
        self,
        beat_id: str,
        theme_id: str,
        manual_score: float,
        reason: str,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Set manual theme resonance score override.

        Strategic Decision 2: Hybrid LLM + manual override.

        Args:
            beat_id: Beat ID
            theme_id: Theme ID
            manual_score: Writer's manual score (0-10)
            reason: Writer's explanation
            db: Optional database session

        Returns:
            Success status dictionary
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            # Find beat
            beat = db.query(Beat).filter(Beat.beat_id == beat_id).first()

            if not beat:
                return {"success": False, "error": "Beat not found"}

            # Create or update override
            existing = db.query(ThemeResonanceOverride).filter(
                ThemeResonanceOverride.project_id == self.project_id,
                ThemeResonanceOverride.beat_id == beat.id,
                ThemeResonanceOverride.theme_id == theme_id
            ).first()

            if existing:
                existing.manual_score = manual_score
                existing.reason = reason
                existing.timestamp = datetime.now(timezone.utc)
            else:
                override = ThemeResonanceOverride(
                    project_id=self.project_id,
                    beat_id=beat.id,
                    theme_id=theme_id,
                    manual_score=manual_score,
                    llm_score=None,  # Will be populated when LLM scoring runs
                    reason=reason,
                    timestamp=datetime.now(timezone.utc)
                )
                db.add(override)

            db.commit()

            logger.info(
                f"Theme override set: beat={beat_id}, theme={theme_id}, "
                f"score={manual_score}"
            )

            return {
                "success": True,
                "beat_id": beat_id,
                "theme_id": theme_id,
                "manual_score": manual_score
            }

        except Exception as e:
            logger.error(f"Failed to set theme override: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}

        finally:
            if close_db:
                db.close()

    def get_all_overrides(
        self,
        project_id: str,
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all manual theme score overrides for a project.

        Args:
            project_id: Project ID
            db: Optional database session

        Returns:
            List of override dictionaries
        """
        close_db = False
        if db is None:
            db = SettingsSessionLocal()
            close_db = True

        try:
            overrides = db.query(ThemeResonanceOverride).filter(
                ThemeResonanceOverride.project_id == project_id
            ).all()

            return [
                {
                    "beat_id": o.beat.beat_id if o.beat else None,
                    "theme_id": o.theme_id,
                    "manual_score": o.manual_score,
                    "llm_score": o.llm_score,
                    "reason": o.reason,
                    "timestamp": o.timestamp.isoformat() if o.timestamp else None
                }
                for o in overrides
            ]

        finally:
            if close_db:
                db.close()


# =============================================================================
# Singleton Access
# =============================================================================

_graph_health_service: Optional[GraphHealthService] = None


def get_graph_health_service(project_id: Optional[str] = None) -> GraphHealthService:
    """Get or create the Graph Health Service singleton."""
    global _graph_health_service
    if _graph_health_service is None or _graph_health_service.project_id != project_id:
        _graph_health_service = GraphHealthService(project_id=project_id)
    return _graph_health_service
