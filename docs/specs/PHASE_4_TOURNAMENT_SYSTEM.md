# Phase 4: Multi-Model Tournament System

## Overview

The Multi-Model Tournament System automates the variant generation workflow from the manual process, enabling parallel generation of 15-25 variants across multiple AI models and writing strategies.

### Key Benefits

1. **Parallel Execution**: Generate variants concurrently instead of sequentially
2. **Multi-Model Diversity**: Leverage different AI models for unique perspectives
3. **Automatic Scoring**: Apply the 5-category scoring rubric automatically
4. **Consensus Detection**: Identify high-confidence decisions vs areas needing review
5. **Hybrid Creation**: Merge best elements from multiple variants

## Manual Workflow Mapping

| Manual Process | Phase 4 Automation | Improvement |
|----------------|-------------------|-------------|
| **STEP 2: Structure Variants** | | |
| 5 variants sequential | `POST /tournament/structure/create` | 15 variants parallel (3 models × 5 strategies) |
| Manual review + selection | `GET /tournament/{id}/results` | Auto-ranking by consensus score |
| **STEP 3: Scene Variants** | | |
| 5 variants sequential | `POST /tournament/scene/create` | 15-25 variants parallel |
| Manual selection | Auto-ranking + consensus detection | Highlight high-agreement variants |
| Manual hybrid creation | `POST /tournament/{id}/hybrid` | Automated paragraph-level merging |

## Architecture

```
backend/
├── models/
│   └── tournament.py          # Data models (Tournament, Variant, etc.)
├── services/
│   └── tournament_service.py  # Core orchestration logic
└── api.py                     # REST endpoints
```

### Data Models

#### Tournament Types

```python
class TournamentType(Enum):
    STRUCTURE_VARIANT = "structure_variant"  # STEP 2: Structure variants
    SCENE_VARIANT = "scene_variant"          # STEP 3: Scene variants
```

#### Variant Strategies

```python
class VariantStrategy(Enum):
    ACTION = "action"          # Fast pacing, physical detail
    CHARACTER = "character"    # Internal landscape, psychology
    DIALOGUE = "dialogue"      # Conversation-centered
    ATMOSPHERIC = "atmospheric" # Setting as character
    BALANCED = "balanced"      # Mix of elements
```

#### Score Breakdown

Uses the existing 5-category, 100-point rubric:
- Voice Authenticity (30 pts)
- Character Consistency (20 pts)
- Metaphor Discipline (20 pts)
- Anti-Pattern Compliance (15 pts)
- Phase Appropriateness (15 pts)

## API Reference

### Tournament Lifecycle

#### Create Structure Tournament
```http
POST /tournament/structure/create
```

Creates a tournament for structural variants (STEP 2).

**Request Body:**
```json
{
  "tournament_type": "structure_variant",
  "project_id": "my_project",
  "agents": [
    {
      "agent_id": "claude",
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "quality_tier": "premium",
      "enabled": true
    },
    {
      "agent_id": "gpt4",
      "provider": "openai",
      "model": "gpt-4o",
      "quality_tier": "premium",
      "enabled": true
    },
    {
      "agent_id": "deepseek",
      "provider": "deepseek",
      "model": "deepseek-chat",
      "quality_tier": "budget",
      "enabled": true
    }
  ],
  "strategies": ["action", "character", "dialogue", "atmospheric", "balanced"],
  "source_material": "The scene content to generate variants from...",
  "source_context": "Chapter 3, tense confrontation scene",
  "voice_bundle_path": "/path/to/voice_bundle",
  "max_variants_per_agent": 5,
  "parallel_execution": true,
  "auto_score": true
}
```

**Response:**
```json
{
  "status": "created",
  "tournament_id": "tournament_my_project_20241125_143052_abc123",
  "tournament_type": "structure_variant",
  "config": { ... },
  "expected_variants": 15
}
```

#### Create Scene Tournament
```http
POST /tournament/scene/create
```

Creates a tournament for scene variants (STEP 3).

