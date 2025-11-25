# Settings & Configuration Specification

**Version**: 2.0
**Status**: Phase 3C - Implementation In Progress
**Priority**: P0 Critical - Blocks Universal Framework Goal
**Moved Up From**: Phase 5 → Phase 3C (November 24, 2025)

---

## Overview

Writers Factory needs a Settings system that allows experienced writers to customize the application's behavior. This goes beyond typical "preferences" - it exposes craft-meaningful knobs that let writers tune the AI assistance to their specific needs.

### Why This Matters

The Director Mode services encode craft rules that worked brilliantly for one style (see [Agent Handoff Wisdom](../dev_logs/AGENT_HANDOFF_WISDOM.md)) but may not suit every writer:

| Hard-Coded Default | But Some Writers... |
|-------------------|---------------------|
| Similes penalized (-1 each) | Love similes as their signature style |
| First-person italics = zero-tolerance | Use interior monologue extensively |
| Max 30% any metaphor domain | Deliberately saturate one domain |
| "with X precision" = violation | Don't mind this phrase |
| 6-pass enhancement always | Want lighter touch on polish |

**The scoring and enhancement pipeline works** - but the parameters must be configurable.

### Design Principles

1. **Meaningful Language** - No raw technical jargon. "Voice Strictness" not "temperature". "Metaphor Diversity Threshold" not "domain_saturation_limit".
2. **Sensible Defaults** - Works out of the box for beginners. Advanced settings hidden until needed.
3. **Per-Project Override** - Global defaults can be overridden per project.
4. **Portable** - Settings exportable/importable for backup or sharing.
5. **Voice Bundle Integration** - Settings flow into Voice Calibration Document and persist with project.

---

## Settings Categories

### 1. API Keys & Agents

**Location:** Settings → Agents

| Setting | Type | Description |
|---------|------|-------------|
| OpenAI API Key | secret | For GPT-4, GPT-4o access |
| Anthropic API Key | secret | For Claude Sonnet, Opus access |
| Google AI API Key | secret | For Gemini access |
| Ollama Endpoint | url | Local Ollama server (default: localhost:11434) |
| Default Tournament Agents | multi-select | Which agents compete in tournaments |
| Foreman Model | select | Which Ollama model powers The Foreman |

**UI Notes:**
- Keys masked after entry (show last 4 chars)
- "Test Connection" button per key
- Agent status indicators (Ready / Missing Key / Error)

---

### 2. Scoring Rubric Weights

**Location:** Settings → Scoring

Writers can adjust the weight of each scoring category to match their priorities.

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Voice Authenticity Weight | 30 | 10-50 | How heavily to penalize AI-sounding prose |
| Character Consistency Weight | 20 | 10-30 | Psychology, capability, relationship alignment |
| Metaphor Discipline Weight | 20 | 10-30 | Domain rotation and transformation quality |
| Anti-Pattern Compliance Weight | 15 | 5-25 | Pattern avoidance strictness |
| Phase Appropriateness Weight | 15 | 5-25 | Voice complexity matching story phase |

**Presets:**
- **Literary Fiction** - Voice 40, Character 25, Metaphor 15, Anti-Pattern 10, Phase 10
- **Commercial Thriller** - Voice 25, Character 20, Metaphor 15, Anti-Pattern 25, Phase 15
- **Genre Romance** - Voice 20, Character 30, Metaphor 20, Anti-Pattern 15, Phase 15
- **Balanced (Default)** - Voice 30, Character 20, Metaphor 20, Anti-Pattern 15, Phase 15

**Note:** Weights must sum to 100.

---

### 3. Voice Authentication Strictness

**Location:** Settings → Scoring → Voice Details

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Authenticity Test Strictness | Medium | Low/Medium/High | How strict on "AI explaining character" detection |
| Purpose Test Strictness | Medium | Low/Medium/High | How tightly scenes must serve theme |
| Fusion Test Strictness | Medium | Low/Medium/High | How seamlessly expertise must blend with personality |

