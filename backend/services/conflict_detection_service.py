"""
Conflict Detection Service - Phase 2 of Distillation Pipeline

Detects contradictions in research content before they pollute the Knowledge Graph.

Key Features:
1. Stage Check - Distinguish raw (Stage 1) from distilled (Stage 2) content
2. Hard Rules Priority - World Hard Rules violations are BREAKING severity
3. Category-specific fact checking - Focus on relevant facts per category
4. Graceful skipping - Voice category has no fact conflicts

Phase 2 of WORKSPACE_FILE_SYSTEM.md
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
import os
import re


class ConflictSeverity(Enum):
    """Severity levels for detected conflicts."""
    MINOR = "minor"           # Easily reconciled, stylistic
    SIGNIFICANT = "significant"  # Needs author decision
    BREAKING = "breaking"     # Fundamentally incompatible with Hard Rules


@dataclass
class Conflict:
    """Represents a detected conflict between content."""
    file: str
    description: str
    severity: ConflictSeverity
    rule_violated: Optional[str] = None  # If Hard Rule, which one?

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "description": self.description,
            "severity": self.severity.value,
            "rule_violated": self.rule_violated
        }


@dataclass
class ConflictResult:
    """Result of conflict detection."""
    stage_warning: bool = False
    stage_message: str = ""
    conflicts: List[Conflict] = field(default_factory=list)
    action_required: Optional[str] = None

    @property
    def has_breaking_conflicts(self) -> bool:
        return any(c.severity == ConflictSeverity.BREAKING for c in self.conflicts)

    @property
    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def to_dict(self) -> dict:
        return {
            "stage_warning": self.stage_warning,
            "stage_message": self.stage_message,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "action_required": self.action_required,
            "has_breaking_conflicts": self.has_breaking_conflicts,
            "has_conflicts": self.has_conflicts
        }


# Stage 2 markers by category
STAGE2_MARKERS = {
    "characters": ["fatal flaw", "the lie", "arc:", "true character", "character arc"],
    "world": ["hard rule", "cannot be broken", "world rule", "law:", "immutable"],
    "theme": ["central question", "theme:", "thesis", "counter-thesis", "argument for", "argument against"],
    "plot": ["beat", "catalyst", "midpoint", "all is lost", "act 1", "act 2", "break into"],
    "voice": []  # Voice is always treated as Stage 2 if saved
}

# Conflict focus areas by category
CONFLICT_FOCUS = {
    "characters": "ages, relationships, capabilities, physical descriptions, backstory facts",
    "world": "locations, rules, factions, timeline, technology limits, magic systems",
    "theme": "central argument, thesis vs counter-thesis consistency",
    "plot": "event sequence, causality, beat placement, timeline",
    "voice": None  # Voice doesn't get fact-checked
}


def is_structured_stage2_content(content: str, category: str) -> bool:
    """
    Check if content appears to be distilled Stage 2 data.

    Stage 2 content should have explicit structure markers based on category.
    Voice category is always treated as Stage 2.

    Args:
        content: The content to check
        category: The research category

    Returns:
        True if content appears to be Stage 2 (distilled), False if Stage 1 (raw)
    """
    category = category.lower()

    # Voice is always Stage 2 - no structure required
    if category == "voice":
        return True

    # Check for markers
    markers = STAGE2_MARKERS.get(category, [])
    if not markers:
        # Unknown category - assume Stage 2 to avoid false warnings
        return True

    content_lower = content.lower()
    return any(marker in content_lower for marker in markers)


def get_stage1_guidance(category: str) -> str:
    """
    Get distillation guidance for Stage 1 content.

    Args:
        category: The research category

    Returns:
        Guidance message with distillation prompt suggestion
    """
    prompts = {
        "characters": """Try this Distillation Prompt in your NotebookLM Character notebook:

"Based on these sources, create a character profile with:
- Fatal Flaw (an internal weakness, NOT a circumstance like 'is poor')
- The Lie (a mistaken belief driving the flaw)
- True Character (who they become after the arc)
- Arc: starting state → midpoint crisis → resolution
- Key relationships to other characters"

Save the result as a new note, then save it here.""",

        "world": """Try this Distillation Prompt in your NotebookLM World notebook:

"From these sources, extract:
- 5 Hard Rules (physics, magic limits, society laws) that CANNOT be broken
- Key Locations (name + significance to plot)
- What is known publicly vs. what is secret
- How different systems interact (e.g., magic + politics)"

Save the result as a new note, then save it here.""",

        "theme": """Try this Distillation Prompt in your NotebookLM Theme notebook:

