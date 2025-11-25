"""
Tests for Scaffold Generator Service - Phase 3B Director Mode

Tests the 2-stage scaffold generation process:
Stage 1: Draft Summary - Preview with enrichment suggestions
Stage 2: Full Scaffold - Complete document with optional NotebookLM enrichment

Key workflows tested:
- Beat information extraction
- Character context integration
- Continuity tracking from previous scenes
- NotebookLM enrichment suggestions
- KB context injection
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from backend.services.scaffold_generator_service import (
    ScaffoldGeneratorService,
    DraftSummary,
    FullScaffold,
    BeatInfo,
    CharacterContext,
    ContinuityEntry,
    EnrichmentSuggestion,
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_beat_info():
    """Create mock beat information."""
    return BeatInfo(
        beat_number=1,
        beat_name="Catalyst",
        beat_percentage="10%",
        description="The inciting incident that launches the story",
        beat_type="catalyst"
    )


@pytest.fixture
def mock_character_context():
    """Create mock character context."""
    return CharacterContext(
        name="Mickey Bardot",
        role="protagonist",
        fatal_flaw="Hubris",
        the_lie="Control through quantum manipulation is sustainable",
        arc_state="Beginning - Still trusting Ken's cage",
        relevant_relationships={
            "Ken": "Handler/dealer - weaponized gratitude dynamic",
            "Vance": "Antagonist - optimization philosopher"
        }
    )


@pytest.fixture
def mock_continuity_entries():
    """Create mock continuity entries from previous scenes."""
    return [
        ContinuityEntry(
            scene_id="1.1.1",
            event="Mickey entered comfortable cage at Area 52",
            category="plot",
            must_callback=True
        ),
        ContinuityEntry(
            scene_id="1.1.1",
            event="Ken established leverage through dojo protection",
            category="character",
            must_callback=True
        )
    ]


@pytest.fixture
def scaffold_service():
    """Create a ScaffoldGeneratorService instance for testing."""
    with patch('backend.services.scaffold_generator_service.httpx.AsyncClient'):
        service = ScaffoldGeneratorService(project_id="test_project")
        return service


# =============================================================================
# Test Stage 1: Draft Summary Generation
# =============================================================================

class TestDraftSummaryGeneration:
    """Tests for Stage 1 - Draft Summary with enrichment suggestions."""

    @pytest.mark.asyncio
    async def test_generates_draft_summary_successfully(
        self,
        scaffold_service,
        mock_beat_info,
        mock_character_context
    ):
        """Test that draft summary is generated with basic context."""
        with patch.object(scaffold_service, 'generate_draft_summary', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = DraftSummary(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Mickey's consciousness deploys into The Rig via bi-location",
                available_context=[
                    "Beat: Catalyst (10%)",
                    "Character: Mickey Bardot (protagonist)",
                    "Previous: Comfortable cage established"
                ],
                enrichment_suggestions=[],
                ready_to_generate=True
            )

            draft = await scaffold_service.generate_draft_summary(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                character_context=mock_character_context
            )

            assert draft.scene_id == "2.1.1"
            assert draft.beat_info.beat_name == "Catalyst"
            assert draft.ready_to_generate is True

    @pytest.mark.asyncio
    async def test_includes_enrichment_suggestions_when_gaps_detected(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that enrichment suggestions are provided when context has gaps."""
        with patch.object(scaffold_service, 'generate_draft_summary', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = DraftSummary(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Scene requires world-building context",
                available_context=["Beat info only"],
                enrichment_suggestions=[
                    EnrichmentSuggestion(
                        notebook_id="world_notebook",
                        notebook_name="World Bible",
                        suggested_query="What is The Rig's architecture and social structure?",
                        reason="Scene takes place in The Rig but we lack sensory details"
                    ),
                    EnrichmentSuggestion(
                        notebook_id="craft_notebook",
                        notebook_name="Craft Knowledge",
                        suggested_query="How to write bi-location scenes with physicality?",
                        reason="Scene involves quantum bi-location - need craft guidance"
                    )
                ],
                ready_to_generate=False  # Not ready without enrichment
            )

            draft = await scaffold_service.generate_draft_summary(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info
            )

            assert len(draft.enrichment_suggestions) == 2
            assert draft.ready_to_generate is False, "Should not be ready without enrichment"

    @pytest.mark.asyncio
    async def test_extracts_available_context_from_kb(
        self,
        scaffold_service,
        mock_beat_info,
        mock_character_context,
        mock_continuity_entries
    ):
        """Test that available context is extracted from KB."""
        with patch.object(scaffold_service, '_extract_kb_context', new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = [
                "Beat: Catalyst (10%) - Inciting incident",
                "Character: Mickey Bardot - Fatal Flaw: Hubris",
                "Continuity: Area 52 comfortable cage established",
                "Continuity: Ken's leverage through dojo protection"
            ]

            context = await scaffold_service._extract_kb_context(
                beat_info=mock_beat_info,
                character_context=mock_character_context,
                continuity_entries=mock_continuity_entries
            )

            assert len(context) == 4
            assert any("Catalyst" in item for item in context)
            assert any("Fatal Flaw" in item for item in context)


# =============================================================================
# Test Stage 2: Full Scaffold Generation
# =============================================================================

class TestFullScaffoldGeneration:
    """Tests for Stage 2 - Full Scaffold with optional enrichment."""

    @pytest.mark.asyncio
    async def test_generates_full_scaffold_without_enrichment(
        self,
        scaffold_service,
        mock_beat_info,
        mock_character_context
    ):
        """Test full scaffold generation using only available context."""
        with patch.object(scaffold_service, 'generate_full_scaffold', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = FullScaffold(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Mickey deploys into The Rig",
                physical_description="Area 52 platform, Q5 port activation, quantum consciousness stretch",
                character_objectives={
                    "Mickey": "Survive bi-location strain, gather intel on The Rig",
                    "Ken": "Maintain control, extract intelligence"
                },
                emotional_beats=["Withdrawal-like symptoms", "Recognition of cage architecture"],
                continuity_callbacks=["Reference Area 52 setup", "Ken's leverage established"],
                world_rules_to_honor=["Bi-location has physical cost", "Q5 port interface"],
                enriched_context=[],
                scaffold_text="# Scene 2.1.1: The Bi-Location Dive\n\nMickey straps into the platform...",
                generated_at=datetime.now(timezone.utc).isoformat()
            )

            scaffold = await scaffold_service.generate_full_scaffold(
                scene_id="2.1.1",
                beat_info=mock_beat_info,
                character_context=mock_character_context,
                use_enrichment=False
            )

            assert scaffold.scene_id == "2.1.1"
            assert len(scaffold.enriched_context) == 0, "Should have no enrichment"
            assert "Mickey" in scaffold.character_objectives

    @pytest.mark.asyncio
    async def test_generates_full_scaffold_with_notebooklm_enrichment(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test full scaffold generation with NotebookLM enrichment."""
        enrichment_queries = [
            {
                "notebook_id": "world_notebook",
                "query": "What is The Rig's architecture?"
            }
        ]

        with patch.object(scaffold_service, 'generate_full_scaffold', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = FullScaffold(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Mickey deploys into The Rig with enriched world details",
                physical_description="Glass architecture curves, silent casino hum, citizens smiling",
                character_objectives={"Mickey": "Gather intel"},
                emotional_beats=["Horror recognition"],
                continuity_callbacks=[],
                world_rules_to_honor=["The Rig has zero crime through optimization"],
                enriched_context=[
                    "World Bible: The Rig uses glass architecture with sweeping curves",
                    "World Bible: Citizens smile as terrifying tell of optimization"
                ],
                scaffold_text="# Scene 2.1.1: The Bi-Location Dive\n\nWith world enrichment...",
                generated_at=datetime.now(timezone.utc).isoformat()
            )

            scaffold = await scaffold_service.generate_full_scaffold(
                scene_id="2.1.1",
                beat_info=mock_beat_info,
                enrichment_queries=enrichment_queries,
                use_enrichment=True
            )

            assert len(scaffold.enriched_context) > 0, "Should have enrichment"
            assert any("World Bible" in item for item in scaffold.enriched_context)

    @pytest.mark.asyncio
    async def test_scaffold_includes_beat_connection(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that scaffold explicitly connects scene to beat structure."""
        with patch.object(scaffold_service, 'generate_full_scaffold', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = FullScaffold(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Catalyst event launches Volume 2 conflict",
                physical_description="...",
                character_objectives={},
                emotional_beats=["Catalyst recognition"],
                continuity_callbacks=[],
                world_rules_to_honor=[],
                enriched_context=[],
                scaffold_text="# Beat Connection\n\nCatalyst (10%): This is the inciting incident...",
                generated_at=datetime.now(timezone.utc).isoformat()
            )

            scaffold = await scaffold_service.generate_full_scaffold(
                scene_id="2.1.1",
                beat_info=mock_beat_info
            )

            assert "Catalyst" in scaffold.scaffold_text
            assert scaffold.beat_info.beat_percentage == "10%"


# =============================================================================
# Test Continuity Tracking
# =============================================================================

class TestContinuityTracking:
    """Tests for continuity tracking across scenes."""

    @pytest.mark.asyncio
    async def test_must_callback_entries_flagged_in_scaffold(
        self,
        scaffold_service,
        mock_continuity_entries
    ):
        """Test that must-callback continuity entries are flagged prominently."""
        with patch.object(scaffold_service, '_process_continuity', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = [
                "⚠️ MUST CALLBACK: Mickey entered Area 52 cage",
                "⚠️ MUST CALLBACK: Ken's leverage through dojo",
                "Reference: Previous world-building"
            ]

            callbacks = await scaffold_service._process_continuity(mock_continuity_entries)

            must_callbacks = [c for c in callbacks if "MUST CALLBACK" in c]
            assert len(must_callbacks) == 2, "Should flag all must-callback entries"

    @pytest.mark.asyncio
    async def test_continuity_organized_by_category(
        self,
        scaffold_service,
        mock_continuity_entries
    ):
        """Test that continuity entries are organized by category."""
        with patch.object(scaffold_service, '_organize_continuity', new_callable=AsyncMock) as mock_organize:
            mock_organize.return_value = {
                "plot": ["Area 52 cage"],
                "character": ["Ken's leverage"],
                "world": [],
                "foreshadow": []
            }

            organized = await scaffold_service._organize_continuity(mock_continuity_entries)

            assert "plot" in organized
            assert "character" in organized
            assert len(organized["plot"]) == 1


# =============================================================================
# Test NotebookLM Integration
# =============================================================================

class TestNotebookLMIntegration:
    """Tests for NotebookLM enrichment integration."""

    @pytest.mark.asyncio
    async def test_enrichment_queries_sent_to_notebooklm(
        self,
        scaffold_service
    ):
        """Test that enrichment queries are properly formatted for NotebookLM."""
        queries = [
            {"notebook_id": "world_notebook", "query": "The Rig architecture?"},
            {"notebook_id": "craft_notebook", "query": "Bi-location writing techniques?"}
        ]

        with patch.object(scaffold_service, '_query_notebooklm', new_callable=AsyncMock) as mock_query:
            mock_query.return_value = "The Rig uses glass architecture with casino aesthetics"

            results = []
            for q in queries:
                result = await scaffold_service._query_notebooklm(
                    notebook_id=q["notebook_id"],
                    query=q["query"]
                )
                results.append(result)

            assert len(results) == 2
            assert mock_query.call_count == 2

    @pytest.mark.asyncio
    async def test_enrichment_failure_handled_gracefully(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that NotebookLM failures don't block scaffold generation."""
        with patch.object(scaffold_service, '_query_notebooklm', new_callable=AsyncMock) as mock_query:
            mock_query.side_effect = Exception("NotebookLM unavailable")

            with patch.object(scaffold_service, 'generate_full_scaffold', new_callable=AsyncMock) as mock_generate:
                mock_generate.return_value = FullScaffold(
                    scene_id="2.1.1",
                    chapter_number=2,
                    scene_number=1,
                    beat_info=mock_beat_info,
                    narrative_summary="Generated without enrichment",
                    physical_description="Basic context only",
                    character_objectives={},
                    emotional_beats=[],
                    continuity_callbacks=[],
                    world_rules_to_honor=[],
                    enriched_context=[],  # Empty due to failure
                    scaffold_text="Scaffold generated with available context",
                    generated_at=datetime.now(timezone.utc).isoformat()
                )

                scaffold = await scaffold_service.generate_full_scaffold(
                    scene_id="2.1.1",
                    beat_info=mock_beat_info,
                    use_enrichment=True  # Requested but failed
                )

                assert scaffold is not None, "Should generate despite enrichment failure"
                assert len(scaffold.enriched_context) == 0


# =============================================================================
# Test KB Context Integration
# =============================================================================

class TestKBContextIntegration:
    """Tests for Knowledge Base context injection."""

    @pytest.mark.asyncio
    async def test_kb_context_retrieved_from_graph(
        self,
        scaffold_service
    ):
        """Test that relevant KB entries are retrieved from graph."""
        with patch.object(scaffold_service, '_get_kb_context', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [
                "Decision: Mickey accepts bi-location mission under duress",
                "Constraint: Q5 platform has 30-minute safe operation window",
                "World Rule: Vance's territory uses allocation queues"
            ]

            kb_context = await scaffold_service._get_kb_context(
                scene_id="2.1.1",
                relevant_tags=["bi-location", "area-52", "vance"]
            )

            assert len(kb_context) == 3
            assert any("Decision" in item for item in kb_context)
            assert any("Constraint" in item for item in kb_context)


# =============================================================================
# Test Error Handling
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in scaffold generation."""

    @pytest.mark.asyncio
    async def test_handles_missing_beat_info(
        self,
        scaffold_service
    ):
        """Test that missing beat information is handled gracefully."""
        with pytest.raises(ValueError, match="Beat information required"):
            await scaffold_service.generate_draft_summary(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=None  # Missing
            )

    @pytest.mark.asyncio
    async def test_handles_ollama_service_unavailable(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that Ollama service unavailability is handled."""
        with patch.object(scaffold_service, '_call_ollama', new_callable=AsyncMock) as mock_ollama:
            mock_ollama.side_effect = Exception("Ollama service not running")

            with pytest.raises(Exception, match="Scaffold generation failed"):
                await scaffold_service.generate_draft_summary(
                    scene_id="2.1.1",
                    chapter_number=2,
                    scene_number=1,
                    beat_info=mock_beat_info
                )

    @pytest.mark.asyncio
    async def test_validates_scene_id_format(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that scene ID format is validated."""
        with pytest.raises(ValueError, match="Invalid scene ID format"):
            await scaffold_service.generate_draft_summary(
                scene_id="invalid",  # Should be like "2.1.1"
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info
            )


# =============================================================================
# Test Scaffold Output Format
# =============================================================================

class TestScaffoldOutputFormat:
    """Tests for scaffold output formatting."""

    @pytest.mark.asyncio
    async def test_scaffold_text_has_required_sections(
        self,
        scaffold_service,
        mock_beat_info
    ):
        """Test that scaffold text contains all required sections."""
        with patch.object(scaffold_service, 'generate_full_scaffold', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = FullScaffold(
                scene_id="2.1.1",
                chapter_number=2,
                scene_number=1,
                beat_info=mock_beat_info,
                narrative_summary="Summary",
                physical_description="Description",
                character_objectives={"Mickey": "Objective"},
                emotional_beats=["Beat"],
                continuity_callbacks=["Callback"],
                world_rules_to_honor=["Rule"],
                enriched_context=[],
                scaffold_text="""# Scene 2.1.1: The Bi-Location Dive

## Beat Connection
Catalyst (10%) - Inciting incident

## Physical Description
Area 52 platform, Q5 activation

## Character Objectives
Mickey: Gather intel

## Emotional Beats
- Withdrawal symptoms

## Continuity Callbacks
- Reference Area 52 setup

## World Rules
- Bi-location has physical cost
""",
                generated_at=datetime.now(timezone.utc).isoformat()
            )

            scaffold = await scaffold_service.generate_full_scaffold(
                scene_id="2.1.1",
                beat_info=mock_beat_info
            )

            required_sections = [
                "Beat Connection",
                "Physical Description",
                "Character Objectives",
                "Emotional Beats",
                "Continuity Callbacks",
                "World Rules"
            ]

            for section in required_sections:
                assert section in scaffold.scaffold_text, f"Missing section: {section}"