**Strictness Levels:**
- **Low** - Forgiving. Good for early drafts. Score rarely drops below 6/10.
- **Medium** - Balanced. Production-ready prose. Standard calibration.
- **High** - Demanding. Publication-quality expectation. Score of 8+ is excellent.

---

### 4. Metaphor Discipline Settings

**Location:** Settings → Scoring → Metaphor Details

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Domain Saturation Threshold | 30% | 20-50% | Max percentage for any single metaphor domain |
| Primary Domain Allowance | 35% | 25-45% | Higher limit for ONE designated primary domain |
| Simile Tolerance | 2 | 0-5 | How many similes allowed before penalty |
| Minimum Domains Required | 3 | 2-6 | How many different domains must appear |

**Example Configurations:**
- **Tight Rotation** - Saturation 25%, Simile Tolerance 0, Min Domains 4
- **Loose Rotation** - Saturation 40%, Simile Tolerance 4, Min Domains 2
- **Character-Focused** - Primary Allowance 45% (one domain can dominate if it's the character's expertise)

---

### 5. Anti-Pattern Detection

**Location:** Settings → Scoring → Anti-Patterns

| Setting | Default | Description |
|---------|---------|-------------|
| Zero-Tolerance Patterns | [list] | Patterns that always deduct -2 points |
| Formulaic Patterns | [list] | Patterns that deduct -1 point |
| Custom Patterns | [list] | Writer-defined patterns to detect |
| Severity Overrides | [map] | Change severity of built-in patterns |

**Customization Example:**
```yaml
# Writer decides "despite the" is acceptable in their style
severity_overrides:
  despite_the: ignore  # Changed from -1 to no penalty

# Writer adds custom patterns to avoid
custom_patterns:
  - pattern: "suddenly"
    severity: formulaic  # -1
    reason: "Overused surprise word"
  - pattern: "very"
    severity: formulaic
    reason: "Weak intensifier"
```

---

### 6. Enhancement Pipeline Settings

**Location:** Settings → Enhancement

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Auto-Enhancement Threshold | 85 | 70-95 | Score below which enhancement is suggested |
| Action Prompt Threshold | 85 | 80-95 | Score above which surgical fixes are used |
| 6-Pass Threshold | 70 | 60-80 | Score below which full enhancement runs |
| Rewrite Threshold | 60 | 50-70 | Score below which rewrite is recommended |
| Enhancement Aggressiveness | Medium | Conservative/Medium/Aggressive | How much the enhancer changes |

**Aggressiveness Levels:**
- **Conservative** - Minimal changes. Preserve writer's prose. Only fix violations.
- **Medium** - Balanced polish. Fix violations + improve weak areas.
- **Aggressive** - Heavy rewrite. Optimize for score improvement.

---

### 7. Tournament Settings

**Location:** Settings → Tournaments

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Variants per Agent | 5 | 3-10 | How many variants each agent generates |
| Tournament Strategies | [all 5] | multi-select | Which strategies to use (ACTION, CHARACTER, DIALOGUE, ATMOSPHERIC, BALANCED) |
| Auto-Score Variants | true | bool | Automatically score all variants |
| Show Losing Variants | true | bool | Display all variants or just top N |
| Top N Display | 5 | 3-10 | How many top variants to highlight |

---

### 8. Foreman Behavior

**Location:** Settings → Foreman

| Setting | Default | Description |
|---------|---------|-------------|
| Proactiveness | Medium | How often Foreman suggests next steps |
| Challenge Intensity | Medium | How strongly Foreman pushes back on weak choices |
| Explanation Verbosity | Medium | How much Foreman explains its reasoning |
| Auto-KB-Writes | true | Automatically save decisions to Knowledge Base |

**Levels:**
- **Low** - Foreman responds when asked. Minimal suggestions.
- **Medium** - Foreman guides the process. Reasonable challenges.
- **High** - Foreman is directive. Strong challenges. Detailed explanations.

---

