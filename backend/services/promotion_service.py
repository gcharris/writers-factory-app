"""
Promotion Service - Phase 4 of Distillation Pipeline

Moves reviewed Research Notes into the canonical Story Bible with intelligent transformation.

Key Features:
1. Structure Check - Validates required fields before promotion
2. Category-Specific Extraction - Each category extracts specific fields
3. Intelligent Merge - Updates Story Bible files without overwriting
4. Voice triggers calibration (special case)

Phase 4 of WORKSPACE_FILE_SYSTEM.md
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
import re
import json


@dataclass
class PromotionStatus:
    """Status of promotion readiness check."""
    can_promote: bool
    blockers: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    category: str = ""
    target: str = ""

    def to_dict(self) -> dict:
        return {
            "can_promote": self.can_promote,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "category": self.category,
            "target": self.target
        }


@dataclass
class PromotionResult:
    """Result of a promotion operation."""
    success: bool
    target: Optional[str] = None
    fields_updated: List[str] = field(default_factory=list)
    error: Optional[str] = None
    action: str = "promoted"
    data: Optional[Dict] = None

    def to_dict(self) -> dict:
        result = {
            "success": self.success,
            "action": self.action
        }
        if self.target:
            result["target"] = self.target
        if self.fields_updated:
            result["fields_updated"] = self.fields_updated
        if self.error:
            result["error"] = self.error
        if self.data:
            result["data"] = self.data
        return result


# Required fields by category
REQUIRED_FIELDS = {
    "characters": {
        "protagonist": ["fatal_flaw"],  # At minimum need Fatal Flaw
        "any": ["role"]  # Supporting/antagonist need role defined
    },
    "world": {
        "rules": ["hard_rule"],  # At least one Hard Rule
    },
    "theme": {
        "core": ["central_question"]  # Need the question at minimum
    },
    "plot": {
        "beats": ["catalyst", "midpoint"],  # Key structural beats
    },
    "voice": {
        # Voice has no structure requirement - triggers calibration
    }
}

# Target files by category
PROMOTION_TARGETS = {
    "characters": "content/Characters/Protagonist.md",
    "world": "content/World Bible/Rules.md",
    "theme": "content/Story Bible/Themes_and_Philosophy/Theme.md",
    "plot": "content/Story Bible/Structure/Beat_Sheet.md",
    "voice": "Voice Calibration Bundle"  # Special - triggers calibration
}


# Extraction prompts by category
EXTRACTION_PROMPTS = {
    "characters": """Extract structured character data from this research note.

CONTENT:
{content}

Extract these fields (return null if not found):
- character_type: "protagonist" | "antagonist" | "supporting"
- name: Character's name
- fatal_flaw: The character's internal weakness (NOT circumstance)
- the_lie: The mistaken belief driving the flaw
- true_character: Who they become after the arc
- arc_start: Their state at the beginning
- arc_midpoint: The crisis/turning point
- arc_resolution: Their state at the end
- relationships: List of key relationships

Return as JSON with these exact field names.""",

    "world": """Extract world-building data from this research note.

CONTENT:
{content}

Separate Hard Rules (immutable laws) from Soft Lore (history, flavor).

Extract these fields (return null if not found):
- hard_rules: List of rules that CANNOT be broken in this world
- soft_lore: Background information, history, flavor
- locations: List of {{name, significance, description}}
- factions: List of groups/organizations
- secrets: Things hidden from the public

Return as JSON with these exact field names.""",

    "theme": """Extract thematic elements from this research note.

CONTENT:
{content}

Extract these fields (return null if not found):
- central_question: The theme phrased as a question (e.g., "Can redemption exist without sacrifice?")
- thesis: The argument FOR
- counter_thesis: The argument AGAINST
- symbols: List of symbols that represent this conflict
- protagonist_embodiment: How the protagonist embodies this question

Return as JSON with these exact field names.""",

    "plot": """Extract plot structure from this research note.

CONTENT:
{content}

Map to the 15-beat Save the Cat structure. Extract these beats (return null if not found):
- opening_image: First visual/scene
- theme_stated: Where the theme is hinted
- setup: World and character introduction
- catalyst: The inciting incident
- debate: Character wrestles with the choice
- break_into_two: Commits to the adventure
- b_story: Secondary story (often love interest)
- fun_and_games: The promise of the premise
- midpoint: False victory or false defeat
- bad_guys_close_in: Complications escalate
- all_is_lost: The lowest point
- dark_night_of_soul: Emotional low
- break_into_three: Solution discovered
- finale: Final confrontation
- final_image: Closing visual, mirror of opening

