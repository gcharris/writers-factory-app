# Configurable Model Assignments

**Phase 3E Feature**: All AI model assignments are fully configurable, allowing writers to choose the optimal model for each task type based on their preferences, budget, and quality requirements.

## Overview

The Writers Factory supports multiple AI providers and allows you to assign specific models to specific tasks. You can mix and match local models (via Ollama) with cloud models (OpenAI, Anthropic, DeepSeek, Qwen) based on your needs.

---

## Foreman Task-Specific Models

The Foreman uses different models for different types of tasks. Configure these in your `settings.yaml` or via the API.

### Default Configuration

```yaml
foreman:
  coordinator_model: "mistral"  # Fallback for undefined tasks

  task_models:
    coordinator: "mistral"                      # Simple coordination
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
    default_model: "llama3.2"  # Fallback

    # Task-specific assignments (Phase 3E)
    timeline_consistency: "claude-3-5-sonnet"  # Best at narrative reasoning
    theme_resonance: "gpt-4o"                   # Excellent thematic analysis
    flaw_challenges: "deepseek-chat"            # Deep character psychology
    cast_function: "qwen-plus"                  # Fast, cheap, good enough
    pacing_analysis: "mistral"                  # Local for fast iteration
    beat_progress: "mistral"                    # Structural validation
    symbolic_layering: "gpt-4o"                 # Pattern recognition
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
| `mistral` | 7B | Coordination, structure validation | Very Fast |
| `llama3.2` | 3B | Simple tasks, ultra-fast responses | Fastest |
| `llama3.1` | 8B-70B | General purpose, good quality | Fast-Medium |

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
  theme_analysis: "gemini-1.5-pro"
  structural_planning: "gemini-1.5-flash"  # Faster, cheaper
```

**Cost**: ~$1.25/1M tokens (Pro), ~$0.075/1M tokens (Flash)
**Best For**: Multimodal analysis, long-context reasoning, creative tasks

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
  coordinator_model: "mistral"
  task_models:
    coordinator: "mistral"
    health_check_review: "mistral"
    voice_calibration_guidance: "mistral"
    beat_structure_advice: "mistral"
    conflict_resolution: "mistral"
    scaffold_enrichment_decisions: "mistral"
    theme_analysis: "mistral"
    structural_planning: "mistral"

health_checks:
  models:
    default_model: "mistral"
    timeline_consistency: "mistral"
    theme_resonance: "mistral"
    flaw_challenges: "mistral"
    cast_function: "mistral"
```

**Cost**: $0/month
**Quality**: Good for structure, adequate for creativity

### Example 2: Smart Budget (DeepSeek First)

```yaml
foreman:
  task_models:
    coordinator: "mistral"  # Fast, local
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
    cast_function: "mistral"  # Local is fine here
```

**Cost**: ~$0.50-1/month
**Quality**: Excellent, 90% of premium quality

### Example 3: Quality First (Optimal Models)

```yaml
foreman:
  task_models:
    coordinator: "mistral"
    health_check_review: "claude-3-5-sonnet"
    voice_calibration_guidance: "claude-3-5-sonnet"
    beat_structure_advice: "claude-3-5-sonnet"
    conflict_resolution: "claude-3-5-sonnet"
    scaffold_enrichment_decisions: "deepseek-chat"
    theme_analysis: "gpt-4o"
    structural_planning: "claude-3-5-sonnet"

health_checks:
  models:
    timeline_consistency: "claude-3-5-sonnet"
    theme_resonance: "gpt-4o"
    flaw_challenges: "deepseek-chat"
    cast_function: "qwen-plus"
    pacing_analysis: "mistral"
    beat_progress: "mistral"
    symbolic_layering: "gpt-4o"
```

**Cost**: ~$3-5/month
**Quality**: Best possible, each task optimized

---

*Last Updated: November 24, 2025 - Phase 3E*
