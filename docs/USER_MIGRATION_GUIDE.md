# Squad System Migration Guide

> **For Writers Factory Users**: Upgrading from Individual Model Configuration to Squad System

---

## What's Changing?

### Before (Phase 3E): Configure 9+ Models Individually

```
Settings Panel
├── Foreman Coordinator Model: [dropdown]
├── Strategic Analysis Model: [dropdown]
├── Tournament Models (3-5): [multi-select]
└── Health Check Models (8 types):
    ├── Timeline Consistency: [dropdown]
    ├── Theme Resonance: [dropdown]
    ├── Flaw Challenges: [dropdown]
    ├── Cast Function: [dropdown]
    ├── Pacing Analysis: [dropdown]
    ├── Beat Progress: [dropdown]
    ├── Symbolic Layering: [dropdown]
    └── Default: [dropdown]
```

**Problem**: Overwhelming! Which model for which task? What will this cost?

---

### After (Phase 3F): Choose Your Squad

```
Squad Selection
├── 🏠 Local Squad (Free)
├── 💎 Hybrid Squad (Recommended - $2/month)
└── 🚀 Pro Squad (Premium - $15/month)
```

**Solution**: One choice instead of 9+. Pre-optimized configurations with cost estimates!

---

## Do I Have to Migrate?

**No!** Your current configuration keeps working. The Squad System is **opt-in**.

### You Should Try Squads If:

- ✅ You find model configuration confusing
- ✅ You want cost predictability
- ✅ You're starting a new project
- ✅ You want to simplify your workflow

### Stick With Manual Config If:

- ✅ You have a custom configuration you love
- ✅ You're using models not included in squads
- ✅ You prefer fine-grained control

---

## The Three Squads

### 🏠 Local Squad (Free)

**Best For**: Privacy-focused writers, offline work, zero budget

**Models Used**:
- **Coordinator**: Mistral 7B (local via Ollama)
- **Strategic Tasks**: Llama 3.2 (local via Ollama)
- **Tournament**: 3 local models
- **Health Checks**: All local

**Requirements**:
- 8GB RAM minimum
- Ollama installed
- ~10GB disk space for models

**Cost**: $0/month

**Speed**: Fast coordination, slower strategic analysis

---

### 💎 Hybrid Squad (RECOMMENDED)

**Best For**: Most writers, best value, course default

**Models Used**:
- **Coordinator**: Mistral 7B (local - fast)
- **Strategic Tasks**: DeepSeek V3 (cloud - powerful)
- **Tournament**: 4 budget models (DeepSeek, Qwen Plus, Zhipu GLM-4, Gemini 2.0 Flash)
- **Health Checks**: Smart routing (simple → local, complex → cloud)

**Requirements**:
- 8GB RAM minimum
- Ollama installed (for coordinator)
- DeepSeek API key (free tier: 1M tokens/month)

**Cost**: ~$2/month for typical usage (20 tournaments/week)

**Speed**: Fast coordinator + powerful strategic analysis

**Why This Squad?**
- DeepSeek V3 is one of the best value models in 2025 (~80% of GPT-4o quality at 1/10th the price)
- Local coordinator means instant task routing
- Budget tournament models offer diverse perspectives
- Cost-effective for novel-length projects

---

### 🚀 Pro Squad (Premium)

**Best For**: Professional writers, maximum quality, serious projects

**Models Used**:
- **Coordinator**: Mistral 7B (local - fast)
- **Strategic Tasks**: Claude 3.7 Sonnet (cloud - top-tier)
- **Tournament**: 6 premium models (Claude, GPT-4o, Grok 2, Mistral Large, DeepSeek, Qwen Plus)
- **Health Checks**: Claude 3.7 Sonnet for all complex checks

**Requirements**:
- 8GB RAM minimum
- Ollama installed
- Anthropic API key (pay-as-you-go)
- OpenAI API key (pay-as-you-go)

**Cost**: ~$15/month for typical usage (20 tournaments/week)

**Speed**: Same fast coordinator, premium strategic analysis

**Why This Squad?**
- Claude 3.7 Sonnet is the best creative writing model (as of Jan 2025)
- GPT-4o, Grok 2, Mistral Large provide premium diversity
- Maximum quality for publishable work

---

## How to Migrate (Step-by-Step)

### Step 1: Check Your Hardware

Open Terminal and run:

```bash
curl http://localhost:8000/system/hardware
```

**Look for**:
- `"ram_gb": 8` or higher ✅
- `"ollama_installed": true` ✅
- `"ollama_models": ["mistral:7b", ...]` ✅

**If Ollama is NOT installed**:

```bash
# macOS
brew install ollama

# Start Ollama
ollama serve

# Pull required models
ollama pull mistral:7b
ollama pull llama3.2:3b
```

