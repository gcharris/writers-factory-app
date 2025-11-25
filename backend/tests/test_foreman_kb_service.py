"""
Tests for ForemanKBService - Persistent Decision Storage

This service manages the Foreman's Knowledge Base - crystallized decisions
from creative conversations that persist across sessions.

Architecture:
- SQLite for immediate writes (survives crashes)
- Consolidator promotes "hard facts" to knowledge_graph.json
- Separates "soft" decisions from "hard" facts

Test Coverage:
- Save decisions (create and update)
- Retrieve decisions (by project, category, promotion status)
- Mark decisions as promoted (for Consolidator)
- Context generation for Foreman prompts (foundational vs volatile)
- Project KB deletion
- Statistics and reporting
- Category-aware context (character/constraint always included)
"""

import pytest
from datetime import datetime
from typing import List

from backend.services.foreman_kb_service import (
    ForemanKBService,
    ForemanKBEntry,
    KBSessionLocal,
)

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def kb_service():
    """Create ForemanKBService instance for testing."""
    service = ForemanKBService()
    yield service
    service.close()


@pytest.fixture
def clean_kb():
    """Clean the KB database before each test."""
    db = KBSessionLocal()
    try:
        # Clear all entries
        db.query(ForemanKBEntry).delete()
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_decisions(kb_service, clean_kb):
    """Create sample KB entries for testing."""
    entries = [
        # Foundational - Character
        kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="mickey_fatal_flaw",
            value="Addiction to quantum perception - needs the rush of seeing probability waves collapse",
            source="Chapter 1 conversation"
        ),
        kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="mickey_the_lie",
            value="Believes he can control the addiction through willpower alone",
            source="Chapter 1 conversation"
        ),
        # Foundational - Constraint
        kb_service.save_decision(
            project_id="test_project",
            category="constraint",
            key="no_exposition_dumps",
            value="Show quantum mechanics through Mickey's sensory experience, never explain",
            source="Voice calibration"
        ),
        # Volatile - World
        kb_service.save_decision(
            project_id="test_project",
            category="world",
            key="area_51_quantum_lab",
            value="Underground facility 200 feet below surface, accessed via Q5 neural port",
            source="Chapter 2 conversation"
        ),
        # Volatile - Structure
        kb_service.save_decision(
            project_id="test_project",
            category="structure",
            key="beat_3_catalyst",
            value="Mickey discovers quantum surveillance network threatening free will",
            source="Story Bible"
        ),
        # Volatile - Preference
        kb_service.save_decision(
            project_id="test_project",
            category="preference",
            key="metaphor_domain",
            value="Primary domain: quantum/cybernetics, avoid similes",
            source="Voice calibration"
        ),
    ]
    return entries


@pytest.fixture
def multi_project_decisions(kb_service, clean_kb):
    """Create decisions for multiple projects to test isolation."""
    # Project 1
    kb_service.save_decision(
        project_id="project_1",
        category="character",
        key="protagonist_name",
        value="Alice",
        source="Setup"
    )
    kb_service.save_decision(
        project_id="project_1",
        category="world",
        key="setting",
        value="Victorian London",
        source="Setup"
    )

    # Project 2
    kb_service.save_decision(
        project_id="project_2",
        category="character",
        key="protagonist_name",
        value="Bob",
        source="Setup"
    )
    kb_service.save_decision(
        project_id="project_2",
        category="world",
        key="setting",
        value="Mars Colony",
        source="Setup"
    )

    return ["project_1", "project_2"]


# =============================================================================
# Test Save Decisions
# =============================================================================

