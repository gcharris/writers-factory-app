"""
Tests for Scene Enhancement Service - Phase 3B Director Mode

Tests the 2-mode enhancement pipeline:
1. Action Prompt Mode (85+): Surgical fixes for high-scoring scenes
2. 6-Pass Enhancement Mode (70-84): Full enhancement ritual
3. Rewrite Mode (<70): Signal rewrite needed

Based on STEP 4 from the manual Explants workflow.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from backend.services.scene_enhancement_service import (
    SceneEnhancementService,
    EnhancementMode,
    EnhancementResult,
    ActionPrompt,
    Fix,
    PassResult,
)
from backend.services.scene_analyzer_service import (
    SceneAnalysisResult,
    PatternViolation,
    VoiceBundleContext,
    StoryBibleContext,
    MetaphorAnalysis,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_scene_content():
    """Create sample scene content for testing."""
    return """
The Q5 port at the base of Mickey's skull hummed with residual charge. Area 52's
fluorescent buzz cut through his consciousness like a knife through butter—quantum
fatigue manifesting with clinical precision.

Ken entered carrying a manila folder. "Beautiful morning," he said, settling into
the chair with calculated precision.

Mickey's thumb found its familiar groove—three taps, pause, three more. The addiction
tell that survived decades of suppression.
"""


@pytest.fixture
def mock_enhanced_content():
    """Create enhanced scene content for testing."""
    return """
The Q5 port at the base of Mickey's skull hummed with residual charge. Area 52's
fluorescent buzz weaponized his consciousness—quantum fatigue becoming analog pain.

Ken entered carrying a manila folder. "Beautiful morning," he said, settling into
the chair across from Mickey's platform.

Mickey's thumb found its familiar groove—three taps, pause, three more. The addiction
tell that survived decades of suppression.
"""


@pytest.fixture
def mock_analysis_high_score():
    """Create mock analysis for high-scoring scene (85+)."""
    return SceneAnalysisResult(
        scene_id="test_scene_001",
        total_score=87,
        grade="A",
        quality_level="EXCELLENT",
        violations=[
            PatternViolation(
                pattern_type="simile",
                description="Simile: 'like a knife through butter'",
                matched_text="like a knife through butter",
                line_number=2,
                penalty=3,
                severity="critical",
            ),
            PatternViolation(
                pattern_type="zero_tolerance",
                description="Anti-pattern: 'with clinical precision'",
                matched_text="with clinical precision",
                line_number=3,
                penalty=5,
                severity="zero_tolerance",
            ),
            PatternViolation(
                pattern_type="zero_tolerance",
                description="Anti-pattern: 'with calculated precision'",
                matched_text="with calculated precision",
                line_number=5,
                penalty=5,
                severity="zero_tolerance",
            ),
        ],
        metaphor_analysis=None,
    )


@pytest.fixture
def mock_analysis_medium_score():
    """Create mock analysis for medium-scoring scene (70-84)."""
    return SceneAnalysisResult(
        scene_id="test_scene_002",
        total_score=75,
        grade="B+",
        quality_level="ACCEPTABLE",
        violations=[
            PatternViolation(
                pattern_type="simile",
                description="Multiple similes detected",
                matched_text="like X",
                line_number=2,
                penalty=3,
                severity="critical",
            ),
        ],
        metaphor_analysis=MetaphorAnalysis(
            total_metaphors=8,
            domain_counts={"gambling": 5, "surveillance": 2, "addiction": 1},
            saturated_domains=["gambling"],  # 62.5% saturation
            diversity_score=45,
        ),
    )


@pytest.fixture
def mock_analysis_low_score():
    """Create mock analysis for low-scoring scene (<70)."""
    return SceneAnalysisResult(
        scene_id="test_scene_003",
        total_score=65,
        grade="C+",
        quality_level="NEEDS WORK",
        violations=[],
        metaphor_analysis=None,
    )


@pytest.fixture
def mock_voice_bundle():
    """Create a mock voice bundle for testing."""
    return VoiceBundleContext(
        gold_standard="""
