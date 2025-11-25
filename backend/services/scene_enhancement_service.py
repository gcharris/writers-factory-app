"""
Scene Enhancement Service - Phase 3B Director Mode

Polish pipeline with two modes based on score threshold:
- Action Prompt (85+): Surgical fixes for specific violations
- 6-Pass Enhancement (70-84): Full enhancement ritual
- Rewrite (<70): Return to Scene Writer (not handled here)

Based on the proven explants-scene-enhancement skill workflow.
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
from backend.services.scene_analyzer_service import (
    SceneAnalyzerService,
    get_scene_analyzer_service,
    SceneAnalysisResult,
    PatternViolation,
    VoiceBundleContext,
    StoryBibleContext,
)
from backend.services.settings_service import settings_service

logger = logging.getLogger(__name__)


# =============================================================================
# Constants (Fallback defaults - overridden by Settings Service)
# =============================================================================

class EnhancementMode(str, Enum):
    """Enhancement mode based on score."""
    ACTION_PROMPT = "action_prompt"  # Score 85+: Surgical fixes
    SIX_PASS = "six_pass"            # Score 70-84: Full enhancement
    REWRITE = "rewrite"              # Score <70: Return to Scene Writer


# DEFAULT THRESHOLD VALUES - Used ONLY if Settings Service fails to load
# The actual values come from settings_service.get() which uses 3-tier resolution
ACTION_PROMPT_THRESHOLD = 85
SIX_PASS_THRESHOLD = 70


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Fix:
    """A single surgical fix to apply."""
    fix_number: int
    description: str
    old_text: str
    new_text: str
    line_number: Optional[int] = None
    category: str = "anti_pattern"  # anti_pattern, metaphor, voice, etc.

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ActionPrompt:
    """Generated action prompt for surgical fixes."""
    scene_id: str
    original_score: int
    fixes: List[Fix]
    preservation_notes: List[str]
    expected_score_improvement: int

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "original_score": self.original_score,
            "fixes": [f.to_dict() for f in self.fixes],
            "preservation_notes": self.preservation_notes,
            "expected_score_improvement": self.expected_score_improvement,
        }

    def to_markdown(self) -> str:
        """Generate markdown action prompt document."""
        fixes_md = "\n\n".join([
            f"""### FIX {f.fix_number}: {f.description}
**Category:** {f.category}
**Line:** {f.line_number or 'N/A'}

**OLD:**
```
{f.old_text}
```

**NEW:**
```
{f.new_text}
```"""
            for f in self.fixes
        ])

        preservation_md = "\n".join([f"- {note}" for note in self.preservation_notes])

        return f"""## ENHANCEMENT ACTION PROMPT

### TARGET SCENE
Scene ID: {self.scene_id}
Original Score: {self.original_score}/100

---

## FIXES TO APPLY

{fixes_md}

---

## CRITICAL: DO NOT MODIFY
{preservation_md}

---

## VERIFICATION CHECKLIST
- [ ] All {len(self.fixes)} fixes applied successfully
- [ ] Preservation elements unchanged
- [ ] No new anti-patterns introduced
- [ ] Scene function maintained