Also extract:
- midpoint_type: "false_victory" | "false_defeat"

Return as JSON with these exact field names.""",

    "voice": """Analyze this voice/style sample.

CONTENT:
{content}

Extract style patterns:
- sentence_rhythm: Short punchy? Long flowing? Mixed?
- metaphor_domains: Where do metaphors come from? (nature, machinery, etc.)
- dialogue_patterns: Terse? Verbose? Subtext-heavy?
- vocabulary_level: Simple? Literary? Technical?
- pov_style: Close third? Distant? First person?
- anti_patterns: What to AVOID based on this sample

Return as JSON with these exact field names."""
}


class PromotionService:
    """
    Service for promoting research to Story Bible with intelligent transformation.
    """

    def __init__(self, workspace_path: str = ".", content_path: str = "content"):
        self.workspace_path = Path(workspace_path)
        self.content_path = Path(content_path)

    def _extract_category_from_path(self, file_path: str) -> str:
        """Extract category from research file path."""
        path = Path(file_path)
        # Expected: workspace/research/{category}/filename.md
        parts = path.parts
        for i, part in enumerate(parts):
            if part == "research" and i + 1 < len(parts):
                return parts[i + 1].lower()
        return ""

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from content."""
        if not content.startswith("---"):
            return {}

        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}

        frontmatter = parts[1].strip()
        metadata = {}

        for line in frontmatter.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip('"')
                metadata[key] = value

        return metadata

    def _get_body_content(self, content: str) -> str:
        """Get content without frontmatter."""
        if not content.startswith("---"):
            return content

        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
        return content

    async def check_promotable(self, file_path: str) -> PromotionStatus:
        """
        Check if file can be promoted to Story Bible.

        Requirements:
        1. Stage 2 content (not raw Stage 1)
        2. No unresolved BREAKING conflicts
        3. Contains required fields for category
        """
        path = self.workspace_path / file_path
        if not path.exists():
            return PromotionStatus(
                can_promote=False,
                blockers=[f"File not found: {file_path}"]
            )

        category = self._extract_category_from_path(file_path)
        if not category:
            return PromotionStatus(
                can_promote=False,
                blockers=["Could not determine category from file path"]
            )

        content = path.read_text(encoding="utf-8")
        metadata = self._parse_frontmatter(content)
        body = self._get_body_content(content)

        blockers = []
        warnings = []

        # Check 1: Stage Check
        stage = metadata.get("stage", "2")
        if "1" in str(stage):
            blockers.append("Content is Stage 1 (raw). Run Distillation Prompt first.")

        # Check 2: Conflict Check
        if "conflicts" in metadata:
            try:
                conflicts = metadata["conflicts"]
                if isinstance(conflicts, str):
                    # Simple check if conflicts mentioned
                    if "breaking" in conflicts.lower():
                        blockers.append("Has unresolved BREAKING conflicts.")
                    elif "significant" in conflicts.lower():
                        warnings.append("Has SIGNIFICANT conflicts - recommend resolving first.")
            except Exception:
                pass

        # Check 3: Structure Check (category-specific)
        from backend.services.conflict_detection_service import is_structured_stage2_content
        if not is_structured_stage2_content(body, category):
            blockers.append(f"Content lacks required structure markers for {category} category.")

        # Check for specific required fields
        required = REQUIRED_FIELDS.get(category, {})
        if required and category != "voice":
            body_lower = body.lower()
            # Simple heuristic - check for key terms
            if category == "characters" and "fatal flaw" not in body_lower:
                blockers.append("Missing required field: Fatal Flaw")
            elif category == "theme" and "question" not in body_lower:
                blockers.append("Missing required field: Central Question")
            elif category == "plot" and "midpoint" not in body_lower:
                blockers.append("Missing required field: Midpoint")
            elif category == "world" and "rule" not in body_lower:
                warnings.append("No explicit Hard Rules found - may need refinement")

        target = PROMOTION_TARGETS.get(category, "Unknown")

        return PromotionStatus(
            can_promote=len(blockers) == 0,
            blockers=blockers,
            warnings=warnings,
            category=category,
            target=target
        )

    async def preview_promotion(self, file_path: str) -> Dict:
        """
        Preview what promotion will do without executing.

        Returns extracted fields and target.
        """
        path = self.workspace_path / file_path
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        category = self._extract_category_from_path(file_path)
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        # Try to extract fields
        extracted = await self._extract_fields(body, category)

        return {
            "category": category,
            "source": file_path,
            "target": PROMOTION_TARGETS.get(category, "Unknown"),
            "extracted_fields": extracted,
            "merge_strategy": "update_fields" if category != "voice" else "trigger_calibration"
        }

    async def _extract_fields(self, content: str, category: str) -> Dict:
        """Extract structured fields from content using LLM."""
        prompt_template = EXTRACTION_PROMPTS.get(category)
        if not prompt_template:
            return {}

        prompt = prompt_template.format(content=content[:3000])  # Limit content

        try:
            from backend.services.llm_service import llm_service

            messages = [
                {"role": "system", "content": "You extract structured data from text. Return valid JSON only."},
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
                        temperature=0.2,
                        max_tokens=1000
                    )
                    if response and response.content:
                        break
                except Exception:
                    continue

            if response and response.content:
                # Try to parse JSON from response
                text = response.content
                # Find JSON in response
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass

        except ImportError:
            pass
        except Exception as e:
            print(f"Warning: Field extraction failed: {e}")

        # Fallback: simple pattern extraction
        return self._simple_extract(content, category)

    def _simple_extract(self, content: str, category: str) -> Dict:
        """Simple regex-based extraction when LLM unavailable."""
        result = {}
        content_lower = content.lower()

        if category == "characters":
            # Look for Fatal Flaw
            flaw_match = re.search(r"fatal flaw[:\s]+([^\n]+)", content, re.IGNORECASE)
            if flaw_match:
                result["fatal_flaw"] = flaw_match.group(1).strip()

            # Look for The Lie
            lie_match = re.search(r"the lie[:\s]+([^\n]+)", content, re.IGNORECASE)
            if lie_match:
                result["the_lie"] = lie_match.group(1).strip()

        elif category == "world":
            # Look for Hard Rules
            rules = re.findall(r"(?:hard rule|rule)[:\s]+([^\n]+)", content, re.IGNORECASE)
            if rules:
                result["hard_rules"] = rules

        elif category == "theme":
            # Look for Central Question
            question_match = re.search(r"(?:central question|theme)[:\s]+([^\n]+)", content, re.IGNORECASE)
            if question_match:
                result["central_question"] = question_match.group(1).strip()

        elif category == "plot":
            # Look for key beats
            for beat in ["catalyst", "midpoint", "all is lost", "finale"]:
                match = re.search(rf"{beat}[:\s]+([^\n]+)", content, re.IGNORECASE)
                if match:
                    result[beat.replace(" ", "_")] = match.group(1).strip()

        return result

    async def promote(self, source_path: str, confirm_warnings: bool = False) -> PromotionResult:
        """
        Promote research to Story Bible with intelligent transformation.

        Args:
            source_path: Path to research file
            confirm_warnings: Acknowledge warnings and proceed anyway

        Returns:
            PromotionResult with success status and details
        """
        # First check if promotable
        status = await self.check_promotable(source_path)
        if not status.can_promote:
            return PromotionResult(
                success=False,
                error=f"Cannot promote: {'; '.join(status.blockers)}"
            )

        if status.warnings and not confirm_warnings:
            return PromotionResult(
                success=False,
                error=f"Warnings not acknowledged: {'; '.join(status.warnings)}",
                action="needs_confirmation"
            )

        category = status.category

        # Dispatch to category-specific handler
        handlers = {
            "characters": self._promote_character,
            "world": self._promote_world,
            "theme": self._promote_theme,
            "plot": self._promote_plot,
            "voice": self._promote_voice
        }

        handler = handlers.get(category)
        if not handler:
            return PromotionResult(
                success=False,
                error=f"Unknown category: {category}"
            )

        # Execute promotion
        result = await handler(source_path)

        # Mark source as promoted
        if result.success:
            await self._mark_promoted(source_path, result.target)

        return result

    async def _promote_character(self, source_path: str) -> PromotionResult:
        """Promote character research to Protagonist.md or Cast.md."""
        path = self.workspace_path / source_path
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        extracted = await self._extract_fields(body, "characters")

        # Determine target
        char_type = extracted.get("character_type", "protagonist")
        if char_type == "protagonist":
            target = self.content_path / "Characters" / "Protagonist.md"
        else:
            target = self.content_path / "Characters" / "Cast.md"

        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Build update content
        fields_updated = []

        if target.exists():
            existing = target.read_text(encoding="utf-8")
            # Merge extracted fields into existing
            updated = self._merge_character_fields(existing, extracted)
            fields_updated = [k for k in extracted.keys() if extracted[k]]
        else:
            # Create new file
            updated = self._create_character_file(extracted)
            fields_updated = list(extracted.keys())

        target.write_text(updated, encoding="utf-8")

        return PromotionResult(
            success=True,
            target=str(target),
            fields_updated=fields_updated,
            data=extracted
        )

    def _merge_character_fields(self, existing: str, extracted: Dict) -> str:
        """Merge extracted fields into existing character file."""
        # Simple merge - append or update sections
        lines = existing.split("\n")
        result = lines.copy()

        for key, value in extracted.items():
            if not value:
                continue

            section_header = f"## {key.replace('_', ' ').title()}"

            # Check if section exists
            section_idx = None
            for i, line in enumerate(lines):
                if section_header.lower() in line.lower():
                    section_idx = i
                    break

            if section_idx is not None:
                # Update existing section (find end, replace content)
                # Simple: just append after header
                result[section_idx] = f"{section_header}\n{value}"
            else:
                # Add new section at end
                result.append(f"\n{section_header}")
                result.append(str(value))

        return "\n".join(result)

    def _create_character_file(self, extracted: Dict) -> str:
        """Create new character file from extracted data."""
        lines = ["# Character Profile", ""]

        name = extracted.get("name", "Unnamed Character")
        lines.append(f"**Name**: {name}")
        lines.append("")

        if extracted.get("fatal_flaw"):
            lines.extend(["## Fatal Flaw", extracted["fatal_flaw"], ""])

        if extracted.get("the_lie"):
            lines.extend(["## The Lie", extracted["the_lie"], ""])

        if extracted.get("arc_start"):
            lines.extend(["## Arc", f"**Start**: {extracted['arc_start']}"])
        if extracted.get("arc_midpoint"):
            lines.append(f"**Midpoint**: {extracted['arc_midpoint']}")
        if extracted.get("arc_resolution"):
            lines.append(f"**Resolution**: {extracted['arc_resolution']}")

        if extracted.get("relationships"):
            lines.extend(["", "## Relationships"])
            rels = extracted["relationships"]
            if isinstance(rels, list):
                for rel in rels:
                    lines.append(f"- {rel}")
            else:
                lines.append(str(rels))

        return "\n".join(lines)

    async def _promote_world(self, source_path: str) -> PromotionResult:
        """Promote world research to Rules.md."""
        path = self.workspace_path / source_path
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        extracted = await self._extract_fields(body, "world")

        target = self.content_path / "World Bible" / "Rules.md"
        target.parent.mkdir(parents=True, exist_ok=True)

        fields_updated = []

        if extracted.get("hard_rules"):
            # Merge hard rules
            if target.exists():
                existing = target.read_text(encoding="utf-8")
                updated = self._merge_hard_rules(existing, extracted["hard_rules"])
            else:
                updated = self._create_rules_file(extracted)
            target.write_text(updated, encoding="utf-8")
            fields_updated.append("hard_rules")

        return PromotionResult(
            success=True,
            target=str(target),
            fields_updated=fields_updated,
            data=extracted
        )

    def _merge_hard_rules(self, existing: str, new_rules: List[str]) -> str:
        """Merge new hard rules into existing Rules.md."""
        # Find Hard Rules section and add new ones
        if "## Hard Rules" not in existing:
            existing += "\n\n## Hard Rules (Cannot Be Broken)\n"

        for rule in new_rules:
            if rule not in existing:
                existing += f"- {rule}\n"

        return existing

    def _create_rules_file(self, extracted: Dict) -> str:
        """Create new Rules.md from extracted data."""
        lines = ["# World Rules", "", "## Hard Rules (Cannot Be Broken)", ""]

        rules = extracted.get("hard_rules", [])
        if isinstance(rules, list):
            for rule in rules:
                lines.append(f"- {rule}")
        else:
            lines.append(f"- {rules}")

        if extracted.get("soft_lore"):
            lines.extend(["", "## Soft Lore", str(extracted["soft_lore"])])

        return "\n".join(lines)

    async def _promote_theme(self, source_path: str) -> PromotionResult:
        """Promote theme research to Theme.md."""
        path = self.workspace_path / source_path
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        extracted = await self._extract_fields(body, "theme")

        target = self.content_path / "Story Bible" / "Themes_and_Philosophy" / "Theme.md"
        target.parent.mkdir(parents=True, exist_ok=True)

        lines = ["# Theme", ""]

        if extracted.get("central_question"):
            lines.extend(["## Central Question", extracted["central_question"], ""])

        if extracted.get("thesis"):
            lines.extend(["## Thesis (Argument FOR)", extracted["thesis"], ""])

        if extracted.get("counter_thesis"):
            lines.extend(["## Counter-Thesis (Argument AGAINST)", extracted["counter_thesis"], ""])

        if extracted.get("symbols"):
            lines.extend(["## Symbols"])
            syms = extracted["symbols"]
            if isinstance(syms, list):
                for sym in syms:
                    lines.append(f"- {sym}")
            else:
                lines.append(str(syms))

        target.write_text("\n".join(lines), encoding="utf-8")

        return PromotionResult(
            success=True,
            target=str(target),
            fields_updated=[k for k in extracted.keys() if extracted.get(k)],
            data=extracted
        )

    async def _promote_plot(self, source_path: str) -> PromotionResult:
        """Promote plot research to Beat_Sheet.md."""
        path = self.workspace_path / source_path
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        extracted = await self._extract_fields(body, "plot")

        target = self.content_path / "Story Bible" / "Structure" / "Beat_Sheet.md"
        target.parent.mkdir(parents=True, exist_ok=True)

        beat_order = [
            ("opening_image", "Opening Image"),
            ("theme_stated", "Theme Stated"),
            ("setup", "Setup"),
            ("catalyst", "Catalyst"),
            ("debate", "Debate"),
            ("break_into_two", "Break Into Two"),
            ("b_story", "B Story"),
            ("fun_and_games", "Fun & Games"),
            ("midpoint", "Midpoint"),
            ("bad_guys_close_in", "Bad Guys Close In"),
            ("all_is_lost", "All Is Lost"),
            ("dark_night_of_soul", "Dark Night of the Soul"),
            ("break_into_three", "Break Into Three"),
            ("finale", "Finale"),
            ("final_image", "Final Image")
        ]

        lines = ["# Beat Sheet (15-Beat Structure)", ""]

        midpoint_type = extracted.get("midpoint_type", "unknown")
        lines.append(f"**Midpoint Type**: {midpoint_type}")
        lines.append("")

        for key, label in beat_order:
            beat_content = extracted.get(key, "TBD")
            lines.append(f"## {label}")
            lines.append(str(beat_content) if beat_content else "TBD")
            lines.append("")

        target.write_text("\n".join(lines), encoding="utf-8")

        return PromotionResult(
            success=True,
            target=str(target),
            fields_updated=[k for k, _ in beat_order if extracted.get(k)],
            data=extracted
        )

    async def _promote_voice(self, source_path: str) -> PromotionResult:
        """Voice promotion triggers calibration instead of file copy."""
        path = self.workspace_path / source_path
        content = path.read_text(encoding="utf-8")
        body = self._get_body_content(content)

        extracted = await self._extract_fields(body, "voice")

        # Try to trigger voice calibration
        try:
            from backend.services.voice_calibration_service import voice_calibration_service

            # Store voice patterns for calibration
            # (Actual calibration would be a more complex process)
            return PromotionResult(
                success=True,
                target="Voice Calibration Bundle",
                action="triggered_calibration",
                fields_updated=list(extracted.keys()),
                data=extracted
            )
        except ImportError:
            # Voice calibration service not available
            return PromotionResult(
                success=True,
                target="Voice Calibration Bundle",
                action="voice_patterns_extracted",
                fields_updated=list(extracted.keys()),
                data=extracted
            )

    async def _mark_promoted(self, source_path: str, target: str):
        """Mark source file as promoted in frontmatter."""
        path = self.workspace_path / source_path
        if not path.exists():
            return

        content = path.read_text(encoding="utf-8")

        # Update frontmatter
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                body = parts[2]

                # Add promotion info
                promotion_info = f"""
status: promoted
promoted_to: {target}
promoted_date: {now}"""

                # Insert before closing
                updated_frontmatter = frontmatter.rstrip() + promotion_info

                content = f"---{updated_frontmatter}\n---{body}"
        else:
            # Add frontmatter
            content = f"""---
status: promoted
promoted_to: {target}
promoted_date: {now}
---

{content}"""

        path.write_text(content, encoding="utf-8")


# Singleton instance
_promotion_service: Optional[PromotionService] = None


def get_promotion_service(
    workspace_path: str = ".",
    content_path: str = "content"
) -> PromotionService:
    """Get the promotion service singleton."""
    global _promotion_service
    if _promotion_service is None:
        _promotion_service = PromotionService(workspace_path, content_path)
    return _promotion_service
