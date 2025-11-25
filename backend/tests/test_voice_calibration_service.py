"""
Tests for Voice Calibration Service - Phase 2B

Tests the voice tournament system that:
1. Runs multi-agent tournaments (5 agents × 5 strategies = 25 variants)
2. Generates Voice Reference Bundle files (Gold Standard, Anti-Patterns, Phase Evolution)
3. Stores voice calibration in KB for Knowledge Graph promotion
4. Creates voice_settings.yaml for dynamic Director Mode services

Based on the manual voice discovery workflow from The Explants.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock, mock_open
from datetime import datetime, timezone
from pathlib import Path
import json
import yaml

from backend.services.voice_calibration_service import (
    VoiceCalibrationService,
    TournamentStatus,
    TournamentResult,
    VoiceVariant,
    AgentInfo,
    VoiceCalibrationDocument,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_agents_yaml():
    """Create mock agents.yaml configuration."""
    return {
        'agents': [
            {
                'id': 'claude-sonnet-4',
                'name': 'Claude Sonnet 4',
                'provider': 'anthropic',
                'model': 'claude-sonnet-4-20250514',
                'role': 'Primary creative writing agent',
                'enabled': True,
                'api_key_env': 'ANTHROPIC_API_KEY',
                'use_cases': ['tournament', 'scene_generation', 'enhancement'],
            },
            {
                'id': 'gpt-4o',
                'name': 'GPT-4o',
                'provider': 'openai',
                'model': 'gpt-4o',
                'role': 'Alternative creative perspective',
                'enabled': True,
                'api_key_env': 'OPENAI_API_KEY',
                'use_cases': ['tournament', 'scene_generation'],
            },
            {
                'id': 'deepseek-chat',
                'name': 'DeepSeek Chat',
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'role': 'Cost-effective alternative',
                'enabled': False,
                'api_key_env': 'DEEPSEEK_API_KEY',
                'use_cases': ['tournament', 'scene_generation'],
            },
            {
                'id': 'llama3-local',
                'name': 'Llama 3.2 Local',
                'provider': 'ollama',
                'model': 'llama3.2',
                'role': 'Free local processing',
                'enabled': True,
                'api_key_env': None,  # No key needed for local
                'use_cases': ['tournament', 'scaffold'],
            },
        ]
    }


@pytest.fixture
def mock_test_prompt():
    """Create a mock test prompt for voice calibration."""
    return """
Write the opening of Chapter 2. Mickey enters the Area 52 briefing room where
Ken Dalton waits with evidence about the quantum surveillance network.
Establish Mickey's addiction tell (thumb tapping) and his con artist pattern
recognition struggling against quantum hindsight. Use casino/performance metaphors.
"""


@pytest.fixture
def mock_test_context():
    """Create mock test context."""
    return """
SETTING: Area 51 Area 52 underground briefing room, 2:00 AM
CHARACTERS: Mickey Bardot (POV character), Ken Dalton
MOOD: Tense, quantum fatigue affecting Mickey's perception
VOICE: Third-person limited, past tense, cyber-noir with con artist sensibility
"""


@pytest.fixture
def mock_voice_description():
    """Create mock voice description from writer."""
    return """
I want a voice that fuses con artist pattern recognition with quantum physics expertise.
Think Philip K. Dick meets David Mamet. Use embedded philosophical argument through
dramatic action. Metaphors from gambling, performance, and surveillance. Never say
"with precision" or use similes like "like X" or "as if Y".
"""


@pytest.fixture
def mock_winning_variant():
    """Create a mock winning variant."""
    return """
The Q5 port at the base of Mickey's skull hummed with residual charge from overnight
surveillance duty. Area 52's fluorescent buzz cut through his consciousness—quantum
fatigue manifesting as analog pain.

Ken entered carrying two items: a manila folder and a tablet displaying satellite imagery.

"Beautiful morning," Ken said, settling into the chair across from Mickey's platform.
He opened the folder first, spreading photographs across the metal table. "I thought
you'd like to see how your investment is performing."