class TestSaveDecisions:
    """Tests for saving decisions to the KB."""

    def test_save_new_decision(self, kb_service, clean_kb):
        """Test saving a new decision creates an entry."""
        entry = kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="protagonist_flaw",
            value="Pride leads to downfall",
            source="Chapter 1"
        )

        assert entry is not None
        assert entry.id is not None
        assert entry.project_id == "test_project"
        assert entry.category == "character"
        assert entry.key == "protagonist_flaw"
        assert entry.value == "Pride leads to downfall"
        assert entry.source == "Chapter 1"
        assert entry.is_promoted is False

    def test_save_decision_without_source(self, kb_service, clean_kb):
        """Test that source is optional."""
        entry = kb_service.save_decision(
            project_id="test_project",
            category="world",
            key="magic_system",
            value="Elemental magic through hand gestures"
        )

        assert entry.source is None
        assert entry.value == "Elemental magic through hand gestures"

    def test_update_existing_decision(self, kb_service, clean_kb):
        """Test that updating a decision modifies the existing entry."""
        # Create initial decision
        initial = kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="protagonist_age",
            value="25 years old",
            source="Chapter 1"
        )
        initial_id = initial.id

        # Update the same key
        updated = kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="protagonist_age",
            value="27 years old",
            source="Chapter 3 - retcon"
        )

        # Should have same ID (updated, not created)
        assert updated.id == initial_id
        assert updated.value == "27 years old"
        assert updated.source == "Chapter 3 - retcon"
        assert updated.is_promoted is False  # Reset on update

    def test_update_resets_promotion_status(self, kb_service, clean_kb):
        """Test that updating a decision resets its promotion status."""
        # Create and mark as promoted
        entry = kb_service.save_decision(
            project_id="test_project",
            category="world",
            key="setting",
            value="New York City",
            source="Initial"
        )
        kb_service.mark_promoted([entry.id])

        # Verify promoted
        promoted_entry = kb_service.db.query(ForemanKBEntry).get(entry.id)
        assert promoted_entry.is_promoted is True

        # Update the decision
        updated = kb_service.save_decision(
            project_id="test_project",
            category="world",
            key="setting",
            value="Los Angeles",
            source="Changed mind"
        )

        # Promotion status should be reset
        assert updated.is_promoted is False

    def test_save_all_category_types(self, kb_service, clean_kb):
        """Test saving decisions across all category types."""
        categories = {
            "character": "Protagonist is a rogue AI",
            "world": "Cyberpunk dystopia 2077",
            "structure": "Three-act structure with prologue",
            "constraint": "No deus ex machina endings",
            "preference": "Dark and gritty tone"
        }

        for category, value in categories.items():
            entry = kb_service.save_decision(
                project_id="test_project",
                category=category,
                key=f"test_{category}",
                value=value
            )
            assert entry.category == category
            assert entry.value == value


# =============================================================================
# Test Retrieve Decisions
# =============================================================================

class TestRetrieveDecisions:
    """Tests for retrieving decisions from the KB."""

    def test_get_decisions_for_project(self, kb_service, sample_decisions):
        """Test retrieving all decisions for a project."""
        decisions = kb_service.get_decisions(project_id="test_project")

        assert len(decisions) == 6
        keys = {d.key for d in decisions}
        assert "mickey_fatal_flaw" in keys
        assert "mickey_the_lie" in keys

    def test_get_decisions_by_category(self, kb_service, sample_decisions):
        """Test filtering decisions by category."""
        character_decisions = kb_service.get_decisions(
            project_id="test_project",
            category="character"
        )

        assert len(character_decisions) == 2
        assert all(d.category == "character" for d in character_decisions)
        keys = {d.key for d in character_decisions}
        assert "mickey_fatal_flaw" in keys
        assert "mickey_the_lie" in keys

    def test_get_decisions_ordered_by_recency(self, kb_service, sample_decisions):
        """Test that decisions are ordered newest first."""
        decisions = kb_service.get_decisions(project_id="test_project")

        # Should be in descending order (newest first)
        for i in range(len(decisions) - 1):
            assert decisions[i].created_at >= decisions[i+1].created_at

    def test_get_unpromoted_decisions(self, kb_service, sample_decisions):
        """Test retrieving only unpromoted decisions."""
        # Mark some as promoted
        first_two = sample_decisions[:2]
        kb_service.mark_promoted([e.id for e in first_two])

        # Get unpromoted only
        unpromoted = kb_service.get_unpromoted_decisions(project_id="test_project")

        assert len(unpromoted) == 4  # 6 total - 2 promoted
        assert all(not d.is_promoted for d in unpromoted)

    def test_get_decisions_include_promoted(self, kb_service, sample_decisions):
        """Test that include_promoted flag works."""
        # Mark some as promoted
        first_two = sample_decisions[:2]
        kb_service.mark_promoted([e.id for e in first_two])

        # Include promoted (default)
        with_promoted = kb_service.get_decisions(
            project_id="test_project",
            include_promoted=True
        )
        assert len(with_promoted) == 6

        # Exclude promoted
        without_promoted = kb_service.get_decisions(
            project_id="test_project",
            include_promoted=False
        )
        assert len(without_promoted) == 4

    def test_get_decisions_empty_project(self, kb_service, clean_kb):
        """Test retrieving decisions for a project with no entries."""
        decisions = kb_service.get_decisions(project_id="nonexistent_project")

        assert len(decisions) == 0


