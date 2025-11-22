# Scoring Rubrics Specification

**Version**: 1.0
**Status**: Draft
**Related**: ARCHITECTURE.md, Voice Consistency Tester (writers-factory-core)

---

## Problem Statement

The Writers Factory needs objective quality metrics to:

1. Compare scene variants from multiple AI models
2. Track manuscript quality over time
3. Identify specific improvement areas
4. Maintain voice consistency across the novel

This spec defines the scoring rubrics and Critic Agent prompts for Stage 5 (Scoring) of the workflow pipeline.

---

## Scoring Dimensions

### Overview

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Voice Consistency | 25 | Adherence to established character/narrative voice |
| Metaphor Discipline | 25 | Coherent domain usage, no mixed metaphors |
| Anti-Pattern Compliance | 20 | Avoiding known bad patterns |
| Structural Requirements | 20 | Scene beats, Goal/Conflict/Outcome |
| Scene Functionality | 10 | Serves the story purpose |

**Total: 100 points**

---

## Dimension 1: Voice Consistency (25 points)

### Rubric

| Score | Criteria |
|-------|----------|
| 25 | Perfect adherence to voice guide; indistinguishable from reference scenes |
| 20-24 | Minor deviations; 1-2 phrases feel slightly off |
| 15-19 | Noticeable inconsistencies; 3-5 passages diverge from voice |
| 10-14 | Significant voice drift; character sounds different |
| 0-9 | Voice not recognizable; sounds like different author |

### Critic Prompt

```
You are a Voice Consistency Critic for a novel-writing system.

VOICE REFERENCE:
{voice_guide}

REFERENCE SCENES (examples of correct voice):
{reference_scenes}

SCENE TO EVALUATE:
{scene_content}

Evaluate this scene's voice consistency on a scale of 0-25.

Consider:
1. Sentence rhythm and length patterns
2. Vocabulary level and word choices
3. POV adherence (internal vs external observation)
4. Emotional temperature
5. Characteristic phrases or patterns from reference

Provide:
- SCORE: [0-25]
- VOICE DRIFT LOCATIONS: [Quote specific passages that diverge]
- ANALYSIS: [Why these passages don't match the voice]
- FIXES: [How to revise for voice consistency]
```

---

## Dimension 2: Metaphor Discipline (25 points)

### Rubric

| Score | Criteria |
|-------|----------|
| 25 | All metaphors from allowed domains; beautifully coherent |
| 20-24 | Consistent domains; 1 minor domain stretch |
| 15-19 | 2-3 mixed metaphors or domain violations |
| 10-14 | Frequent mixing; metaphors clash with each other |
| 0-9 | Chaotic metaphor usage; no discipline apparent |

### Allowed Metaphor Domains (Configurable per Project)

```yaml
# config/metaphor_domains.yaml
project: "The Explants"
allowed_domains:
  - quantum_mechanics:
      terms: [entanglement, superposition, wave function, collapse, uncertainty]
      usage: "For consciousness and identity concepts"
  - organic_biology:
      terms: [roots, growth, symbiosis, metabolism, decay]
      usage: "For relationships and development"
  - architecture:
      terms: [foundation, scaffold, framework, structure, collapse]
      usage: "For mental states and plans"
  - water:
      terms: [flow, current, depth, surface, drowning]
      usage: "For emotions and time"

forbidden_domains:
  - military: "Too aggressive for this voice"
  - sports: "Not in character vocabulary"
  - corporate: "Breaks the philosophical tone"
```

### Critic Prompt

```
You are a Metaphor Discipline Critic for a novel-writing system.

ALLOWED METAPHOR DOMAINS:
{allowed_domains}

FORBIDDEN DOMAINS:
{forbidden_domains}

SCENE TO EVALUATE:
{scene_content}

Evaluate metaphor discipline on a scale of 0-25.

Tasks:
1. Identify ALL metaphors and figurative language in the scene
2. Categorize each by domain
3. Flag any that violate allowed/forbidden rules
4. Flag any mixed metaphors (combining incompatible domains)

Provide:
- SCORE: [0-25]
- METAPHOR INVENTORY:
  - "[metaphor text]" → Domain: [domain], Status: [OK/VIOLATION]
- MIXED METAPHORS: [List any that clash]
- FIXES: [Alternative metaphors from allowed domains]
```

---

## Dimension 3: Anti-Pattern Compliance (20 points)