Mickey's thumb found its familiar groove against his finger—three taps, pause, three more.
The addiction tell that survived decades of suppression.
"""


@pytest.fixture
def calibration_service(mock_agents_yaml):
    """Create a VoiceCalibrationService instance for testing."""
    with patch('backend.services.voice_calibration_service.LLMService'), \
         patch('backend.services.voice_calibration_service.get_foreman_kb_service'), \
         patch('backend.services.voice_calibration_service.Path.open', mock_open()):

        service = VoiceCalibrationService.__new__(VoiceCalibrationService)
        service.llm_service = MagicMock()
        service.kb_service = MagicMock()
        service.agents_config = mock_agents_yaml
        service._tournaments = {}

        return service


# =============================================================================
# Test Agent Configuration
# =============================================================================

class TestAgentConfiguration:
    """Tests for agent configuration and availability checking."""

    def test_get_available_agents(self, calibration_service):
        """Test getting list of available agents."""
        agents = calibration_service.get_available_agents(use_case="tournament")

        assert len(agents) == 4
        assert all(isinstance(a, AgentInfo) for a in agents)
        assert all("tournament" in a.use_cases for a in agents)

    def test_filter_agents_by_use_case(self, calibration_service):
        """Test filtering agents by use case."""
        tournament_agents = calibration_service.get_available_agents(use_case="tournament")
        enhancement_agents = calibration_service.get_available_agents(use_case="enhancement")

        assert len(tournament_agents) == 4  # All have 'tournament'
        assert len(enhancement_agents) == 1  # Only claude has 'enhancement'

    def test_api_key_validation_for_cloud_agents(self, calibration_service):
        """Test API key validation for cloud-based agents."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-ant-real-key'}):
            agent = calibration_service.agents_config['agents'][0]
            has_key = calibration_service._check_api_key_valid(agent)
            assert has_key is True

        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-xxx-placeholder'}):
            has_key = calibration_service._check_api_key_valid(agent)
            assert has_key is False

    def test_ollama_agents_dont_need_keys(self, calibration_service):
        """Test that Ollama agents are always valid (no API key needed)."""
        ollama_agent = calibration_service.agents_config['agents'][3]
        assert ollama_agent['provider'] == 'ollama'

        has_key = calibration_service._check_api_key_valid(ollama_agent)
        assert has_key is True  # Local agents don't need keys

    def test_get_ready_agents_filters_enabled_and_keyed(self, calibration_service):
        """Test that get_ready_agents only returns enabled agents with valid keys."""
        with patch.dict('os.environ', {
            'ANTHROPIC_API_KEY': 'sk-ant-valid',
            'OPENAI_API_KEY': 'sk-openai-valid',
        }):
            ready_agents = calibration_service.get_ready_agents(use_case="tournament")

            # Should have: claude (enabled+key), gpt-4o (enabled+key), llama (enabled+no key needed)
            # Should NOT have: deepseek (disabled)
            assert len(ready_agents) == 3
            assert all(a.enabled for a in ready_agents)
            assert all(a.has_valid_key for a in ready_agents)

            agent_ids = [a.id for a in ready_agents]
            assert 'claude-sonnet-4' in agent_ids
            assert 'gpt-4o' in agent_ids
            assert 'llama3-local' in agent_ids
            assert 'deepseek-chat' not in agent_ids  # Disabled


# =============================================================================
# Test Tournament Execution
# =============================================================================