# =============================================================================
# Test Project Isolation
# =============================================================================

class TestProjectIsolation:
    """Tests for ensuring project data is properly isolated."""

    def test_decisions_isolated_by_project(self, kb_service, multi_project_decisions):
        """Test that decisions are isolated per project."""
        project_1_decisions = kb_service.get_decisions(project_id="project_1")
        project_2_decisions = kb_service.get_decisions(project_id="project_2")

        assert len(project_1_decisions) == 2
        assert len(project_2_decisions) == 2

        # Check values are correct
        p1_protagonist = [d for d in project_1_decisions if d.key == "protagonist_name"][0]
        p2_protagonist = [d for d in project_2_decisions if d.key == "protagonist_name"][0]

        assert p1_protagonist.value == "Alice"
        assert p2_protagonist.value == "Bob"

    def test_update_does_not_affect_other_projects(self, kb_service, multi_project_decisions):
        """Test that updating a decision in one project doesn't affect others."""
        # Update project_1
        kb_service.save_decision(
            project_id="project_1",
            category="character",
            key="protagonist_name",
            value="Alice Updated",
            source="Revision"
        )

        # Check project_1 updated
        p1_decisions = kb_service.get_decisions(project_id="project_1")
        p1_protagonist = [d for d in p1_decisions if d.key == "protagonist_name"][0]
        assert p1_protagonist.value == "Alice Updated"

        # Check project_2 unchanged
        p2_decisions = kb_service.get_decisions(project_id="project_2")
        p2_protagonist = [d for d in p2_decisions if d.key == "protagonist_name"][0]
        assert p2_protagonist.value == "Bob"


# =============================================================================
# Test Mark Promoted
# =============================================================================

class TestMarkPromoted:
    """Tests for marking decisions as promoted to the graph."""

    def test_mark_single_entry_promoted(self, kb_service, sample_decisions):
        """Test marking a single entry as promoted."""
        entry_id = sample_decisions[0].id

        count = kb_service.mark_promoted([entry_id])

        assert count == 1

        # Verify promotion status
        entry = kb_service.db.query(ForemanKBEntry).get(entry_id)
        assert entry.is_promoted is True

    def test_mark_multiple_entries_promoted(self, kb_service, sample_decisions):
        """Test marking multiple entries as promoted."""
        entry_ids = [e.id for e in sample_decisions[:3]]

        count = kb_service.mark_promoted(entry_ids)

        assert count == 3

        # Verify all marked
        for entry_id in entry_ids:
            entry = kb_service.db.query(ForemanKBEntry).get(entry_id)
            assert entry.is_promoted is True

    def test_mark_promoted_empty_list(self, kb_service, sample_decisions):
        """Test marking promoted with empty list."""
        count = kb_service.mark_promoted([])

        assert count == 0

    def test_mark_promoted_nonexistent_ids(self, kb_service, sample_decisions):
        """Test marking nonexistent IDs doesn't error."""
        count = kb_service.mark_promoted([99999, 99998])

        assert count == 0  # Nothing updated


# =============================================================================
# Test Context Generation
# =============================================================================