Same request body structure as structure tournament.

#### Run Tournament Round
```http
POST /tournament/{tournament_id}/run
```

Executes the tournament - generates and scores all variants.

**Request Body:**
```json
{
  "tournament_id": "tournament_my_project_20241125_143052_abc123",
  "round_number": 1
}
```

**Response:**
```json
{
  "status": "round_complete",
  "tournament_id": "tournament_my_project_20241125_143052_abc123",
  "round_number": 1,
  "variant_count": 15,
  "consensus_score": 78.5,
  "tournament": { ... },
  "ranked_results": {
    "ranked_variants": [
      {
        "variant_id": "...",
        "rank": 1,
        "score": 92,
        "grade": "A",
        "agent_id": "claude",
        "strategy": "character"
      },
      ...
    ],
    "top_tier": ["variant_1", "variant_2", "variant_3"],
    "mid_tier": ["variant_4", ...],
    "bottom_tier": ["variant_13", "variant_14", "variant_15"],
    "average_score": 82.5,
    "median_score": 84,
    "score_std_dev": 7.2
  },
  "consensus_report": {
    "overall_consensus": 78.5,
    "high_agreement_sections": ["voice_authenticity", "anti_pattern_compliance"],
    "divergent_sections": ["character_consistency"],
    "variant_alignments": { "variant_1": 0.95, ... },
    "recommendation": "Moderate consensus. Review top 3 variants..."
  }
}
```

### Tournament Results

#### Get Tournament Results
```http
GET /tournament/{tournament_id}/results
```

Returns complete results with rankings and consensus analysis.

#### Get Tournament Variants
```http
GET /tournament/{tournament_id}/variants?agent_id=claude&strategy=action
```

Returns variants with optional filtering.

#### Get Consensus Analysis
```http
GET /tournament/{tournament_id}/consensus
```

Returns detailed consensus report.

### Tournament Completion

#### Select Winner
```http
POST /tournament/{tournament_id}/select-winner
```

**Request Body:**
```json
{
  "tournament_id": "...",
  "winner_variant_id": "variant_abc123"
}
```

#### Create Hybrid
```http
POST /tournament/{tournament_id}/hybrid
```

Merges selected variants into a hybrid scene.

**Request Body:**
```json
{
  "tournament_id": "...",
  "selected_variant_ids": ["variant_1", "variant_3", "variant_5"],
  "merge_strategy": "paragraph",
  "preserve_voice_from": "variant_1",
  "target_word_count": 800,
  "maintain_pacing": true,
  "smooth_transitions": true
}
```

**Response:**
```json
{
  "status": "hybrid_created",
  "tournament_id": "...",
  "hybrid_content": "The merged scene content...",
  "word_count": 823,
  "source_variants": ["variant_1", "variant_3", "variant_5"]
}
```

### Tournament Management

#### List Tournaments
```http
GET /tournaments?project_id=my_project&status=complete
```

#### Get Tournament Details
```http
GET /tournament/{tournament_id}
```

## Integration Points

### Model Orchestrator (Phase 3E)
- Tier-based model routing (budget/balanced/premium)
- Parallel model calls
- Cost tracking per tournament

### SceneAnalyzerService (Phase 3B)
- 5-category, 100-point scoring
- Anti-pattern detection
- Voice authentication checks

### Knowledge Graph (Phase 3D)
- Context injection from KB
- Track tournament decisions as events

## Consensus Detection Algorithm

The consensus algorithm analyzes score spread and category agreement:

```python
# Overall consensus = inverse of score spread
overall_consensus = max(0, 100 - (max_score - min_score))

# Per-category analysis
for category in categories:
    spread = max(category_scores) - min(category_scores)
    if spread <= 5:
        high_agreement.append(category)
    elif spread >= 10:
        divergent.append(category)

# Recommendations based on consensus
if consensus >= 80:
    "High consensus - safe to pick top variant"
elif consensus >= 60:
    "Moderate consensus - review top 3"
elif consensus >= 40:
    "Mixed consensus - consider hybrid"
else:
    "Low consensus - manual review needed"
```

