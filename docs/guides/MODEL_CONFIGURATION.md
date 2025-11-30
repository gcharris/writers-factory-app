# Configurable Model Assignments

**✅ IMPLEMENTED (Phase 3E)**: All AI model assignments are fully configurable, allowing writers to choose the optimal model for each task type based on their preferences, budget, and quality requirements.

## Overview

The Writers Factory supports multiple AI providers and allows you to assign specific models to specific tasks. You can mix and match local models (via Ollama) with cloud models (OpenAI, Anthropic, DeepSeek, Qwen, Google Gemini) based on your needs.

**Current Status**: This feature is fully implemented and working in the codebase. All configuration examples below are functional and can be used immediately.

---

## Foreman Task-Specific Models

The Foreman uses different models for different types of tasks. Configure these in your `settings.yaml` or via the API.

### Default Configuration

```yaml
foreman:
  coordinator_model: "mistral:7b"  # Fallback for undefined tasks (local Ollama)

  task_models:
    coordinator: "mistral:7b"                   # Simple coordination (local)
    health_check_review: "deepseek-chat"        # Health check interpretation
    voice_calibration_guidance: "deepseek-chat" # Voice tournament guidance
    beat_structure_advice: "deepseek-chat"      # Beat structure analysis
    conflict_resolution: "deepseek-chat"        # Timeline/character conflicts
    scaffold_enrichment_decisions: "deepseek-chat" # Scaffold enrichment
    theme_analysis: "deepseek-chat"             # Theme and symbolism
    structural_planning: "deepseek-chat"        # High-level planning
```

### Task Types Explained

| Task Type | When Triggered | Example Messages |
|-----------|----------------|------------------|
| `coordinator` | Simple status checks, template updates | "What's the status?", "Mark template complete" |
| `health_check_review` | Interpreting health check results | "The health check score is 73. What does that mean?" |
| `voice_calibration_guidance` | Voice tournament decisions | "Which voice variant should I choose?" |
| `beat_structure_advice` | Beat structure questions | "Is my midpoint in the right place?" |
| `conflict_resolution` | Timeline/character conflicts | "There's a timeline contradiction in Chapter 3" |
| `scaffold_enrichment_decisions` | Scaffold enrichment | "Should I enrich this scaffold from the notebook?" |
| `theme_analysis` | Theme and symbolism | "What does this symbol represent?" |
| `structural_planning` | High-level planning | "How should I structure Act 2?" |

---

## Health Check Model Assignments

Graph Health Service checks can each use different models optimized for their specific analysis type.

### Default Configuration

```yaml
health_checks:
  models:
    default_model: "llama3.2:3b"  # Fallback (local)

    # Task-specific assignments (Phase 3E - Implemented)
    timeline_consistency: "claude-3-7-sonnet-20250219"  # Best at narrative reasoning
    theme_resonance: "gpt-4o"                            # Excellent thematic analysis
    flaw_challenges: "deepseek-chat"                     # Deep character psychology
    cast_function: "qwen-plus"                           # Fast, cheap, good enough
    pacing_analysis: "mistral:7b"                        # Local for fast iteration
    beat_progress: "mistral:7b"                          # Structural validation
    symbolic_layering: "gpt-4o"                          # Pattern recognition
```

### Health Check Types

| Check Type | Purpose | Recommended Model | Why |
|------------|---------|-------------------|-----|
| `timeline_consistency` | Detect timeline contradictions | Claude Sonnet | Best at narrative reasoning & context |
| `theme_resonance` | Score theme presence at beats | GPT-4o | Excellent thematic analysis |
| `flaw_challenges` | Monitor Fatal Flaw testing | DeepSeek V3 | Deep character psychology, cheap |
| `cast_function` | Track supporting characters | Qwen Plus | Fast, cheap, good enough |
| `pacing_analysis` | Detect pacing plateaus | Mistral (local) | Fast iteration, no cost |
| `beat_progress` | Validate 15-beat structure | Mistral (local) | Structural validation |
| `symbolic_layering` | Track symbol evolution | GPT-4o | Pattern recognition |

---

## Available Models

### Local Models (via Ollama)

**Pros**: Free, private, no API limits, low latency
**Cons**: Requires local GPU/CPU, smaller context windows, less capable

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| `mistral:7b` | 7B | Coordination, structure validation, prose | Very Fast |
| `llama3.2:3b` | 3B | Simple tasks, ultra-fast responses | Fastest |
| `llama3.1` | 8B-70B | General purpose, good quality (if installed) | Fast-Medium |

