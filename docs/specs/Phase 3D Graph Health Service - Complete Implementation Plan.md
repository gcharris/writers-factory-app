# Phase 3D: Graph Health Service - Complete Implementation Plan

Based on the specification documents and Phase 3C completion, here's the comprehensive plan for Phase 3D implementation.



------

## Overview

**Goal:** Macro-level structural validation at chapter/act/manuscript level
**Priority:** P1 High - Completes Director Mode quality loop
**Effort:** 12-15 hours
**Status:** Ready to implement (Phase 3C Settings Service complete ✓)



------

## Problem Statement

Scene Analyzer (Phase 3B) validates individual scenes but **cannot detect**:



- **Pacing Plateaus** → 3 consecutive chapters with flat tension
- **Dropped Threads** → Setup introduced but never resolved
- **Character Absences** → Supporting character vanishes for 10+ chapters
- **Beat Deviation** → Act 2 finishes at wrong percentage of manuscript
- **Flaw Challenge Gaps** → Protagonist's Fatal Flaw untested for too long
- **Timeline Conflicts** → Character in two places simultaneously

------

## Architecture: Two-Tier Quality System

```
┌─────────────────────────────────────────────────────┐
│ TIER 1: Scene Analyzer (Immediate)                  │
│ - Voice authenticity                                 │
│ - Anti-pattern detection                             │
│ - Metaphor discipline                                │
│ - Individual scene quality                           │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ TIER 2: Graph Health Service (Asynchronous)         │
│ - Pacing across chapters                            │
│ - Beat structure compliance                          │
│ - Character arc health                               │
│ - Thematic consistency                               │
└─────────────────────────────────────────────────────┘
```

------

## Task Breakdown

### ✅ Task 0: Prerequisites (Already Complete)

- **Settings Service** with health check thresholds (Phase 3C)
- **Knowledge Graph** infrastructure (Phase 1)
- **Scene Analyzer** for individual scene scoring (Phase 3B)

------

### 📋 Task 1: Extend Knowledge Graph Schema (3-4 hours)

**File to Modify:** `backend/graph/schema.py`

 

**New Node Types:**



```python
class Scene(Base):
    """Scene node - connects to Chapter, tracks tension and content."""
    __tablename__ = "scenes"
    
    id = Column(Integer, primary_key=True)
    scene_id = Column(String, unique=True, nullable=False, index=True)
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), index=True)
    scene_number = Column(Integer)  # Within chapter
    word_count = Column(Integer)
    tension_score = Column(Float)  # 1-10 scale
    score = Column(Integer)  # Scene Analyzer score (0-100)
    content_hash = Column(String)  # SHA256 of content
    status = Column(String)  # draft, polished, complete
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="scenes")
    character_appearances = relationship("CharacterAppearance", back_populates="scene")

class Chapter(Base):
    """Chapter node - aggregates scenes, tracks beat progress."""
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True)
    chapter_id = Column(String, unique=True, nullable=False, index=True)
    chapter_number = Column(Integer, index=True)
    title = Column(String)
    act = Column(String)  # act1, act2a, act2b, act3
    beat_number = Column(Integer)  # Which 15-beat this covers
    word_count = Column(Integer)
    avg_tension = Column(Float)  # Average of scene tensions
    status = Column(String)  # draft, complete
    assembled_at = Column(DateTime)
    
    # Relationships
    scenes = relationship("Scene", back_populates="chapter", order_by="Scene.scene_number")

class Beat(Base):
    """Beat node - 15-beat structure tracking."""
    __tablename__ = "beats"
    
    id = Column(Integer, primary_key=True)
    beat_number = Column(Integer, unique=True, nullable=False)  # 1-15
    name = Column(String)  # "Opening Image", "Catalyst", etc.
    target_percentage = Column(Float)  # Expected % of manuscript
    actual_percentage = Column(Float, nullable=True)  # Actual % when reached
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), nullable=True)
    status = Column(String)  # planned, in_progress, complete
    
    # Relationships
    chapter = relationship("Chapter")

class TensionTrack(Base):
    """Tension tracking over story progression."""
    __tablename__ = "tension_tracks"
    
    id = Column(Integer, primary_key=True)
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), index=True)
    scene_id = Column(String, ForeignKey('scenes.scene_id'), index=True)
    sequence_number = Column(Integer)  # Global story sequence
    tension_value = Column(Float)  # 1-10
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter")
    scene = relationship("Scene")

class CharacterAppearance(Base):
    """Track character appearances in scenes."""
    __tablename__ = "character_appearances"
    
    id = Column(Integer, primary_key=True)
    character_name = Column(String, index=True)
    scene_id = Column(String, ForeignKey('scenes.scene_id'), index=True)
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), index=True)
    pov_character = Column(Boolean, default=False)
    line_count = Column(Integer, nullable=True)  # Approximate speaking lines
    
    # Relationships
    scene = relationship("Scene", back_populates="character_appearances")
    chapter = relationship("Chapter")

class FlawChallenge(Base):
    """Track when protagonist's Fatal Flaw is tested."""
    __tablename__ = "flaw_challenges"
    
    id = Column(Integer, primary_key=True)
    scene_id = Column(String, ForeignKey('scenes.scene_id'), index=True)
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), index=True)
    flaw_type = Column(String)  # Name of the flaw
    challenge_type = Column(String)  # test, failure, growth, triumph
    intensity = Column(Float)  # 1-10
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship("Scene")
    chapter = relationship("Chapter")

class SymbolOccurrence(Base):
    """Track thematic symbol recurrences."""
    __tablename__ = "symbol_occurrences"
    
    id = Column(Integer, primary_key=True)
    symbol_name = Column(String, index=True)
    scene_id = Column(String, ForeignKey('scenes.scene_id'), index=True)
    chapter_id = Column(String, ForeignKey('chapters.chapter_id'), index=True)
    meaning = Column(Text)  # How the symbol is used in this context
    evolution_stage = Column(String)  # introduction, development, transformation
    
    # Relationships
    scene = relationship("Scene")
    chapter = relationship("Chapter")
```

