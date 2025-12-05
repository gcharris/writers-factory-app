"""
Story Bible Service

Manages Story Bible scaffolding, parsing, and validation.
Implements Phase 2: Story Bible System from the technical specification.

Key responsibilities:
- Create Story Bible directory structure and templates
- Parse Protagonist.md and Beat_Sheet.md for structured data
- Run Level 2 Health Checks for Story Bible completeness
- Support AI Scaffolding Agent for NotebookLM synthesis
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ProtagonistData:
    """Structured data extracted from Protagonist.md"""
    name: str = ""
    true_character: str = ""
    characterization: str = ""
    fatal_flaw: str = ""
    the_lie: str = ""
    arc_start: str = ""
    arc_midpoint: str = ""
    arc_resolution: str = ""
    relationships: list[dict] = field(default_factory=list)
    contradiction_score: float = 0.0  # 0.0-1.0, measures character complexity

    @property
    def is_valid(self) -> bool:
        """Check if minimum required fields are present."""
        return bool(self.name and self.fatal_flaw and self.the_lie)


@dataclass
class BeatData:
    """Data for a single beat in the Beat Sheet."""
    number: int
    name: str
    percentage: str
    description: str = ""
    scene_link: str = ""  # e.g., "1.5.2"

    @property
    def is_complete(self) -> bool:
        return bool(self.name and self.description)


@dataclass
class BeatSheetData:
    """Structured data extracted from Beat_Sheet.md"""
    title: str = ""
    beats: list[BeatData] = field(default_factory=list)
    current_beat: int = 1
    midpoint_type: str = ""  # "false_victory" or "false_defeat"
    theme_stated: str = ""  # From Beat 2

    @property
    def is_valid(self) -> bool:
        """Check if all 15 beats are defined."""
        return len(self.beats) == 15 and all(b.is_complete for b in self.beats)

    @property
    def completion_percentage(self) -> float:
        """How complete is the beat sheet."""
        if not self.beats:
            return 0.0
        complete = sum(1 for b in self.beats if b.is_complete)
        return (complete / 15) * 100


@dataclass
class StoryBibleStatus:
    """Status of Story Bible completeness (Level 2 Health Check)."""
    protagonist_exists: bool = False
    protagonist_has_flaw: bool = False
    protagonist_has_lie: bool = False
    beat_sheet_exists: bool = False
    beat_sheet_complete: bool = False
    scene_strategy_exists: bool = False
    theme_defined: bool = False
    world_rules_exist: bool = False

    # Parsed data
    protagonist: Optional[ProtagonistData] = None
    beat_sheet: Optional[BeatSheetData] = None

    @property
    def phase2_complete(self) -> bool:
        """Can we proceed to Phase 3 (Execution)?"""
        return (
            self.protagonist_exists and
            self.protagonist_has_flaw and
            self.protagonist_has_lie and
            self.beat_sheet_exists and
            self.beat_sheet_complete
        )

    @property
    def completion_score(self) -> float:
        """Overall completion percentage."""
        checks = [
            self.protagonist_exists,
            self.protagonist_has_flaw,
            self.protagonist_has_lie,
            self.beat_sheet_exists,
            self.beat_sheet_complete,
            self.theme_defined,
            self.world_rules_exist,
        ]
        return (sum(checks) / len(checks)) * 100


# =============================================================================
# Templates
# =============================================================================

PROTAGONIST_TEMPLATE = '''# {name}

## True Character vs Characterization

### Characterization (Surface)
*How they appear to others - observable qualities, mannerisms, speech patterns*

{characterization}

### True Character (Core)
*Who they really are under pressure - their authentic self*

{true_character}

### Core Contradiction
*The tension between surface and core that creates dimensional character*

{contradiction}

---

## Fatal Flaw

*The internal weakness that blocks their success and drives the plot*

{fatal_flaw}

---

## The Lie

*The mistaken belief that drives the Fatal Flaw*

{the_lie}

---

## Arc

### Starting State
*Where they begin - their worldview, relationships, capabilities*

{arc_start}

### Midpoint Shift
*What challenges The Lie - the event or realization that begins change*

{arc_midpoint}

### Resolution
*How they change (or fail to) - the transformed (or destroyed) character*

{arc_resolution}

---

## Relationships

*Other characters and their function in the protagonist's arc*

{relationships}

---

## Voice Profile

*Distinctive speech patterns, vocabulary, rhythms for dialogue consistency*

{voice_profile}

---

*Generated by Writers Factory Story Bible System*
*Last Updated: {timestamp}*
'''

BEAT_SHEET_TEMPLATE = '''# Beat Sheet - {title}

## Act 1: Setup (Beats 1-5)

### 1. Opening Image (1%)
*Visual/scene that captures the starting state - this is the "before" snapshot*

{beat_1}

### 2. Theme Stated (5%)
*Where the theme is hinted - often in dialogue, easily missed by protagonist*

{beat_2}

### 3. Setup (1-10%)
*The protagonist's ordinary world - establish status quo, introduce key characters*

{beat_3}

### 4. Catalyst (10%)
*The inciting incident - life-changing event that demands a response*

{beat_4}

### 5. Debate (10-20%)
*Protagonist's hesitation - should they accept the call? What's at stake?*

{beat_5}

---

## Act 2A: Fun & Games (Beats 6-9)

### 6. Break into Two (20%)
*Protagonist commits - crosses the threshold into the new world/situation*

{beat_6}

### 7. B Story (22%)
*Subplot begins - often a love interest or mentor who helps carry the theme*

{beat_7}

### 8. Fun & Games (20-50%)
*The promise of the premise - what the audience came to see*

{beat_8}

### 9. Midpoint (50%)
*False victory OR false defeat - stakes raise, no going back*
**Type:** {midpoint_type}

{beat_9}

---

## Act 2B: Bad Guys Close In (Beats 10-12)

### 10. Bad Guys Close In (50-75%)
*Opposition tightens - internal/external enemies gain ground*

{beat_10}

### 11. All Is Lost (75%)
*Lowest point - whiff of death (literal or metaphorical)*

{beat_11}

### 12. Dark Night of the Soul (75-80%)
*Protagonist despairs - all hope seems lost*

{beat_12}

---

## Act 3: Resolution (Beats 13-15)

### 13. Break into Three (80%)
*Solution discovered - often from B Story, protagonist finds the answer*

{beat_13}

### 14. Finale (80-99%)
*Final confrontation - protagonist applies lessons learned, defeats opposition*

{beat_14}

### 15. Final Image (99-100%)
*Mirror of opening image - showing the transformation (or tragic failure)*

{beat_15}

---

## Progress Tracking

- **Active Beat**: {current_beat}
- **Last Scene Written**: {last_scene}
- **Manuscript Progress**: {progress_percent}%

---

*Generated by Writers Factory Story Bible System*
*Last Updated: {timestamp}*
'''

SCENE_STRATEGY_TEMPLATE = '''# Scene Strategy

## How to Use This Document

For each scene you plan to write, fill out the Goal/Conflict/Outcome framework.
This ensures every scene has narrative purpose and connects to the larger structure.

---

## Scene {scene_id}: {scene_title}

### Goal
*What does the POV character want in this scene?*

{goal}

### Conflict
*What stands in their way?*

{conflict}

### Outcome
Select one:
- [ ] Yes - They get what they want
- [ ] No - They don't get it
- [ ] Yes, But - They get it with complications
- [x] No, And - They don't get it, plus things get worse

**Chosen Outcome:** {outcome}

### Beat Connection
*Which of the 15 beats does this scene serve?*

Beat {beat_number}: {beat_name}

### Character Arc Progress
*Does this scene challenge the Fatal Flaw / The Lie? How?*

{arc_progress}

---

*Add new scenes by copying the template above*

---

*Generated by Writers Factory Story Bible System*
*Last Updated: {timestamp}*
'''

THEME_TEMPLATE = '''# Theme - {title}

## Central Theme

*The core idea or question the story explores*

{central_theme}

---

## Theme Statement

*A one-sentence encapsulation (often stated in Beat 2)*

"{theme_statement}"

---

## Thematic Argument

### Thesis
*The positive argument - what the story says is true*

{thesis}

### Antithesis
*The counter-argument - embodied by antagonist or world*

{antithesis}

### Synthesis
*The nuanced truth that emerges - neither extreme is fully correct*

{synthesis}

---

## Symbolic Elements

*Objects, settings, or motifs that carry thematic weight*

{symbols}

---

## Character Theme Connections

| Character | Relationship to Theme |
|-----------|----------------------|
| Protagonist | {protag_theme} |
| Antagonist | {antag_theme} |
| B Story Character | {bstory_theme} |

---

*Generated by Writers Factory Story Bible System*
*Last Updated: {timestamp}*
'''

WORLD_RULES_TEMPLATE = '''# World Rules - {title}

## Fundamental Rules

*The non-negotiable laws of your story world*

{fundamental_rules}

---

## Technology/Magic System

*How special capabilities work - costs, limits, source*

{system_rules}

---

## Social Structure

*How society is organized - power structures, hierarchies*

{social_rules}

---

## History That Matters

*Only backstory that directly impacts the current narrative*

{history}

---

## Locations

| Location | Significance | First Appears |
|----------|-------------|---------------|
{locations_table}

---

## Consistency Notes

*Rules established in scenes that must be maintained*

{consistency_notes}

---

*Generated by Writers Factory Story Bible System*
*Last Updated: {timestamp}*
'''


# =============================================================================
# Parsers
# =============================================================================

class ProtagonistParser:
    """
    Parses Protagonist.md to extract structured character data.

    Handles both the structured template format and freeform documents
    by looking for key markers and sections.
    """

    def parse(self, content: str, filename: str = "") -> ProtagonistData:
        """Parse protagonist file content into structured data."""
        data = ProtagonistData()

        # Extract name from filename or first heading
        if filename:
            # Remove .md and common suffixes
            name = filename.replace('.md', '')
            for suffix in ['_Enhanced_Identity', '_Character', '_Protagonist']:
                name = name.replace(suffix, '')
            name = name.replace('_', ' ')
            data.name = name
        else:
            # Try to extract from first heading
            heading_match = re.search(r'^#\s+(.+?)(?:\n|$)', content, re.MULTILINE)
            if heading_match:
                data.name = heading_match.group(1).strip()

        # Extract Fatal Flaw
        data.fatal_flaw = self._extract_section(content, [
            'Fatal Flaw',
            'Fatal_Flaw',
            'Core Flaw',
            'Internal Weakness'
        ])

        # Extract The Lie
        data.the_lie = self._extract_section(content, [
            'The Lie',
            'The_Lie',
            'Mistaken Belief',
            'False Belief'
        ])

        # Extract True Character
        data.true_character = self._extract_section(content, [
            'True Character',
            'True_Character',
            'Core',
            'Authentic Self'
        ])

        # Extract Characterization
        data.characterization = self._extract_section(content, [
            'Characterization',
            'Surface',
            'Observable',
            'External Presentation'
        ])

        # Extract Arc components
        data.arc_start = self._extract_section(content, [
            'Starting State',
            'Arc Start',
            'Beginning State'
        ])
        data.arc_midpoint = self._extract_section(content, [
            'Midpoint Shift',
            'Arc Midpoint',
            'Turning Point'
        ])
        data.arc_resolution = self._extract_section(content, [
            'Resolution',
            'Arc Resolution',
            'Ending State',
            'Transformation'
        ])

        # Extract relationships
        data.relationships = self._extract_relationships(content)

        # Calculate contradiction score
        data.contradiction_score = self._calculate_contradiction_score(data)

        return data

    def _extract_section(self, content: str, headers: list[str]) -> str:
        """Extract content under any of the given headers."""
        for header in headers:
            # Try markdown heading formats
            patterns = [
                rf'##?\s*{re.escape(header)}[^\n]*\n(.*?)(?=\n##|\n---|\Z)',
                rf'\*\*{re.escape(header)}\*\*[:\s]*(.*?)(?=\n\*\*|\n##|\n---|\Z)',
            ]

            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    text = match.group(1).strip()
                    # Clean up markdown artifacts
                    text = re.sub(r'^\*+|\*+$', '', text)
                    text = re.sub(r'\n\s*\n', '\n', text)
                    if text and len(text) > 10:
                        return text

        return ""

    def _extract_relationships(self, content: str) -> list[dict]:
        """Extract character relationships from content."""
        relationships = []

        # Look for relationships section
        rel_section = self._extract_section(content, [
            'Relationships',
            'Core Relationships',
            'Character Relationships'
        ])

        if rel_section:
            # Parse bullet points
            for line in rel_section.split('\n'):
                line = line.strip()
                if line.startswith(('-', '•', '*')):
                    line = line.lstrip('-•* ')
                    # Try to parse "Name: Function" or "Name - Function"
                    parts = re.split(r'[:\-–—]', line, maxsplit=1)
                    if len(parts) == 2:
                        relationships.append({
                            'character': parts[0].strip(),
                            'function': parts[1].strip()
                        })

        return relationships

    def _calculate_contradiction_score(self, data: ProtagonistData) -> float:
        """
        Calculate character complexity score based on contradictions.

        A score of 0.0 means flat character, 1.0 means highly complex.
        """
        score = 0.0

        # Has both True Character and Characterization that differ
        if data.true_character and data.characterization:
            # Simple heuristic: they should be different
            if data.true_character.lower() != data.characterization.lower():
                score += 0.3

        # Has Fatal Flaw that creates internal conflict
        if data.fatal_flaw:
            score += 0.3

        # Has The Lie that contrasts with truth
        if data.the_lie:
            score += 0.2

        # Has arc with change
        if data.arc_start and data.arc_resolution:
            if data.arc_start.lower() != data.arc_resolution.lower():
                score += 0.2

        return min(score, 1.0)


class BeatSheetParser:
    """
    Parses Beat_Sheet.md to extract the 15-beat structure.

    Strictly enforces the Save the Cat! methodology.
    """

    BEAT_NAMES = [
        "Opening Image",
        "Theme Stated",
        "Setup",
        "Catalyst",
        "Debate",
        "Break into Two",
        "B Story",
        "Fun & Games",
        "Midpoint",
        "Bad Guys Close In",
        "All Is Lost",
        "Dark Night of the Soul",
        "Break into Three",
        "Finale",
        "Final Image"
    ]

    BEAT_PERCENTAGES = [
        "1%", "5%", "1-10%", "10%", "10-20%",
        "20%", "22%", "20-50%", "50%",
        "50-75%", "75%", "75-80%",
        "80%", "80-99%", "99-100%"
    ]

    def parse(self, content: str) -> BeatSheetData:
        """Parse beat sheet content into structured data."""
        data = BeatSheetData()

        # Extract title
        title_match = re.search(r'#\s+Beat Sheet\s*[-–—]\s*(.+?)(?:\n|$)', content)
        if title_match:
            data.title = title_match.group(1).strip()

        # Extract beats
        for i, beat_name in enumerate(self.BEAT_NAMES, 1):
            beat = self._extract_beat(content, i, beat_name)
            data.beats.append(beat)

        # Extract midpoint type
        midpoint_section = self._extract_beat_content(content, 9, "Midpoint")
        if midpoint_section:
            if 'false victory' in midpoint_section.lower():
                data.midpoint_type = "false_victory"
            elif 'false defeat' in midpoint_section.lower():
                data.midpoint_type = "false_defeat"

            # Also check for Type: marker
            type_match = re.search(r'\*\*Type:\*\*\s*(\w+)', midpoint_section)
            if type_match:
                data.midpoint_type = type_match.group(1).lower().replace(' ', '_')

        # Extract theme stated (Beat 2)
        if len(data.beats) >= 2:
            data.theme_stated = data.beats[1].description

        # Extract current progress
        progress_match = re.search(r'\*\*Active Beat\*\*:\s*(\d+)', content)
        if progress_match:
            data.current_beat = int(progress_match.group(1))

        return data

    def _extract_beat(self, content: str, beat_num: int, beat_name: str) -> BeatData:
        """Extract a single beat's data."""
        beat = BeatData(
            number=beat_num,
            name=beat_name,
            percentage=self.BEAT_PERCENTAGES[beat_num - 1] if beat_num <= len(self.BEAT_PERCENTAGES) else ""
        )

        beat.description = self._extract_beat_content(content, beat_num, beat_name)

        # Look for scene links like "Scene 1.5.2"
        scene_match = re.search(
            rf'{beat_num}\.\s+\*\*{re.escape(beat_name)}.*?Scene\s+([\d.]+)',
            content,
            re.IGNORECASE | re.DOTALL
        )
        if scene_match:
            beat.scene_link = scene_match.group(1)

        return beat

    def _extract_beat_content(self, content: str, beat_num: int, beat_name: str) -> str:
        """Extract the description content for a beat."""
        # Pattern: ### N. Beat Name (percentage)
        pattern = rf'###\s*{beat_num}\.\s+{re.escape(beat_name)}.*?\n(.*?)(?=###\s*\d+\.|---|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            text = match.group(1).strip()
            # Remove the italicized instruction text
            text = re.sub(r'^\*[^*]+\*\s*', '', text)
            # Clean up
            text = re.sub(r'\n\s*\n+', '\n', text)
            return text.strip()

        return ""