## Hybrid Creation

The hybrid creator uses LLM intelligence to merge variants:

1. **Input**: 2+ variants selected by user
2. **Analysis**: LLM identifies strongest paragraphs from each
3. **Merge**: Creates cohesive scene preserving best elements
4. **Voice Consistency**: Maintains voice from primary variant
5. **Transitions**: Smooths connections between merged sections

### Merge Strategies

- `paragraph`: Combine best paragraphs (default)
- `section`: Combine best sections (opening, middle, climax, etc.)
- `sentence`: Fine-grained sentence-level merging

## Usage Example

### Complete Tournament Workflow

```python
import httpx

async def run_scene_tournament():
    base_url = "http://localhost:8000"

    # 1. Create tournament
    response = await httpx.post(f"{base_url}/tournament/scene/create", json={
        "tournament_type": "scene_variant",
        "project_id": "explants_ch3",
        "agents": [
            {"agent_id": "claude", "provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "quality_tier": "premium", "enabled": True},
            {"agent_id": "gpt4", "provider": "openai", "model": "gpt-4o", "quality_tier": "premium", "enabled": True},
            {"agent_id": "deepseek", "provider": "deepseek", "model": "deepseek-chat", "quality_tier": "budget", "enabled": True},
        ],
        "source_material": "Chapter 3 scene with detective confrontation...",
        "source_context": "Tense noir atmosphere, key revelation moment",
        "parallel_execution": True,
        "auto_score": True,
    })
    tournament_id = response.json()["tournament_id"]

    # 2. Run tournament round
    response = await httpx.post(f"{base_url}/tournament/{tournament_id}/run", json={
        "tournament_id": tournament_id,
        "round_number": 1,
    })
    results = response.json()

    # 3. Check consensus
    consensus = results["consensus_report"]
    print(f"Consensus: {consensus['overall_consensus']}")
    print(f"Recommendation: {consensus['recommendation']}")

    # 4. Get top variants
    ranked = results["ranked_results"]["ranked_variants"]
    top_3 = ranked[:3]

    # 5. Select winner or create hybrid
    if consensus["overall_consensus"] >= 80:
        # High consensus - select winner
        await httpx.post(f"{base_url}/tournament/{tournament_id}/select-winner", json={
            "tournament_id": tournament_id,
            "winner_variant_id": top_3[0]["variant_id"],
        })
    else:
        # Lower consensus - create hybrid from top 3
        response = await httpx.post(f"{base_url}/tournament/{tournament_id}/hybrid", json={
            "tournament_id": tournament_id,
            "selected_variant_ids": [v["variant_id"] for v in top_3],
            "merge_strategy": "paragraph",
            "target_word_count": 800,
        })
        hybrid = response.json()["hybrid_content"]
```

## Cost Tracking

Every tournament tracks:
- `total_cost_usd`: Cumulative cost of all API calls
- `total_tokens_input`: Input tokens across all variants
- `total_tokens_output`: Output tokens generated

Per-variant tracking:
- `cost_usd`: Cost for this specific variant
- `token_count_input`: Input tokens
- `token_count_output`: Output tokens
- `generation_time_ms`: How long generation took

## Future Enhancements

1. **Multi-Round Tournaments**: Top variants from round 1 compete in round 2
2. **Persistent Storage**: Database storage for tournament history
3. **Fine-Grained Hybrid Control**: UI for selecting specific paragraphs
4. **A/B Testing**: Track which models consistently win for different strategies
5. **Cost Optimization**: Auto-select models based on budget constraints

## Related Documentation

- [Director Mode Specification](./DIRECTOR_MODE_SPECIFICATION.md)
- [Scoring Rubrics](./SCORING_RUBRICS.md)
- [Settings Configuration](./SETTINGS_CONFIGURATION.md)
- [UI Implementation Plan V3](./UI_IMPLEMENTATION_PLAN_V3.md)