**Migration Script:**



```python
# backend/graph/migrations/add_health_tables.py
def upgrade(engine):
    Base.metadata.create_all(engine, tables=[
        Scene.__table__,
        Chapter.__table__,
        Beat.__table__,
        TensionTrack.__table__,
        CharacterAppearance.__table__,
        FlawChallenge.__table__,
        SymbolOccurrence.__table__,
    ])
```

------

### 📋 Task 2: Create Graph Health Service (4-5 hours)

**File to Create:** `backend/services/graph_health_service.py`

 

**Data Classes:**



```python
@dataclass
class HealthWarning:
    """A single health check warning."""
    check_type: str  # "pacing", "beat", "character", "theme", "timeline"
    severity: str  # "info", "warning", "error"
    title: str
    description: str
    affected_chapters: List[str]
    affected_entities: List[str]  # Character names, beat numbers, etc.
    recommendation: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class HealthReport:
    """Complete health check report."""
    report_id: str
    scope: str  # "chapter", "act", "manuscript"
    scope_identifier: str  # chapter_id, act name, or "full"
    timestamp: str
    warnings: List[HealthWarning]
    stats: Dict[str, Any]  # Overall statistics
    passed_checks: List[str]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "warnings": [w.to_dict() for w in self.warnings],
        }
```

**7 Health Check Algorithms:**