"Looking at these sources, define:
- The Central Question (phrased as a question, e.g., 'Can redemption exist without sacrifice?')
- The argument FOR (the thesis)
- The argument AGAINST (the counter-thesis)
- Symbols that could represent this conflict
- How the protagonist embodies this question"

Save the result as a new note, then save it here.""",

        "plot": """Try this Distillation Prompt in your NotebookLM Plot notebook:

"Map the story to the 15-beat Save the Cat structure:
1. Opening Image, 2. Theme Stated, 3. Setup, 4. Catalyst, 5. Debate,
6. Break into Two, 7. B Story, 8. Fun & Games, 9. Midpoint, 10. Bad Guys Close In,
11. All Is Lost, 12. Dark Night of the Soul, 13. Break into Three, 14. Finale, 15. Final Image
- Is the Midpoint a FALSE VICTORY or FALSE DEFEAT?"

Save the result as a new note, then save it here.""",
    }
    return prompts.get(category, "Consider structuring this content with clear facts and markers.")


def load_hard_rules(content_path: str = "content") -> List[str]:
    """
    Load Hard Rules from World Bible.

    Looks for rules in:
    1. content/World Bible/Rules.md
    2. workspace/research/world/hard_rules.md

    Args:
        content_path: Base path to content directory

    Returns:
        List of hard rule strings
    """
    rules = []

    # Try World Bible Rules.md
    rules_paths = [
        Path(content_path) / "World Bible" / "Rules.md",
        Path(content_path) / "World Bible" / "Hard_Rules.md",
        Path("workspace") / "research" / "world" / "hard_rules.md",
    ]

    for rules_path in rules_paths:
        if rules_path.exists():
            content = rules_path.read_text(encoding="utf-8")
            # Extract rules from markdown
            extracted = extract_hard_rules_from_markdown(content)
            rules.extend(extracted)

    return list(set(rules))  # Deduplicate


def extract_hard_rules_from_markdown(content: str) -> List[str]:
    """
    Extract hard rules from markdown content.

    Looks for:
    - Sections titled "Hard Rules" or similar
    - Numbered or bulleted lists after such headers
    - Lines containing "cannot be broken" or similar markers

    Args:
        content: Markdown content

    Returns:
        List of extracted rules
    """
    rules = []

    # Find "Hard Rules" section
    hard_rules_pattern = r"(?:#+\s*Hard\s+Rules?|##\s*Rules?\s*\([Cc]annot\s+[Bb]e\s+[Bb]roken\))"
    sections = re.split(hard_rules_pattern, content, flags=re.IGNORECASE)

    if len(sections) > 1:
        # Extract from the section after the header
        rules_section = sections[1].split("\n#")[0]  # Stop at next header

        # Extract numbered or bulleted items
        items = re.findall(r"^[\s]*[-*\d.]+\s*(.+?)$", rules_section, re.MULTILINE)
        for item in items:
            item = item.strip()
            if item and len(item) > 10:  # Skip short fragments
                rules.append(item)

    # Also extract any line that explicitly mentions "cannot be broken"
    explicit_rules = re.findall(
        r"^.*(?:cannot be broken|immutable|absolute rule).*$",
        content,
        re.MULTILINE | re.IGNORECASE
    )
    for rule in explicit_rules:
        rule = rule.strip("- *#").strip()
        if rule and rule not in rules:
            rules.append(rule)

    return rules


class ConflictDetectionService:
    """
    Service for detecting conflicts in research content.

    Implements:
    1. Stage Check - Detect raw vs distilled content
    2. Hard Rules Check - Flag violations as BREAKING
    3. Category Fact Check - Compare with existing research
    """

    def __init__(self, content_path: str = "content", workspace_path: str = "."):
        self.content_path = content_path
        self.workspace_path = workspace_path

    async def detect_conflicts(
        self,
        new_content: str,
        category: str,
        skip_stage_check: bool = False
    ) -> ConflictResult:
        """
        Detect conflicts with existing research.

        Steps:
        1. Stage Check - skip if raw Stage 1 data
        2. Hard Rules Check - any World Hard Rule violations?
        3. Category Facts Check - contradicting established facts?

        Args:
            new_content: The new content to check
            category: The research category (characters, world, theme, plot, voice)
            skip_stage_check: If True, skip the Stage 1 detection

        Returns:
            ConflictResult with warnings and conflicts
        """
        category = category.lower()

        # Step 1: Stage Check
        if not skip_stage_check and not is_structured_stage2_content(new_content, category):
            guidance = get_stage1_guidance(category)
            return ConflictResult(
                stage_warning=True,
                stage_message=f"This appears to be raw Stage 1 research that hasn't been distilled yet. Conflict detection cannot compare 'vibes' to 'facts'.\n\n{guidance}",
                conflicts=[],
                action_required="distill_first"
            )

        conflicts = []

        # Step 2: Hard Rules Check (always, regardless of category)
        hard_rules = load_hard_rules(self.content_path)
        if hard_rules:
            rule_violations = await self._check_hard_rules(new_content, hard_rules)
            conflicts.extend(rule_violations)

        # Step 3: Category-Specific Fact Check
        if category != "voice":  # Voice has no fact conflicts
            category_conflicts = await self._check_category_conflicts(new_content, category)
            conflicts.extend(category_conflicts)

        # Determine action required
        action_required = None
        if any(c.severity == ConflictSeverity.BREAKING for c in conflicts):
            action_required = "resolve_breaking"
        elif conflicts:
            action_required = "review_conflicts"

        return ConflictResult(
            stage_warning=False,
            stage_message="",
            conflicts=conflicts,
            action_required=action_required
        )

    async def _check_hard_rules(self, content: str, hard_rules: List[str]) -> List[Conflict]:
        """
        Check content against Hard Rules.

        Uses LLM to detect violations.

        Args:
            content: Content to check
            hard_rules: List of hard rules

        Returns:
            List of BREAKING conflicts for any violations
        """
        if not hard_rules:
            return []

        conflicts = []

        try:
            from backend.services.llm_service import llm_service

            rules_text = "\n".join(f"- {rule}" for rule in hard_rules)

            prompt = f"""You are checking if new content violates established HARD RULES.

