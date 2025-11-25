# Phase 3E Quick Start Guide

**Intelligent Foreman - Cloud-Native Multi-Model AI**

---

## 🚀 What's New

Your Writers Factory now has **intelligent AI routing**:
- **15 different task types** automatically routed to optimal models
- **Cloud AI** for strategic reasoning (DeepSeek, Claude, GPT-4o)
- **Local AI** for fast coordination (Mistral, Llama)
- **100% configurable** - customize every model choice
- **Cost-conscious** - $0/month (local) to $5/month (premium)

---

## ⚡ Quick Setup

### Option 1: Use Defaults (Recommended)

**No configuration needed!** The system works out of the box:
- Coordination tasks → Mistral (local, free)
- Strategic tasks → DeepSeek V3 (cloud, cheap)
- Health checks → Optimal models per check type

Just make sure you have API keys in `.env`:
```bash
DEEPSEEK_API_KEY=your_key_here
ANTHROPIC_API_KEY=optional_claude_key
OPENAI_API_KEY=optional_gpt4_key
```

### Option 2: Customize Models

Edit `settings.yaml` to override any model:

```yaml
foreman:
  task_models:
    coordinator: "mistral"                    # Local, fast
    health_check_review: "gpt-4o"             # Override to GPT-4o
    theme_analysis: "claude-3-5-sonnet"       # Override to Claude

health_checks:
  models:
    timeline_consistency: "claude-3-5-sonnet"
    theme_resonance: "gpt-4o"
```

### Option 3: All Local (Free)

Want to use only free local models? Set everything to `mistral`:

```yaml
foreman:
  task_models:
    coordinator: "mistral"
    health_check_review: "mistral"
    voice_calibration_guidance: "mistral"
    beat_structure_advice: "mistral"
    conflict_resolution: "mistral"
    scaffold_enrichment_decisions: "mistral"
    theme_analysis: "mistral"
    structural_planning: "mistral"
```

---

## 📊 How It Works

### Automatic Task Routing

The Foreman automatically detects what you're asking and routes to the right model:

**Simple coordination** → Mistral (local)
```
User: "What's the status of my work order?"
→ Uses: mistral (local) ⚡ Fast & Free
```

**Strategic reasoning** → DeepSeek/Claude/GPT (cloud)
```
User: "The health check says my pacing score is 73. What does that mean?"
→ Uses: deepseek-chat (cloud) 🧠 Smart & Cheap

User: "How should I structure Act 2 to build tension?"
→ Uses: deepseek-chat (cloud) 🧠 Deep Reasoning
```

**Health checks** → Optimal model per check
```
Timeline consistency → claude-3-5-sonnet (best at narrative reasoning)
Theme resonance → gpt-4o (excellent thematic analysis)
Flaw challenges → deepseek-chat (deep character psychology)
Cast function → qwen-plus (fast, cheap, good enough)
```

---

## 💰 Cost Examples

### Free (Local Only)
- All models: mistral
- **Cost**: $0/month
- **Quality**: Good for structure, adequate for strategy

### Smart Budget (<$1/month)
- Coordination: mistral (local)
- Strategic: deepseek-chat (cloud)
- **Cost**: ~$0.50/month
- **Quality**: Excellent reasoning, 90% of premium quality

### Premium ($3-5/month)
- Optimal model for each task
- Timeline: claude-3-5-sonnet
- Theme: gpt-4o
- Strategic: deepseek-chat
- **Cost**: ~$3-5/month
- **Quality**: Best possible

---

## 🎯 Common Tasks

### Check Current Configuration

```bash
# See all default settings
curl http://localhost:8000/settings/defaults | python -m json.tool

# See specific category
curl http://localhost:8000/settings/foreman
```

### Update Models via API

```bash
# Change theme analysis to GPT-4o
curl -X POST http://localhost:8000/settings/update \
  -H "Content-Type: application/json" \
  -d '{"foreman.task_models.theme_analysis": "gpt-4o"}'
```