```python
class GraphHealthService:
    """
    Macro-level structural validation service.
    
    Runs asynchronous health checks on manuscript structure after
    chapter assembly or on-demand.
    """
    
    def __init__(
        self,
        graph_service: KnowledgeGraphService,
        project_id: Optional[str] = None,
    ):
        self.graph = graph_service
        self.project_id = project_id
        self._load_settings()
    
    def _load_settings(self):
        """Load health check thresholds from Settings Service."""
        try:
            health_config = settings_service.get_category("health_checks", self.project_id)
            
            # Pacing thresholds
            self.plateau_window = health_config.get("health_checks.pacing.plateau_window", 3)
            self.plateau_tolerance = health_config.get("health_checks.pacing.plateau_tolerance", 1.0)
            
            # Structure thresholds
            self.beat_deviation_warning = health_config.get("health_checks.structure.beat_deviation_warning", 5)
            self.beat_deviation_error = health_config.get("health_checks.structure.beat_deviation_error", 10)
            
            # Character thresholds
            self.flaw_challenge_frequency = health_config.get("health_checks.character.flaw_challenge_frequency", 10)
            self.min_cast_appearances = health_config.get("health_checks.character.min_cast_appearances", 3)
            
            # Theme thresholds
            self.min_symbol_occurrences = health_config.get("health_checks.theme.min_symbol_occurrences", 3)
            self.min_resonance_score = health_config.get("health_checks.theme.min_resonance_score", 6)
            
        except Exception as e:
            logger.error(f"Failed to load health check settings: {e}")
            # Use defaults from SETTINGS_CONFIGURATION.md
            self.plateau_window = 3
            self.plateau_tolerance = 1.0
            self.beat_deviation_warning = 5
            self.beat_deviation_error = 10
            self.flaw_challenge_frequency = 10
            self.min_cast_appearances = 3
            self.min_symbol_occurrences = 3
            self.min_resonance_score = 6
    
    # =========================================================================
    # A. Structural Integrity Checks
    # =========================================================================
    
    def check_pacing_plateaus(self, chapters: List[Chapter]) -> List[HealthWarning]:
        """
        Detect flat pacing across consecutive chapters.
        
        Algorithm:
        1. Get tension scores for each chapter (average of scene tensions)
        2. Use sliding window of N chapters (default: 3)
        3. Flag if max(window) - min(window) <= tolerance (default: 1.0)
        """
        warnings = []
        
        if len(chapters) < self.plateau_window:
            return warnings
        
        tension_scores = [ch.avg_tension for ch in chapters]
        
        for i in range(len(tension_scores) - self.plateau_window + 1):
            window = tension_scores[i:i + self.plateau_window]
            tension_range = max(window) - min(window)
            
            if tension_range <= self.plateau_tolerance:
                affected = chapters[i:i + self.plateau_window]
                warnings.append(HealthWarning(
                    check_type="pacing",
                    severity="warning",
                    title=f"Pacing Plateau Detected",
                    description=(
                        f"Chapters {affected[0].chapter_number}-{affected[-1].chapter_number} "
                        f"have flat tension (range: {tension_range:.1f}). "
                        f"Reader engagement may drop."
                    ),
                    affected_chapters=[ch.chapter_id for ch in affected],
                    affected_entities=[],
                    recommendation=(
                        "Consider escalating conflict or introducing a complication "
                        "to increase tension in the next scene."
                    )
                ))
        
        return warnings
    
    def check_beat_progress(self, beats: List[Beat], total_word_count: int) -> List[HealthWarning]:
        """
        Validate 15-beat structure compliance.
        
        Algorithm:
        1. For each completed beat, calculate actual_percentage
        2. Compare to target_percentage from Beat_Sheet.md
        3. Flag if deviation exceeds thresholds
        """
        warnings = []
        
        for beat in beats:
            if beat.status != "complete" or not beat.actual_percentage:
                continue
            
            deviation = abs(beat.actual_percentage - beat.target_percentage)
            
            if deviation >= self.beat_deviation_error:
                warnings.append(HealthWarning(
                    check_type="beat",
                    severity="error",
                    title=f"Beat {beat.beat_number} ({beat.name}) Severely Off Target",
                    description=(
                        f"Expected at {beat.target_percentage:.1f}% of manuscript, "
                        f"but reached at {beat.actual_percentage:.1f}% "
                        f"(deviation: {deviation:.1f}%)"
                    ),
                    affected_chapters=[beat.chapter_id] if beat.chapter_id else [],
                    affected_entities=[f"Beat {beat.beat_number}"],
                    recommendation=(
                        "Major structural issue. Consider restructuring chapters "
                        "or adjusting beat placement to align with story pacing."
                    )
                ))
            elif deviation >= self.beat_deviation_warning:
                warnings.append(HealthWarning(
                    check_type="beat",
                    severity="warning",
                    title=f"Beat {beat.beat_number} ({beat.name}) Off Target",
                    description=(
                        f"Expected at {beat.target_percentage:.1f}%, "
                        f"reached at {beat.actual_percentage:.1f}% "
                        f"(deviation: {deviation:.1f}%)"
                    ),
                    affected_chapters=[beat.chapter_id] if beat.chapter_id else [],
                    affected_entities=[f"Beat {beat.beat_number}"],
                    recommendation=(
                        "Minor timing issue. Monitor future beats to ensure "
                        "structure doesn't drift further."
                    )
                ))
        
        return warnings
    
    def check_timeline_consistency(self, scenes: List[Scene]) -> List[HealthWarning]:
        """
        Detect timeline conflicts and dropped threads.
        
        Algorithm:
        1. Parse World/Rules.md for established facts
        2. Track character locations and states across scenes
        3. Flag contradictions or unresolved setups
        
        NOTE: This is the most complex check and may need LLM assistance
        for semantic understanding of scene content.
        """
        warnings = []
        # TODO: Implement timeline tracking logic
        # This requires:
        # - Parsing scene content for location mentions
        # - Tracking character states (injured, aware of X, etc.)
        # - Detecting contradictions
        
        return warnings
    
    # =========================================================================
    # B. Character Arc Health Checks
    # =========================================================================
    
    def check_flaw_challenges(
        self,
        flaw_challenges: List[FlawChallenge],
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Monitor that protagonist's Fatal Flaw is regularly tested.
        
        Algorithm:
        1. Sort flaw challenges by chapter sequence
        2. Calculate gap between challenges (in chapter count)
        3. Flag if gap exceeds frequency threshold
        """
        warnings = []
        
        if not flaw_challenges:
            warnings.append(HealthWarning(
                check_type="character",
                severity="error",
                title="No Flaw Challenges Detected",
                description=(
                    "Protagonist's Fatal Flaw has not been tested in any scenes. "
                    "Character arc may feel flat or unearned."
                ),
                affected_chapters=[],
                affected_entities=["Protagonist"],
                recommendation=(
                    "Add scenes that force the protagonist to confront their flaw. "
                    "Reference Character.md for the Fatal Flaw definition."
                )
            ))
            return warnings
        
        # Sort by chapter number
        challenges_by_chapter = sorted(
            flaw_challenges,
            key=lambda fc: next(
                (ch.chapter_number for ch in chapters if ch.chapter_id == fc.chapter_id),
                0
            )
        )
        
        # Check gaps
        for i in range(len(challenges_by_chapter) - 1):
            current_ch_num = next(
                ch.chapter_number for ch in chapters 
                if ch.chapter_id == challenges_by_chapter[i].chapter_id
            )
            next_ch_num = next(
                ch.chapter_number for ch in chapters 
                if ch.chapter_id == challenges_by_chapter[i+1].chapter_id
            )
            
            gap = next_ch_num - current_ch_num
            
            if gap > self.flaw_challenge_frequency:
                warnings.append(HealthWarning(
                    check_type="character",
                    severity="warning",
                    title=f"Flaw Challenge Gap: {gap} Chapters",
                    description=(
                        f"Protagonist's flaw untested from Chapter {current_ch_num} "
                        f"to Chapter {next_ch_num}. Character growth may stall."
                    ),
                    affected_chapters=[
                        ch.chapter_id for ch in chapters 
                        if current_ch_num <= ch.chapter_number <= next_ch_num
                    ],
                    affected_entities=["Protagonist"],
                    recommendation=(
                        "Add a scene where the protagonist's flaw creates a problem "
                        "or prevents them from achieving a goal."
                    )
                ))
        
        return warnings
    
    def check_cast_function(
        self,
        character_appearances: List[CharacterAppearance],
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Verify supporting characters serve their story function.
        
        Algorithm:
        1. Group appearances by character
        2. Check if appearance count meets minimum threshold
        3. Flag characters with too few appearances
        """
        warnings = []
        
        # Group by character
        appearances_by_char = {}
        for app in character_appearances:
            if app.character_name not in appearances_by_char:
                appearances_by_char[app.character_name] = []
            appearances_by_char[app.character_name].append(app)
        
        for char_name, appearances in appearances_by_char.items():
            if len(appearances) < self.min_cast_appearances:
                warnings.append(HealthWarning(
                    check_type="character",
                    severity="info",
                    title=f"Character '{char_name}' Underutilized",
                    description=(
                        f"'{char_name}' appears in only {len(appearances)} scene(s). "
                        f"Consider whether this character is necessary or needs "
                        f"more development."
                    ),
                    affected_chapters=[app.chapter_id for app in appearances],
                    affected_entities=[char_name],
                    recommendation=(
                        "Either give this character a stronger role in the story "
                        "or consider removing them to reduce cast complexity."
                    )
                ))
        
        return warnings
    
    # =========================================================================
    # C. Thematic Health Checks
    # =========================================================================
    
    def check_symbolic_layering(
        self,
        symbol_occurrences: List[SymbolOccurrence],
        chapters: List[Chapter]
    ) -> List[HealthWarning]:
        """
        Track symbol recurrence and meaning evolution.
        
        Algorithm:
        1. Group occurrences by symbol name
        2. Check recurrence count meets minimum
        3. Verify meaning evolves (not static)
        """
        warnings = []
        
        # Group by symbol
        occurrences_by_symbol = {}
        for occ in symbol_occurrences:
            if occ.symbol_name not in occurrences_by_symbol:
                occurrences_by_symbol[occ.symbol_name] = []
            occurrences_by_symbol[occ.symbol_name].append(occ)
        
        for symbol_name, occurrences in occurrences_by_symbol.items():
            # Check recurrence
            if len(occurrences) < self.min_symbol_occurrences:
                warnings.append(HealthWarning(
                    check_type="theme",
                    severity="info",
                    title=f"Symbol '{symbol_name}' Insufficient Recurrence",
                    description=(
                        f"'{symbol_name}' appears {len(occurrences)} time(s). "
                        f"Thematic symbols need repetition to resonate."
                    ),
                    affected_chapters=[occ.chapter_id for occ in occurrences],
                    affected_entities=[symbol_name],
                    recommendation=(
                        "Add 1-2 more instances of this symbol, showing how its "
                        "meaning evolves as the character grows."
                    )
                ))
            
            # Check evolution stages
            stages = {occ.evolution_stage for occ in occurrences}
            if len(stages) == 1 and len(occurrences) >= 3:
                warnings.append(HealthWarning(
                    check_type="theme",
                    severity="warning",
                    title=f"Symbol '{symbol_name}' Static Meaning",
                    description=(
                        f"'{symbol_name}' appears {len(occurrences)} times but "
                        f"meaning doesn't evolve. Symbol should transform with character."
                    ),
                    affected_chapters=[occ.chapter_id for occ in occurrences],
                    affected_entities=[symbol_name],
                    recommendation=(
                        "Show how the symbol's meaning changes: introduction → "
                        "development → transformation as protagonist's worldview shifts."
                    )
                ))
        
        return warnings
    
    def check_theme_resonance(
        self,
        chapters: List[Chapter],
        beats: List[Beat],
        theme_statement: str
    ) -> List[HealthWarning]:
        """
        Assess theme resonance at critical structural beats.
        
        Algorithm:
        1. Identify critical beats (2: Catalyst, 6: Midpoint, 12: All Is Lost, 15: Resolution)
        2. For chapters covering these beats, assess theme resonance
        3. Flag if resonance score < threshold
        
        NOTE: This requires LLM analysis of scene content against theme
        """
        warnings = []
        
        critical_beats = [2, 6, 12, 15]
        
        for beat_num in critical_beats:
            beat = next((b for b in beats if b.beat_number == beat_num), None)
            if not beat or not beat.chapter_id:
                continue
            
            # TODO: Implement theme resonance scoring
            # This requires:
            # - Loading scenes from the beat's chapter
            # - LLM analysis: "Does this scene reinforce the theme?"
            # - Scoring 1-10
            
            resonance_score = 5  # Placeholder
            
            if resonance_score < self.min_resonance_score:
                chapter = next((ch for ch in chapters if ch.chapter_id == beat.chapter_id), None)
                warnings.append(HealthWarning(
                    check_type="theme",
                    severity="warning",
                    title=f"Weak Theme Resonance at Beat {beat_num} ({beat.name})",
                    description=(
                        f"Critical story beat has low theme resonance (score: {resonance_score}/10). "
                        f"Theme: '{theme_statement}'"
                    ),
                    affected_chapters=[beat.chapter_id],
                    affected_entities=[f"Beat {beat_num}"],
                    recommendation=(
                        "Strengthen the connection between this pivotal moment and "
                        "the central theme. The theme should be most visible at critical beats."
                    )
                ))
        
        return warnings
    
    # =========================================================================
    # Main Health Check Entry Points
    # =========================================================================
    
    async def check_chapter_health(self, chapter_id: str) -> HealthReport:
        """Run health checks for a single chapter."""
        # Implementation
        pass
    
    async def check_act_health(self, act_name: str) -> HealthReport:
        """Run health checks for an act (act1, act2a, act2b, act3)."""
        # Implementation
        pass
    
    async def check_manuscript_health(self) -> HealthReport:
        """Run all health checks across entire manuscript."""
        warnings = []
        
        # Load all data from graph
        chapters = self.graph.get_all_chapters()
        scenes = self.graph.get_all_scenes()
        beats = self.graph.get_all_beats()
        flaw_challenges = self.graph.get_all_flaw_challenges()
        character_appearances = self.graph.get_all_character_appearances()
        symbol_occurrences = self.graph.get_all_symbol_occurrences()
        
        # Run all checks
        warnings.extend(self.check_pacing_plateaus(chapters))
        warnings.extend(self.check_beat_progress(beats, sum(ch.word_count for ch in chapters)))
        warnings.extend(self.check_flaw_challenges(flaw_challenges, chapters))
        warnings.extend(self.check_cast_function(character_appearances, chapters))
        warnings.extend(self.check_symbolic_layering(symbol_occurrences, chapters))
        
        # Load theme from Story Bible
        theme_statement = self.graph.get_theme_statement()
        warnings.extend(self.check_theme_resonance(chapters, beats, theme_statement))
        
        # Compile stats
        stats = {
            "total_chapters": len(chapters),
            "total_scenes": len(scenes),
            "total_words": sum(ch.word_count for ch in chapters),
            "beats_complete": len([b for b in beats if b.status == "complete"]),
            "avg_tension": sum(ch.avg_tension for ch in chapters) / len(chapters) if chapters else 0,
        }
        
        # Passed checks
        passed = []
        if not any(w.check_type == "pacing" for w in warnings):
            passed.append("Pacing healthy - no plateaus detected")
        if not any(w.check_type == "beat" for w in warnings):
            passed.append("Beat structure on track")
        # ... etc
        
        return HealthReport(
            report_id=f"health_{datetime.utcnow().isoformat()}",
            scope="manuscript",
            scope_identifier="full",
            timestamp=datetime.utcnow().isoformat(),
            warnings=warnings,
            stats=stats,
            passed_checks=passed,
        )
```