### Cloud Models

**Pros**: Powerful, large context windows, no local resources
**Cons**: Cost per token, API rate limits, requires internet

#### OpenAI (GPT-4o, etc.)
```yaml
# Requires OPENAI_API_KEY in .env
task_models:
  theme_analysis: "gpt-4o"
  symbolic_layering: "gpt-4o-mini"  # Cheaper alternative
```

**Cost**: ~$2.50/1M tokens (GPT-4o), ~$0.15/1M tokens (GPT-4o-mini)
**Best For**: Thematic analysis, creative tasks, versatile reasoning

#### Anthropic (Claude Sonnet, Opus)
```yaml
# Requires ANTHROPIC_API_KEY in .env
task_models:
  conflict_resolution: "claude-3-5-sonnet"
  health_check_review: "claude-3-opus"  # Most capable
```

**Cost**: ~$3.00/1M tokens (Sonnet), ~$15.00/1M tokens (Opus)
**Best For**: Narrative reasoning, timeline analysis, complex character psychology

#### DeepSeek (V3)
```yaml
# Requires DEEPSEEK_API_KEY in .env
task_models:
  beat_structure_advice: "deepseek-chat"
  voice_calibration_guidance: "deepseek-chat"
```

**Cost**: ~$0.27/1M tokens
**Best For**: Deep reasoning, strategic planning, character analysis (best value!)

#### Qwen (Alibaba)
```yaml
# Requires QWEN_API_KEY in .env
task_models:
  coordinator: "qwen-plus"
  cast_function: "qwen-turbo"  # Faster, cheaper
```

**Cost**: ~$0.40/1M tokens (Plus), ~$0.12/1M tokens (Turbo)
**Best For**: Fast iteration, supporting character tracking, general tasks

#### Google Gemini
```yaml
# Requires GEMINI_API_KEY in .env
task_models:
  theme_analysis: "gemini-2.0-flash-exp"
  structural_planning: "gemini-2.0-flash-exp"
```

**Cost**: Free during experimental period, then ~$0.075/1M tokens
**Best For**: Multimodal analysis, long-context reasoning (1M tokens), creative tasks, fast iteration
**Model ID in agents.yaml**: `gemini-2.0-flash-exp`

---

## Configuration Methods

### Method 1: settings.yaml (Recommended)

Create or edit `settings.yaml` in your project root:

```yaml
foreman:
  task_models:
    coordinator: "mistral"                    # Local, free
    health_check_review: "deepseek-chat"      # Cloud, cheap
    voice_calibration_guidance: "claude-3-5-sonnet"  # Cloud, premium
    theme_analysis: "gpt-4o"                  # Cloud, premium

health_checks:
  models:
    timeline_consistency: "claude-3-5-sonnet"
    theme_resonance: "gpt-4o"
    flaw_challenges: "deepseek-chat"
    cast_function: "qwen-plus"
```

### Method 2: API (Dynamic Updates)

Update settings via POST request:

```bash
curl -X POST http://localhost:8000/settings/update \
  -H "Content-Type: application/json" \
  -d '{
    "foreman.task_models.theme_analysis": "gpt-4o",
    "health_checks.models.timeline_consistency": "claude-3-5-sonnet"
  }'
```

### Method 3: Environment Variables

Override specific models via environment:

```bash
export FOREMAN_TASK_MODEL_THEME_ANALYSIS="gpt-4o"
export HEALTH_CHECK_MODEL_TIMELINE="claude-3-5-sonnet"
```

---

## Cost Optimization Strategies

### Strategy 1: Local-First (Free)

Use local Ollama models for everything:

```yaml
foreman:
  task_models:
    coordinator: "mistral"
    health_check_review: "mistral"
    voice_calibration_guidance: "mistral"
    beat_structure_advice: "mistral"
    # ... all tasks use mistral
```

**Monthly Cost**: $0
**Quality**: Good for structure, adequate for strategy

### Strategy 2: Budget Cloud (< $1/month)

Use DeepSeek V3 for strategic tasks, local for coordination:

```yaml
foreman:
  task_models:
    coordinator: "mistral"  # Free
    health_check_review: "deepseek-chat"  # $0.27/1M
    voice_calibration_guidance: "deepseek-chat"
    beat_structure_advice: "deepseek-chat"
    theme_analysis: "deepseek-chat"
```