**Expected Score Improvement:** {self.original_score} → {self.original_score + self.expected_score_improvement} (+{self.expected_score_improvement} points)
"""


@dataclass
class PassResult:
    """Result of a single enhancement pass."""
    pass_number: int
    pass_name: str
    changes_made: int
    changes: List[str]  # Brief description of each change
    notes: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class EnhancementResult:
    """Result of scene enhancement."""
    scene_id: str
    mode: EnhancementMode
    original_content: str
    enhanced_content: str
    original_score: int
    final_score: Optional[int] = None

    # Mode-specific details
    action_prompt: Optional[ActionPrompt] = None
    fixes_applied: List[Dict] = field(default_factory=list)
    passes_completed: List[PassResult] = field(default_factory=list)

    # Metadata
    enhanced_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict:
        return {
            "scene_id": self.scene_id,
            "mode": self.mode.value,
            "original_content": self.original_content,
            "enhanced_content": self.enhanced_content,
            "original_score": self.original_score,
            "final_score": self.final_score,
            "action_prompt": self.action_prompt.to_dict() if self.action_prompt else None,
            "fixes_applied": self.fixes_applied,
            "passes_completed": [p.to_dict() for p in self.passes_completed],
            "enhanced_at": self.enhanced_at,
        }


# =============================================================================
# Scene Enhancement Service
# =============================================================================

class SceneEnhancementService:
    """
    Polish pipeline with two enhancement modes.

    Mode A: Action Prompt (Score 85+)
    - Generate surgical fixes based on violations
    - Apply OLD → NEW replacements
    - Preserve everything else

    Mode B: 6-Pass Enhancement (Score 70-84)
    - Pass 1: Sensory Anchoring
    - Pass 2: Verb Promotion + Simile Elimination
    - Pass 3: Metaphor Rotation
    - Pass 4: Voice Embed (Not Hover)
    - Pass 5: Italics Gate
    - Pass 6: Voice Authentication
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        analyzer_service: Optional[SceneAnalyzerService] = None,
        project_id: Optional[str] = None,
    ):
        """
        Initialize Scene Enhancement Service with dynamic settings.

        Args:
            llm_service: LLM service for enhancement
            analyzer_service: Scene analyzer for re-scoring
            project_id: Optional project ID for project-specific settings
        """
        self.llm_service = llm_service or LLMService()
        self.analyzer_service = analyzer_service or get_scene_analyzer_service()
        self.project_id = project_id

        # Load dynamic thresholds from Settings Service
        self._load_settings()

    def _load_settings(self):
        """Load dynamic enhancement thresholds from Settings Service."""
        try:
            self.action_prompt_threshold = settings_service.get(
                "enhancement.action_prompt_threshold", self.project_id
            ) or ACTION_PROMPT_THRESHOLD

            self.six_pass_threshold = settings_service.get(
                "enhancement.six_pass_threshold", self.project_id
            ) or SIX_PASS_THRESHOLD

            self.rewrite_threshold = settings_service.get(
                "enhancement.rewrite_threshold", self.project_id
            ) or 60

            self.aggressiveness = settings_service.get(
                "enhancement.aggressiveness", self.project_id
            ) or "medium"

            logger.info(
                f"Scene Enhancement settings loaded: "
                f"action_prompt={self.action_prompt_threshold}, "
                f"six_pass={self.six_pass_threshold}, "
                f"rewrite={self.rewrite_threshold}, "
                f"aggressiveness={self.aggressiveness}"
            )

        except Exception as e:
            logger.error(f"Failed to load enhancement settings, using defaults: {e}")
            self.action_prompt_threshold = ACTION_PROMPT_THRESHOLD
            self.six_pass_threshold = SIX_PASS_THRESHOLD
            self.rewrite_threshold = 60
            self.aggressiveness = "medium"

    # -------------------------------------------------------------------------
    # Main Enhancement Entry Point
    # -------------------------------------------------------------------------

    async def enhance_scene(
        self,
        scene_id: str,
        scene_content: str,
        analysis: SceneAnalysisResult,
        voice_bundle: Optional[VoiceBundleContext] = None,
        story_bible: Optional[StoryBibleContext] = None,
        force_mode: Optional[EnhancementMode] = None,
    ) -> EnhancementResult:
        """
        Enhance a scene based on its score.

        Args:
            scene_id: Scene identifier
            scene_content: The scene text to enhance
            analysis: Previous analysis result with violations
            voice_bundle: Voice Bundle for context
            story_bible: Story Bible context
            force_mode: Override automatic mode selection

        Returns:
            EnhancementResult with enhanced content
        """
        # Determine mode
        mode = force_mode or self._determine_mode(analysis.total_score)

        logger.info(f"Enhancing {scene_id} with mode {mode.value} (score: {analysis.total_score})")

        if mode == EnhancementMode.REWRITE:
            # Don't enhance, signal rewrite needed
            return EnhancementResult(
                scene_id=scene_id,
                mode=mode,
                original_content=scene_content,
                enhanced_content=scene_content,  # No change
                original_score=analysis.total_score,
            )

        if mode == EnhancementMode.ACTION_PROMPT:
            return await self._apply_action_prompt_mode(
                scene_id=scene_id,
                scene_content=scene_content,
                analysis=analysis,
                voice_bundle=voice_bundle,
            )

        # Six-pass mode
        return await self._apply_six_pass_mode(
            scene_id=scene_id,
            scene_content=scene_content,
            analysis=analysis,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
        )

    def _determine_mode(self, score: int) -> EnhancementMode:
        """
        Determine enhancement mode from score using dynamic thresholds.

        Thresholds are loaded from Settings Service and can be configured
        per-project via voice_settings.yaml.
        """
        if score >= self.action_prompt_threshold:
            return EnhancementMode.ACTION_PROMPT
        elif score >= self.six_pass_threshold:
            return EnhancementMode.SIX_PASS
        else:
            return EnhancementMode.REWRITE

    # -------------------------------------------------------------------------
    # Mode A: Action Prompt (Surgical Fixes)
    # -------------------------------------------------------------------------

    async def _apply_action_prompt_mode(
        self,
        scene_id: str,
        scene_content: str,
        analysis: SceneAnalysisResult,
        voice_bundle: Optional[VoiceBundleContext],
    ) -> EnhancementResult:
        """
        Apply surgical fixes for high-scoring scenes (85+).

        Generates specific OLD → NEW fixes and applies them.
        """
        logger.info(f"Applying action prompt mode for {scene_id}")

        # Generate fixes from violations
        action_prompt = await self._generate_action_prompt(
            scene_id=scene_id,
            scene_content=scene_content,
            analysis=analysis,
            voice_bundle=voice_bundle,
        )

        # Apply fixes
        enhanced_content = scene_content
        fixes_applied = []

        for fix in action_prompt.fixes:
            if fix.old_text in enhanced_content:
                enhanced_content = enhanced_content.replace(fix.old_text, fix.new_text, 1)
                fixes_applied.append({
                    "fix_number": fix.fix_number,
                    "description": fix.description,
                    "status": "applied",
                })
            else:
                fixes_applied.append({
                    "fix_number": fix.fix_number,
                    "description": fix.description,
                    "status": "not_found",
                })

        # Re-score after enhancement
        final_analysis = await self.analyzer_service.analyze_scene(
            scene_id=f"{scene_id}-enhanced",
            scene_content=enhanced_content,
            voice_bundle=voice_bundle,
            phase=analysis.categories.get("phase_appropriateness", {}).get("phase", "act2") if hasattr(analysis, 'categories') else "act2",
        )

        return EnhancementResult(
            scene_id=scene_id,
            mode=EnhancementMode.ACTION_PROMPT,
            original_content=scene_content,
            enhanced_content=enhanced_content,
            original_score=analysis.total_score,
            final_score=final_analysis.total_score,
            action_prompt=action_prompt,
            fixes_applied=fixes_applied,
        )

    async def _generate_action_prompt(
        self,
        scene_id: str,
        scene_content: str,
        analysis: SceneAnalysisResult,
        voice_bundle: Optional[VoiceBundleContext],
    ) -> ActionPrompt:
        """Generate surgical fixes from analysis violations."""
        fixes = []
        fix_number = 1

        # Generate fixes from detected violations
        for violation in analysis.violations:
            fix = await self._generate_fix_for_violation(
                violation=violation,
                scene_content=scene_content,
                voice_bundle=voice_bundle,
                fix_number=fix_number,
            )
            if fix:
                fixes.append(fix)
                fix_number += 1

        # Generate fixes for metaphor saturation if needed
        if analysis.metaphor_analysis and analysis.metaphor_analysis.saturated_domains:
            for domain in analysis.metaphor_analysis.saturated_domains[:2]:
                fix = await self._generate_metaphor_rebalance_fix(
                    domain=domain,
                    scene_content=scene_content,
                    voice_bundle=voice_bundle,
                    fix_number=fix_number,
                )
                if fix:
                    fixes.append(fix)
                    fix_number += 1

        # Generate preservation notes
        preservation_notes = [
            "Do not modify scene opening paragraph unless specifically targeted",
            "Preserve all dialogue attribution and tags",
            "Maintain existing paragraph structure",
            "Keep character-specific voice patterns intact",
        ]

        # Estimate score improvement
        expected_improvement = min(len(fixes) * 2, 10)  # ~2 points per fix, max 10

        return ActionPrompt(
            scene_id=scene_id,
            original_score=analysis.total_score,
            fixes=fixes,
            preservation_notes=preservation_notes,
            expected_score_improvement=expected_improvement,
        )

    async def _generate_fix_for_violation(
        self,
        violation: PatternViolation,
        scene_content: str,
        voice_bundle: Optional[VoiceBundleContext],
        fix_number: int,
    ) -> Optional[Fix]:
        """Generate a specific fix for a violation."""
        # Get context around the violation
        lines = scene_content.split("\n")
        line_idx = violation.line_number - 1

        if 0 <= line_idx < len(lines):
            old_text = lines[line_idx]
        else:
            old_text = violation.matched_text

        # Generate replacement based on violation type
        prompt = f"""Generate a fix for this anti-pattern violation.

VIOLATION: {violation.description}
MATCHED TEXT: "{violation.matched_text}"
FULL LINE: "{old_text}"
PENALTY: {violation.penalty} points

Generate a replacement that:
1. Eliminates the anti-pattern
2. Maintains the same meaning
3. Uses active voice and direct metaphors
4. Sounds like the character thinking, not AI explaining

Respond with ONLY the replacement text for the full line. No explanation."""

        try:
            new_text = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are a fiction editor fixing anti-patterns. Respond with only the replacement text.",
                prompt=prompt,
            )

            return Fix(
                fix_number=fix_number,
                description=violation.description,
                old_text=old_text,
                new_text=new_text.strip(),
                line_number=violation.line_number,
                category=violation.pattern_type,
            )

        except Exception as e:
            logger.error(f"Failed to generate fix for violation: {e}")
            return None

    async def _generate_metaphor_rebalance_fix(
        self,
        domain: str,
        scene_content: str,
        voice_bundle: Optional[VoiceBundleContext],
        fix_number: int,
    ) -> Optional[Fix]:
        """Generate a fix for metaphor domain saturation."""
        # Find a metaphor in the saturated domain
        domain_keywords = {
            "gambling": ["bet", "odds", "gamble", "wager", "poker", "cards", "chips", "dealer"],
            "music": ["rhythm", "tempo", "harmony", "melody", "crescendo", "note"],
            "cooking": ["simmer", "boil", "recipe", "ingredient", "stew"],
            "architecture": ["foundation", "scaffold", "blueprint", "structure"],
            "medicine": ["diagnosis", "symptom", "treatment", "surgical"],
        }

        keywords = domain_keywords.get(domain, [])
        if not keywords:
            return None

        # Find first occurrence
        for keyword in keywords:
            pattern = rf"\b{keyword}\b"
            match = re.search(pattern, scene_content, re.IGNORECASE)
            if match:
                # Get the full sentence containing the keyword
                start = scene_content.rfind(".", 0, match.start()) + 1
                end = scene_content.find(".", match.end())
                if end == -1:
                    end = len(scene_content)
                old_text = scene_content[start:end].strip()

                # Generate replacement with different domain
                prompt = f"""Rewrite this sentence to use a metaphor from a DIFFERENT domain.

ORIGINAL: "{old_text}"
CURRENT DOMAIN: {domain} (overused)
AVOID: {', '.join(keywords)}

Use one of these domains instead: performance, addiction, martial arts, surveillance, nature

Respond with ONLY the rewritten sentence. No explanation."""

                try:
                    new_text = await self.llm_service.generate_response(
                        provider="anthropic",
                        model="claude-sonnet-4-20250514",
                        system_role="You are rewriting a metaphor to a different domain.",
                        prompt=prompt,
                    )

                    return Fix(
                        fix_number=fix_number,
                        description=f"Rebalance {domain} metaphor saturation",
                        old_text=old_text,
                        new_text=new_text.strip(),
                        category="metaphor",
                    )

                except Exception as e:
                    logger.error(f"Failed to generate metaphor fix: {e}")
                    return None

        return None

    # -------------------------------------------------------------------------
    # Mode B: 6-Pass Enhancement
    # -------------------------------------------------------------------------

    async def _apply_six_pass_mode(
        self,
        scene_id: str,
        scene_content: str,
        analysis: SceneAnalysisResult,
        voice_bundle: Optional[VoiceBundleContext],
        story_bible: Optional[StoryBibleContext],
    ) -> EnhancementResult:
        """
        Apply full 6-pass enhancement ritual.

        Pass 1: Sensory Anchoring
        Pass 2: Verb Promotion + Simile Elimination
        Pass 3: Metaphor Rotation
        Pass 4: Voice Embed (Not Hover)
        Pass 5: Italics Gate (optional)
        Pass 6: Voice Authentication
        """
        logger.info(f"Applying 6-pass enhancement for {scene_id}")

        passes_completed = []
        current_content = scene_content

        # Build voice context
        voice_context = ""
        if voice_bundle:
            if voice_bundle.gold_standard:
                voice_context += f"\n## VOICE GOLD STANDARD\n{voice_bundle.gold_standard[:1500]}"
            if voice_bundle.anti_patterns:
                voice_context += f"\n## ANTI-PATTERNS\n{voice_bundle.anti_patterns[:1000]}"

        # Pass 1: Sensory Anchoring
        result, content = await self._pass_sensory_anchoring(current_content, voice_context)
        passes_completed.append(result)
        current_content = content

        # Pass 2: Verb Promotion + Simile Elimination
        result, content = await self._pass_verb_promotion(current_content, voice_context)
        passes_completed.append(result)
        current_content = content

        # Pass 3: Metaphor Rotation
        result, content = await self._pass_metaphor_rotation(current_content, voice_context, analysis)
        passes_completed.append(result)
        current_content = content

        # Pass 4: Voice Embed
        result, content = await self._pass_voice_embed(current_content, voice_context)
        passes_completed.append(result)
        current_content = content

        # Pass 5: Italics Gate
        result, content = await self._pass_italics_gate(current_content)
        passes_completed.append(result)
        current_content = content

        # Pass 6: Voice Authentication
        result, content = await self._pass_voice_authentication(current_content, voice_context, story_bible)
        passes_completed.append(result)
        current_content = content

        # Re-score after enhancement
        final_analysis = await self.analyzer_service.analyze_scene(
            scene_id=f"{scene_id}-enhanced",
            scene_content=current_content,
            voice_bundle=voice_bundle,
            story_bible=story_bible,
        )

        return EnhancementResult(
            scene_id=scene_id,
            mode=EnhancementMode.SIX_PASS,
            original_content=scene_content,
            enhanced_content=current_content,
            original_score=analysis.total_score,
            final_score=final_analysis.total_score,
            passes_completed=passes_completed,
        )

    async def _pass_sensory_anchoring(
        self,
        content: str,
        voice_context: str,
    ) -> Tuple[PassResult, str]:
        """Pass 1: Replace abstract moods with concrete sensory details."""
        prompt = f"""Enhance this scene with sensory anchoring.

{voice_context}

SCENE:
{content}

INSTRUCTIONS:
1. Find abstract mood descriptions (e.g., "the atmosphere was tense")
2. Replace with concrete sensory details: air, light, texture, sound, smell
3. Target 3 sensory anchors per major section
4. Do NOT change dialogue or major plot points
5. Keep the same word count approximately

Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are enhancing fiction with sensory details.",
                prompt=prompt,
            )

            changes = self._count_changes(content, enhanced)

            return PassResult(
                pass_number=1,
                pass_name="Sensory Anchoring",
                changes_made=changes,
                changes=["Added concrete sensory details"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 1 failed: {e}")
            return PassResult(pass_number=1, pass_name="Sensory Anchoring", changes_made=0, changes=[], notes=str(e)), content

    async def _pass_verb_promotion(
        self,
        content: str,
        voice_context: str,
    ) -> Tuple[PassResult, str]:
        """Pass 2: Verb promotion and simile elimination."""
        prompt = f"""Enhance this scene with verb promotion and simile elimination.