------

### 📋 Task 3: Integrate with Chapter Assembly & Foreman (2-3 hours)

**File to Modify:** `backend/agents/foreman.py`

 

**Add Health Check Trigger:**



```python
async def on_chapter_complete(self, chapter_id: str):
    """
    Triggered when all scenes in a chapter are marked complete.
    
    Workflow:
    1. Assemble chapter (combine scenes)
    2. Calculate chapter-level stats (avg tension, word count)
    3. Trigger Graph Health Service check
    4. If warnings found, present to writer with guidance
    """
    # Assemble chapter
    chapter = await self.assemble_chapter(chapter_id)
    
    # Run health check
    health_service = get_graph_health_service(project_id=self.project_id)
    health_report = await health_service.check_chapter_health(chapter_id)
    
    # If warnings, guide the writer
    if health_report.warnings:
        severity_counts = {
            "error": len([w for w in health_report.warnings if w.severity == "error"]),
            "warning": len([w for w in health_report.warnings if w.severity == "warning"]),
            "info": len([w for w in health_report.warnings if w.severity == "info"]),
        }
        
        message = f"Chapter {chapter.chapter_number} complete, but health check found:\n"
        message += f"- {severity_counts['error']} errors\n"
        message += f"- {severity_counts['warning']} warnings\n"
        message += f"- {severity_counts['info']} info items\n\n"
        
        # Show top 3 most severe warnings
        top_warnings = sorted(
            health_report.warnings,
            key=lambda w: {"error": 0, "warning": 1, "info": 2}[w.severity]
        )[:3]
        
        for warning in top_warnings:
            message += f"**{warning.title}**\n"
            message += f"{warning.description}\n"
            message += f"→ {warning.recommendation}\n\n"
        
        # Store in KB for context
        self.kb_service.write_entry(
            project_id=self.project_id,
            category="health_check",
            key=f"chapter_{chapter_id}_health",
            value=health_report.to_dict(),
        )
        
        return {
            "status": "complete_with_warnings",
            "chapter_id": chapter_id,
            "message": message,
            "health_report": health_report.to_dict(),
        }
    else:
        return {
            "status": "complete",
            "chapter_id": chapter_id,
            "message": f"Chapter {chapter.chapter_number} complete. All health checks passed!",
        }
```