**Monthly Cost**: ~$0.50 (heavy usage: 1000 strategic queries)
**Quality**: Excellent reasoning, 90% as good as premium models

### Strategy 3: Premium Hybrid (Best Quality)

Use optimal model for each task:

```yaml
foreman:
  task_models:
    coordinator: "mistral"  # Fast, free
    health_check_review: "deepseek-chat"  # Cheap, smart
    voice_calibration_guidance: "claude-3-5-sonnet"  # Best reasoning
    theme_analysis: "gpt-4o"  # Best thematic analysis
    beat_structure_advice: "claude-3-5-sonnet"  # Best narrative

health_checks:
  models:
    timeline_consistency: "claude-3-5-sonnet"
    theme_resonance: "gpt-4o"
    flaw_challenges: "deepseek-chat"
```

**Monthly Cost**: ~$2-5 (heavy usage)
**Quality**: Best possible, each task uses optimal model

---

## Model Selection Guide

### When to Use Local Models (Mistral, Llama)

✅ Simple coordination tasks
✅ Structural validation (beat progress, pacing)
✅ High iteration tasks (called frequently)
✅ Privacy-sensitive projects
✅ Budget constraints

❌ Complex narrative reasoning
❌ Deep thematic analysis
❌ Nuanced character psychology

### When to Use DeepSeek V3

✅ Strategic reasoning
✅ Beat structure analysis
✅ Character arc planning
✅ Budget-conscious quality
✅ Most strategic tasks (best value!)

❌ Thematic subtlety (use GPT-4o)
❌ Timeline reasoning (use Claude)

### When to Use Claude Sonnet

✅ Timeline consistency analysis
✅ Narrative reasoning
✅ Complex character psychology
✅ Conflict resolution
✅ Long-context analysis

❌ Simple coordination (overkill)
❌ Budget-constrained projects (use DeepSeek)

### When to Use GPT-4o

✅ Thematic analysis
✅ Symbolic pattern recognition
✅ Creative interpretation
✅ Voice calibration guidance

❌ Simple tasks (overkill)
❌ Budget-constrained (use DeepSeek)

### When to Use Qwen Plus

✅ Supporting character tracking
✅ Fast iteration tasks
✅ General coordination (cloud alternative)
✅ Budget-conscious cloud option

### When to Use Gemini (Pro/Flash)

✅ Long-context analysis (up to 1M tokens)
✅ Multimodal tasks (images, diagrams)
✅ Creative writing assistance
✅ Thematic exploration
✅ Fast iteration (Flash is very cheap and fast)

❌ Highly structured reasoning (use Claude)
❌ Deep character psychology (use DeepSeek)

---

## FAQ

### Q: Can I use different models for different projects?

**A**: Yes! Settings can be project-specific. Create a `settings.yaml` in each project directory, and it will override global settings.

### Q: What happens if I don't have an API key?

**A**: The system automatically falls back to local Ollama models. You'll see a warning in logs but the system continues working.

### Q: Can I add new task types?

**A**: Not yet, but this is planned for Phase 3F. Currently, task types are fixed but model assignments are fully configurable.

### Q: How do I see which model was used?

**A**: Check the Foreman logs. You'll see:
- 📋 `Using mistral for coordinator` (local/fast tasks)
- 🧠 `Using deepseek-chat for theme_analysis` (strategic tasks)

### Q: Can I force a specific model for one query?

**A**: Yes! When calling the Foreman API, pass `model` parameter:

```json
POST /foreman/chat
{
  "message": "Analyze this theme",
  "model": "gpt-4o"
}
```

---

## Examples

### Example 1: Budget Writer (All Free)

```yaml
foreman:
  coordinator_model: "mistral:7b"
  task_models:
    coordinator: "mistral:7b"
    health_check_review: "mistral:7b"
    voice_calibration_guidance: "mistral:7b"
    beat_structure_advice: "mistral:7b"
    conflict_resolution: "mistral:7b"
    scaffold_enrichment_decisions: "mistral:7b"
    theme_analysis: "mistral:7b"
    structural_planning: "mistral:7b"

health_checks:
  models:
    default_model: "mistral:7b"
    timeline_consistency: "mistral:7b"
    theme_resonance: "mistral:7b"
    flaw_challenges: "mistral:7b"
    cast_function: "mistral:7b"
```

**Cost**: $0/month
**Quality**: Good for structure, adequate for creativity, decent prose

### Example 2: Smart Budget (DeepSeek First)