### Test Model Routing

Start a Foreman session and ask different types of questions:

```python
from backend.agents.foreman import get_foreman

foreman = get_foreman()
await foreman.start_project("Test", "Protagonist")

# Simple coordination (uses mistral)
response = await foreman.chat("What's the status?")

# Strategic reasoning (uses deepseek-chat)
response = await foreman.chat("How should I structure my Act 2?")

# Check which model was used
print(response["model_routing"])
# {'task_type': 'structural_planning', 'is_advisor_task': True}
```

---

## 📖 Task Types Reference

### Foreman Tasks (8 Types)

| Message Contains | Task Type | Default Model | Purpose |
|------------------|-----------|---------------|---------|
| "status", "complete" | `coordinator` | mistral | Fast coordination |
| "health check", "score" | `health_check_review` | deepseek-chat | Interpret results |
| "voice", "tournament" | `voice_calibration_guidance` | deepseek-chat | Voice selection |
| "beat", "structure", "pacing" | `beat_structure_advice` | deepseek-chat | Beat structure |
| "conflict", "contradiction" | `conflict_resolution` | deepseek-chat | Timeline issues |
| "enrich", "scaffold" | `scaffold_enrichment_decisions` | deepseek-chat | Scaffold work |
| "theme", "symbolism" | `theme_analysis` | deepseek-chat | Theme analysis |
| "plan", "outline", "strategy" | `structural_planning` | deepseek-chat | High-level planning |

### Health Check Types (7 Types)

| Check | Default Model | What It Detects |
|-------|---------------|-----------------|
| Timeline Consistency | claude-3-5-sonnet | Character teleportation, world rules violations |
| Theme Resonance | gpt-4o | Weak themes at critical beats |
| Flaw Challenges | deepseek-chat | Fatal Flaw challenge gaps |
| Cast Function | qwen-plus | Underutilized characters |
| Pacing Analysis | mistral | Flat tension across chapters |
| Beat Progress | mistral | Beat structure deviations |
| Symbolic Layering | gpt-4o | Symbol evolution |

---

## 🔍 Monitoring & Logs

### Watch Model Selection

Tail the logs to see which models are being used:

```bash
# In terminal where API is running, you'll see:
# 📋 Using mistral for coordinator           (local/fast)
# 🧠 Using deepseek-chat for theme_analysis  (strategic)
```

### Check API Keys

```bash
# Verify API keys are detected
python -c "import os; print('DEEPSEEK_API_KEY:', 'Found' if os.getenv('DEEPSEEK_API_KEY') else 'Missing')"
```

---

## 🆘 Troubleshooting

### "Falling back to Ollama"

**Cause**: API key not found or invalid

**Fix**: Add API key to `.env`:
```bash
DEEPSEEK_API_KEY=your_key_here
```

### "Ollama query failed"

**Cause**: Ollama not running

**Fix**: Start Ollama:
```bash
ollama serve
```

### Models still using default

**Cause**: Settings not loaded

**Fix**: Restart API server after updating `settings.yaml`

---

## 📚 Full Documentation

- **Quick Start**: This document
- **Complete Guide**: `docs/CONFIGURABLE_MODEL_ASSIGNMENTS.md` (430 lines)
- **Implementation Details**: `docs/dev_logs/PHASE_3E_NEXT_STEPS.md`
- **Completion Summary**: `docs/dev_logs/PHASE_3E_COMPLETION_SUMMARY.md`

---

## ✅ Verification Checklist

- [ ] API server starts without errors
- [ ] Can query settings: `GET /settings/defaults`
- [ ] Foreman responds to messages
- [ ] Logs show model routing (📋 or 🧠 indicators)
- [ ] Health checks run without errors
- [ ] API keys detected (or graceful fallback to Ollama)

---

**That's it! You're ready to use the intelligent multi-model system.** 🎉

*For detailed configuration options, see `docs/CONFIGURABLE_MODEL_ASSIGNMENTS.md`*