The Q5 port at the base of Mickey's skull hummed with residual charge from overnight
surveillance duty. Area 52's fluorescent buzz cut through his consciousness—quantum
fatigue manifesting as analog pain.
""",
        anti_patterns=[
            "with [adjective] precision",
            "like [simile]",
            "seemed to [verb]",
            "as if [clause]",
        ],
        principles=[
            "Embedded philosophical argument through dramatic action",
            "Cognitive fusion: con artist wisdom + quantum hindsight",
            "Process-over-noun thinking",
        ],
    )


@pytest.fixture
def mock_story_bible():
    """Create a mock story bible for testing."""
    return StoryBibleContext(
        protagonist_name="Mickey Bardot",
        fatal_flaw="Addiction to control through prediction",
        the_lie="Perfect knowledge prevents loss",
        genre="Cyber-noir techno-thriller",
        theme="The illusion of certainty in an uncertain world",
    )


@pytest.fixture
def enhancement_service():
    """Create a SceneEnhancementService instance for testing."""
    with patch('backend.services.scene_enhancement_service.LLMService'), \
         patch('backend.services.scene_enhancement_service.get_scene_analyzer_service'):
        service = SceneEnhancementService(project_id="test_project")
        return service


# =============================================================================
# Test Mode Selection
# =============================================================================

class TestModeSelection:
    """Tests for enhancement mode selection based on score thresholds."""

    def test_action_prompt_mode_for_high_score(self, enhancement_service):
        """Test that score 85+ triggers Action Prompt mode."""
        mode = enhancement_service._determine_mode(87)
        assert mode == EnhancementMode.ACTION_PROMPT

    def test_six_pass_mode_for_medium_score(self, enhancement_service):
        """Test that score 70-84 triggers 6-Pass mode."""
        mode = enhancement_service._determine_mode(75)
        assert mode == EnhancementMode.SIX_PASS

    def test_rewrite_mode_for_low_score(self, enhancement_service):
        """Test that score <70 triggers Rewrite mode."""
        mode = enhancement_service._determine_mode(65)
        assert mode == EnhancementMode.REWRITE

    def test_threshold_boundaries(self, enhancement_service):
        """Test exact threshold boundaries."""
        assert enhancement_service._determine_mode(85) == EnhancementMode.ACTION_PROMPT
        assert enhancement_service._determine_mode(84) == EnhancementMode.SIX_PASS
        assert enhancement_service._determine_mode(70) == EnhancementMode.SIX_PASS
        assert enhancement_service._determine_mode(69) == EnhancementMode.REWRITE

    def test_dynamic_threshold_loading(self):
        """Test that thresholds can be loaded from Settings Service."""
        with patch('backend.services.scene_enhancement_service.LLMService'), \
             patch('backend.services.scene_enhancement_service.get_scene_analyzer_service'), \
             patch('backend.services.scene_enhancement_service.settings_service.get') as mock_get:

            # Mock custom thresholds
            mock_get.side_effect = lambda key, project_id: {
                "enhancement.action_prompt_threshold": 90,
                "enhancement.six_pass_threshold": 75,
                "enhancement.rewrite_threshold": 60,
                "enhancement.aggressiveness": "high",
            }.get(key)

            service = SceneEnhancementService(project_id="custom_project")

            assert service.action_prompt_threshold == 90
            assert service.six_pass_threshold == 75
            assert service.rewrite_threshold == 60
            assert service.aggressiveness == "high"


# =============================================================================
# Test Action Prompt Mode (85+)
# =============================================================================

class TestActionPromptMode:
    """Tests for Action Prompt mode (surgical fixes for high-scoring scenes)."""

    @pytest.mark.asyncio
    async def test_generates_action_prompt_with_fixes(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_high_score,
        mock_voice_bundle
    ):
        """Test that action prompt generates surgical fixes from violations."""
        with patch.object(
            enhancement_service,
            '_generate_action_prompt',
            new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = ActionPrompt(
                scene_id="test_scene_001",
                original_score=87,
                fixes=[
                    Fix(
                        fix_number=1,
                        description="Remove simile: 'like a knife through butter'",
                        old_text="like a knife through butter",
                        new_text="weaponized his consciousness",
                        line_number=2,
                        category="simile",
                    ),
                    Fix(
                        fix_number=2,
                        description="Remove 'with clinical precision'",
                        old_text="with clinical precision",
                        new_text="becoming analog pain",
                        line_number=3,
                        category="zero_tolerance",
                    ),
                ],
                preservation_notes=["Preserve all dialogue", "Maintain paragraph structure"],
                expected_score_improvement=6,
            )

            action_prompt = await enhancement_service._generate_action_prompt(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=mock_analysis_high_score,
                voice_bundle=mock_voice_bundle,
            )

            assert len(action_prompt.fixes) == 2
            assert action_prompt.original_score == 87
            assert action_prompt.expected_score_improvement == 6
            assert any("simile" in f.description.lower() for f in action_prompt.fixes)

    @pytest.mark.asyncio
    async def test_applies_fixes_to_scene_content(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_high_score,
        mock_voice_bundle
    ):
        """Test that fixes are correctly applied to scene content."""
        with patch.object(
            enhancement_service,
            '_generate_action_prompt',
            new_callable=AsyncMock
        ) as mock_generate, \
             patch.object(
                 enhancement_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            mock_generate.return_value = ActionPrompt(
                scene_id="test_scene_001",
                original_score=87,
                fixes=[
                    Fix(
                        fix_number=1,
                        description="Fix simile",
                        old_text="like a knife through butter",
                        new_text="weaponized",
                        line_number=2,
                        category="simile",
                    ),
                ],
                preservation_notes=["Preserve dialogue"],
                expected_score_improvement=4,
            )

            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test_scene_001-enhanced",
                total_score=91,
                grade="A+",
                quality_level="GOLD STANDARD",
                violations=[],
                metaphor_analysis=None,
            )

            result = await enhancement_service._apply_action_prompt_mode(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=mock_analysis_high_score,
                voice_bundle=mock_voice_bundle,
            )

            assert result.mode == EnhancementMode.ACTION_PROMPT
            assert result.original_score == 87
            assert result.final_score == 91
            assert "weaponized" in result.enhanced_content
            assert "like a knife through butter" not in result.enhanced_content

    @pytest.mark.asyncio
    async def test_handles_fix_not_found(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_high_score,
        mock_voice_bundle
    ):
        """Test handling when fix text is not found in scene."""
        with patch.object(
            enhancement_service,
            '_generate_action_prompt',
            new_callable=AsyncMock
        ) as mock_generate, \
             patch.object(
                 enhancement_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            mock_generate.return_value = ActionPrompt(
                scene_id="test_scene_001",
                original_score=87,
                fixes=[
                    Fix(
                        fix_number=1,
                        description="Fix nonexistent text",
                        old_text="THIS TEXT DOES NOT EXIST IN SCENE",
                        new_text="replacement",
                        line_number=99,
                        category="test",
                    ),
                ],
                preservation_notes=[],
                expected_score_improvement=2,
            )

            mock_analyze.return_value = mock_analysis_high_score

            result = await enhancement_service._apply_action_prompt_mode(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=mock_analysis_high_score,
                voice_bundle=mock_voice_bundle,
            )

            # Should have fix marked as "not_found"
            assert any(f["status"] == "not_found" for f in result.fixes_applied)

    @pytest.mark.asyncio
    async def test_generates_fixes_for_metaphor_saturation(
        self,
        enhancement_service,
        mock_scene_content,
        mock_voice_bundle
    ):
        """Test that metaphor saturation triggers domain rebalancing fixes."""
        analysis = SceneAnalysisResult(
            scene_id="test_scene_001",
            total_score=85,
            grade="A",
            quality_level="EXCELLENT",
            violations=[],
            metaphor_analysis=MetaphorAnalysis(
                total_metaphors=10,
                domain_counts={"gambling": 7, "surveillance": 2, "addiction": 1},
                saturated_domains=["gambling"],  # 70% saturation
                diversity_score=30,
            ),
        )

        with patch.object(
            enhancement_service,
            '_generate_metaphor_rebalance_fix',
            new_callable=AsyncMock
        ) as mock_metaphor:
            mock_metaphor.return_value = Fix(
                fix_number=1,
                description="Rebalance gambling metaphor saturation",
                old_text="the odds were stacked",
                new_text="the pattern screamed danger",
                category="metaphor",
            )

            action_prompt = await enhancement_service._generate_action_prompt(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=analysis,
                voice_bundle=mock_voice_bundle,
            )

            # Should have called metaphor rebalance
            assert mock_metaphor.called

    def test_action_prompt_markdown_generation(self):
        """Test that action prompt generates proper markdown format."""
        action_prompt = ActionPrompt(
            scene_id="test_scene_001",
            original_score=87,
            fixes=[
                Fix(
                    fix_number=1,
                    description="Remove simile",
                    old_text="like water",
                    new_text="flowed",
                    line_number=5,
                    category="simile",
                ),
            ],
            preservation_notes=["Preserve dialogue"],
            expected_score_improvement=4,
        )

        markdown = action_prompt.to_markdown()

        assert "## ENHANCEMENT ACTION PROMPT" in markdown
        assert "FIX 1: Remove simile" in markdown
        assert "**OLD:**" in markdown
        assert "**NEW:**" in markdown
        assert "like water" in markdown
        assert "flowed" in markdown
        assert "Preserve dialogue" in markdown
        assert "87 → 91" in markdown  # 87 + 4


# =============================================================================
# Test 6-Pass Enhancement Mode (70-84)
# =============================================================================

class TestSixPassMode:
    """Tests for 6-Pass Enhancement mode (full enhancement ritual)."""

    @pytest.mark.asyncio
    async def test_executes_all_six_passes(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_medium_score,
        mock_voice_bundle,
        mock_story_bible
    ):
        """Test that all 6 enhancement passes are executed."""
        with patch.object(
            enhancement_service,
            '_pass_sensory_anchoring',
            new_callable=AsyncMock
        ) as mock_pass1, \
             patch.object(
                 enhancement_service,
                 '_pass_verb_promotion',
                 new_callable=AsyncMock
             ) as mock_pass2, \
             patch.object(
                 enhancement_service,
                 '_pass_metaphor_rotation',
                 new_callable=AsyncMock
             ) as mock_pass3, \
             patch.object(
                 enhancement_service,
                 '_pass_voice_embed',
                 new_callable=AsyncMock
             ) as mock_pass4, \
             patch.object(
                 enhancement_service,
                 '_pass_italics_gate',
                 new_callable=AsyncMock
             ) as mock_pass5, \
             patch.object(
                 enhancement_service,
                 '_pass_voice_authentication',
                 new_callable=AsyncMock
             ) as mock_pass6, \
             patch.object(
                 enhancement_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            # Mock each pass to return a PassResult and modified content
            mock_pass1.return_value = (
                PassResult(1, "Sensory Anchoring", 3, ["Added sensory details"]),
                mock_scene_content + " [pass1]"
            )
            mock_pass2.return_value = (
                PassResult(2, "Verb Promotion", 2, ["Promoted verbs"]),
                mock_scene_content + " [pass2]"
            )
            mock_pass3.return_value = (
                PassResult(3, "Metaphor Rotation", 1, ["Rebalanced gambling"]),
                mock_scene_content + " [pass3]"
            )
            mock_pass4.return_value = (
                PassResult(4, "Voice Embed", 2, ["Embedded insights"]),
                mock_scene_content + " [pass4]"
            )
            mock_pass5.return_value = (
                PassResult(5, "Italics Gate", 0, ["Italics within limit"]),
                mock_scene_content + " [pass5]"
            )
            mock_pass6.return_value = (
                PassResult(6, "Voice Authentication", 1, ["Passed voice tests"]),
                mock_scene_content + " [pass6]"
            )

            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test_scene_002-enhanced",
                total_score=82,
                grade="A-",
                quality_level="STRONG",
                violations=[],
                metaphor_analysis=None,
            )

            result = await enhancement_service._apply_six_pass_mode(
                scene_id="test_scene_002",
                scene_content=mock_scene_content,
                analysis=mock_analysis_medium_score,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
            )

            assert result.mode == EnhancementMode.SIX_PASS
            assert len(result.passes_completed) == 6
            assert result.original_score == 75
            assert result.final_score == 82

            # Verify all passes were called
            assert mock_pass1.called
            assert mock_pass2.called
            assert mock_pass3.called
            assert mock_pass4.called
            assert mock_pass5.called
            assert mock_pass6.called

    @pytest.mark.asyncio
    async def test_pass1_sensory_anchoring(self, enhancement_service):
        """Test Pass 1: Sensory Anchoring."""
        content = "The room was tense. He felt nervous."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "The air thickened with ozone. His palms slicked against metal."

            result, enhanced = await enhancement_service._pass_sensory_anchoring(
                content=content,
                voice_context="## VOICE CONTEXT\nUse concrete sensory details",
            )

            assert result.pass_number == 1
            assert result.pass_name == "Sensory Anchoring"
            assert "ozone" in enhanced
            assert "palms slicked" in enhanced

    @pytest.mark.asyncio
    async def test_pass2_verb_promotion(self, enhancement_service):
        """Test Pass 2: Verb Promotion + Simile Elimination."""
        content = "The air was like ice. He moved like a ghost."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "The air froze. He ghosted through the doorway."

            result, enhanced = await enhancement_service._pass_verb_promotion(
                content=content,
                voice_context="## ANTI-PATTERNS\nAvoid similes",
            )

            assert result.pass_number == 2
            assert result.pass_name == "Verb Promotion + Simile Elimination"
            assert "froze" in enhanced
            assert "like" not in enhanced

    @pytest.mark.asyncio
    async def test_pass3_metaphor_rotation(self, enhancement_service, mock_analysis_medium_score):
        """Test Pass 3: Metaphor Rotation."""
        content = "He bet on the outcome. The odds were against him. Time to fold."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "He predicted the outcome. The pattern screamed danger. Time to retreat."

            result, enhanced = await enhancement_service._pass_metaphor_rotation(
                content=content,
                voice_context="## VOICE\nRotate metaphor domains",
                analysis=mock_analysis_medium_score,
            )

            assert result.pass_number == 3
            assert result.pass_name == "Metaphor Rotation"
            assert "Rebalanced gambling" in str(result.changes)

    @pytest.mark.asyncio
    async def test_pass4_voice_embed(self, enhancement_service):
        """Test Pass 4: Voice Embed (Not Hover)."""
        content = "He noticed the pattern. This suggested danger. It was concerning."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "The pattern screamed danger."

            result, enhanced = await enhancement_service._pass_voice_embed(
                content=content,
                voice_context="## VOICE\nEmbed insights in action",
            )

            assert result.pass_number == 4
            assert result.pass_name == "Voice Embed (Not Hover)"
            # Should be more concise (fewer words)
            assert len(enhanced.split()) < len(content.split())

    @pytest.mark.asyncio
    async def test_pass5_italics_gate_within_limit(self, enhancement_service):
        """Test Pass 5: Italics Gate when within limit."""
        content = "He knew the truth. *Some things can't be predicted.*"

        result, enhanced = await enhancement_service._pass_italics_gate(content)

        assert result.pass_number == 5
        assert result.pass_name == "Italics Gate"
        assert result.changes_made == 0
        assert "Italics within limit" in str(result.changes)
        assert enhanced == content  # No changes

    @pytest.mark.asyncio
    async def test_pass5_italics_gate_over_limit(self, enhancement_service):
        """Test Pass 5: Italics Gate when over limit."""
        content = "He knew. *First truth.* Then realized. *Second truth.* Finally. *Third truth.*"

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "He knew. *The only truth that mattered.* Then realized. Second truth. Finally. Third truth."

            result, enhanced = await enhancement_service._pass_italics_gate(content)

            assert result.pass_number == 5
            assert result.changes_made > 0
            # Should have reduced italics count
            assert enhanced.count("*") < content.count("*")

    @pytest.mark.asyncio
    async def test_pass6_voice_authentication(self, enhancement_service, mock_story_bible):
        """Test Pass 6: Voice Authentication."""
        content = "The system analyzed the situation with enhanced precision."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = "Mickey read the tells. The house edge was showing."

            result, enhanced = await enhancement_service._pass_voice_authentication(
                content=content,
                voice_context="## GOLD STANDARD\nCon artist + quantum hindsight",
                story_bible=mock_story_bible,
            )

            assert result.pass_number == 6
            assert result.pass_name == "Voice Authentication"
            assert "Mickey" in enhanced
            # Should remove AI-contaminated language
            assert "enhanced precision" not in enhanced


# =============================================================================
# Test Rewrite Mode (<70)
# =============================================================================

class TestRewriteMode:
    """Tests for Rewrite mode (scenes scoring below 70)."""

    @pytest.mark.asyncio
    async def test_rewrite_mode_returns_unchanged_content(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_low_score
    ):
        """Test that rewrite mode returns original content unchanged."""
        result = await enhancement_service.enhance_scene(
            scene_id="test_scene_003",
            scene_content=mock_scene_content,
            analysis=mock_analysis_low_score,
        )

        assert result.mode == EnhancementMode.REWRITE
        assert result.enhanced_content == mock_scene_content  # Unchanged
        assert result.original_score == 65
        assert result.final_score is None  # No re-scoring

    @pytest.mark.asyncio
    async def test_rewrite_mode_signals_rewrite_needed(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_low_score
    ):
        """Test that rewrite mode signals that scene needs rewriting."""
        result = await enhancement_service.enhance_scene(
            scene_id="test_scene_003",
            scene_content=mock_scene_content,
            analysis=mock_analysis_low_score,
        )

        # Mode indicates rewrite needed
        assert result.mode == EnhancementMode.REWRITE
        # No enhancement attempted
        assert len(result.fixes_applied) == 0
        assert len(result.passes_completed) == 0


# =============================================================================
# Test Force Mode Override
# =============================================================================

class TestForceModeOverride:
    """Tests for force_mode parameter to override automatic mode selection."""

    @pytest.mark.asyncio
    async def test_force_action_prompt_on_medium_score(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_medium_score,
        mock_voice_bundle
    ):
        """Test that force_mode can override automatic mode selection."""
        with patch.object(
            enhancement_service,
            '_apply_action_prompt_mode',
            new_callable=AsyncMock
        ) as mock_action:
            mock_action.return_value = EnhancementResult(
                scene_id="test_scene_002",
                mode=EnhancementMode.ACTION_PROMPT,
                original_content=mock_scene_content,
                enhanced_content=mock_scene_content,
                original_score=75,
            )

            result = await enhancement_service.enhance_scene(
                scene_id="test_scene_002",
                scene_content=mock_scene_content,
                analysis=mock_analysis_medium_score,
                force_mode=EnhancementMode.ACTION_PROMPT,  # Force action prompt
            )

            assert result.mode == EnhancementMode.ACTION_PROMPT
            assert mock_action.called


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in scene enhancement."""

    @pytest.mark.asyncio
    async def test_pass_failure_returns_original_content(self, enhancement_service):
        """Test that pass failure returns original content with error note."""
        content = "Test scene content."

        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.side_effect = Exception("LLM service unavailable")

            result, enhanced = await enhancement_service._pass_sensory_anchoring(
                content=content,
                voice_context="## VOICE",
            )

            assert result.pass_number == 1
            assert result.changes_made == 0
            assert "LLM service unavailable" in result.notes
            assert enhanced == content  # Original returned

    @pytest.mark.asyncio
    async def test_handles_missing_voice_bundle(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_high_score
    ):
        """Test that enhancement works without voice bundle."""
        with patch.object(
            enhancement_service,
            '_apply_action_prompt_mode',
            new_callable=AsyncMock
        ) as mock_action:
            mock_action.return_value = EnhancementResult(
                scene_id="test_scene_001",
                mode=EnhancementMode.ACTION_PROMPT,
                original_content=mock_scene_content,
                enhanced_content=mock_scene_content,
                original_score=87,
            )

            result = await enhancement_service.enhance_scene(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=mock_analysis_high_score,
                voice_bundle=None,  # No voice bundle
            )

            assert result is not None
            assert mock_action.called