### 8. AI Intelligence & Model Orchestration (Phase 3E)

**Location:** Settings → AI Intelligence

This category provides intelligent model selection and multi-model consensus for critical decisions. Phase 3E transforms the Writers Factory from manual model assignment into an intelligent orchestrator with budget controls and quality tiers.

#### 8.1 Model Orchestrator (Phase 3)

Automatic model selection based on quality requirements and budget constraints.

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| Enable Orchestrator | bool | false | - | When enabled, overrides manual task_models with automatic selection |
| Quality Tier | select | Balanced | Budget/Balanced/Premium | Automatic model selection strategy |
| Monthly Budget | number | None | $0-100 USD | Cost limit per month (None = unlimited) |
| Prefer Local Models | bool | false | - | Prefer local Ollama models when quality is similar |
| Cost Tracking Enabled | bool | true | - | Track and display monthly AI spending |

**Quality Tiers**:
- **Budget** - Cheapest models with quality ≥ 6/10 (mostly local Mistral + DeepSeek for critical tasks)
- **Balanced** - Best quality per dollar (DeepSeek for strategic reasoning, local for coordination)
- **Premium** - Highest quality available (Claude 3.5 Sonnet for narrative, GPT-4o for themes, DeepSeek for psychology)

**Cost Estimates** (typical usage patterns):
- **Budget**: $0/month (all local Ollama models)
- **Balanced**: ~$0.50-1.00/month (DeepSeek for 7/8 strategic tasks, local for coordination)
- **Premium**: ~$3-5/month (optimal model per task: Claude, GPT-4o, DeepSeek mix)

**How It Works**:
1. Writer sets Quality Tier (or Monthly Budget)
2. System consults capabilities matrix (model strengths, costs, quality scores)
3. For each task, orchestrator selects optimal model within constraints
4. Budget tracking prevents overspending (falls back to local when exhausted)

#### 8.2 Multi-Model Tournament (Phase 4)

Query multiple models in parallel for critical story decisions to detect consensus or disagreement.

| Setting | Type | Default | Range | Description |
|---------|------|---------|-------|-------------|
| Enable Tournaments | bool | false | - | Query 3+ models for critical tasks |
| Critical Tasks | multi-select | [beat_structure_advice, structural_planning, theme_analysis] | - | Which task types trigger tournaments |
| Models per Tournament | number | 3 | 2-5 | How many models to query in parallel |
| Consensus Threshold | number | 0.7 | 0.5-0.9 | Agreement level to declare consensus |
| Max Tournaments per Day | number | 10 | 1-50 | Cost control limit |
| Show All Responses | bool | true | - | Display all model outputs or just consensus |

**Critical Tasks** (default tournament triggers):
- `beat_structure_advice` - Major structural decisions (Midpoint placement, Act 2 length)
- `structural_planning` - High-level story planning (How to structure Act 2?)
- `theme_analysis` - Thematic interpretation (What does this symbol mean?)

**Tournament Flow**:
1. Foreman detects critical task type
2. Queries 3 models in parallel (diverse providers: local + 2 cloud)
3. Analyzes responses for consensus (semantic similarity ≥ 0.7)
4. **Consensus**: Returns agreed-upon response (high confidence)
5. **Dispute**: Flags disagreement, shows all responses for human review

**Cost Warning**: Tournaments are expensive (~$0.02-0.05 per tournament). Daily limits prevent budget overruns.

**Configuration Example:**
```yaml
# settings.yaml
orchestrator:
  enabled: true
  quality_tier: "balanced"
  monthly_budget: 2.00  # $2/month limit
  prefer_local: false
  cost_tracking_enabled: true

  # Current month tracking (auto-updated)
  current_month: "2025-11"
  current_month_spend: 0.47

tournament:
  enabled: false  # Optional advanced feature
  critical_tasks:
    - beat_structure_advice
    - structural_planning
    - theme_analysis
  num_models: 3
  consensus_threshold: 0.7
  max_tournaments_per_day: 10
  show_all_responses: true
```

