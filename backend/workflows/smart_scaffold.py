"""
Smart Scaffold Workflow

Queries NotebookLM to extract character, plot, and world information,
then synthesizes this into structured Story Bible templates.

This is the "AI Scaffolding Agent" that converts unstructured research
into the required Narrative Protocol artifacts.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .base import Workflow, WorkflowResult

logger = logging.getLogger(__name__)


# Prompts for querying NotebookLM to extract Story Bible data
PROTAGONIST_QUERY = """Based on all the sources in this notebook, provide a detailed character profile for the protagonist. Include:

1. **Name**: The character's full name
2. **True Character**: Their core traits - who they really are under pressure (loyal, cowardly, ambitious, etc.)
3. **Characterization**: How they appear to others - observable qualities, mannerisms, speech patterns
4. **Fatal Flaw**: Their internal weakness that drives conflict - what blocks their success
5. **The Lie**: The mistaken belief that drives the Fatal Flaw - what they wrongly believe about themselves or the world
6. **Arc Starting State**: Where they begin emotionally and psychologically
7. **Arc Midpoint**: What challenges or changes The Lie
8. **Arc Resolution**: How they change (or fail to change) by the end

Be specific and cite sources where possible."""

BEAT_SHEET_QUERY = """Based on all the sources in this notebook, outline the 15-beat story structure (Save the Cat! format):

1. **Opening Image** (1%): The "before" snapshot
2. **Theme Stated** (5%): Where the theme is hinted
3. **Setup** (1-10%): The protagonist's ordinary world
4. **Catalyst** (10%): The inciting incident
5. **Debate** (10-20%): The protagonist's hesitation
6. **Break into Two** (20%): Commitment to the new world
7. **B Story** (22%): The subplot that carries the theme
8. **Fun & Games** (20-50%): The promise of the premise
9. **Midpoint** (50%): False victory or false defeat - specify which
10. **Bad Guys Close In** (50-75%): Opposition tightens
11. **All Is Lost** (75%): Lowest point, whiff of death
12. **Dark Night of the Soul** (75-80%): Protagonist despairs
13. **Break into Three** (80%): Solution discovered
14. **Finale** (80-99%): Final confrontation
15. **Final Image** (99-100%): Mirror of opening, showing change

For each beat, describe what happens based on the story materials."""

THEME_QUERY = """Based on all the sources in this notebook, identify the story's themes:

1. **Central Theme**: The core idea or question the story explores
2. **Theme Statement**: A one-sentence encapsulation
3. **Thesis**: What the story argues is true
4. **Antithesis**: The counter-argument (embodied by antagonist or world)
5. **Synthesis**: The nuanced truth that emerges

Also identify any symbolic elements that carry thematic weight."""

WORLD_RULES_QUERY = """Based on all the sources in this notebook, describe the world rules:

1. **Fundamental Rules**: Non-negotiable laws of this story world
2. **Special Systems**: How technology/magic/abilities work - costs, limits, sources
3. **Social Structure**: How society is organized
4. **Key Locations**: Important settings and their significance