# =============================================================================
# Story Bible Service
# =============================================================================

class StoryBibleService:
    """
    Main service for Story Bible management.

    Handles:
    - Directory structure creation
    - Template scaffolding
    - Parsing existing documents
    - Level 2 Health Checks
    """

    def __init__(self, content_path: Path):
        self.content_path = content_path
        self.story_bible_path = content_path / "Story Bible"
        self.protagonist_parser = ProtagonistParser()
        self.beat_sheet_parser = BeatSheetParser()

    # -------------------------------------------------------------------------
    # Directory Structure
    # -------------------------------------------------------------------------

    def ensure_directory_structure(self) -> dict:
        """
        Create the required Story Bible directory structure.

        Returns dict of created directories.
        """
        directories = {
            'story_bible': self.story_bible_path,
            'characters': self.content_path / "Characters",
            'story_structure': self.story_bible_path / "Structure",
            'themes': self.story_bible_path / "Themes_and_Philosophy",
            'world': self.content_path / "World Bible",
            'research': self.story_bible_path / "Research",
        }

        created = []
        for name, path in directories.items():
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created.append(name)
                logger.info(f"Created directory: {path}")

        return {
            'directories': directories,
            'created': created
        }

    # -------------------------------------------------------------------------
    # Template Generation
    # -------------------------------------------------------------------------

    def generate_protagonist_template(
        self,
        name: str,
        pre_filled: dict = None
    ) -> str:
        """Generate a Protagonist.md template, optionally pre-filled."""
        data = pre_filled or {}
        timestamp = datetime.now(timezone.utc).isoformat()

        return PROTAGONIST_TEMPLATE.format(
            name=name,
            characterization=data.get('characterization', '*[Define observable qualities]*'),
            true_character=data.get('true_character', '*[Define core traits under pressure]*'),
            contradiction=data.get('contradiction', '*[Define the tension between surface and core]*'),
            fatal_flaw=data.get('fatal_flaw', '*[Define the internal weakness]*'),
            the_lie=data.get('the_lie', '*[Define the mistaken belief]*'),
            arc_start=data.get('arc_start', '*[Where do they begin?]*'),
            arc_midpoint=data.get('arc_midpoint', '*[What challenges The Lie?]*'),
            arc_resolution=data.get('arc_resolution', '*[How do they change?]*'),
            relationships=data.get('relationships', '- *[Character]*: *[Function in arc]*'),
            voice_profile=data.get('voice_profile', '*[Define speech patterns, vocabulary]*'),
            timestamp=timestamp
        )

    def generate_beat_sheet_template(
        self,
        title: str,
        pre_filled: dict = None
    ) -> str:
        """Generate a Beat_Sheet.md template, optionally pre-filled."""
        data = pre_filled or {}
        timestamp = datetime.now(timezone.utc).isoformat()

        return BEAT_SHEET_TEMPLATE.format(
            title=title,
            beat_1=data.get('beat_1', '*[Opening scene/image]*'),
            beat_2=data.get('beat_2', '*[Where is theme hinted?]*'),
            beat_3=data.get('beat_3', '*[Ordinary world details]*'),
            beat_4=data.get('beat_4', '*[Inciting incident]*'),
            beat_5=data.get('beat_5', '*[Protagonist hesitation]*'),
            beat_6=data.get('beat_6', '*[Commitment to new world]*'),
            beat_7=data.get('beat_7', '*[Subplot/love interest]*'),
            beat_8=data.get('beat_8', '*[Promise of premise]*'),
            midpoint_type=data.get('midpoint_type', 'false_victory OR false_defeat'),
            beat_9=data.get('beat_9', '*[Stakes raise, no going back]*'),
            beat_10=data.get('beat_10', '*[Opposition tightens]*'),
            beat_11=data.get('beat_11', '*[Lowest point]*'),
            beat_12=data.get('beat_12', '*[Protagonist despairs]*'),
            beat_13=data.get('beat_13', '*[Solution discovered]*'),
            beat_14=data.get('beat_14', '*[Final confrontation]*'),
            beat_15=data.get('beat_15', '*[Mirror of opening]*'),
            current_beat=data.get('current_beat', '1'),
            last_scene=data.get('last_scene', 'None'),
            progress_percent=data.get('progress_percent', '0'),
            timestamp=timestamp
        )

    def generate_scene_strategy_template(
        self,
        scene_id: str = "X.X.X",
        scene_title: str = "Scene Title"
    ) -> str:
        """Generate a Scene_Strategy.md template."""
        timestamp = datetime.now(timezone.utc).isoformat()

        return SCENE_STRATEGY_TEMPLATE.format(
            scene_id=scene_id,
            scene_title=scene_title,
            goal='*[What does the POV character want?]*',
            conflict='*[What opposes them?]*',
            outcome='*[Yes/No/Yes-But/No-And]*',
            beat_number='X',
            beat_name='*[Beat name]*',
            arc_progress='*[How does this challenge the Fatal Flaw?]*',
            timestamp=timestamp
        )

    def generate_theme_template(self, title: str) -> str:
        """Generate a Theme.md template."""
        timestamp = datetime.now(timezone.utc).isoformat()

        return THEME_TEMPLATE.format(
            title=title,
            central_theme='*[The core idea explored]*',
            theme_statement='*[One-sentence encapsulation]*',
            thesis='*[What the story argues is true]*',
            antithesis='*[The counter-argument]*',
            synthesis='*[The nuanced truth]*',
            symbols='*[Objects/motifs carrying thematic weight]*',
            protag_theme='*[How protagonist embodies/struggles with theme]*',
            antag_theme='*[How antagonist challenges theme]*',
            bstory_theme='*[How B Story illuminates theme]*',
            timestamp=timestamp
        )

    def generate_world_rules_template(self, title: str) -> str:
        """Generate a World_Rules.md template."""
        timestamp = datetime.now(timezone.utc).isoformat()

        return WORLD_RULES_TEMPLATE.format(
            title=title,
            fundamental_rules='*[Non-negotiable laws of the world]*',
            system_rules='*[How special capabilities work]*',
            social_rules='*[How society is organized]*',
            history='*[Backstory that impacts current narrative]*',
            locations_table='| *[Location]* | *[Significance]* | *[Scene ID]* |',
            consistency_notes='*[Rules established in scenes]*',
            timestamp=timestamp
        )

    # -------------------------------------------------------------------------
    # Scaffold Creation
    # -------------------------------------------------------------------------

    def scaffold_story_bible(
        self,
        project_title: str,
        protagonist_name: str,
        pre_filled: dict = None
    ) -> dict:
        """
        Create complete Story Bible scaffolding.

        Creates all required files with templates.
        Returns dict of created files.
        """
        pre_filled = pre_filled or {}

        # Ensure directories exist
        self.ensure_directory_structure()

        created_files = []

        # 1. Protagonist.md
        protag_path = self.content_path / "Characters" / f"{protagonist_name.replace(' ', '_')}.md"
        if not protag_path.exists():
            content = self.generate_protagonist_template(
                protagonist_name,
                pre_filled.get('protagonist', {})
            )
            protag_path.write_text(content, encoding='utf-8')
            created_files.append(str(protag_path))
            logger.info(f"Created: {protag_path}")

        # 2. Beat_Sheet.md
        beat_path = self.story_bible_path / "Structure" / "Beat_Sheet.md"
        beat_path.parent.mkdir(parents=True, exist_ok=True)
        if not beat_path.exists():
            content = self.generate_beat_sheet_template(
                project_title,
                pre_filled.get('beat_sheet', {})
            )
            beat_path.write_text(content, encoding='utf-8')
            created_files.append(str(beat_path))
            logger.info(f"Created: {beat_path}")

        # 3. Scene_Strategy.md
        strategy_path = self.story_bible_path / "Structure" / "Scene_Strategy.md"
        if not strategy_path.exists():
            content = self.generate_scene_strategy_template()
            strategy_path.write_text(content, encoding='utf-8')
            created_files.append(str(strategy_path))
            logger.info(f"Created: {strategy_path}")

        # 4. Theme.md
        theme_path = self.story_bible_path / "Themes_and_Philosophy" / "04_Theme.md"
        theme_path.parent.mkdir(parents=True, exist_ok=True)
        if not theme_path.exists():
            content = self.generate_theme_template(project_title)
            theme_path.write_text(content, encoding='utf-8')
            created_files.append(str(theme_path))
            logger.info(f"Created: {theme_path}")

        # 5. World_Rules.md
        rules_path = self.content_path / "World Bible" / "Rules.md"
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        if not rules_path.exists():
            content = self.generate_world_rules_template(project_title)
            rules_path.write_text(content, encoding='utf-8')
            created_files.append(str(rules_path))
            logger.info(f"Created: {rules_path}")

        return {
            'created_files': created_files,
            'project_title': project_title,
            'protagonist_name': protagonist_name,
        }

    # -------------------------------------------------------------------------
    # Parsing
    # -------------------------------------------------------------------------

    def parse_protagonist(self, file_path: Path = None) -> ProtagonistData:
        """
        Parse protagonist file(s) and return structured data.

        If file_path not specified, searches Characters/ directory.
        """
        if file_path and file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            return self.protagonist_parser.parse(content, file_path.name)

        # Search for protagonist files
        char_dir = self.content_path / "Characters"
        if char_dir.exists():
            for md_file in char_dir.glob("*.md"):
                content = md_file.read_text(encoding='utf-8')
                data = self.protagonist_parser.parse(content, md_file.name)
                if data.is_valid:
                    return data
                # Return first character found even if incomplete
                if data.name:
                    return data

        return ProtagonistData()

    def parse_beat_sheet(self, file_path: Path = None) -> BeatSheetData:
        """
        Parse Beat_Sheet.md and return structured data.
        """
        if file_path is None:
            file_path = self.story_bible_path / "Structure" / "Beat_Sheet.md"

        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            return self.beat_sheet_parser.parse(content)

        return BeatSheetData()

    # -------------------------------------------------------------------------
    # Validation (Level 2 Health Checks)
    # -------------------------------------------------------------------------

    def validate_story_bible(self) -> StoryBibleStatus:
        """
        Run Level 2: Story Bible Completeness checks.

        Returns comprehensive status including parsed data.
        """
        status = StoryBibleStatus()

        # Parse protagonist
        protagonist = self.parse_protagonist()
        status.protagonist = protagonist
        status.protagonist_exists = bool(protagonist.name)
        status.protagonist_has_flaw = bool(protagonist.fatal_flaw)
        status.protagonist_has_lie = bool(protagonist.the_lie)

        # Parse beat sheet
        beat_sheet = self.parse_beat_sheet()
        status.beat_sheet = beat_sheet
        status.beat_sheet_exists = bool(beat_sheet.title or beat_sheet.beats)
        status.beat_sheet_complete = beat_sheet.is_valid

        # Check scene strategy exists
        strategy_path = self.story_bible_path / "Structure" / "Scene_Strategy.md"
        status.scene_strategy_exists = strategy_path.exists()

        # Check theme defined
        theme_path = self.story_bible_path / "Themes_and_Philosophy" / "04_Theme.md"
        if theme_path.exists():
            content = theme_path.read_text(encoding='utf-8')
            # Check if it has actual content beyond template
            status.theme_defined = '*[' not in content[:500]  # Has been filled in

        # Check world rules exist
        rules_path = self.content_path / "World Bible" / "Rules.md"
        status.world_rules_exist = rules_path.exists()

        return status

    # -------------------------------------------------------------------------
    # Convenience Methods for Prerequisite Checks
    # -------------------------------------------------------------------------

    def has_protagonist(self) -> bool:
        """Check if a valid protagonist exists."""
        protagonist = self.parse_protagonist()
        return bool(protagonist.name)

    def beat_count(self) -> int:
        """Return the number of filled beats in the beat sheet."""
        beat_sheet = self.parse_beat_sheet()
        if not beat_sheet.beats:
            return 0
        return sum(1 for b in beat_sheet.beats if b.content)

    def is_complete(self) -> bool:
        """Check if the Story Bible is complete for Phase 2."""
        status = self.validate_story_bible()
        return status.phase2_complete

    def get_validation_report(self) -> dict:
        """
        Generate a human-readable validation report.
        """
        status = self.validate_story_bible()

        checks = [
            ("Protagonist file exists", status.protagonist_exists),
            ("Protagonist has Fatal Flaw defined", status.protagonist_has_flaw),
            ("Protagonist has The Lie defined", status.protagonist_has_lie),
            ("Beat Sheet exists", status.beat_sheet_exists),
            ("Beat Sheet is complete (all 15 beats)", status.beat_sheet_complete),
            ("Scene Strategy exists", status.scene_strategy_exists),
            ("Theme is defined", status.theme_defined),
            ("World Rules exist", status.world_rules_exist),
        ]

        report = {
            'phase2_complete': status.phase2_complete,
            'completion_score': status.completion_score,
            'checks': [
                {'name': name, 'passed': passed, 'status': '✓' if passed else '✗'}
                for name, passed in checks
            ],
            'protagonist': asdict(status.protagonist) if status.protagonist else None,
            'beat_sheet': {
                'title': status.beat_sheet.title if status.beat_sheet else None,
                'completion': status.beat_sheet.completion_percentage if status.beat_sheet else 0,
                'current_beat': status.beat_sheet.current_beat if status.beat_sheet else None,
                'midpoint_type': status.beat_sheet.midpoint_type if status.beat_sheet else None,
            },
            'can_proceed_to_execution': status.phase2_complete,
            'blocking_issues': [
                check['name'] for check in [
                    {'name': name, 'passed': passed} for name, passed in checks
                ] if not check['passed'] and check['name'] in [
                    "Protagonist has Fatal Flaw defined",
                    "Protagonist has The Lie defined",
                    "Beat Sheet is complete (all 15 beats)",
                ]
            ]
        }

        return report


# =============================================================================
# Singleton Instance
# =============================================================================

# Default content path - can be overridden by setting CONTENT_PATH env var
import os
_content_path = Path(os.environ.get('CONTENT_PATH', Path(__file__).parent.parent.parent / 'content'))
story_bible_service = StoryBibleService(_content_path)