---

### 9. Context Window Management

**Location:** Settings → Advanced

| Setting | Default | Description |
|---------|---------|-------------|
| Max Conversation History | 20 | Messages kept in Foreman context |
| KB Context Limit | 1000 | Tokens allocated to KB entries |
| Voice Bundle Injection | Full | Full / Summary / Minimal |
| Continuity Context Depth | 3 | How many previous scenes to include |

---

### 10. Graph Health Checks (Phase 3D)

**Location:** Settings → Health Checks

Writers can configure sensitivity for macro-level structural validation.

| Setting | Default | Range | Description |
|---------|---------|-------|-------------|
| Health Check Model | llama3.2 | select | Which Ollama model to use for semantic analysis (timeline, theme scoring) |
| Pacing Plateau Window | 3 | 2-5 | How many consecutive chapters to check for flat tension |
| Pacing Plateau Tolerance | 1.0 | 0.5-2.0 | Max tension variation to still flag as plateau |
| Beat Deviation Warning | 5 | 3-10 | % off target to trigger warning |
| Beat Deviation Error | 10 | 8-15 | % off target to trigger error |
| Flaw Challenge Frequency | 10 | 5-20 | Max scenes before protagonist's flaw must be tested |
| Min Cast Appearances | 3 | 1-5 | Minimum appearances for supporting characters |
| Min Symbol Occurrences | 3 | 2-6 | Minimum recurrences for thematic symbols |
| Min Resonance Score | 6 | 4-8 | Minimum theme resonance at critical beats |
| Timeline Analysis Model | Same as Health Check Model | select | Model for timeline consistency checks (can override) |
| Theme Scoring Model | Same as Health Check Model | select | Model for theme resonance auto-scoring (can override) |

**Configuration Example:**
```yaml
# voice_settings.yaml
health_checks:
  enabled: true

  # Model Selection for LLM-powered checks
  models:
    health_check_model: "llama3.2"  # Default for all semantic analysis
    timeline_analysis_model: "llama3.2"  # Can override for timeline checks
    theme_scoring_model: "llama3.2"  # Can override for theme scoring

  pacing:
    plateau_window: 3
    plateau_tolerance: 1.0
    enabled: true

  structure:
    beat_deviation_warning: 5
    beat_deviation_error: 10
    enabled: true

  character:
    flaw_challenge_frequency: 10
    min_cast_appearances: 3
    enabled: true

  theme:
    min_symbol_occurrences: 3
    min_resonance_score: 6
    enabled: true
```

**Model Selection Notes:**
- **Default Model**: Uses Ollama, can be any available model (llama3.2, mistral, etc.)
- **Override Flexibility**: Timeline and theme checks can use different models if needed
- **Performance Consideration**: Larger models = better accuracy but slower analysis
- **Recommended**: llama3.2 for speed, llama3.1-70b for maximum accuracy

**Strictness Presets:**
- **Lenient** - Plateau tolerance 2.0, Flaw frequency 20, Beat deviation 10%
- **Balanced (Default)** - Current defaults
- **Strict** - Plateau tolerance 0.5, Flaw frequency 5, Beat deviation 3%

---

## Data Structure

### Global Settings (SQLite)

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT,  -- JSON serialized
    category TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Per-Project Overrides

```sql
CREATE TABLE project_settings (
    project_id TEXT,
    key TEXT,
    value TEXT,  -- JSON serialized
    PRIMARY KEY (project_id, key)
);
```

### Settings Resolution

```python
def get_setting(key: str, project_id: Optional[str] = None) -> Any:
    """
    Get setting with project override priority.

    1. Check project-specific override
    2. Fall back to global setting
    3. Fall back to default
    """
    if project_id:
        override = db.get_project_setting(project_id, key)
        if override is not None:
            return override

    global_setting = db.get_global_setting(key)
    if global_setting is not None:
        return global_setting

    return DEFAULTS[key]
```

---