**Add Foreman Action Handlers:**



```python
# In foreman.py action handlers section

async def _handle_check_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle manual health check request.
    
    Params:
        scope: "chapter", "act", or "manuscript"
        scope_id: chapter_id, act name, or None
    """
    scope = params.get("scope", "manuscript")
    scope_id = params.get("scope_id")
    
    health_service = get_graph_health_service(project_id=self.project_id)
    
    if scope == "chapter":
        report = await health_service.check_chapter_health(scope_id)
    elif scope == "act":
        report = await health_service.check_act_health(scope_id)
    else:
        report = await health_service.check_manuscript_health()
    
    return {
        "action": "check_health",
        "scope": scope,
        "report": report.to_dict(),
    }
```

------

### 📋 Task 4: Health Report Data Classes & Export (1-2 hours)

**Already defined in Task 2** - Just add export methods:



```python
# In graph_health_service.py

def export_health_report_markdown(self, report: HealthReport) -> str:
    """
    Export health report as formatted markdown.
    
    Returns:
        Markdown string suitable for display or file export
    """
    md = f"# Health Report: {report.scope.title()}\n\n"
    md += f"**Generated:** {report.timestamp}\n"
    md += f"**Scope:** {report.scope_identifier}\n\n"
    
    md += "## Statistics\n\n"
    for key, value in report.stats.items():
        md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
    
    md += "\n## Warnings\n\n"
    
    if not report.warnings:
        md += "*No warnings detected. All health checks passed!*\n\n"
    else:
        # Group by severity
        errors = [w for w in report.warnings if w.severity == "error"]
        warnings = [w for w in report.warnings if w.severity == "warning"]
        infos = [w for w in report.warnings if w.severity == "info"]
        
        if errors:
            md += "### 🔴 Errors\n\n"
            for warning in errors:
                md += f"**{warning.title}**\n\n"
                md += f"{warning.description}\n\n"
                md += f"*Recommendation:* {warning.recommendation}\n\n"
                md += "---\n\n"
        
        if warnings:
            md += "### 🟡 Warnings\n\n"
            for warning in warnings:
                md += f"**{warning.title}**\n\n"
                md += f"{warning.description}\n\n"
                md += f"*Recommendation:* {warning.recommendation}\n\n"
                md += "---\n\n"
        
        if infos:
            md += "### ℹ️ Info\n\n"
            for warning in infos:
                md += f"**{warning.title}**\n\n"
                md += f"{warning.description}\n\n"
                md += f"*Recommendation:* {warning.recommendation}\n\n"
                md += "---\n\n"
    
    md += "## Passed Checks\n\n"
    for check in report.passed_checks:
        md += f"- ✅ {check}\n"
    
    return md
```