class TestContextGeneration:
    """Tests for generating context for Foreman prompts."""

    def test_get_context_with_decisions(self, kb_service, sample_decisions):
        """Test generating context string from decisions."""
        context = kb_service.get_context_for_foreman(
            project_id="test_project",
            limit=10
        )

        assert "## Known Decisions & Facts" in context
        assert "### Foundational (Always Active)" in context
        assert "mickey_fatal_flaw" in context
        assert "mickey_the_lie" in context
        assert "no_exposition_dumps" in context

    def test_context_prioritizes_foundational_categories(self, kb_service, clean_kb):
        """Test that character and constraint are always included."""
        # Create 5 character decisions and 5 world decisions
        for i in range(5):
            kb_service.save_decision(
                project_id="test_project",
                category="character",
                key=f"character_{i}",
                value=f"Character decision {i}"
            )
            kb_service.save_decision(
                project_id="test_project",
                category="world",
                key=f"world_{i}",
                value=f"World decision {i}"
            )

        # Get context with limit of 6
        context = kb_service.get_context_for_foreman(
            project_id="test_project",
            limit=6
        )

        # All 5 character decisions should be included (foundational)
        for i in range(5):
            assert f"character_{i}" in context

        # Only 1 world decision should fit (6 - 5 character = 1 slot)
        world_count = sum(1 for i in range(5) if f"world_{i}" in context)
        assert world_count == 1

    def test_context_empty_kb(self, kb_service, clean_kb):
        """Test context generation with empty KB."""
        context = kb_service.get_context_for_foreman(
            project_id="empty_project",
            limit=10
        )

        assert context == ""

    def test_context_includes_recent_volatile(self, kb_service, sample_decisions):
        """Test that recent volatile decisions are included."""
        context = kb_service.get_context_for_foreman(
            project_id="test_project",
            limit=10
        )

        # Should include volatile categories
        assert "### Recent Decisions" in context
        # Check for volatile entries
        volatile_present = any(key in context for key in [
            "area_51_quantum_lab",
            "beat_3_catalyst",
            "metaphor_domain"
        ])
        assert volatile_present

    def test_context_respects_limit(self, kb_service, clean_kb):
        """Test that context generation respects the limit parameter."""
        # Create 20 world decisions (volatile category)
        for i in range(20):
            kb_service.save_decision(
                project_id="test_project",
                category="world",
                key=f"world_{i}",
                value=f"World decision {i}"
            )

        # Get context with limit of 5
        context = kb_service.get_context_for_foreman(
            project_id="test_project",
            limit=5
        )

        # Count how many decisions are in the context
        decision_count = context.count("world_")
        assert decision_count <= 5


# =============================================================================
# Test Delete Operations
# =============================================================================

class TestDeleteOperations:
    """Tests for deleting KB entries."""

    def test_delete_project_kb(self, kb_service, sample_decisions):
        """Test deleting all KB entries for a project."""
        # Verify entries exist
        assert len(kb_service.get_decisions(project_id="test_project")) == 6

        # Delete all
        count = kb_service.delete_project_kb(project_id="test_project")

        assert count == 6

        # Verify all deleted
        assert len(kb_service.get_decisions(project_id="test_project")) == 0

    def test_delete_project_kb_isolated(self, kb_service, multi_project_decisions):
        """Test that deleting one project doesn't affect others."""
        # Delete project_1
        count = kb_service.delete_project_kb(project_id="project_1")

        assert count == 2

        # Verify project_1 deleted
        assert len(kb_service.get_decisions(project_id="project_1")) == 0

        # Verify project_2 untouched
        assert len(kb_service.get_decisions(project_id="project_2")) == 2

    def test_delete_nonexistent_project(self, kb_service, clean_kb):
        """Test deleting a nonexistent project returns 0."""
        count = kb_service.delete_project_kb(project_id="nonexistent")

        assert count == 0


# =============================================================================
# Test Statistics
# =============================================================================

class TestStatistics:
    """Tests for KB statistics and reporting."""

    def test_get_stats_basic(self, kb_service, sample_decisions):
        """Test getting basic stats for a project."""
        stats = kb_service.get_stats(project_id="test_project")

        assert stats["project_id"] == "test_project"
        assert stats["total_entries"] == 6
        assert stats["promoted"] == 0
        assert stats["pending"] == 6

    def test_get_stats_with_promotions(self, kb_service, sample_decisions):
        """Test stats with some entries promoted."""
        # Mark first 2 as promoted
        kb_service.mark_promoted([sample_decisions[0].id, sample_decisions[1].id])

        stats = kb_service.get_stats(project_id="test_project")

        assert stats["total_entries"] == 6
        assert stats["promoted"] == 2
        assert stats["pending"] == 4

    def test_get_stats_by_category(self, kb_service, sample_decisions):
        """Test that stats include breakdown by category."""
        stats = kb_service.get_stats(project_id="test_project")

        assert "by_category" in stats
        assert stats["by_category"]["character"] == 2
        assert stats["by_category"]["constraint"] == 1
        assert stats["by_category"]["world"] == 1
        assert stats["by_category"]["structure"] == 1
        assert stats["by_category"]["preference"] == 1

    def test_get_stats_empty_project(self, kb_service, clean_kb):
        """Test stats for empty project."""
        stats = kb_service.get_stats(project_id="empty_project")

        assert stats["total_entries"] == 0
        assert stats["promoted"] == 0
        assert stats["pending"] == 0
        assert all(count == 0 for count in stats["by_category"].values())


# =============================================================================
# Test Data Model
# =============================================================================