# =============================================================================
# Test Integration Scenarios
# =============================================================================

class TestIntegrationScenarios:
    """Tests for realistic enhancement scenarios."""

    @pytest.mark.asyncio
    async def test_complete_action_prompt_workflow(
        self,
        enhancement_service,
        mock_scene_content,
        mock_enhanced_content,
        mock_analysis_high_score,
        mock_voice_bundle
    ):
        """Test complete action prompt workflow from analysis to final score."""
        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm, \
             patch.object(
                 enhancement_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            # Mock fix generation
            mock_llm.return_value = "weaponized his consciousness"

            # Mock final analysis with improved score
            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test_scene_001-enhanced",
                total_score=93,
                grade="A+",
                quality_level="GOLD STANDARD",
                violations=[],
                metaphor_analysis=None,
            )

            result = await enhancement_service.enhance_scene(
                scene_id="test_scene_001",
                scene_content=mock_scene_content,
                analysis=mock_analysis_high_score,
                voice_bundle=mock_voice_bundle,
            )

            assert result.mode == EnhancementMode.ACTION_PROMPT
            assert result.original_score == 87
            assert result.final_score == 93
            assert len(result.fixes_applied) > 0

    @pytest.mark.asyncio
    async def test_complete_six_pass_workflow(
        self,
        enhancement_service,
        mock_scene_content,
        mock_analysis_medium_score,
        mock_voice_bundle,
        mock_story_bible
    ):
        """Test complete 6-pass workflow with all passes."""
        with patch.object(
            enhancement_service.llm_service,
            'generate_response',
            new_callable=AsyncMock
        ) as mock_llm, \
             patch.object(
                 enhancement_service.analyzer_service,
                 'analyze_scene',
                 new_callable=AsyncMock
             ) as mock_analyze:

            # Mock LLM responses for all passes
            mock_llm.return_value = mock_scene_content + " [enhanced]"

            # Mock final analysis with improved score
            mock_analyze.return_value = SceneAnalysisResult(
                scene_id="test_scene_002-enhanced",
                total_score=84,
                grade="A",
                quality_level="EXCELLENT",
                violations=[],
                metaphor_analysis=None,
            )

            result = await enhancement_service.enhance_scene(
                scene_id="test_scene_002",
                scene_content=mock_scene_content,
                analysis=mock_analysis_medium_score,
                voice_bundle=mock_voice_bundle,
                story_bible=mock_story_bible,
            )

            assert result.mode == EnhancementMode.SIX_PASS
            assert len(result.passes_completed) == 6
            assert result.original_score == 75
            assert result.final_score == 84
            assert all(p.pass_number in [1, 2, 3, 4, 5, 6] for p in result.passes_completed)
