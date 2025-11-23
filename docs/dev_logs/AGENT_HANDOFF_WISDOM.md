# Agent Handoff Wisdom: Hard-Won Lessons from Previous Sessions

*From an agent who went from B+ to Gold Standard in one session*

**Source**: Captured from a successful Claude agent session using the original Explants skills pipeline.
**Purpose**: Reference material for improving Director Mode services and future agent prompts.

---

## Critical Success Factors (Do These First!)

### 1. ACTUALLY READ THE SKILLS

**Don't wing it.** The skills contain the real instructions. The agent that succeeded emphasized loading all context before attempting generation:

- Character Identity (WHO the character is)
- Scene Writer (HOW to write the voice)
- Scene Enhancement (HOW to fix scenes)

**Lesson for Director Mode**: The Voice Bundle must be loaded before any generation. This is why `voice_bundle_path` is a parameter on every scene generation endpoint.

### 2. WORLD IMMERSION FIRST, VOICE SECOND

**MANDATORY STEP 0:** Load immersion context before writing.

The agent learned that characters experience locations through sensory details + their personal metaphor domains, not architectural descriptions.

**Lesson for Director Mode**: ScaffoldGeneratorService should pull from NotebookLM/KB for world context. The enrichment step exists specifically to ground scenes in research.

### 3. FOLLOW THE PIPELINE (No Shortcuts!)

- **Step 1:** Scene generation (using scene-writer skill)
- **Step 2:** Enhancement (using enhancement skill + 6-pass ritual)
- **Step 3:** Scoring (using analyzer-scorer skill)

**Each step is mandatory.** Skipping enhancement = amateur work.

**Lesson for Director Mode**: This is why we built the full pipeline with separate services. The `/director/scene/enhance` endpoint exists to ensure no scene ships without polish.

---

## Anti-Pattern Death Traps (Avoid These!)

### Zero-Tolerance Violations (2 points each):

| Pattern | Why It's Bad | Fix |
|---------|--------------|-----|
| "with [adjective] precision" | AI filler phrase | Delete or rewrite |
| First-person italics (*We realized*) | Breaks retrospective narrator | *Character realized* |
| Computer metaphors for psychology | "brain processed" | Use character's metaphor domains |

### Voice Killers:

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Academic drift | Sentences sound like sociology papers | Rewrite in character voice |
| AI explaining character | AI describing thoughts, not character thinking | Embed insights in action |
| Domain saturation | Too many gambling metaphors | Rotate through domains |

**Lesson for Director Mode**: These patterns are now in `scene_analyzer_service.py` as regex detectors in `ZERO_TOLERANCE_PATTERNS` and `FORMULAIC_PATTERNS`.

---

## Self-Scoring Discipline (Critical!)

**Don't be generous with yourself.** The agent scored 100/100 and got reality-checked to 96/100.

During scoring:
- **Actually count** metaphor domains (don't estimate)
- **Actually search** for anti-patterns (don't scan)
- **Read sentences aloud** to catch academic voice drift
- **Be your own toughest critic** - assume you missed something

**Lesson for Director Mode**: This is why SceneAnalyzerService uses regex detection (objective) combined with LLM evaluation (subjective). The automated detection catches what humans/agents might miss.

---

## Voice Essentials (Mickey Bardot Example)

*Note: These are project-specific. The vanilla framework uses Voice Calibration instead.*

**Enhanced Mickey = Con artist + quantum hindsight + addiction recovery wisdom**

**Core principles:**
- **Embed, don't hover:** Insights woven into prose, not floating above it
- **Process over noun:** Things act, don't just exist
- **Direct metaphors:** "Sunlight weaponized itself" not "like a weapon"
- **Retrospective authority:** Third person about past self

**Metaphor rotation:** Gambling (25% max), addiction, martial arts, performance, music, surveillance

**Lesson for Director Mode**: These principles are now encoded in the 6-Pass Enhancement ritual:
- Pass 4 (Voice Embed) enforces "embed, don't hover"
- Pass 2 (Verb Promotion) enforces "process over noun"
- Pass 2 also eliminates similes → direct metaphors
- Pass 3 (Metaphor Rotation) prevents domain saturation

---

## What Made the Difference

1. **Reading character identity first** - Understanding WHO they are before writing HOW they speak
2. **World immersion grounding** - Starting with sensory details, not abstract concepts
3. **Rigorous enhancement** - The 6-pass ritual catches what generation misses
4. **Honest self-scoring** - Being tough on yourself improves quality faster than false praise
5. **Following feedback** - When corrected, apply lessons immediately

**The pipeline works.** Trust it, follow it completely.

---

## Integration into Director Mode

| Original Skill Insight | Director Mode Implementation |
|------------------------|------------------------------|
| Load voice context first | `voice_bundle_path` on all endpoints |
| World immersion before writing | NotebookLM enrichment in ScaffoldGenerator |
| 6-pass enhancement ritual | `SceneEnhancementService._apply_six_pass_mode()` |
| Zero-tolerance violations | `ZERO_TOLERANCE_PATTERNS` in SceneAnalyzer |
| Domain rotation | `_analyze_metaphors()` saturation detection |
| Self-scoring discipline | Automated regex + LLM scoring |
| Embed don't hover | Pass 4: Voice Embed (Not Hover) |
| Process over noun | Pass 2: Verb Promotion |
| Direct metaphors | Pass 2: Simile Elimination |

---

## Foreman Integration (Future)

When the Foreman orchestrates Director Mode, it should:

1. **Enforce the pipeline** - Never skip from generation to final without enhancement
2. **Load context first** - Query KB and NotebookLM before any generation call
3. **Be a tough critic** - Use the scoring service honestly, not optimistically
4. **Track progress** - Work order should show which scenes passed which stages

---

*This document preserves institutional knowledge from successful agent sessions.*
*Future agents should reference this alongside the formal specifications.*