class TestTournamentExecution:
    """Tests for tournament creation and variant generation."""

    @pytest.mark.asyncio
    async def test_start_tournament_creates_tournament_result(
        self,
        calibration_service,
        mock_test_prompt,
        mock_test_context
    ):
        """Test that starting a tournament creates a TournamentResult."""
        result = await calibration_service.start_tournament(
            project_id="test_project",
            test_prompt=mock_test_prompt,
            test_context=mock_test_context,
            agent_ids=['claude-sonnet-4', 'gpt-4o'],
            variants_per_agent=5,
        )

        assert isinstance(result, TournamentResult)
        assert result.project_id == "test_project"
        assert result.status == TournamentStatus.RUNNING
        assert result.selected_agents == ['claude-sonnet-4', 'gpt-4o']
        assert result.test_prompt == mock_test_prompt

    @pytest.mark.asyncio
    async def test_tournament_generates_variants_from_all_agents(
        self,
        calibration_service,
        mock_test_prompt,
        mock_test_context,
        mock_winning_variant
    ):
        """Test that tournament generates 5 variants from each agent."""
        # Mock LLM responses
        calibration_service.llm_service.generate_response = AsyncMock(
            return_value=mock_winning_variant
        )

        # Create tournament result
        result = TournamentResult(
            tournament_id="test_tournament_001",
            project_id="test_project",
            test_prompt=mock_test_prompt,
            test_context=mock_test_context,
            status=TournamentStatus.RUNNING,
            selected_agents=['claude-sonnet-4', 'gpt-4o'],
        )

        # Run tournament
        await calibration_service._run_tournament(
            result,
            variants_per_agent=5,
            voice_description="Test voice",
        )

        # Should have 2 agents × 5 variants = 10 variants
        assert len(result.variants) == 10
        assert result.status == TournamentStatus.AWAITING_SELECTION

    @pytest.mark.asyncio
    async def test_variant_generation_uses_strategy(
        self,
        calibration_service,
        mock_winning_variant
    ):
        """Test that each variant uses a different strategy."""
        agent_config = {
            'id': 'claude-sonnet-4',
            'name': 'Claude Sonnet 4',
            'provider': 'anthropic',
            'model': 'claude-sonnet-4-20250514',
        }

        calibration_service.llm_service.generate_response = AsyncMock(
            return_value=mock_winning_variant
        )

        variant = await calibration_service._generate_variant(
            agent_config=agent_config,
            system_prompt="System prompt",
            test_prompt="Test prompt",
            strategy_name="ACTION_EMPHASIS",
            strategy_desc="Fast pacing, physical detail",
            variant_number=1,
        )

        assert isinstance(variant, VoiceVariant)
        assert variant.agent_id == 'claude-sonnet-4'
        assert variant.strategy == "ACTION_EMPHASIS"
        assert variant.variant_number == 1
        assert variant.word_count > 0

    @pytest.mark.asyncio
    async def test_tournament_handles_agent_failures_gracefully(
        self,
        calibration_service,
        mock_test_prompt,
        mock_test_context
    ):
        """Test that tournament continues even if some agents fail."""
        # Mock one success and one failure
        async def mock_generate(*args, **kwargs):
            if 'claude' in str(kwargs):
                return "Valid response"
            else:
                raise Exception("API error")

        calibration_service.llm_service.generate_response = mock_generate

        result = TournamentResult(
            tournament_id="test_tournament_002",
            project_id="test_project",
            test_prompt=mock_test_prompt,
            test_context=mock_test_context,
            status=TournamentStatus.RUNNING,
            selected_agents=['claude-sonnet-4', 'gpt-4o'],
        )

        await calibration_service._run_tournament(
            result,
            variants_per_agent=2,
            voice_description=None,
        )

        # Should have some variants from claude, none from gpt-4o
        assert len(result.variants) < 4  # Less than 2 agents × 2 variants
        assert result.status == TournamentStatus.AWAITING_SELECTION

    def test_variant_strategies_count(self, calibration_service):
        """Test that exactly 5 variant strategies are defined."""
        assert len(calibration_service.VARIANT_STRATEGIES) == 5

        strategies = [s[0] for s in calibration_service.VARIANT_STRATEGIES]
        assert "ACTION_EMPHASIS" in strategies
        assert "CHARACTER_DEPTH" in strategies
        assert "DIALOGUE_FOCUS" in strategies
        assert "BRAINSTORMING" in strategies
        assert "BALANCED" in strategies


# =============================================================================
# Test Tournament Selection
# =============================================================================