### Rubric

| Score | Criteria |
|-------|----------|
| 20 | No anti-patterns detected |
| 15-19 | 1-2 minor anti-patterns |
| 10-14 | 3-5 anti-patterns or 1-2 severe ones |
| 5-9 | Multiple severe anti-patterns |
| 0-4 | Riddled with anti-patterns |

### Anti-Pattern Catalog

```yaml
# config/anti_patterns.yaml

severe:
  - name: "Head-Hopping"
    description: "POV shifts within scene without clear break"
    detection: "Multiple characters' internal thoughts in same scene"
    penalty: -5

  - name: "Telling Emotions"
    description: "Stating emotions instead of showing"
    examples: ["She felt sad", "He was angry", "They were scared"]
    penalty: -3

  - name: "Purple Prose"
    description: "Overwritten, flowery language that obscures meaning"
    indicators: ["3+ adjectives per noun", "nested metaphors"]
    penalty: -4

moderate:
  - name: "Filter Words"
    description: "Unnecessary narrative distance"
    examples: ["She saw", "He heard", "They noticed", "She felt"]
    penalty: -2

  - name: "Dialogue Tags Overload"
    description: "Excessive or creative dialogue tags"
    examples: ["he exclaimed", "she pontificated", "they ejaculated"]
    penalty: -2

  - name: "Repetitive Structure"
    description: "Same sentence structure 3+ times consecutively"
    penalty: -1

minor:
  - name: "Adverb Overuse"
    description: "More than 2 -ly adverbs per paragraph"
    penalty: -1

  - name: "Weak Verbs"
    description: "Overuse of was/were/had/have"
    penalty: -1
```

### Critic Prompt

```
You are an Anti-Pattern Critic for a novel-writing system.

ANTI-PATTERN CATALOG:
{anti_pattern_catalog}

SCENE TO EVALUATE:
{scene_content}

Detect and catalog all anti-patterns in this scene.

Provide:
- SCORE: [0-20] (start at 20, subtract penalties)
- VIOLATIONS:
  - Line [N]: "[quote]" → Pattern: [name], Severity: [severe/moderate/minor], Penalty: [-N]
- TOTAL PENALTY: [sum of penalties, cap at -20]
- FIXES: [How to revise each violation]
```

---

## Dimension 4: Structural Requirements (20 points)

### Rubric

| Score | Criteria |
|-------|----------|
| 20 | All structural elements present and well-executed |
| 15-19 | Minor structural weakness in 1 element |
| 10-14 | 1-2 elements missing or poorly executed |
| 5-9 | Major structural issues; scene lacks direction |
| 0-4 | No discernible structure |

### Required Elements

1. **Goal** (5 points): POV character wants something specific
2. **Conflict** (5 points): Something opposes the goal
3. **Outcome** (5 points): Yes/No/Yes-But/No-And resolution
4. **Beat Alignment** (5 points): Scene serves its designated beat

### Critic Prompt

```
You are a Structure Critic for a novel-writing system.

SCENE STRATEGY (from Story Bible):
Goal: {goal}
Conflict: {conflict}
Expected Outcome: {outcome}
Beat Connection: {beat}

SCENE TO EVALUATE:
{scene_content}

Evaluate structural requirements on a scale of 0-20.

Score each element (0-5):
1. GOAL: Is the POV character's want clear and present?
2. CONFLICT: Is opposition to the goal shown?
3. OUTCOME: Does the scene resolve with a clear outcome?
4. BEAT: Does the scene serve its designated beat?

Provide:
- GOAL SCORE: [0-5] - [explanation]
- CONFLICT SCORE: [0-5] - [explanation]
- OUTCOME SCORE: [0-5] - [explanation]
- BEAT SCORE: [0-5] - [explanation]
- TOTAL: [0-20]
- MISSING ELEMENTS: [What needs to be added]
```

---

## Dimension 5: Scene Functionality (10 points)

### Rubric

| Score | Criteria |
|-------|----------|
| 10 | Scene is essential; removing it would damage the story |
| 7-9 | Scene serves clear purpose; minor fat could be trimmed |
| 4-6 | Scene partially functional; significant filler |
| 1-3 | Mostly filler; could be summarized in one paragraph |
| 0 | Scene serves no purpose; should be cut |

### Functionality Criteria