```yaml
foreman:
  task_models:
    coordinator: "mistral:7b"  # Fast, local
    health_check_review: "deepseek-chat"
    voice_calibration_guidance: "deepseek-chat"
    beat_structure_advice: "deepseek-chat"
    conflict_resolution: "deepseek-chat"
    scaffold_enrichment_decisions: "deepseek-chat"
    theme_analysis: "deepseek-chat"
    structural_planning: "deepseek-chat"

health_checks:
  models:
    timeline_consistency: "deepseek-chat"
    theme_resonance: "deepseek-chat"
    flaw_challenges: "deepseek-chat"
    cast_function: "mistral:7b"  # Local is fine here
```

**Cost**: ~$0.50-1/month
**Quality**: Excellent, 90% of premium quality

### Example 3: Quality First (Optimal Models)

```yaml
foreman:
  task_models:
    coordinator: "mistral:7b"
    health_check_review: "claude-3-7-sonnet-20250219"
    voice_calibration_guidance: "claude-3-7-sonnet-20250219"
    beat_structure_advice: "claude-3-7-sonnet-20250219"
    conflict_resolution: "claude-3-7-sonnet-20250219"
    scaffold_enrichment_decisions: "deepseek-chat"
    theme_analysis: "gpt-4o"
    structural_planning: "claude-3-7-sonnet-20250219"

health_checks:
  models:
    timeline_consistency: "claude-3-7-sonnet-20250219"
    theme_resonance: "gpt-4o"
    flaw_challenges: "deepseek-chat"
    cast_function: "qwen-plus"
    pacing_analysis: "mistral:7b"
    beat_progress: "mistral:7b"
    symbolic_layering: "gpt-4o"
```

**Cost**: ~$3-5/month
**Quality**: Best possible, each task optimized

---

## Phase 3E Implementation Status

**✅ Currently Implemented**:

1. **Task-Specific Model Assignment** ([backend/services/settings_service.py:183-192](backend/services/settings_service.py))
   - The Foreman dynamically selects models based on task type
   - Configuration via `foreman.task_models.*` in settings.yaml
   - Runtime override via API `model` parameter

2. **Health Check Model Assignment** ([backend/services/graph_health_service.py:211-226](backend/services/graph_health_service.py))
   - Each health check type can use a different model
   - Configuration via `health_checks.models.*` in settings.yaml
   - Default fallback model for undefined checks

3. **Multi-Provider Support** ([agents.yaml:1-93](agents.yaml))
   - OpenAI (GPT-4o, GPT-4o-mini)
   - Anthropic (Claude 3.7 Sonnet, Claude 3 Opus)
   - DeepSeek (DeepSeek V3)
   - Qwen (Qwen Plus, Qwen Turbo)
   - Mistral AI (Mistral Large)
   - Zhipu AI (GLM-4)
   - Google (Gemini 2.0 Flash)
   - xAI (Grok 2)
   - Ollama (Mistral 7B, Llama 3.2 3B)

4. **Settings Management**
   - YAML configuration files (project-level and global)
   - Environment variable overrides
   - REST API for dynamic updates
   - Automatic fallback to local models when API keys missing

---

## Future Enhancements

These features are planned but not yet implemented. They represent the natural evolution of the configurable model system.

### 1. Usage Analytics Dashboard

**Problem**: Writers don't know how much they're actually spending on AI models or which models they use most.

**Solution**: Real-time usage tracking and cost analysis.

**Features**:
- **Token Usage by Model**: See exactly how many tokens each model consumed
- **Cost Breakdown**: Daily/weekly/monthly spend per model and per task type
- **Usage Patterns**: Which tasks run most frequently, peak usage times
- **Cost Projections**: "At current usage, you'll spend $X this month"
- **Budget Alerts**: Notifications when approaching spending limits

**UI Mockup**:
```
┌─────────────────────────────────────────────┐
│ Model Usage (Last 30 Days)                 │
├─────────────────────────────────────────────┤
│ DeepSeek V3          1.2M tokens    $0.32   │
│ Mistral 7B (Local)   3.4M tokens    $0.00   │
│ Claude 3.7 Sonnet    245K tokens    $0.74   │
│ GPT-4o               89K tokens     $0.22   │
├─────────────────────────────────────────────┤
│ Total Spend: $1.28 | Projected: $1.85      │
└─────────────────────────────────────────────┘
```