class TestTournamentSelection:
    """Tests for winner selection and voice document generation."""

    @pytest.mark.asyncio
    async def test_select_winner_creates_voice_document(
        self,
        calibration_service,
        mock_winning_variant
    ):
        """Test that selecting winner creates VoiceCalibrationDocument."""
        # Create tournament with variants
        result = TournamentResult(
            tournament_id="test_tournament_003",
            project_id="test_project",
            test_prompt="Test prompt",
            test_context="Test context",
            status=TournamentStatus.AWAITING_SELECTION,
            selected_agents=['claude-sonnet-4'],
            variants=[
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude Sonnet 4',
                    variant_number=1,
                    strategy='ACTION_EMPHASIS',
                    content=mock_winning_variant,
                    word_count=150,
                ),
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude Sonnet 4',
                    variant_number=2,
                    strategy='CHARACTER_DEPTH',
                    content="Another variant",
                    word_count=140,
                ),
            ],
        )

        calibration_service._tournaments["test_tournament_003"] = result
        calibration_service._store_voice_calibration = AsyncMock()

        voice_config = {
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling', 'surveillance', 'performance'],
            'sentence_rhythm': 'varied',
            'vocabulary_level': 'literary',
            'characteristic_phrases': ['quantum fatigue', 'addiction tell'],
            'anti_patterns': ['with [adjective] precision', 'like [simile]'],
            'phase_evolution': {
                'act1': 'Controlled, analytical voice',
                'act2': 'Voice fragmenting under pressure',
                'act3': 'Fully integrated wisdom',
            },
        }

        voice_doc = await calibration_service.select_winner(
            tournament_id="test_tournament_003",
            winner_agent_id='claude-sonnet-4',
            winner_variant_index=0,
            voice_config=voice_config,
        )

        assert isinstance(voice_doc, VoiceCalibrationDocument)
        assert voice_doc.project_id == "test_project"
        assert voice_doc.pov == 'third_limited'
        assert voice_doc.winning_agent == 'claude-sonnet-4'
        assert voice_doc.reference_sample == mock_winning_variant
        assert 'gambling' in voice_doc.metaphor_domains
        assert 'with [adjective] precision' in voice_doc.anti_patterns

    @pytest.mark.asyncio
    async def test_select_winner_updates_tournament_status(
        self,
        calibration_service,
        mock_winning_variant
    ):
        """Test that selecting winner updates tournament status to COMPLETE."""
        result = TournamentResult(
            tournament_id="test_tournament_004",
            project_id="test_project",
            test_prompt="Test",
            test_context="Context",
            status=TournamentStatus.AWAITING_SELECTION,
            selected_agents=['claude-sonnet-4'],
            variants=[
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude',
                    variant_number=1,
                    strategy='BALANCED',
                    content=mock_winning_variant,
                    word_count=150,
                ),
            ],
        )

        calibration_service._tournaments["test_tournament_004"] = result
        calibration_service._store_voice_calibration = AsyncMock()

        await calibration_service.select_winner(
            tournament_id="test_tournament_004",
            winner_agent_id='claude-sonnet-4',
            winner_variant_index=0,
            voice_config={'pov': 'third_limited', 'tense': 'past', 'voice_type': 'character_voice'},
        )

        assert result.status == TournamentStatus.COMPLETE
        assert result.winner_agent_id == 'claude-sonnet-4'
        assert result.winner_variant_index == 0
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_select_winner_rejects_invalid_tournament(self, calibration_service):
        """Test that selecting winner fails for invalid tournament ID."""
        with pytest.raises(ValueError, match="Tournament .* not found"):
            await calibration_service.select_winner(
                tournament_id="nonexistent_tournament",
                winner_agent_id='claude-sonnet-4',
                winner_variant_index=0,
                voice_config={},
            )

    @pytest.mark.asyncio
    async def test_select_winner_rejects_wrong_status(self, calibration_service):
        """Test that selecting winner fails if tournament not ready."""
        result = TournamentResult(
            tournament_id="test_tournament_005",
            project_id="test_project",
            test_prompt="Test",
            test_context="Context",
            status=TournamentStatus.RUNNING,  # Still running, not ready
            selected_agents=['claude-sonnet-4'],
        )

        calibration_service._tournaments["test_tournament_005"] = result

        with pytest.raises(ValueError, match="not ready for selection"):
            await calibration_service.select_winner(
                tournament_id="test_tournament_005",
                winner_agent_id='claude-sonnet-4',
                winner_variant_index=0,
                voice_config={},
            )

    @pytest.mark.asyncio
    async def test_select_winner_rejects_invalid_variant_index(
        self,
        calibration_service,
        mock_winning_variant
    ):
        """Test that selecting winner fails for invalid variant index."""
        result = TournamentResult(
            tournament_id="test_tournament_006",
            project_id="test_project",
            test_prompt="Test",
            test_context="Context",
            status=TournamentStatus.AWAITING_SELECTION,
            selected_agents=['claude-sonnet-4'],
            variants=[
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude',
                    variant_number=1,
                    strategy='BALANCED',
                    content=mock_winning_variant,
                    word_count=150,
                ),
            ],
        )

        calibration_service._tournaments["test_tournament_006"] = result

        with pytest.raises(ValueError, match="Invalid winner selection"):
            await calibration_service.select_winner(
                tournament_id="test_tournament_006",
                winner_agent_id='claude-sonnet-4',
                winner_variant_index=99,  # Out of range
                voice_config={},
            )