1. **Plot Advancement** (3 points): Events that matter
2. **Character Development** (3 points): Arc progress, flaw challenge
3. **Information Delivery** (2 points): Reader learns something necessary
4. **Tension/Stakes** (2 points): Stakes raised or maintained

### Critic Prompt

```
You are a Scene Functionality Critic for a novel-writing system.

STORY CONTEXT:
Current Beat: {current_beat}
Protagonist's Fatal Flaw: {fatal_flaw}
The Lie: {the_lie}

SCENE TO EVALUATE:
{scene_content}

Evaluate scene functionality on a scale of 0-10.

Consider:
1. PLOT (0-3): What plot-relevant events occur?
2. CHARACTER (0-3): How does this challenge/develop the protagonist?
3. INFORMATION (0-2): What essential information is delivered?
4. STAKES (0-2): How are stakes established/maintained?

Provide:
- PLOT SCORE: [0-3] - [what advances]
- CHARACTER SCORE: [0-3] - [arc progress]
- INFORMATION SCORE: [0-2] - [what's learned]
- STAKES SCORE: [0-2] - [tension level]
- TOTAL: [0-10]
- CUT TEST: Could this scene be cut? What would be lost?
```

---

## Aggregate Scoring

### Scene Score Calculation

```python
# backend/services/scoring_service.py
from dataclasses import dataclass

@dataclass
class SceneScore:
    voice_consistency: int      # 0-25
    metaphor_discipline: int    # 0-25
    anti_pattern: int          # 0-20
    structure: int             # 0-20
    functionality: int         # 0-10

    @property
    def total(self) -> int:
        return (
            self.voice_consistency +
            self.metaphor_discipline +
            self.anti_pattern +
            self.structure +
            self.functionality
        )

    @property
    def grade(self) -> str:
        total = self.total
        if total >= 90: return 'A'
        if total >= 80: return 'B'
        if total >= 70: return 'C'
        if total >= 60: return 'D'
        return 'F'

    @property
    def weakest_dimension(self) -> str:
        scores = {
            'Voice Consistency': self.voice_consistency / 25,
            'Metaphor Discipline': self.metaphor_discipline / 25,
            'Anti-Pattern': self.anti_pattern / 20,
            'Structure': self.structure / 20,
            'Functionality': self.functionality / 10,
        }
        return min(scores, key=scores.get)


class ScoringService:
    """
    Orchestrates scoring across all dimensions.
    Uses LLM as Critic for each dimension.
    """

    def __init__(self, critic_model: str = 'claude-sonnet-4-5'):
        self.critic_model = critic_model
        self.prompts = self._load_prompts()

    async def score_scene(
        self,
        scene_content: str,
        context: dict  # voice_guide, reference_scenes, scene_strategy, etc.
    ) -> SceneScore:
        """
        Score a scene across all dimensions.

        Runs all 5 critics and aggregates results.
        """
        # Run critics in parallel
        results = await asyncio.gather(
            self._run_voice_critic(scene_content, context),
            self._run_metaphor_critic(scene_content, context),
            self._run_antipattern_critic(scene_content, context),
            self._run_structure_critic(scene_content, context),
            self._run_functionality_critic(scene_content, context),
        )

        return SceneScore(
            voice_consistency=results[0]['score'],
            metaphor_discipline=results[1]['score'],
            anti_pattern=results[2]['score'],
            structure=results[3]['score'],
            functionality=results[4]['score'],
        )

    async def compare_variants(
        self,
        variants: dict[str, str],  # model_name -> scene_content
        context: dict
    ) -> dict:
        """
        Score multiple scene variants and rank them.

        Returns ranked list with scores and winner.
        """
        scores = {}
        for model, content in variants.items():
            scores[model] = await self.score_scene(content, context)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1].total,
            reverse=True
        )

        return {
            'winner': ranked[0][0],
            'rankings': [
                {
                    'rank': i + 1,
                    'model': model,
                    'score': score.total,
                    'grade': score.grade,
                    'breakdown': {
                        'voice': score.voice_consistency,
                        'metaphor': score.metaphor_discipline,
                        'anti_pattern': score.anti_pattern,
                        'structure': score.structure,
                        'functionality': score.functionality,
                    },
                    'weakest': score.weakest_dimension,
                }
                for i, (model, score) in enumerate(ranked)
            ]
        }
```

---

## Manuscript Health Aggregation