------

### 📋 Task 5: Add API Endpoints (2 hours)

**File to Modify:** `backend/api.py`

 

**Pydantic Models:**



```python
class HealthCheckRequest(BaseModel):
    scope: str  # "chapter", "act", "manuscript"
    scope_id: Optional[str] = None  # chapter_id or act name
    project_id: Optional[str] = None

class HealthReportExportRequest(BaseModel):
    report_id: str
    format: str = "markdown"  # markdown, json, pdf (future)
```

**Endpoints:**



```python
# ============================================================================
# GRAPH HEALTH API
# ============================================================================

@app.post("/health/check", summary="Run health check")
async def run_health_check(request: HealthCheckRequest):
    """
    Run health checks on manuscript structure.
    
    Scope options:
    - "chapter": Check single chapter (requires scope_id)
    - "act": Check entire act (requires scope_id like "act2a")
    - "manuscript": Check entire manuscript
    
    Examples:
        POST /health/check {"scope": "manuscript"}
        POST /health/check {"scope": "chapter", "scope_id": "ch_001"}
        POST /health/check {"scope": "act", "scope_id": "act2a"}
    """
    try:
        health_service = get_graph_health_service(request.project_id)
        
        if request.scope == "chapter":
            if not request.scope_id:
                raise HTTPException(400, "scope_id required for chapter health check")
            report = await health_service.check_chapter_health(request.scope_id)
        
        elif request.scope == "act":
            if not request.scope_id:
                raise HTTPException(400, "scope_id required for act health check")
            report = await health_service.check_act_health(request.scope_id)
        
        else:  # manuscript
            report = await health_service.check_manuscript_health()
        
        return report.to_dict()
    
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        raise HTTPException(500, f"Health check failed: {str(e)}")


@app.get("/health/report/{report_id}", summary="Get health report")
async def get_health_report(report_id: str):
    """
    Retrieve a previously generated health report.
    
    Reports are cached in the knowledge graph for retrieval.
    """
    try:
        # TODO: Implement report caching/retrieval
        raise HTTPException(501, "Health report retrieval not yet implemented")
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/health/export", summary="Export health report")
async def export_health_report(request: HealthReportExportRequest):
    """
    Export health report in specified format.
    
    Formats:
    - "markdown": Formatted markdown
    - "json": Raw JSON
    - "pdf": PDF report (future)
    """
    try:
        health_service = get_graph_health_service()
        
        # TODO: Load report by ID
        # For now, return placeholder
        
        if request.format == "markdown":
            markdown = health_service.export_health_report_markdown(report)
            return {"format": "markdown", "content": markdown}
        
        elif request.format == "json":
            return {"format": "json", "content": report.to_dict()}
        
        else:
            raise HTTPException(400, f"Unsupported format: {request.format}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# Singleton access
_graph_health_service: Optional[GraphHealthService] = None

def get_graph_health_service(project_id: Optional[str] = None) -> GraphHealthService:
    """Get or create the GraphHealthService singleton."""
    global _graph_health_service
    if _graph_health_service is None:
        graph_service = get_knowledge_graph_service()
        _graph_health_service = GraphHealthService(graph_service, project_id)
    return _graph_health_service
```