# =============================================================================
# Test Voice Bundle Generation
# =============================================================================

class TestVoiceBundleGeneration:
    """Tests for Voice Reference Bundle file generation."""

    @pytest.mark.asyncio
    async def test_generate_voice_bundle_creates_all_files(
        self,
        calibration_service,
        tmp_path,
        mock_winning_variant
    ):
        """Test that generate_voice_bundle creates all required files."""
        voice_doc = {
            'project_id': 'test_project',
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling', 'surveillance'],
            'sentence_rhythm': 'varied',
            'vocabulary_level': 'literary',
            'characteristic_phrases': ['quantum fatigue'],
            'anti_patterns': ['with precision'],
            'phase_evolution': {'act1': 'Controlled'},
            'winning_agent': 'claude-sonnet-4',
            'reference_sample': mock_winning_variant,
        }

        calibration_service.kb_service.get = AsyncMock(
            return_value=json.dumps(voice_doc)
        )

        files = await calibration_service.generate_voice_bundle(
            project_id='test_project',
            output_dir=tmp_path,
        )

        assert 'gold_standard' in files
        assert 'anti_patterns' in files
        assert 'phase_evolution' in files

        assert files['gold_standard'].exists()
        assert files['anti_patterns'].exists()
        assert files['phase_evolution'].exists()

    def test_gold_standard_file_format(self, calibration_service, mock_winning_variant):
        """Test that gold standard file has correct format."""
        voice_doc = {
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling', 'surveillance'],
            'sentence_rhythm': 'varied',
            'vocabulary_level': 'literary',
            'characteristic_phrases': ['quantum fatigue'],
            'winning_agent': 'claude-sonnet-4',
            'reference_sample': mock_winning_variant,
        }

        content = calibration_service._generate_gold_standard(voice_doc)

        assert "# Voice Gold Standard" in content
        assert "Third Limited" in content  # POV
        assert "Past" in content  # Tense
        assert "gambling" in content
        assert "surveillance" in content
        assert mock_winning_variant in content
        assert "Authenticity Test" in content
        assert "Purpose Test" in content
        assert "Fusion Test" in content

    def test_anti_pattern_sheet_format(self, calibration_service):
        """Test that anti-pattern sheet has correct format."""
        voice_doc = {
            'anti_patterns': [
                'with [adjective] precision',
                'like [simile]',
                'as if [clause]',
            ],
        }

        content = calibration_service._generate_anti_pattern_sheet(voice_doc)

        assert "# Voice Anti-Pattern Sheet" in content
        assert "with [adjective] precision" in content
        assert "like [simile]" in content
        assert "## Universal AI Anti-Patterns" in content
        assert "crucial" in content  # Universal AI vocabulary
        assert "nestled" in content  # Promotional puffery
        assert "Zero-Tolerance Violations" in content

    def test_phase_evolution_guide_format(self, calibration_service):
        """Test that phase evolution guide has correct format."""
        voice_doc = {
            'phase_evolution': {
                'act1': 'Controlled, analytical voice with tight metaphors',
                'act2': 'Voice fragmenting under quantum pressure',
                'act3': 'Fully integrated quantum hindsight wisdom',
            },
        }

        content = calibration_service._generate_phase_guide(voice_doc)

        assert "# Phase Evolution Guide" in content
        assert "act1" in content
        assert "act2" in content
        assert "act3" in content
        assert "Controlled, analytical" in content
        assert "fragmenting under quantum" in content

    @pytest.mark.asyncio
    async def test_voice_bundle_without_phase_evolution(
        self,
        calibration_service,
        tmp_path,
        mock_winning_variant
    ):
        """Test that voice bundle works without phase evolution."""
        voice_doc = {
            'project_id': 'test_project',
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling'],
            'sentence_rhythm': 'varied',
            'vocabulary_level': 'literary',
            'characteristic_phrases': [],
            'anti_patterns': [],
            'phase_evolution': {},  # Empty
            'winning_agent': 'claude-sonnet-4',
            'reference_sample': mock_winning_variant,
        }

        calibration_service.kb_service.get = AsyncMock(
            return_value=json.dumps(voice_doc)
        )

        files = await calibration_service.generate_voice_bundle(
            project_id='test_project',
            output_dir=tmp_path,
        )

        # Should still create files even without phase evolution
        assert 'gold_standard' in files
        assert 'anti_patterns' in files