HARD RULES (These CANNOT be broken in this story world):
{rules_text}

NEW CONTENT:
{content}

For each Hard Rule, check if the new content violates it.
A violation means the new content describes something that contradicts a Hard Rule.

Respond in this exact format:
VIOLATIONS:
- [rule text]: [explanation of how it's violated] (or "none" if no violations)

Be strict - only flag actual contradictions, not thematic tensions."""

            messages = [
                {"role": "system", "content": "You analyze content for rule violations. Be precise."},
                {"role": "user", "content": prompt}
            ]

            # Try available LLM
            response = None
            for provider, model in [
                ("deepseek", "deepseek-chat"),
                ("ollama", "llama3.2:3b"),
            ]:
                try:
                    response = await llm_service.generate(
                        provider=provider,
                        model=model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=500
                    )
                    if response and response.content:
                        break
                except Exception:
                    continue

            if response and response.content:
                # Parse response for violations
                response_text = response.content.lower()
                if "none" not in response_text and "no violation" not in response_text:
                    # Check each rule
                    for rule in hard_rules:
                        rule_lower = rule.lower()
                        # Simple heuristic - if the rule is mentioned in context of violation
                        if any(word in response_text for word in rule_lower.split()[:3]):
                            # Extract explanation if possible
                            conflicts.append(Conflict(
                                file="content/World Bible/Rules.md",
                                description=f"May violate Hard Rule: {rule}",
                                severity=ConflictSeverity.BREAKING,
                                rule_violated=rule
                            ))

        except ImportError:
            # LLM service not available - do simple keyword matching
            content_lower = content.lower()
            for rule in hard_rules:
                # Very basic contradiction detection
                rule_words = set(rule.lower().split())
                content_words = set(content_lower.split())
                overlap = rule_words & content_words
                # If significant overlap but negation present, might be violation
                if len(overlap) >= 3:
                    negations = ["not", "no", "never", "cannot", "without", "lacks"]
                    if any(neg in content_lower for neg in negations):
                        conflicts.append(Conflict(
                            file="content/World Bible/Rules.md",
                            description=f"Possible Hard Rule conflict (manual review needed): {rule}",
                            severity=ConflictSeverity.SIGNIFICANT,  # Downgrade without LLM
                            rule_violated=rule
                        ))
        except Exception as e:
            print(f"Warning: Hard rules check failed: {e}")

        return conflicts

    async def _check_category_conflicts(self, content: str, category: str) -> List[Conflict]:
        """
        Check content against existing research in the same category.

        Uses LLM to compare facts.

        Args:
            content: New content
            category: Research category

        Returns:
            List of conflicts with existing files
        """
        conflicts = []
        focus = CONFLICT_FOCUS.get(category)
        if not focus:
            return conflicts

        # Load existing research files
        research_path = Path(self.workspace_path) / "workspace" / "research" / category
        if not research_path.exists():
            return conflicts

        existing_files = list(research_path.glob("*.md"))
        if not existing_files:
            return conflicts

        try:
            from backend.services.llm_service import llm_service

            for file_path in existing_files[:5]:  # Limit to avoid token explosion
                existing_content = file_path.read_text(encoding="utf-8")

                # Skip frontmatter
                if existing_content.startswith("---"):
                    parts = existing_content.split("---", 2)
                    if len(parts) >= 3:
                        existing_content = parts[2].strip()

                # Skip empty or very short files
                if len(existing_content) < 50:
                    continue

                prompt = f"""Compare these two research excerpts for factual contradictions.

CATEGORY: {category}
FOCUS ON: {focus}

EXCERPT A (NEW):
{content[:1500]}

EXCERPT B (EXISTING, from {file_path.name}):
{existing_content[:1500]}

Ignore: writing style differences, level of detail, opinion vs fact, Stage 1 "vibes".
Report only FACTUAL contradictions.

Respond with:
CONTRADICTION: yes/no
SEVERITY: minor/significant (only if contradiction is yes)
EXPLANATION: (brief description, or "No contradictions found")"""

                messages = [
                    {"role": "system", "content": "You detect factual contradictions in research notes."},
                    {"role": "user", "content": prompt}
                ]

                response = None
                for provider, model in [
                    ("deepseek", "deepseek-chat"),
                    ("ollama", "llama3.2:3b"),
                ]:
                    try:
                        response = await llm_service.generate(
                            provider=provider,
                            model=model,
                            messages=messages,
                            temperature=0.3,
                            max_tokens=300
                        )
                        if response and response.content:
                            break
                    except Exception:
                        continue

                if response and response.content:
                    response_text = response.content.lower()
                    if "contradiction: yes" in response_text or "contradiction:yes" in response_text:
                        # Determine severity
                        severity = ConflictSeverity.MINOR
                        if "significant" in response_text:
                            severity = ConflictSeverity.SIGNIFICANT

                        # Extract explanation
                        explanation = "Factual contradiction detected"
                        if "explanation:" in response_text:
                            explanation = response.content.split("explanation:")[-1].strip()[:200]

                        conflicts.append(Conflict(
                            file=str(file_path.relative_to(self.workspace_path)),
                            description=explanation,
                            severity=severity
                        ))

        except ImportError:
            pass  # LLM not available - skip category conflicts
        except Exception as e:
            print(f"Warning: Category conflict check failed: {e}")

        return conflicts

    def get_conflict_summary(self, result: ConflictResult) -> str:
        """
        Generate a human-readable summary of conflicts.

        Args:
            result: The conflict detection result

        Returns:
            Formatted summary string
        """
        if result.stage_warning:
            return f"⚠️ Stage 1 Warning\n\n{result.stage_message}"

        if not result.conflicts:
            return "✅ No conflicts detected. Safe to save."

        lines = [f"Found {len(result.conflicts)} conflict(s):\n"]

        # Group by severity
        breaking = [c for c in result.conflicts if c.severity == ConflictSeverity.BREAKING]
        significant = [c for c in result.conflicts if c.severity == ConflictSeverity.SIGNIFICANT]
        minor = [c for c in result.conflicts if c.severity == ConflictSeverity.MINOR]

        if breaking:
            lines.append("🔴 BREAKING (must resolve):")
            for c in breaking:
                lines.append(f"  • {c.description}")
                if c.rule_violated:
                    lines.append(f"    Rule: {c.rule_violated}")

        if significant:
            lines.append("\n🟡 SIGNIFICANT (recommend resolving):")
            for c in significant:
                lines.append(f"  • {c.description} ({c.file})")

        if minor:
            lines.append("\n⚪ MINOR (can ignore):")
            for c in minor:
                lines.append(f"  • {c.description}")

        return "\n".join(lines)


# Singleton instance
_conflict_detection_service: Optional[ConflictDetectionService] = None


def get_conflict_detection_service(
    content_path: str = "content",
    workspace_path: str = "."
) -> ConflictDetectionService:
    """
    Get the conflict detection service singleton.

    Args:
        content_path: Path to content directory
        workspace_path: Path to workspace root

    Returns:
        ConflictDetectionService instance
    """
    global _conflict_detection_service
    if _conflict_detection_service is None:
        _conflict_detection_service = ConflictDetectionService(content_path, workspace_path)
    return _conflict_detection_service