```python
# backend/services/manuscript_health.py

class ManuscriptHealth:
    """
    Aggregate scene scores into manuscript-level metrics.
    """

    def __init__(self, db_path: Path):
        self.db = Database(db_path)

    def get_manuscript_score(self) -> dict:
        """
        Calculate overall manuscript health from all scored scenes.
        """
        scene_scores = self.db.get_all_scene_scores()

        if not scene_scores:
            return {'status': 'no_scored_scenes'}

        # Aggregate by dimension
        aggregates = {
            'voice_consistency': [],
            'metaphor_discipline': [],
            'anti_pattern': [],
            'structure': [],
            'functionality': [],
        }

        for score in scene_scores:
            for dim in aggregates:
                aggregates[dim].append(getattr(score, dim))

        # Calculate means and identify problem areas
        means = {dim: sum(vals) / len(vals) for dim, vals in aggregates.items()}

        # Normalize to percentages
        max_scores = {
            'voice_consistency': 25,
            'metaphor_discipline': 25,
            'anti_pattern': 20,
            'structure': 20,
            'functionality': 10,
        }

        percentages = {
            dim: (means[dim] / max_scores[dim]) * 100
            for dim in means
        }

        # Identify weakest scenes
        weakest_scenes = sorted(
            scene_scores,
            key=lambda s: s.total
        )[:5]

        return {
            'overall_percentage': sum(percentages.values()) / len(percentages),
            'dimension_percentages': percentages,
            'weakest_dimension': min(percentages, key=percentages.get),
            'scenes_scored': len(scene_scores),
            'weakest_scenes': [
                {'scene_id': s.scene_id, 'score': s.total, 'grade': s.grade}
                for s in weakest_scenes
            ],
            'recommendations': self._generate_recommendations(percentages),
        }

    def _generate_recommendations(self, percentages: dict) -> list[str]:
        """Generate actionable recommendations based on weak areas."""
        recs = []

        if percentages['voice_consistency'] < 70:
            recs.append("Review voice guide and reference scenes; consider voice consistency pass")

        if percentages['metaphor_discipline'] < 70:
            recs.append("Audit metaphor usage; ensure all are from allowed domains")

        if percentages['anti_pattern'] < 70:
            recs.append("Run anti-pattern detection; focus on severe patterns first")

        if percentages['structure'] < 70:
            recs.append("Review Scene Strategy documents; ensure Goal/Conflict/Outcome clarity")

        if percentages['functionality'] < 70:
            recs.append("Consider cutting or combining low-functionality scenes")

        return recs
```

---

## API Endpoints

```python
# In api.py

@app.post("/scoring/scene")
async def score_scene(request: ScoreSceneRequest):
    """Score a single scene across all dimensions."""
    scorer = ScoringService()
    score = await scorer.score_scene(request.content, request.context)

    return {
        'total': score.total,
        'grade': score.grade,
        'breakdown': {
            'voice_consistency': score.voice_consistency,
            'metaphor_discipline': score.metaphor_discipline,
            'anti_pattern': score.anti_pattern,
            'structure': score.structure,
            'functionality': score.functionality,
        },
        'weakest': score.weakest_dimension,
    }

@app.post("/scoring/compare")
async def compare_variants(request: CompareVariantsRequest):
    """Score and rank multiple scene variants."""
    scorer = ScoringService()
    result = await scorer.compare_variants(request.variants, request.context)
    return result

@app.get("/scoring/manuscript")
async def manuscript_health():
    """Get aggregate manuscript health from all scored scenes."""
    health = ManuscriptHealth(DB_PATH)
    return health.get_manuscript_score()
```

---

## Integration with Voice Consistency Tester

The existing `voice_consistency_tester.py` from writers-factory-core already implements a similar scoring system. This spec extends it with:

1. **Persistent storage** of scores in database
2. **Manuscript-level aggregation**
3. **API endpoints** for UI integration
4. **Configurable rubrics** per project

Migration path: Port the core scoring logic, wrap with service layer, expose via API.

---

## Success Criteria

- [ ] All 5 dimensions scored with explicit rubrics
- [ ] Critic prompts produce consistent, reproducible scores
- [ ] Scene variants can be compared and ranked
- [ ] Manuscript health aggregated from scene scores
- [ ] Weakest dimension identified per scene and manuscript
- [ ] Actionable recommendations generated
- [ ] Anti-pattern catalog configurable per project
- [ ] Metaphor domains configurable per project
- [ ] Scores persisted for trend tracking