# =============================================================================
# Test Knowledge Base Storage
# =============================================================================

class TestKnowledgeBaseStorage:
    """Tests for storing voice calibration in KB."""

    @pytest.mark.asyncio
    async def test_stores_voice_calibration_in_kb(
        self,
        calibration_service,
        mock_winning_variant
    ):
        """Test that voice calibration is stored in KB with all components."""
        voice_doc = VoiceCalibrationDocument(
            project_id='test_project',
            pov='third_limited',
            tense='past',
            voice_type='character_voice',
            metaphor_domains=['gambling', 'surveillance'],
            sentence_rhythm='varied',
            vocabulary_level='literary',
            characteristic_phrases=['quantum fatigue'],
            anti_patterns=['with precision'],
            phase_evolution={'act1': 'Controlled'},
            winning_agent='claude-sonnet-4',
            reference_sample=mock_winning_variant,
        )

        calibration_service.kb_service.set = AsyncMock()

        await calibration_service._store_voice_calibration(
            project_id='test_project',
            voice_doc=voice_doc,
        )

        # Should store multiple KB entries
        assert calibration_service.kb_service.set.call_count >= 6

        # Check that main document was stored
        calls = calibration_service.kb_service.set.call_args_list
        main_call = next(c for c in calls if c[1]['key'] == 'voice_calibration')
        assert main_call is not None
        assert main_call[1]['category'] == 'voice'


# =============================================================================
# Test Tournament Status and Variants
# =============================================================================

class TestTournamentStatus:
    """Tests for tournament status tracking and variant retrieval."""

    def test_get_tournament_status(self, calibration_service):
        """Test retrieving tournament status."""
        result = TournamentResult(
            tournament_id="test_tournament_007",
            project_id="test_project",
            test_prompt="Test",
            test_context="Context",
            status=TournamentStatus.RUNNING,
            selected_agents=['claude-sonnet-4'],
        )

        calibration_service._tournaments["test_tournament_007"] = result

        status = calibration_service.get_tournament_status("test_tournament_007")

        assert status is not None
        assert status.tournament_id == "test_tournament_007"
        assert status.status == TournamentStatus.RUNNING

    def test_get_tournament_variants(self, calibration_service, mock_winning_variant):
        """Test retrieving tournament variants."""
        result = TournamentResult(
            tournament_id="test_tournament_008",
            project_id="test_project",
            test_prompt="Test",
            test_context="Context",
            status=TournamentStatus.AWAITING_SELECTION,
            selected_agents=['claude-sonnet-4', 'gpt-4o'],
            variants=[
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude',
                    variant_number=1,
                    strategy='ACTION_EMPHASIS',
                    content=mock_winning_variant,
                    word_count=150,
                ),
                VoiceVariant(
                    agent_id='gpt-4o',
                    agent_name='GPT-4o',
                    variant_number=1,
                    strategy='CHARACTER_DEPTH',
                    content="GPT variant",
                    word_count=140,
                ),
                VoiceVariant(
                    agent_id='claude-sonnet-4',
                    agent_name='Claude',
                    variant_number=2,
                    strategy='DIALOGUE_FOCUS',
                    content="Claude variant 2",
                    word_count=145,
                ),
            ],
        )

        calibration_service._tournaments["test_tournament_008"] = result

        # Get all variants
        all_variants = calibration_service.get_tournament_variants("test_tournament_008")
        assert len(all_variants) == 3

        # Get claude variants only
        claude_variants = calibration_service.get_tournament_variants(
            "test_tournament_008",
            agent_id='claude-sonnet-4'
        )
        assert len(claude_variants) == 2
        assert all(v.agent_id == 'claude-sonnet-4' for v in claude_variants)