class TestDataModel:
    """Tests for ForemanKBEntry data model."""

    def test_entry_to_dict(self, kb_service, clean_kb):
        """Test converting entry to dictionary."""
        entry = kb_service.save_decision(
            project_id="test_project",
            category="character",
            key="test_key",
            value="test_value",
            source="test_source"
        )

        entry_dict = entry.to_dict()

        assert entry_dict["id"] == entry.id
        assert entry_dict["project_id"] == "test_project"
        assert entry_dict["category"] == "character"
        assert entry_dict["key"] == "test_key"
        assert entry_dict["value"] == "test_value"
        assert entry_dict["source"] == "test_source"
        assert entry_dict["is_promoted"] is False
        assert "created_at" in entry_dict
        assert "updated_at" in entry_dict

    def test_entry_timestamps(self, kb_service, clean_kb):
        """Test that timestamps are set correctly."""
        entry = kb_service.save_decision(
            project_id="test_project",
            category="world",
            key="test_timestamp",
            value="test"
        )

        assert entry.created_at is not None
        assert entry.updated_at is not None
        assert isinstance(entry.created_at, datetime)
        assert isinstance(entry.updated_at, datetime)


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for complete KB workflows."""

    def test_complete_foreman_workflow(self, kb_service, clean_kb):
        """Test complete workflow: save → retrieve → promote → consolidate."""
        project_id = "my_novel"

        # Step 1: Foreman learns character decisions during conversation
        kb_service.save_decision(
            project_id=project_id,
            category="character",
            key="protagonist_flaw",
            value="Hubris",
            source="Chapter 1 conversation"
        )
        kb_service.save_decision(
            project_id=project_id,
            category="constraint",
            key="tone",
            value="Dark and gritty",
            source="Voice calibration"
        )

        # Step 2: Foreman retrieves context for next conversation
        context = kb_service.get_context_for_foreman(project_id=project_id, limit=10)
        assert "protagonist_flaw" in context
        assert "Hubris" in context

        # Step 3: Consolidator identifies decisions to promote
        unpromoted = kb_service.get_unpromoted_decisions(project_id=project_id)
        assert len(unpromoted) == 2

        # Step 4: Consolidator marks as promoted after adding to graph
        entry_ids = [e.id for e in unpromoted]
        count = kb_service.mark_promoted(entry_ids)
        assert count == 2

        # Step 5: Verify no more pending promotions
        still_unpromoted = kb_service.get_unpromoted_decisions(project_id=project_id)
        assert len(still_unpromoted) == 0

        # Step 6: Stats show correct status
        stats = kb_service.get_stats(project_id=project_id)
        assert stats["total_entries"] == 2
        assert stats["promoted"] == 2
        assert stats["pending"] == 0

    def test_multi_session_persistence(self, kb_service, clean_kb):
        """Test that decisions persist across service instances."""
        project_id = "persistent_project"

        # Session 1: Create decision
        kb_service.save_decision(
            project_id=project_id,
            category="world",
            key="magic_system",
            value="Runic magic"
        )

        # Close and create new service instance
        kb_service.close()
        new_service = ForemanKBService()

        try:
            # Session 2: Retrieve decision
            decisions = new_service.get_decisions(project_id=project_id)
            assert len(decisions) == 1
            assert decisions[0].value == "Runic magic"
        finally:
            new_service.close()

    def test_category_aware_context_under_pressure(self, kb_service, clean_kb):
        """Test that foundational decisions survive heavy volatile activity."""
        project_id = "heavy_activity"

        # Day 1: Set character foundations
        kb_service.save_decision(
            project_id=project_id,
            category="character",
            key="fatal_flaw",
            value="Pride",
            source="Day 1"
        )
        kb_service.save_decision(
            project_id=project_id,
            category="constraint",
            key="no_deus_ex_machina",
            value="No sudden saves",
            source="Day 1"
        )

        # Day 2-100: Lots of scene-specific world decisions
        for i in range(50):
            kb_service.save_decision(
                project_id=project_id,
                category="world",
                key=f"scene_{i}_detail",
                value=f"Detail {i}",
                source=f"Chapter {i}"
            )

        # Get context with small limit (simulating token pressure)
        context = kb_service.get_context_for_foreman(
            project_id=project_id,
            limit=5
        )

        # Foundational decisions MUST still be present
        assert "fatal_flaw" in context
        assert "Pride" in context
        assert "no_deus_ex_machina" in context