---

### Step 2: View Available Squads

```bash
curl http://localhost:8000/squad/available
```

**You'll see**:
- Squad details (models, requirements, cost)
- Which squads are available on your system
- Missing requirements (e.g., "DeepSeek API key needed")

---

### Step 3: Apply Your Squad

#### Option A: Local Squad (Free)

```bash
curl -X POST http://localhost:8000/squad/apply \
  -H "Content-Type: application/json" \
  -d '{"squad_id": "local"}'
```

No API keys needed!

---

#### Option B: Hybrid Squad (Recommended)

1. **Get DeepSeek API Key** (free tier):
   - Go to [platform.deepseek.com](https://platform.deepseek.com)
   - Sign up (free)
   - Copy your API key

2. **Add to .env file**:
   ```bash
   # Add this line to backend/.env
   DEEPSEEK_API_KEY=your_api_key_here
   ```

3. **Apply Squad**:
   ```bash
   curl -X POST http://localhost:8000/squad/apply \
     -H "Content-Type: application/json" \
     -d '{"squad_id": "hybrid"}'
   ```

---

#### Option C: Pro Squad (Premium)

1. **Get API Keys**:
   - **Anthropic**: [console.anthropic.com](https://console.anthropic.com) (Claude)
   - **OpenAI**: [platform.openai.com](https://platform.openai.com) (GPT-4o)

2. **Add to .env file**:
   ```bash
   # Add these lines to backend/.env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   OPENAI_API_KEY=your_openai_key_here
   DEEPSEEK_API_KEY=your_deepseek_key_here  # Optional, for cost savings
   ```

3. **Apply Squad**:
   ```bash
   curl -X POST http://localhost:8000/squad/apply \
     -H "Content-Type: application/json" \
     -d '{"squad_id": "pro"}'
   ```

---

### Step 4: Verify Squad is Active

```bash
curl http://localhost:8000/squad/active
```

**Expected Response**:
```json
{
  "squad": "hybrid",
  "setup_complete": true,
  "course_mode": false
}
```

---

## What Happens to My Custom Settings?

### Settings That Change

Only model assignments change:

```yaml
# Before
foreman.coordinator_model: "llama3.2:3b"
tournament.default_models: ["claude-3-7-sonnet-20250219", "gpt-4o"]

# After (Hybrid Squad)
foreman.coordinator_model: "mistral:7b"  # ← Changed
tournament.default_models: ["deepseek-chat", "qwen-plus", ...]  # ← Changed
```

---

### Settings That Don't Change

**Everything else is preserved**:

```yaml
# These stay exactly the same:
scoring.voice_authenticity_weight: 30
scoring.character_consistency_weight: 20
voice.strictness: "high"
voice.min_match_score: 85
enhancement.auto_threshold: 85
foreman.proactiveness: "high"
# ... and all other settings
```

**Your custom scoring weights, voice settings, enhancement thresholds, etc. are untouched!**

---

## Can I Switch Squads Later?

**Yes!** Switching is safe and reversible.

### Example: Upgrade Path

```bash
# Start with Local Squad (free)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "local"}'

# Try Hybrid Squad (add DeepSeek key first)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "hybrid"}'

# Upgrade to Pro Squad (add Claude/GPT keys first)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "pro"}'

# Go back to Hybrid if Pro is too expensive
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "hybrid"}'
```

**No data loss, no corruption.** Just model assignment changes.

---

## Multiple Projects with Different Squads

You can use **different squads for different projects**:

```bash
# Project 1: Practice novel (Local Squad - free)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "local", "project_id": "practice_novel"}'

# Project 2: Serious novel (Pro Squad - premium)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "pro", "project_id": "my_masterpiece"}'

# Project 3: Experimental (Hybrid Squad - balanced)
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "hybrid", "project_id": "experiment"}'
```

**Each project independent!**

---

## Cost Examples

### Typical Novel Project (50,000 words)

#### With Hybrid Squad ($2/month)

**Tournament Usage** (most expensive operation):
- 20 tournaments per week
- 3 models × 3 strategies = 9 variants per tournament
- ~2000 tokens per variant

**Cost Breakdown**:
```
DeepSeek V3: $0.007 per tournament
Qwen Plus: $0.008 per tournament
Gemini 2.0 Flash: $0.002 per tournament
Total per tournament: ~$0.017

Weekly: 20 tournaments × $0.017 = $0.34/week
Monthly: $0.34 × 4 = ~$1.36/month
```

**Plus**:
- Strategic analysis (health checks, theme analysis): ~$0.50/month
- **Total**: ~$2/month

---

#### With Pro Squad ($15/month)

**Tournament Usage**:
```
Claude 3.7 Sonnet: $0.06 per tournament
GPT-4o: $0.05 per tournament
Grok 2: $0.04 per tournament
Total per tournament: ~$0.15

Weekly: 20 tournaments × $0.15 = $3/week
Monthly: $3 × 4 = ~$12/month
```

**Plus**:
- Strategic analysis: ~$3/month
- **Total**: ~$15/month

---

### Cost Saving Tips

1. **Use Hybrid Squad for Drafting**: $2/month while writing
2. **Upgrade to Pro for Final Polish**: 1-2 weeks at $15/month = ~$7 total
3. **Run Fewer Tournaments**: Skip tournaments for less critical scenes
4. **Local Squad for Experimentation**: Free practice with local models

---

## Troubleshooting

### "DeepSeek API key not found"

**Solution**: Add to `backend/.env`:

```bash
DEEPSEEK_API_KEY=sk-...
```

Then restart backend:

```bash
cd backend
python -m uvicorn api:app --reload
```

---

### "Ollama not detected"

**Solution**: Install Ollama:

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

Then pull models:

```bash
ollama pull mistral:7b
ollama pull llama3.2:3b
```

---

### "Insufficient RAM for local models"

**Your System**: < 8GB RAM

**Solution**: Use cloud-only configuration (contact support) or:
- Upgrade RAM
- Use remote Ollama instance
- Stick with Phase 3E manual config (all cloud models)

---

### "Squad applied but models not working"

**Check**:
1. API keys in `.env` file ✅
2. Backend restarted after adding keys ✅
3. Ollama running (`ollama serve`) ✅
4. Models pulled (`ollama list`) ✅

**Test DeepSeek API**:

```bash
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

---

## Frequently Asked Questions

### Q: Will this break my existing project?

**A**: No! Squad System only changes model assignments. All your work (Story Bible, scenes, voice calibration) is untouched.

---

### Q: Can I go back to manual configuration?

**A**: Yes! Just don't apply a squad. Or apply a squad and then manually override individual model settings in the Settings Panel.

---

### Q: What if I use a model not in any squad?

**A**: Keep using Phase 3E manual config! Squads are presets for common use cases. You can always manually configure any model.

---

### Q: How do I know which squad is right for me?

**Decision Tree**:

```
Do you have $0 budget?
  → Yes: Local Squad 🏠

Do you want the absolute best quality?
  → Yes: Pro Squad 🚀

Do you want good quality at low cost?
  → Yes: Hybrid Squad 💎 (RECOMMENDED)

Are you in a course/workshop?
  → Check with instructor (probably Hybrid)
```

---

### Q: Can I customize a squad?

**A**: Sort of! Apply a squad, then manually override specific models:

```bash
# Apply Hybrid Squad
curl -X POST http://localhost:8000/squad/apply \
  -d '{"squad_id": "hybrid"}'

# Then manually override tournament models if desired
# (via Settings Panel or API)
```

---

### Q: What's "Course Mode"?

**A**: A future feature where instructors provide API keys for students. Not implemented yet (Phase 3G).

---

## When UI is Ready (Phase 3G)

**Coming Soon**: Squad Selection Wizard in Settings Panel

Instead of curl commands, you'll see:

```
Settings → Squads Tab
├── 🏠 Local Squad [Free]
│   ├── Requirements: ✅ Ollama installed
│   ├── Cost: $0/month
│   └── [Select This Squad]
├── 💎 Hybrid Squad [Recommended]
│   ├── Requirements: ⚠️ DeepSeek API key needed
│   ├── Cost: ~$2/month
│   └── [Select This Squad]
└── 🚀 Pro Squad [Premium]
    ├── Requirements: ❌ Claude API key missing
    ├── Cost: ~$15/month
    └── [Select This Squad]
```

**For now**: Use the curl commands in this guide!

---

## Summary

### ✅ What You Need to Know

1. **Squad System is optional** - Your current config keeps working
2. **One choice instead of 9+** - Simpler configuration
3. **Hybrid Squad recommended** - Best balance of cost and quality ($2/month)
4. **Reversible** - Switch squads anytime without data loss
5. **Per-project** - Different squads for different novels

### 🚀 Quick Start

```bash
# 1. Check hardware
curl http://localhost:8000/system/hardware

# 2. Apply Hybrid Squad (after adding DEEPSEEK_API_KEY to .env)
curl -X POST http://localhost:8000/squad/apply \
  -H "Content-Type: application/json" \
  -d '{"squad_id": "hybrid"}'

# 3. Start writing!
```

---

**Questions?** Check the [Technical Migration Report](PHASE_3E_TO_3F_MIGRATION_REPORT.md) or contact support.

**Happy Writing!** ✍️