------

## Dependencies & Integration Points

### Phase 3C Integration (Settings Service) ✅

- Health check thresholds loaded from `settings_service.get_category("health_checks")`
- Configurable via `voice_settings.yaml` or global settings
- All thresholds have sensible defaults

### Knowledge Graph Integration ✅

- Extends existing `backend/graph/schema.py`
- Uses existing `KnowledgeGraphService` for queries
- SQLite persistence (same database)

### Foreman Integration

- Auto-trigger on chapter completion
- Manual trigger via `/check-health` command
- Results written to Foreman KB for context

### Story Bible Integration

- Loads theme statement for resonance checks
- References Character.md for Fatal Flaw
- Uses Beat_Sheet.md for structure validation

------

## Testing Strategy

### Unit Tests

```python
# tests/test_graph_health_service.py

def test_pacing_plateau_detection():
    """Test that flat tension windows are detected."""
    chapters = [
        Chapter(chapter_number=1, avg_tension=5.0),
        Chapter(chapter_number=2, avg_tension=5.2),
        Chapter(chapter_number=3, avg_tension=5.1),  # Plateau
        Chapter(chapter_number=4, avg_tension=7.0),
    ]
    
    health_service = GraphHealthService(mock_graph)
    warnings = health_service.check_pacing_plateaus(chapters)
    
    assert len(warnings) == 1
    assert warnings[0].check_type == "pacing"
    assert "Plateau" in warnings[0].title

def test_beat_deviation_warning():
    """Test that beat structure warnings work."""
    beats = [
        Beat(beat_number=2, target_percentage=10.0, actual_percentage=15.0),  # 5% off
    ]
    
    health_service = GraphHealthService(mock_graph)
    health_service.beat_deviation_warning = 3  # Trigger at 3%
    
    warnings = health_service.check_beat_progress(beats, 100000)
    
    assert len(warnings) == 1
    assert warnings[0].severity == "warning"

def test_flaw_challenge_gap():
    """Test flaw challenge monitoring."""
    # Simulate 12-chapter gap
    flaw_challenges = [
        FlawChallenge(chapter_id="ch_1"),
        FlawChallenge(chapter_id="ch_13"),  # 12 chapters later
    ]
    
    health_service = GraphHealthService(mock_graph)
    health_service.flaw_challenge_frequency = 10  # Max 10 chapters between
    
    warnings = health_service.check_flaw_challenges(flaw_challenges, mock_chapters)
    
    assert len(warnings) == 1
    assert "Gap" in warnings[0].title
```