## UI Mockup Concepts

### Settings Panel Structure

```
Settings
├── Agents
│   ├── API Keys (collapsible, secure)
│   └── Default Agents
├── Scoring
│   ├── Category Weights [preset dropdown + custom]
│   ├── Voice Details (expandable)
│   ├── Metaphor Details (expandable)
│   └── Anti-Patterns (expandable)
├── Enhancement
│   ├── Thresholds
│   └── Aggressiveness
├── Tournaments
│   ├── Variants & Strategies
│   └── Display Options
├── Foreman
│   └── Behavior Settings
└── Advanced
    └── Context & Performance
```

### Project Override Indicator

When viewing a setting that has a project-specific override:
```
┌─────────────────────────────────────────┐
│ Voice Authenticity Weight               │
│ ┌─────────────────────────────────────┐ │
│ │  30  [========|--------]  Global    │ │
│ │  40  [==========|------]  This Project (override) │ │
│ └─────────────────────────────────────┘ │
│ [Reset to Global]                       │
└─────────────────────────────────────────┘
```

---

## Export/Import Format

```yaml
# writers-factory-settings.yaml
version: "1.0"
exported_at: "2024-11-23T10:30:00Z"

agents:
  default_tournament_agents: ["claude-sonnet", "gpt-4o", "gemini-pro"]
  foreman_model: "llama3.2"

scoring:
  weights:
    voice_authenticity: 30
    character_consistency: 20
    metaphor_discipline: 20
    anti_pattern_compliance: 15
    phase_appropriateness: 15

  voice:
    authenticity_strictness: "medium"
    purpose_strictness: "medium"
    fusion_strictness: "medium"

  metaphor:
    saturation_threshold: 0.30
    primary_allowance: 0.35
    simile_tolerance: 2
    min_domains: 3

  anti_patterns:
    severity_overrides:
      despite_the: "ignore"
    custom_patterns:
      - pattern: "suddenly"
        severity: "formulaic"

enhancement:
  auto_threshold: 85
  action_prompt_threshold: 85
  six_pass_threshold: 70
  rewrite_threshold: 60
  aggressiveness: "medium"

tournaments:
  variants_per_agent: 5
  strategies: ["ACTION", "CHARACTER", "DIALOGUE", "ATMOSPHERIC", "BALANCED"]

foreman:
  proactiveness: "medium"
  challenge_intensity: "medium"
  explanation_verbosity: "medium"

# API keys are NOT exported for security
```

---

## Implementation Notes

### Phase 3C Tasks (Current - November 2025)
**Priority**: Backend settings infrastructure without UI

1. ✅ **Create Settings Service** - SQLite-backed settings with 3-tier resolution
2. ✅ **Voice Bundle YAML Generation** - Auto-generate `voice_settings.yaml` during Voice Calibration
3. ✅ **Refactor Scene Analyzer** - Dynamic weights, patterns, thresholds
4. ✅ **Refactor Scene Enhancement** - Dynamic enhancement thresholds
5. ✅ **Update VoiceBundleContext** - Load structured settings from YAML

**See**: [PHASE_3C_SETTINGS_IMPLEMENTATION.md](../dev_logs/PHASE_3C_SETTINGS_IMPLEMENTATION.md) for detailed implementation plan.

### Phase 5 Tasks (Future - UI Layer)
1. Create Settings UI panel (Svelte frontend)
2. Visual editing for `voice_settings.yaml`
3. Preset system (Literary Fiction, Thriller, Romance)
4. Export/Import functionality
5. Live preview of scoring changes

---

## Success Criteria

- [ ] Experienced writers can customize scoring to match their style
- [ ] API keys configurable without editing files
- [ ] Settings persist across sessions
- [ ] Per-project overrides work correctly
- [ ] Export/import allows sharing configurations
- [ ] Presets provide quick starting points
- [ ] All settings use meaningful, non-technical language

---

*Settings & Configuration Specification v1.0*
*Writers Factory - Future Phase*