**Implementation Path**:
1. Add usage logging to model orchestrator
2. Store token counts and costs in project SQLite database
3. Create `/analytics/usage` API endpoint
4. Build Svelte dashboard component
5. Add CSV export for external analysis

---

### 2. Model Recommendation Engine

**Problem**: Writers don't know which model to use for each task type. They rely on documentation and guesswork.

**Solution**: Intelligent recommendations based on actual usage patterns and quality metrics.

**Features**:
- **Quality-Based Recommendations**: "For theme_analysis, users who tried GPT-4o rated it 4.8/5"
- **Cost-Aware Suggestions**: "Switch to DeepSeek for 90% of the quality at 10% of the cost"
- **Pattern Detection**: "You use Claude for everything - consider DeepSeek for simple tasks to save $2/month"
- **A/B Test Results**: "Your voice calibration scored higher with DeepSeek than GPT-4o"
- **Automatic Optimization**: "We noticed you're overspending - switch these 3 tasks to save $4/month"

**UI Mockup**:
```
┌─────────────────────────────────────────────┐
│ 💡 Recommendation                           │
├─────────────────────────────────────────────┤
│ Your theme_analysis tasks use GPT-4o        │
│ ($0.35/week). Try DeepSeek V3 instead:      │
│                                             │
│ - 92% similar quality (based on 127 tests)  │
│ - $0.04/week cost (saves $0.31/week)        │
│ - 1.3x faster response time                 │
│                                             │
│ [Try DeepSeek]  [Compare Models]  [Ignore] │
└─────────────────────────────────────────────┘
```

**Implementation Path**:
1. Collect quality ratings (user thumbs up/down on Foreman responses)
2. Store model performance metrics (response time, token efficiency)
3. Build recommendation algorithm (cost vs. quality tradeoffs)
4. Create `/recommendations` API endpoint
5. Add recommendation cards to UI

---

### 3. Model A/B Testing Framework

**Problem**: Writers don't know if switching models will improve quality. They're afraid to experiment.

**Solution**: Run A/B tests to compare models on identical tasks.

**Features**:
- **Blind Comparison**: Generate same task with 2+ models, choose winner without knowing which is which
- **Quality Scoring**: Automatic scoring (via SceneAnalyzerService) plus manual rating
- **Statistical Significance**: "After 15 tests, DeepSeek wins 73% of the time (p < 0.05)"
- **Task-Specific Testing**: Test models specifically for voice_calibration, theme_analysis, etc.
- **Tournament Mode**: Pit 3+ models against each other, winner takes all

**UI Mockup**:
```
┌─────────────────────────────────────────────┐
│ A/B Test: theme_analysis                    │
├─────────────────────────────────────────────┤
│ Prompt: "Analyze the theme of redemption"   │
│                                             │
│ ┌─────────────┐  ┌─────────────┐           │
│ │ Variant A   │  │ Variant B   │           │
│ │ (Score: 87) │  │ (Score: 91) │           │
│ │             │  │             │           │
│ │ [Response]  │  │ [Response]  │           │
│ │             │  │             │           │
│ └─────────────┘  └─────────────┘           │
│                                             │
│ Which is better?  [A]  [B]  [Tie]          │
│                                             │
│ After voting, models revealed:             │
│ A = GPT-4o | B = DeepSeek V3               │
└─────────────────────────────────────────────┘
```

**Implementation Path**:
1. Create A/B test runner service (accepts prompt, runs N models)
2. Store test results with quality scores and user preferences
3. Build statistical analysis (confidence intervals, significance testing)
4. Create `/ab-test` API endpoints
5. Build comparison UI component

---

### 4. Model Capability Matrix

**Problem**: Documentation describes models qualitatively ("good at X"), but writers want objective comparisons.

**Solution**: Quantitative capability comparison table.

**Features**:
- **Benchmark Scores**: Speed, reasoning quality, prose quality, cost per 1M tokens
- **Task Suitability**: Each model rated 1-5 stars for each task type
- **Real Usage Data**: "Based on 1,247 Writer's Factory tasks"
- **Context Window**: Max token limits for each model
- **Latency**: Average response time per model