# =============================================================================
# Test Integration Scenarios
# =============================================================================

class TestIntegrationScenarios:
    """Tests for complete voice calibration workflows."""

    @pytest.mark.asyncio
    async def test_complete_tournament_workflow(
        self,
        calibration_service,
        mock_test_prompt,
        mock_test_context,
        mock_winning_variant
    ):
        """Test complete tournament workflow from start to winner selection."""
        # Mock LLM responses
        calibration_service.llm_service.generate_response = AsyncMock(
            return_value=mock_winning_variant
        )
        calibration_service._store_voice_calibration = AsyncMock()

        # Step 1: Start tournament
        result = await calibration_service.start_tournament(
            project_id="integration_test",
            test_prompt=mock_test_prompt,
            test_context=mock_test_context,
            agent_ids=['claude-sonnet-4'],
            variants_per_agent=3,
            voice_description="Test voice",
        )

        assert result.status == TournamentStatus.RUNNING

        # Step 2: Wait for tournament to complete (simulate)
        await calibration_service._run_tournament(result, 3, "Test voice")

        assert result.status == TournamentStatus.AWAITING_SELECTION
        assert len(result.variants) == 3

        # Step 3: Select winner
        voice_config = {
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling'],
            'anti_patterns': [],
            'phase_evolution': {},
        }

        voice_doc = await calibration_service.select_winner(
            tournament_id=result.tournament_id,
            winner_agent_id='claude-sonnet-4',
            winner_variant_index=0,
            voice_config=voice_config,
        )

        assert result.status == TournamentStatus.COMPLETE
        assert voice_doc.winning_agent == 'claude-sonnet-4'
        assert voice_doc.reference_sample == mock_winning_variant

    @pytest.mark.asyncio
    async def test_complete_voice_bundle_generation_workflow(
        self,
        calibration_service,
        tmp_path,
        mock_winning_variant
    ):
        """Test complete workflow from tournament to voice bundle files."""
        voice_doc = {
            'project_id': 'bundle_test',
            'pov': 'third_limited',
            'tense': 'past',
            'voice_type': 'character_voice',
            'metaphor_domains': ['gambling', 'surveillance', 'performance'],
            'sentence_rhythm': 'varied',
            'vocabulary_level': 'literary',
            'characteristic_phrases': ['quantum fatigue', 'addiction tell'],
            'anti_patterns': ['with [adjective] precision', 'like [simile]'],
            'phase_evolution': {
                'act1': 'Controlled, analytical',
                'act2': 'Fragmenting under pressure',
                'act3': 'Integrated wisdom',
            },
            'winning_agent': 'claude-sonnet-4',
            'reference_sample': mock_winning_variant,
        }

        calibration_service.kb_service.get = AsyncMock(
            return_value=json.dumps(voice_doc)
        )

        # Generate voice bundle
        files = await calibration_service.generate_voice_bundle(
            project_id='bundle_test',
            output_dir=tmp_path,
        )

        # Verify all files exist and have content
        assert files['gold_standard'].exists()
        assert files['anti_patterns'].exists()
        assert files['phase_evolution'].exists()

        gold_content = files['gold_standard'].read_text()
        assert "gambling" in gold_content
        assert "surveillance" in gold_content
        assert mock_winning_variant in gold_content

        anti_content = files['anti_patterns'].read_text()
        assert "with [adjective] precision" in anti_content
        assert "crucial" in anti_content  # Universal AI patterns

        phase_content = files['phase_evolution'].read_text()
        assert "act1" in phase_content
        assert "Controlled, analytical" in phase_content