### Integration Tests

```python
def test_full_manuscript_health_check():
    """Test complete health check workflow."""
    # Setup: Create test manuscript in graph
    # ...
    
    health_service = GraphHealthService(graph_service)
    report = await health_service.check_manuscript_health()
    
    assert report.scope == "manuscript"
    assert len(report.warnings) >= 0
    assert len(report.stats) > 0
```

------

## Success Criteria

-  All 7 health check algorithms implemented and tested
-  Knowledge Graph schema extended with new node types
-  Settings Service integration complete (thresholds configurable)
-  Foreman auto-triggers health check after chapter assembly
-  API endpoints functional (`/health/check/*`)
-  Health reports exportable as markdown
-  No breaking changes to existing Phase 3B functionality
-  Documentation updated with health check descriptions

------

## Deliverables

1. **Code:**
   - `backend/services/graph_health_service.py` (new)
   - `backend/graph/schema.py` (extended)
   - `backend/graph/migrations/add_health_tables.py` (new)
   - `backend/agents/foreman.py` (modified)
   - `backend/api.py` (modified - 3 new endpoints)
2. **Documentation:**
   - Update `docs/04_roadmap.md` (mark Phase 3D complete)
   - Update `docs/specs/DIRECTOR_MODE_SPECIFICATION.md` (add health checks section)
   - Create `docs/HEALTH_CHECKS.md` (user-facing guide)
3. **Tests:**
   - `tests/test_graph_health_service.py`
   - `tests/integration/test_health_workflow.py`

------

## Estimated Timeline

| Task                          | Hours           | Priority           |
| ----------------------------- | --------------- | ------------------ |
| Task 1: Extend Graph Schema   | 3-4             | P0 (foundation)    |
| Task 2: Create Health Service | 4-5             | P0 (core logic)    |
| Task 3: Foreman Integration   | 2-3             | P1 (UX)            |
| Task 4: Health Report Export  | 1-2             | P2 (nice-to-have)  |
| Task 5: API Endpoints         | 2               | P1 (accessibility) |
| **Total**                     | **12-15 hours** |                    |

------

## Open Questions for User

1. **Timeline Consistency Check:** This is the most complex algorithm and may require LLM assistance to parse scene content semantically. Should we implement a simplified version first, or go full LLM-powered analysis?
2. **Theme Resonance Scoring:** Should this use automated LLM scoring or manual writer assessment? LLM = automated but less accurate, Manual = accurate but requires writer input.
3. **Health Check Frequency:** Should we auto-run after every chapter, or only when writer requests? Auto = proactive, Manual = less interruption.
4. **Report Storage:** Should health reports be stored in SQLite for history, or just generated on-demand? History = useful trends, On-demand = simpler.

Ready to begin implementation once you approve this plan! 🚀