{voice_context}

SCENE:
{content}

INSTRUCTIONS:
1. Make environment ACT: "lobby air wheezed," "architecture confessed"
2. Convert ALL similes ("like X", "as if") to direct metaphors
3. Use literal-metaphorical reality: things BECOME, not resemble
4. Promote nouns to verbs where possible

Examples:
- "like a weapon" → "weaponized itself"
- "seemed tense" → "tension architectured itself"
- "felt like drowning" → "consciousness drowned"

Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are eliminating similes and promoting verbs.",
                prompt=prompt,
            )

            changes = self._count_changes(content, enhanced)

            return PassResult(
                pass_number=2,
                pass_name="Verb Promotion + Simile Elimination",
                changes_made=changes,
                changes=["Promoted verbs", "Eliminated similes"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 2 failed: {e}")
            return PassResult(pass_number=2, pass_name="Verb Promotion", changes_made=0, changes=[], notes=str(e)), content

    async def _pass_metaphor_rotation(
        self,
        content: str,
        voice_context: str,
        analysis: SceneAnalysisResult,
    ) -> Tuple[PassResult, str]:
        """Pass 3: Metaphor domain rotation."""
        saturated = []
        if analysis.metaphor_analysis and analysis.metaphor_analysis.saturated_domains:
            saturated = analysis.metaphor_analysis.saturated_domains

        prompt = f"""Rebalance metaphor domains in this scene.

{voice_context}

SCENE:
{content}

SATURATED DOMAINS (overused): {', '.join(saturated) if saturated else 'None detected'}

INSTRUCTIONS:
1. No single domain should exceed 30% of metaphors
2. Gambling metaphors: max 2-3 per scene
3. Rotate between: performance, addiction, martial arts, surveillance, music, nature
4. Replace some metaphors from saturated domains with alternatives

Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are rebalancing metaphor domains.",
                prompt=prompt,
            )

            changes = self._count_changes(content, enhanced)

            return PassResult(
                pass_number=3,
                pass_name="Metaphor Rotation",
                changes_made=changes,
                changes=[f"Rebalanced {d}" for d in saturated] if saturated else ["Verified domain balance"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 3 failed: {e}")
            return PassResult(pass_number=3, pass_name="Metaphor Rotation", changes_made=0, changes=[], notes=str(e)), content

    async def _pass_voice_embed(
        self,
        content: str,
        voice_context: str,
    ) -> Tuple[PassResult, str]:
        """Pass 4: Embed voice in action, don't let it hover."""
        prompt = f"""Embed voice in action - eliminate hovering commentary.

{voice_context}

SCENE:
{content}

INSTRUCTIONS:
1. Delete sentences that "explain" what the previous sentence showed
2. Insights should be EMBEDDED in action, not floating above it
3. No academic meta-commentary ("Enhanced perspective analyzing...")
4. Test each insight: Is it IN the action or ABOUT the action?

BAD: "He noticed the pattern. This suggested danger."
GOOD: "The pattern screamed danger."

Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are embedding voice in action.",
                prompt=prompt,
            )

            changes = self._count_changes(content, enhanced)

            return PassResult(
                pass_number=4,
                pass_name="Voice Embed (Not Hover)",
                changes_made=changes,
                changes=["Embedded insights in action"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 4 failed: {e}")
            return PassResult(pass_number=4, pass_name="Voice Embed", changes_made=0, changes=[], notes=str(e)), content

    async def _pass_italics_gate(
        self,
        content: str,
    ) -> Tuple[PassResult, str]:
        """Pass 5: Italics gate - limit to 0-1 per scene."""
        # Count current italics
        italics_pattern = r"\*[^*]+\*"
        matches = re.findall(italics_pattern, content)

        if len(matches) <= 1:
            return PassResult(
                pass_number=5,
                pass_name="Italics Gate",
                changes_made=0,
                changes=["Italics within limit"],
                notes=f"Found {len(matches)} italics (limit: 1)",
            ), content

        prompt = f"""Reduce italics usage in this scene.

SCENE:
{content}

CURRENT ITALICS COUNT: {len(matches)}
TARGET: 0-1 maximum

INSTRUCTIONS:
1. Keep italics ONLY for: character arc moments, earned wisdom, critical turning points
2. Convert other italics to regular prose
3. The insight should work without italics emphasis

Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are reducing italics usage.",
                prompt=prompt,
            )

            new_matches = re.findall(italics_pattern, enhanced)

            return PassResult(
                pass_number=5,
                pass_name="Italics Gate",
                changes_made=len(matches) - len(new_matches),
                changes=[f"Reduced from {len(matches)} to {len(new_matches)} italics"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 5 failed: {e}")
            return PassResult(pass_number=5, pass_name="Italics Gate", changes_made=0, changes=[], notes=str(e)), content

    async def _pass_voice_authentication(
        self,
        content: str,
        voice_context: str,
        story_bible: Optional[StoryBibleContext],
    ) -> Tuple[PassResult, str]:
        """Pass 6: Voice authentication - final quality check."""
        character_context = ""
        if story_bible:
            character_context = f"""
CHARACTER: {story_bible.protagonist_name}
FATAL FLAW: {story_bible.fatal_flaw}
THE LIE: {story_bible.the_lie}
"""

        prompt = f"""Final voice authentication pass.

{voice_context}
{character_context}

SCENE:
{content}

RUN THESE TESTS:

1. OBSERVER TEST: Does this sound like the character THINKING, or AI EXPLAINING the character?
   - Fix any "AI explaining" moments

2. PURPOSE TEST: Does every beat serve the theme?
   - Remove beats that don't serve purpose

3. FUSION TEST: Is analytical precision fused with character voice?
   - Fix any separation between expertise and personality

Make minimal changes - only fix what fails the tests.
Output the enhanced scene only. No commentary."""

        try:
            enhanced = await self.llm_service.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-20250514",
                system_role="You are authenticating character voice.",
                prompt=prompt,
            )

            changes = self._count_changes(content, enhanced)

            return PassResult(
                pass_number=6,
                pass_name="Voice Authentication",
                changes_made=changes,
                changes=["Passed voice authentication tests"],
            ), enhanced

        except Exception as e:
            logger.error(f"Pass 6 failed: {e}")
            return PassResult(pass_number=6, pass_name="Voice Authentication", changes_made=0, changes=[], notes=str(e)), content

    def _count_changes(self, original: str, enhanced: str) -> int:
        """Rough count of changes between original and enhanced."""
        # Simple word diff count
        original_words = set(original.split())
        enhanced_words = set(enhanced.split())
        return len(original_words.symmetric_difference(enhanced_words))


# =============================================================================
# Service Singleton
# =============================================================================

_scene_enhancement_service: Optional[SceneEnhancementService] = None


def get_scene_enhancement_service() -> SceneEnhancementService:
    """Get or create the SceneEnhancementService singleton."""
    global _scene_enhancement_service
    if _scene_enhancement_service is None:
        _scene_enhancement_service = SceneEnhancementService()
    return _scene_enhancement_service