**UI Mockup**:
```
┌───────────────────────────────────────────────────────────────────┐
│ Model Capability Matrix                                           │
├─────────────┬─────────┬──────────┬───────────┬───────┬───────────┤
│ Model       │ Reason  │ Prose    │ Speed     │ Cost  │ Context   │
├─────────────┼─────────┼──────────┼───────────┼───────┼───────────┤
│ GPT-4o      │ ★★★★★   │ ★★★★☆    │ 1.2s      │ $2.50 │ 128K      │
│ Claude 3.7  │ ★★★★★   │ ★★★★★    │ 1.8s      │ $3.00 │ 200K      │
│ DeepSeek V3 │ ★★★★★   │ ★★★★☆    │ 1.5s      │ $0.27 │ 64K       │
│ Mistral 7B  │ ★★★☆☆   │ ★★★☆☆    │ 0.3s      │ $0.00 │ 33K       │
│ Gemini 2.0  │ ★★★★☆   │ ★★★★☆    │ 0.9s      │ $0.08 │ 1M        │
└─────────────┴─────────┴──────────┴───────────┴───────┴───────────┘

Task Recommendations:
- Voice Calibration: Claude 3.7 (prose ★★★★★)
- Theme Analysis: GPT-4o (reasoning ★★★★★)
- Quick Drafts: Mistral 7B (speed 0.3s, free)
```

**Implementation Path**:
1. Run standardized benchmarks (reasoning, prose, speed tests)
2. Collect real-world performance data from production usage
3. Store capability scores in database
4. Create `/models/capabilities` API endpoint
5. Build comparison table component

---

### 5. Local Model Setup Wizard

**Problem**: Setting up Ollama and local models is intimidating for non-technical writers.

**Solution**: One-click local model installation and configuration.

**Features**:
- **Auto-Detect Ollama**: Check if Ollama is installed, offer download link if not
- **Model Recommendations**: "Your Mac can run Mistral 7B (4.4GB) comfortably"
- **One-Click Install**: Click "Install Mistral 7B" → downloads and configures automatically
- **Hardware Guidance**: "Your GPU can handle 7B models but not 13B"
- **Fallback Config**: Automatically configure local models as fallbacks for cloud models

**UI Mockup**:
```
┌─────────────────────────────────────────────┐
│ Local Model Setup                           │
├─────────────────────────────────────────────┤
│ ✅ Ollama detected (v0.1.45)                │
│                                             │
│ Recommended Models:                         │
│ ┌─────────────────────────────────────────┐ │
│ │ Mistral 7B                              │ │
│ │ Size: 4.4 GB | Speed: Fast             │ │
│ │ Best for: Coordination, quick drafts    │ │
│ │ [Install] [Already Installed ✓]        │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ Llama 3.2 3B                            │ │
│ │ Size: 2.0 GB | Speed: Very Fast        │ │
│ │ Best for: Brainstorming, prototypes     │ │
│ │ [Install]                               │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

**Implementation Path**:
1. Add Ollama detection to settings service
2. Create model download/install API endpoint
3. Build model recommendation algorithm (based on hardware specs)
4. Create setup wizard UI component
5. Add progress tracking for model downloads

---

### 6. Model Migration Assistant

**Problem**: Writers want to switch from one model to another but fear breaking their workflow.

**Solution**: Guided migration with before/after comparison.

**Features**:
- **Impact Preview**: "Switching to DeepSeek will save $3/month but may reduce quality by 5%"
- **Rollback Safety**: "Try DeepSeek for 1 week, revert if unhappy"
- **Side-by-Side Testing**: Run old and new models in parallel for comparison
- **Gradual Migration**: "Switch 25% of tasks to DeepSeek, monitor for 3 days, then 50%, 75%, 100%"

**Implementation Path**:
1. Build migration planner (analyze current config, suggest alternatives)
2. Create staged rollout system (percentage-based routing)
3. Add rollback mechanism (revert to previous settings)
4. Build migration UI with impact previews

---

## Summary: Current vs. Future

| Feature | Status | Location |
|---------|--------|----------|
| **Task-specific models** | ✅ Implemented | `settings_service.py:183-192` |
| **Health check models** | ✅ Implemented | `graph_health_service.py:211-226` |
| **Multi-provider support** | ✅ Implemented | `agents.yaml:1-93` |
| **Settings management** | ✅ Implemented | Full settings system |
| **Usage analytics** | 📋 Planned | Phase 4+ |
| **Model recommendations** | 📋 Planned | Phase 4+ |
| **A/B testing** | 📋 Planned | Phase 4+ |
| **Capability matrix** | 📋 Planned | Phase 4+ |
| **Local setup wizard** | 📋 Planned | Phase 4+ |
| **Migration assistant** | 📋 Planned | Phase 4+ |

---

*Last Updated: November 25, 2025 - Phase 3E*