Focus on rules that directly impact the narrative."""


class SmartScaffoldWorkflow(Workflow):
    """
    Workflow that queries NotebookLM and synthesizes Story Bible artifacts.

    Steps:
    1. Query NotebookLM for protagonist data
    2. Query NotebookLM for beat sheet structure
    3. Query NotebookLM for themes
    4. Query NotebookLM for world rules
    5. Synthesize into Story Bible templates
    6. Validate completeness
    """

    def __init__(
        self,
        notebooklm_client,
        story_bible_service,
    ):
        super().__init__()
        self.nlm = notebooklm_client
        self.story_bible = story_bible_service

    async def run(
        self,
        notebook_id: str,
        project_title: str,
        protagonist_name: str,
    ) -> WorkflowResult:
        """
        Execute the smart scaffold workflow.

        Args:
            notebook_id: The NotebookLM notebook ID containing research
            project_title: Name of the novel project
            protagonist_name: Name of the protagonist character

        Returns:
            WorkflowResult with synthesized Story Bible data
        """
        self.reset()

        # Add steps
        self.add_step(
            "Query Protagonist Data",
            self._query_protagonist,
            notebook_id=notebook_id,
            protagonist_name=protagonist_name,
        )

        self.add_step(
            "Query Beat Sheet",
            self._query_beat_sheet,
            notebook_id=notebook_id,
        )

        self.add_step(
            "Query Themes",
            self._query_themes,
            notebook_id=notebook_id,
        )

        self.add_step(
            "Query World Rules",
            self._query_world_rules,
            notebook_id=notebook_id,
        )

        self.add_step(
            "Synthesize Story Bible",
            self._synthesize_story_bible,
            project_title=project_title,
            protagonist_name=protagonist_name,
        )

        self.add_step(
            "Validate Completeness",
            self._validate_completeness,
        )

        # Execute workflow
        result = await self.execute({
            'notebook_id': notebook_id,
            'project_title': project_title,
            'protagonist_name': protagonist_name,
        })

        return result

    # -------------------------------------------------------------------------
    # Step Implementations
    # -------------------------------------------------------------------------

    async def _query_protagonist(
        self,
        context: Dict[str, Any],
        notebook_id: str,
        protagonist_name: str,
    ) -> Dict[str, Any]:
        """Query NotebookLM for protagonist data."""
        logger.info(f"Querying NotebookLM for protagonist: {protagonist_name}")

        # Build custom query with protagonist name
        query = PROTAGONIST_QUERY.replace("the protagonist", protagonist_name)

        response = await self.nlm.query_notebook(notebook_id, query)

        return {
            'raw_response': response.answer,
            'sources': response.sources,
            'protagonist_name': protagonist_name,
        }

    async def _query_beat_sheet(
        self,
        context: Dict[str, Any],
        notebook_id: str,
    ) -> Dict[str, Any]:
        """Query NotebookLM for beat sheet structure."""
        logger.info("Querying NotebookLM for beat sheet")

        response = await self.nlm.query_notebook(notebook_id, BEAT_SHEET_QUERY)

        return {
            'raw_response': response.answer,
            'sources': response.sources,
        }

    async def _query_themes(
        self,
        context: Dict[str, Any],
        notebook_id: str,
    ) -> Dict[str, Any]:
        """Query NotebookLM for themes."""
        logger.info("Querying NotebookLM for themes")

        response = await self.nlm.query_notebook(notebook_id, THEME_QUERY)

        return {
            'raw_response': response.answer,
            'sources': response.sources,
        }

    async def _query_world_rules(
        self,
        context: Dict[str, Any],
        notebook_id: str,
    ) -> Dict[str, Any]:
        """Query NotebookLM for world rules."""
        logger.info("Querying NotebookLM for world rules")

        response = await self.nlm.query_notebook(notebook_id, WORLD_RULES_QUERY)

        return {
            'raw_response': response.answer,
            'sources': response.sources,
        }

    async def _synthesize_story_bible(
        self,
        context: Dict[str, Any],
        project_title: str,
        protagonist_name: str,
    ) -> Dict[str, Any]:
        """
        Synthesize NotebookLM responses into Story Bible templates.

        Parses the raw responses and populates template fields.
        """
        logger.info("Synthesizing Story Bible from NotebookLM data")

        # Get query results from context
        protagonist_data = context.get('query_protagonist_data', {})
        beat_sheet_data = context.get('query_beat_sheet', {})
        theme_data = context.get('query_themes', {})
        world_data = context.get('query_world_rules', {})

        # Parse protagonist response into template fields
        protagonist_prefill = self._parse_protagonist_response(
            protagonist_data.get('raw_response', ''),
            protagonist_name,
        )

        # Parse beat sheet response
        beat_sheet_prefill = self._parse_beat_sheet_response(
            beat_sheet_data.get('raw_response', ''),
        )

        # Parse theme response
        theme_prefill = self._parse_theme_response(
            theme_data.get('raw_response', ''),
        )

        # Parse world response
        world_prefill = self._parse_world_response(
            world_data.get('raw_response', ''),
        )

        # Create Story Bible scaffold with pre-filled data
        result = self.story_bible.scaffold_story_bible(
            project_title=project_title,
            protagonist_name=protagonist_name,
            pre_filled={
                'protagonist': protagonist_prefill,
                'beat_sheet': beat_sheet_prefill,
                'theme': theme_prefill,
                'world': world_prefill,
            }
        )

        return {
            'created_files': result.get('created_files', []),
            'protagonist_prefill': protagonist_prefill,
            'beat_sheet_prefill': beat_sheet_prefill,
        }

    async def _validate_completeness(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate the synthesized Story Bible."""
        logger.info("Validating Story Bible completeness")

        report = self.story_bible.get_validation_report()

        return {
            'validation': report,
            'phase2_complete': report.get('phase2_complete', False),
            'completion_score': report.get('completion_score', 0),
        }

    # -------------------------------------------------------------------------
    # Response Parsers
    # -------------------------------------------------------------------------

    def _parse_protagonist_response(
        self,
        response: str,
        protagonist_name: str,
    ) -> Dict[str, str]:
        """
        Parse NotebookLM protagonist response into template fields.

        Uses simple section extraction - can be enhanced with LLM parsing.
        """
        result = {
            'name': protagonist_name,
        }

        # Extract sections by looking for bold headers
        sections = {
            'true_character': ['True Character', 'Core Traits'],
            'characterization': ['Characterization', 'Observable'],
            'fatal_flaw': ['Fatal Flaw', 'Internal Weakness'],
            'the_lie': ['The Lie', 'Mistaken Belief'],
            'arc_start': ['Arc Starting State', 'Starting State', 'Beginning'],
            'arc_midpoint': ['Arc Midpoint', 'Midpoint Shift'],
            'arc_resolution': ['Arc Resolution', 'Resolution', 'Ending'],
        }

        for field, headers in sections.items():
            for header in headers:
                content = self._extract_section(response, header)
                if content:
                    result[field] = content
                    break

        return result

    def _parse_beat_sheet_response(self, response: str) -> Dict[str, str]:
        """Parse beat sheet response into template fields."""
        result = {}

        # Map beat numbers to template field names
        beat_names = [
            ('1', 'Opening Image', 'beat_1'),
            ('2', 'Theme Stated', 'beat_2'),
            ('3', 'Setup', 'beat_3'),
            ('4', 'Catalyst', 'beat_4'),
            ('5', 'Debate', 'beat_5'),
            ('6', 'Break into Two', 'beat_6'),
            ('7', 'B Story', 'beat_7'),
            ('8', 'Fun & Games', 'beat_8'),
            ('9', 'Midpoint', 'beat_9'),
            ('10', 'Bad Guys Close In', 'beat_10'),
            ('11', 'All Is Lost', 'beat_11'),
            ('12', 'Dark Night', 'beat_12'),
            ('13', 'Break into Three', 'beat_13'),
            ('14', 'Finale', 'beat_14'),
            ('15', 'Final Image', 'beat_15'),
        ]

        for num, name, field in beat_names:
            # Try to extract by number or name
            content = self._extract_beat(response, num, name)
            if content:
                result[field] = content

        # Check for midpoint type
        if 'false victory' in response.lower():
            result['midpoint_type'] = 'false_victory'
        elif 'false defeat' in response.lower():
            result['midpoint_type'] = 'false_defeat'

        return result

    def _parse_theme_response(self, response: str) -> Dict[str, str]:
        """Parse theme response into template fields."""
        result = {}

        sections = {
            'central_theme': ['Central Theme', 'Core Theme'],
            'theme_statement': ['Theme Statement', 'One-sentence'],
            'thesis': ['Thesis'],
            'antithesis': ['Antithesis'],
            'synthesis': ['Synthesis'],
            'symbols': ['Symbolic', 'Symbols'],
        }

        for field, headers in sections.items():
            for header in headers:
                content = self._extract_section(response, header)
                if content:
                    result[field] = content
                    break

        return result

    def _parse_world_response(self, response: str) -> Dict[str, str]:
        """Parse world rules response into template fields."""
        result = {}

        sections = {
            'fundamental_rules': ['Fundamental Rules', 'Non-negotiable'],
            'system_rules': ['Special Systems', 'Technology', 'Magic'],
            'social_rules': ['Social Structure', 'Society'],
            'history': ['History'],
        }

        for field, headers in sections.items():
            for header in headers:
                content = self._extract_section(response, header)
                if content:
                    result[field] = content
                    break

        return result

    def _extract_section(self, text: str, header: str) -> str:
        """
        Extract content following a header.

        Looks for patterns like:
        - **Header**: Content
        - ## Header
        - Header: Content
        """
        import re

        patterns = [
            # **Header**: Content until next header or end
            rf'\*\*{re.escape(header)}\*\*[:\s]*(.+?)(?=\*\*[A-Z]|\n\n##|\Z)',
            # ## Header followed by content
            rf'##\s*{re.escape(header)}[^\n]*\n(.+?)(?=##|\Z)',
            # N. Header: Content
            rf'\d+\.\s*\*?\*?{re.escape(header)}\*?\*?[:\s]*(.+?)(?=\d+\.|\Z)',
            # Simple Header: Content
            rf'{re.escape(header)}[:\s]+(.+?)(?=\n\n|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Clean up the content
                content = re.sub(r'\n\s*\n+', '\n', content)
                if len(content) > 20:  # Only return if substantial
                    return content

        return ""

    def _extract_beat(self, text: str, num: str, name: str) -> str:
        """Extract a specific beat from the beat sheet response."""
        import re

        patterns = [
            # N. **Name** (X%): Content
            rf'{num}\.\s*\*\*{re.escape(name)}\*\*[^:]*:\s*(.+?)(?=\d+\.\s*\*\*|\Z)',
            # **N. Name**: Content
            rf'\*\*{num}\.\s*{re.escape(name)}\*\*[:\s]*(.+?)(?=\*\*\d+\.|\Z)',
            # Beat N - Name: Content
            rf'Beat\s*{num}[:\-\s]+{re.escape(name)}[:\s]*(.+?)(?=Beat\s*\d+|\Z)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                content = re.sub(r'\n\s*\n+', '\n', content)
                if len(content) > 10:
                    return content

        return ""
