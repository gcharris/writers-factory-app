"""
Verification Service for GraphRAG.

Tiered verification system for narrative consistency:
- FAST tier (<500ms) - Inline checks after generation
- MEDIUM tier (2-5s) - Background checks with notifications
- SLOW tier (5-30s) - On-demand deep analysis

Part of GraphRAG Phase 4 - Tiered Verification System.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import asyncio
import time
import logging

if TYPE_CHECKING:
    from ..graph.graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)


class VerificationTier(Enum):
    """Verification tiers with different performance profiles."""
    FAST = "fast"        # <500ms, always runs inline
    MEDIUM = "medium"    # 2-5s, runs in background
    SLOW = "slow"        # 5-30s, on-demand only


class IssueSeverity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"    # Blocks output, must fix
    WARNING = "warning"      # Show to user, suggest fix
    INFO = "info"            # Log only, no user notification


@dataclass
class VerificationIssue:
    """A verification issue found during checking."""
    check_name: str
    severity: IssueSeverity
    message: str
    location: Optional[str] = None  # Scene/line reference
    suggestion: Optional[str] = None
    auto_fixable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_name": self.check_name,
            "severity": self.severity.value,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion,
            "auto_fixable": self.auto_fixable
        }


@dataclass
class VerificationResult:
    """Result from running verification checks."""
    tier: VerificationTier
    passed: bool
    issues: List[VerificationIssue]
    duration_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tier": self.tier.value,
            "passed": self.passed,
            "issues": [i.to_dict() for i in self.issues],
            "duration_ms": self.duration_ms
        }


class VerificationService:
    """
    Tiered verification system for narrative consistency.

    FAST tier (inline, <500ms):
    - Character alive/dead status
    - Known fact contradictions
    - Required callbacks present

    MEDIUM tier (background, 2-5s):
    - Flaw challenge frequency
    - Beat alignment
    - Timeline consistency

    SLOW tier (on-demand):
    - Full LLM semantic analysis
    - Voice consistency
    - Pacing analysis
    """

    def __init__(
        self,
        graph_service: Optional['KnowledgeGraphService'] = None,
        health_service: Optional[Any] = None
    ):
        """
        Initialize the VerificationService.

        Args:
            graph_service: KnowledgeGraphService for graph access
            health_service: Optional GraphHealthService for slow checks
        """
        self.graph = graph_service
        self.health = health_service

        # Pending notifications for background checks
        self._pending_notifications: List[Dict] = []

        logger.info("VerificationService initialized")

    def _ensure_graph(self):
        """Lazily initialize graph service if needed."""
        if self.graph is None:
            from backend.graph.graph_service import KnowledgeGraphService
            from backend.graph.schema import SessionLocal
            db = SessionLocal()
            self.graph = KnowledgeGraphService(db)

    async def run_fast_checks(
        self,
        content: str,
        scene_context: Optional[Dict] = None
    ) -> VerificationResult:
        """
        Run fast checks inline. Called after every generation.

        Must complete in <500ms.

        Args:
            content: The content to verify
            scene_context: Optional context (callbacks, beat, protagonist, etc.)

        Returns:
            VerificationResult with issues found
        """
        start = time.time()
        issues = []
        scene_context = scene_context or {}

        self._ensure_graph()

        # Check 1: Character status (alive/dead)
        dead_issues = self._check_dead_characters(content)
        issues.extend(dead_issues)

        # Check 2: Required callbacks
        callback_issues = self._check_required_callbacks(content, scene_context)
        issues.extend(callback_issues)

        # Check 3: Known contradictions
        contradiction_issues = self._check_known_contradictions(content)
        issues.extend(contradiction_issues)

        duration = (time.time() - start) * 1000

        if duration > 500:
            logger.warning(f"FAST checks exceeded 500ms: {duration:.2f}ms")

        return VerificationResult(
            tier=VerificationTier.FAST,
            passed=not any(i.severity == IssueSeverity.CRITICAL for i in issues),
            issues=issues,
            duration_ms=duration
        )

    async def run_medium_checks(
        self,
        content: str,
        scene_context: Optional[Dict] = None
    ) -> VerificationResult:
        """
        Run medium checks in background. Results shown as notifications.

        Args:
            content: The content to verify
            scene_context: Optional context

        Returns:
            VerificationResult with issues found
        """
        start = time.time()
        issues = []
        scene_context = scene_context or {}

        self._ensure_graph()

        # Check 1: Flaw challenge frequency
        flaw_issues = await self._check_flaw_challenge_gap(scene_context)
        issues.extend(flaw_issues)

        # Check 2: Beat alignment
        beat_issues = await self._check_beat_alignment(content, scene_context)
        issues.extend(beat_issues)

        # Check 3: Timeline consistency
        timeline_issues = await self._check_timeline(content, scene_context)
        issues.extend(timeline_issues)

        # Check 4: Missing foreshadowing payoffs
        foreshadow_issues = await self._check_foreshadow_payoffs(scene_context)
        issues.extend(foreshadow_issues)

        duration = (time.time() - start) * 1000

        return VerificationResult(
            tier=VerificationTier.MEDIUM,
            passed=not any(i.severity == IssueSeverity.CRITICAL for i in issues),
            issues=issues,
            duration_ms=duration
        )

    async def run_slow_checks(
        self,
        content: str,
        scene_context: Optional[Dict] = None
    ) -> VerificationResult:
        """
        Run slow checks on-demand only. Full LLM analysis.

        Args:
            content: The content to verify
            scene_context: Optional context

        Returns:
            VerificationResult with issues found
        """
        start = time.time()
        issues = []
        scene_context = scene_context or {}

        if self.health:
            # Delegate to existing health service
            try:
                health_report = await self.health.run_full_analysis(
                    content=content,
                    scene_id=scene_context.get("scene_id")
                )
                issues = self._convert_health_report_to_issues(health_report)
            except Exception as e:
                logger.error(f"Health service analysis failed: {e}")
                issues.append(VerificationIssue(
                    check_name="health_service_error",
                    severity=IssueSeverity.INFO,
                    message=f"Full analysis failed: {str(e)}"
                ))
        else:
            # Basic slow checks without health service
            issues.append(VerificationIssue(
                check_name="health_service_unavailable",
                severity=IssueSeverity.INFO,
                message="Full analysis unavailable - GraphHealthService not configured"
            ))

            # Run what we can without LLM
            voice_issues = self._check_voice_consistency_simple(content, scene_context)
            issues.extend(voice_issues)

        duration = (time.time() - start) * 1000

        return VerificationResult(
            tier=VerificationTier.SLOW,
            passed=not any(i.severity == IssueSeverity.CRITICAL for i in issues),
            issues=issues,
            duration_ms=duration
        )

    # =========================================================================
    # FAST CHECK IMPLEMENTATIONS
    # =========================================================================

    def _check_dead_characters(self, content: str) -> List[VerificationIssue]:
        """Check if deceased characters appear in content."""
        issues = []
        deceased = self._get_dead_characters()

        for char in deceased:
            if char.lower() in content.lower():
                issues.append(VerificationIssue(
                    check_name="character_status",
                    severity=IssueSeverity.CRITICAL,
                    message=f"'{char}' appears in scene but is marked deceased",
                    suggestion=f"Remove references to {char} or update their status",
                    auto_fixable=False
                ))

        return issues

    def _get_dead_characters(self) -> List[str]:
        """Get list of characters marked as deceased."""
        deceased = []
        try:
            if not self.graph:
                return deceased

            characters = self.graph.get_nodes_by_type("CHARACTER")
            for node in characters:
                # Check for death status in edges
                edges = self.graph.get_edges(source_id=node.id)
                for edge in edges:
                    if (edge.relation_type == "HAS_STATUS" and
                        "dead" in (edge.description or "").lower()):
                        deceased.append(node.name)
                        break

                # Also check description
                if node.description and "deceased" in node.description.lower():
                    if node.name not in deceased:
                        deceased.append(node.name)

        except Exception as e:
            logger.warning(f"Failed to get dead characters: {e}")

        return deceased

    def _check_required_callbacks(
        self,
        content: str,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Check if required callbacks are present."""
        issues = []
        required_callbacks = scene_context.get("callbacks", [])

        for callback in required_callbacks:
            if callback.lower() not in content.lower():
                issues.append(VerificationIssue(
                    check_name="missing_callback",
                    severity=IssueSeverity.WARNING,
                    message=f"Expected callback to '{callback}' not found",
                    suggestion=f"Add a reference to '{callback}' for continuity"
                ))

        return issues

    def _check_known_contradictions(self, content: str) -> List[VerificationIssue]:
        """Check for known contradictions from graph."""
        issues = []
        try:
            if not self.graph:
                return issues

            contradictions = self.graph.get_edges_by_type("CONTRADICTS")
            for c in contradictions:
                source_node = self.graph.get_node(c.source_id)
                target_node = self.graph.get_node(c.target_id)

                if source_node and target_node:
                    source_in = source_node.name.lower() in content.lower()
                    target_in = target_node.name.lower() in content.lower()

                    if source_in and target_in:
                        issues.append(VerificationIssue(
                            check_name="known_contradiction",
                            severity=IssueSeverity.WARNING,
                            message=f"Scene references both '{source_node.name}' and '{target_node.name}', which are marked as contradictory",
                            suggestion="Review and resolve the contradiction"
                        ))
        except Exception as e:
            logger.warning(f"Failed to check contradictions: {e}")

        return issues

    # =========================================================================
    # MEDIUM CHECK IMPLEMENTATIONS
    # =========================================================================

    async def _check_flaw_challenge_gap(
        self,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Check if protagonist's flaw hasn't been challenged recently."""
        issues = []

        try:
            if not self.graph:
                return issues

            protagonist = scene_context.get("protagonist")
            if not protagonist:
                return issues

            # Check for CHALLENGES edges involving protagonist
            challenges = self.graph.get_edges_by_type("CHALLENGES")
            recent = [c for c in challenges
                     if protagonist.lower() in (c.description or "").lower()]

            if len(recent) == 0:
                issues.append(VerificationIssue(
                    check_name="flaw_challenge_gap",
                    severity=IssueSeverity.WARNING,
                    message="Protagonist's fatal flaw hasn't been challenged recently",
                    suggestion="Consider adding a moment that tests the protagonist's weakness"
                ))

        except Exception as e:
            logger.warning(f"Flaw challenge check failed: {e}")

        return issues

    async def _check_beat_alignment(
        self,
        content: str,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Check if content aligns with expected beat."""
        issues = []
        expected_beat = scene_context.get("beat_alignment") or scene_context.get("current_beat")

        if not expected_beat:
            return issues

        # Keyword markers for different beats
        beat_keywords = {
            "Opening Image": ["begins", "start", "ordinary", "normal", "everyday"],
            "Theme Stated": ["truth", "lesson", "important", "message"],
            "Setup": ["introduces", "establishes", "world", "life", "routine"],
            "Catalyst": ["discovers", "learns", "receives", "finds out", "changes"],
            "Debate": ["hesitates", "unsure", "reluctant", "doubt", "should"],
            "Break into Two": ["decides", "chooses", "commits", "enters", "leaves"],
            "B Story": ["meets", "connection", "friendship", "love"],
            "Fun and Games": ["explores", "adventure", "discovers", "enjoys"],
            "Midpoint": ["realizes", "victory", "defeat", "reversal", "stakes"],
            "Bad Guys Close In": ["pressure", "closing in", "danger", "problems"],
            "All Is Lost": ["lowest", "fails", "loses", "death", "despair"],
            "Dark Night": ["contemplates", "hopeless", "lost", "alone", "broken"],
            "Break into Three": ["realizes", "solution", "answer", "knows"],
            "Finale": ["confronts", "faces", "final", "showdown", "battle"],
            "Final Image": ["ends", "new", "changed", "transformed"],
        }

        # Normalize beat name
        beat_normalized = expected_beat.replace("_", " ").title()
        keywords = beat_keywords.get(beat_normalized, [])

        if keywords:
            content_lower = content.lower()
            matches = sum(1 for k in keywords if k in content_lower)

            if matches == 0:
                issues.append(VerificationIssue(
                    check_name="beat_alignment",
                    severity=IssueSeverity.INFO,
                    message=f"Scene may not align with expected beat: {expected_beat}",
                    suggestion=f"Consider incorporating elements typical of '{expected_beat}'"
                ))

        return issues

    async def _check_timeline(
        self,
        content: str,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Check for timeline inconsistencies."""
        issues = []

        prev_time = scene_context.get("previous_time_of_day")
        current_time = scene_context.get("time_of_day")

        if prev_time and current_time:
            time_order = ["dawn", "morning", "noon", "afternoon", "evening", "night"]

            try:
                prev_idx = time_order.index(prev_time.lower())
                curr_idx = time_order.index(current_time.lower())

                # If going backwards without scene break
                if curr_idx < prev_idx and not scene_context.get("day_changed"):
                    issues.append(VerificationIssue(
                        check_name="timeline_regression",
                        severity=IssueSeverity.WARNING,
                        message=f"Time appears to go backwards: {prev_time} → {current_time}",
                        suggestion="Add a day transition or adjust the time of day"
                    ))
            except ValueError:
                pass  # Unknown time markers

        return issues

    async def _check_foreshadow_payoffs(
        self,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Check for unresolved foreshadowing setups."""
        issues = []

        try:
            if not self.graph:
                return issues

            # Get FORESHADOWS edges
            foreshadows = self.graph.get_edges_by_type("FORESHADOWS")

            # Get CALLBACKS edges
            callbacks = self.graph.get_edges_by_type("CALLBACKS")
            callback_targets = {c.target_id for c in callbacks}

            # Find foreshadows without callbacks
            for f in foreshadows:
                if f.target_id not in callback_targets:
                    target_node = self.graph.get_node(f.target_id)
                    if target_node:
                        issues.append(VerificationIssue(
                            check_name="unresolved_foreshadow",
                            severity=IssueSeverity.INFO,
                            message=f"Foreshadowing of '{target_node.name}' has no callback/payoff yet",
                            suggestion="Consider adding a callback to this setup"
                        ))

        except Exception as e:
            logger.warning(f"Foreshadow check failed: {e}")

        return issues

    # =========================================================================
    # SLOW CHECK IMPLEMENTATIONS
    # =========================================================================

    def _convert_health_report_to_issues(
        self,
        health_report: Dict
    ) -> List[VerificationIssue]:
        """Convert health service report to verification issues."""
        issues = []

        for check_name, result in health_report.get("checks", {}).items():
            score = result.get("score", 1.0)
            if score < 0.7:
                severity = IssueSeverity.WARNING if score >= 0.5 else IssueSeverity.CRITICAL
                issues.append(VerificationIssue(
                    check_name=check_name,
                    severity=severity,
                    message=result.get("message", f"{check_name} check failed"),
                    suggestion=result.get("recommendation")
                ))

        return issues

    def _check_voice_consistency_simple(
        self,
        content: str,
        scene_context: Dict
    ) -> List[VerificationIssue]:
        """Simple voice consistency check without LLM."""
        issues = []

        # Check for common voice inconsistencies
        pov = scene_context.get("pov", "").lower()

        if pov == "first" and " he thought" in content.lower():
            issues.append(VerificationIssue(
                check_name="pov_inconsistency",
                severity=IssueSeverity.WARNING,
                message="First-person POV uses third-person thought attribution",
                suggestion="Use 'I thought' instead of 'he thought'"
            ))

        if pov == "third limited":
            # Check for head-hopping
            pronouns = ["he", "she"]
            thought_markers = ["thought", "wondered", "felt", "knew"]

            # Simple check: multiple distinct pronouns with thought markers
            pronoun_thoughts = set()
            content_lower = content.lower()
            for p in pronouns:
                for m in thought_markers:
                    if f"{p} {m}" in content_lower:
                        pronoun_thoughts.add(p)

            if len(pronoun_thoughts) > 1:
                issues.append(VerificationIssue(
                    check_name="head_hopping",
                    severity=IssueSeverity.WARNING,
                    message="Possible head-hopping detected (multiple POV characters' thoughts)",
                    suggestion="Stick to one character's internal perspective per scene"
                ))

        return issues

    # =========================================================================
    # NOTIFICATION MANAGEMENT
    # =========================================================================

    def add_notification(
        self,
        scene_id: str,
        issues: List[VerificationIssue]
    ) -> None:
        """Queue notifications for frontend."""
        for issue in issues:
            self._pending_notifications.append({
                "id": f"{scene_id}_{issue.check_name}_{int(time.time() * 1000)}",
                "scene_id": scene_id,
                **issue.to_dict()
            })

    def get_pending_notifications(self) -> List[Dict]:
        """Get and clear pending notifications."""
        notifications = self._pending_notifications.copy()
        self._pending_notifications.clear()
        return notifications

    def get_notification_count(self) -> int:
        """Get count of pending notifications."""
        return len(self._pending_notifications)


# Singleton instance
_verification_service: Optional[VerificationService] = None


def get_verification_service(
    graph_service: Optional['KnowledgeGraphService'] = None
) -> VerificationService:
    """
    Get or create singleton VerificationService.

    Args:
        graph_service: Optional KnowledgeGraphService to use

    Returns:
        VerificationService instance
    """
    global _verification_service

    if _verification_service is None or graph_service is not None:
        _verification_service = VerificationService(graph_service)

    return _verification_service


def reset_verification_service():
    """Reset singleton (for testing)."""
    global _verification_service
    _verification_service = None
