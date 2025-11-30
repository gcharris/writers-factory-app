# Live Squad Architecture - Writers Factory

**Version:** 3.0
**Last Updated:** November 25, 2025
**Status:** Design Document (Not Yet Implemented)

---

## Executive Summary

The Writers Factory uses **AI agents** to help writers create novels. Currently, it's too complicated - writers need to understand 9+ different AI models, manage API keys, and configure settings they don't care about.

**The Solution:** A simple 3-tier system where writers pick ONE thing:
1. **Local Squad** (Free, Private, Offline)
2. **Hybrid Squad** (Best Value - Free + Local)
3. **Pro Squad** (Premium Quality, Your API Keys)

Everything else happens automatically.

---

## The Writer's Journey (How It Actually Works)

### Stage 1: Story Bible Creation (ARCHITECT Mode)

**What Happens:**
- Writer opens the app for the first time
- The Foreman asks questions to build the Story Bible (15 templates)
- Takes 1-3 hours of Q&A about characters, world, theme, plot structure

**Current Reality:**
- The Foreman uses **Mistral 7B** (local Ollama model)
- Works immediately, no setup required
- Quality is "good enough" for brainstorming but struggles with complex narrative logic

**The Problem:**
- Mistral 7B (7.3B parameters) isn't smart enough for deep Story Bible work
- Writers hit quality ceiling when dealing with timeline consistency, Fatal Flaw architecture, 15-beat structure validation

**Proposed Change:**
- Switch The Foreman to **DeepSeek V3** for ARCHITECT mode
- **Why DeepSeek?**
  - GPT-4 level intelligence at $0.27/1M tokens (vs. $2.50 for GPT-4o)
  - Can handle complex narrative reasoning
  - Cheap enough to subsidize for all users during Story Bible creation
  - A full Story Bible (~50K tokens) costs $0.01 to generate

**User Experience:**
```
Writer: "Tell me about your protagonist."
Foreman (DeepSeek V3): [Asks intelligent follow-up questions about Fatal Flaw,
                        internal vs external conflict, character arc alignment
                        with 15-beat structure]
```

---

### Stage 2: Voice Calibration (VOICE_CALIBRATION Mode)

**What Happens:**
- Story Bible is complete
- Writer provides 2-3 sample paragraphs of their target voice
- The app runs a **tournament** with multiple AI models trying to match the voice
- Writer picks the best match (becomes their "voice bundle")

**Current Reality:**
- Tournament uses 3 default models: Claude Sonnet, GPT-4o, DeepSeek V3
- Each model generates 5 variants using different strategies
- Writer votes on best variants (scored by Scene Analyzer)
- Winning variant becomes the "voice bundle" injected into all future prompts

**The Problem:**
- Writers don't know which models to include in the tournament
- Default selection may not match their budget or quality needs
- No way to test local models (Mistral 7B, Magnum 12B) that might be "good enough"

**Proposed Solution: Squad Builder Wizard**

**Trigger:** After Story Bible complete, before first Voice Tournament
**Purpose:** Help writer pick their "squad" of models

**Wizard Flow:**

#### Step 1: Hardware Check
```
┌─────────────────────────────────────────────┐
│ System Scan                                 │
├─────────────────────────────────────────────┤
│ ✅ 16GB RAM detected                        │
│ ✅ Ollama installed (v0.1.45)               │
│ ✅ Apple Silicon GPU                        │
│                                             │
│ You can run local models up to 12B params   │
│                                             │
│ [Continue]                                  │
└─────────────────────────────────────────────┘
```

#### Step 2: Choose Your Squad

**Option A: Local Squad** (Free, Private, Offline)
```
┌─────────────────────────────────────────────┐
│ 🏠 Local Squad (100% Offline)               │
├─────────────────────────────────────────────┤
│ Best For: Privacy, zero ongoing costs       │
│                                             │
│ Your Team:                                  │
│ • Logic: Mistral 7B (already installed)     │
│ • Prose: Magnum v4 12B (8GB download)       │
│ • Coordination: Llama 3.2 3B (installed)    │
│                                             │
│ Quality: ⭐⭐⭐⭐☆ (Very Good)               │
│ Cost: $0/month                              │
│ Setup: 15 min download                      │
│                                             │
│ [Select This Squad]                         │
└─────────────────────────────────────────────┘
```

**Option B: Hybrid Squad** (Recommended - Best Value)
```
┌─────────────────────────────────────────────┐
│ 💎 Hybrid Squad (Best Value) ⭐ RECOMMENDED │
├─────────────────────────────────────────────┤
│ Best For: High quality at minimal cost      │
│                                             │
│ Your Team:                                  │
│ • Logic: DeepSeek V3 (cloud API)            │
│ • Prose: Magnum v4 12B (local, 8GB)         │
│ • Coordination: Mistral 7B (local)          │
│                                             │
│ Quality: ⭐⭐⭐⭐⭐ (Excellent)              │
│ Cost: ~$0.50/month (heavy usage)            │
│ Setup: API key + 15 min download            │
│                                             │
│ [Select This Squad]                         │
└─────────────────────────────────────────────┘
```

**Option C: Pro Squad** (Premium Quality)
```
┌─────────────────────────────────────────────┐
│ 🚀 Pro Squad (Maximum Quality)              │
├─────────────────────────────────────────────┤
│ Best For: Professional writers, publishers  │
│                                             │
│ Your Team:                                  │
│ • Logic: GPT-4o (OpenAI)                    │
│ • Prose: Claude 3.7 Sonnet (Anthropic)      │
│ • Coordination: Mistral 7B (local fallback) │
│                                             │
│ Quality: ⭐⭐⭐⭐⭐ (Best Available)         │
│ Cost: ~$3-5/month                           │
│ Setup: Enter your API keys                  │
│                                             │
│ [Select This Squad]                         │
└─────────────────────────────────────────────┘
```

#### Step 3: Setup/Download

If Local or Hybrid selected:
```
┌─────────────────────────────────────────────┐
│ Downloading Magnum v4 12B...                │
├─────────────────────────────────────────────┤
│ ████████████████░░░░░░░░░░ 65%             │
│ 5.2 GB / 8.0 GB                             │
│                                             │
│ Estimated time: 3 minutes                   │
│                                             │
│ [Cancel]                                    │
└─────────────────────────────────────────────┘
```

If Pro selected:
```
┌─────────────────────────────────────────────┐
│ Enter Your API Keys                         │
├─────────────────────────────────────────────┤
│ OpenAI API Key:                             │
│ [sk-proj-... ]                              │
│                                             │
│ Anthropic API Key:                          │
│ [sk-ant-...]                                │
│                                             │
│ [Test Keys]  [Save]                         │
└─────────────────────────────────────────────┘
```

---

### Stage 3: Director Mode (Scene Writing)

**What Happens:**
- Writer selects a scene to write (e.g., "Chapter 3, Midpoint")
- The app generates 15 scene variants in a tournament
- Writer picks the best one or creates a hybrid

**Current Reality:**
- Tournament uses the 3 default models (Claude, GPT-4o, DeepSeek)
- Each model uses 5 different strategies (Action, Dialogue, Logic, Atmosphere, Integration)
- Scene Analyzer scores each variant (Voice Match, Character, Metaphor, Anti-Pattern, Phase Beat)

**Proposed Change: Squad-Based Tournament**

**How It Works:**
- Tournament automatically uses the models from your chosen squad
- **Local Squad:** Mistral 7B + Magnum 12B compete (2 models × 5 strategies = 10 variants)
- **Hybrid Squad:** DeepSeek V3 + Magnum 12B compete (2 models × 5 strategies = 10 variants)
- **Pro Squad:** GPT-4o + Claude 3.7 compete (2 models × 5 strategies = 10 variants)

**User Experience:**
```
[Director Mode - Scene Tournament]

Using your Hybrid Squad:
- DeepSeek V3 (5 variants)
- Magnum 12B (5 variants)

Generating variants... 7/10 complete

[View Results]
```

---

## Technical Implementation

### 1. Data Structures

#### A. Squad Presets (Hardcoded)

Stored in `backend/config/squad_presets.json`:

```json
{
  "local": {
    "name": "Local Squad",
    "description": "100% offline, zero cost",
    "requirements": {
      "min_ram_gb": 16,
      "ollama_required": true
    },
    "models": {
      "flagship": "ollama-mistral-7b",
      "prose": "ollama-magnum-v4-12b",
      "coordinator": "ollama-llama-3.2"
    },
    "auto_downloads": ["ollama-magnum-v4-12b"]
  },
  "hybrid": {
    "name": "Hybrid Squad",
    "description": "Best value - cloud + local",
    "requirements": {
      "min_ram_gb": 16,
      "ollama_required": true,
      "api_keys": ["DEEPSEEK_API_KEY"]
    },
    "models": {
      "flagship": "deepseek-v3",
      "prose": "ollama-magnum-v4-12b",
      "coordinator": "ollama-mistral-7b"
    },
    "auto_downloads": ["ollama-magnum-v4-12b"]
  },
  "pro": {
    "name": "Pro Squad",
    "description": "Maximum quality",
    "requirements": {
      "api_keys": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    },
    "models": {
      "flagship": "gpt-4o",
      "prose": "claude-3-7-sonnet-20250219",
      "coordinator": "ollama-mistral-7b"
    }
  }
}
```

#### B. User Settings (Per-Project)

Stored in `project_settings.json`:

```json
{
  "active_squad": "hybrid",
  "squad_setup_complete": true,
  "foreman": {
    "architect_model": "deepseek-v3",
    "director_model": "mistral:7b",
    "coordinator_model": "mistral:7b"
  }
}
```

### 2. Backend Services

#### `SquadService.py` (New)

```python
class SquadService:
    """Manages squad presets and model selection."""

    def get_available_squads(self, hardware_info: dict) -> List[SquadPreset]:
        """Returns squads user can run based on hardware."""
        squads = load_squad_presets()
        available = []

        for squad in squads:
            if self._can_run_squad(squad, hardware_info):
                available.append(squad)

        return available

    def apply_squad(self, project_id: str, squad_name: str):
        """Sets active squad and triggers downloads if needed."""
        squad = self.get_squad_preset(squad_name)

        # Update project settings
        settings_service.set(f"active_squad", squad_name, project_id)

        # Trigger Ollama downloads if needed
        if squad.get("auto_downloads"):
            for model_id in squad["auto_downloads"]:
                ollama_service.pull_model(model_id)

        # Update Foreman configuration
        if squad_name == "hybrid" or squad_name == "pro":
            settings_service.set("foreman.architect_model", squad["models"]["flagship"], project_id)
        else:
            settings_service.set("foreman.architect_model", squad["models"]["coordinator"], project_id)

    def get_tournament_models(self, project_id: str) -> List[str]:
        """Returns models to use in tournaments based on active squad."""
        squad_name = settings_service.get("active_squad", project_id)
        squad = self.get_squad_preset(squad_name)

        return [
            squad["models"]["flagship"],
            squad["models"]["prose"]
        ]
```

#### Update: `Foreman.__init__()` (Change Default)

```python
def __init__(
    self,
    model: str = "deepseek-v3",  # Changed from mistral:7b
    ollama_url: str = "http://localhost:11434",
    # ... rest
):
    self.model = model
    # ...
```

#### Update: `SceneWriterService.generate_tournament_variants()`

```python
def generate_tournament_variants(self, project_id: str, scene_prompt: str):
    """Generate variants using squad models."""

    # Get models from active squad
    models = squad_service.get_tournament_models(project_id)

    # Generate 5 strategies × N models
    variants = []
    for model_id in models:
        for strategy in ["action", "dialogue", "logic", "atmosphere", "integration"]:
            variant = await self._generate_variant(model_id, strategy, scene_prompt)
            variants.append(variant)

    return variants
```

### 3. Frontend Components

#### `SquadBuilderWizard.svelte` (New)

```svelte
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';

  let hardwareInfo = null;
  let availableSquads = [];
  let selectedSquad = null;
  let setupInProgress = false;

  onMount(async () => {
    // Check hardware
    hardwareInfo = await apiClient.checkHardware();

    // Get available squads
    availableSquads = await apiClient.getAvailableSquads(hardwareInfo);

    // Pre-select recommended squad
    selectedSquad = availableSquads.find(s => s.recommended) || availableSquads[0];
  });

  async function selectSquad(squad) {
    setupInProgress = true;

    try {
      // Apply squad (triggers downloads if needed)
      await apiClient.applySquad(squad.name);

      // Close wizard
      dispatch('complete');
    } catch (error) {
      console.error('Squad setup failed:', error);
    } finally {
      setupInProgress = false;
    }
  }
</script>

<div class="wizard">
  <!-- Step 1: Hardware Info -->
  {#if hardwareInfo}
    <div class="hardware-check">
      <h3>System Scan</h3>
      <p>✅ {hardwareInfo.ram_gb}GB RAM detected</p>
      <p>✅ Ollama installed (v{hardwareInfo.ollama_version})</p>
    </div>
  {/if}

  <!-- Step 2: Squad Selection -->
  <div class="squad-options">
    {#each availableSquads as squad}
      <button
        class="squad-card"
        class:selected={selectedSquad === squad}
        on:click={() => selectedSquad = squad}
      >
        <h3>{squad.name}</h3>
        <p>{squad.description}</p>
        <div class="models">
          {#each Object.entries(squad.models) as [role, model]}
            <span>{role}: {model}</span>
          {/each}
        </div>
      </button>
    {/each}
  </div>

  <!-- Step 3: Confirm -->
  <button
    on:click={() => selectSquad(selectedSquad)}
    disabled={setupInProgress}
  >
    {setupInProgress ? 'Setting up...' : 'Confirm Squad'}
  </button>
</div>
```

---

## Migration Path

### For New Users
1. Install app → Story Bible creation uses DeepSeek V3 (subsidized)
2. After Story Bible → Squad Builder Wizard appears
3. Choose squad → Downloads happen automatically
4. Start writing → Tournament uses squad models

### For Existing Users
1. Next time they open the app → "New: Squad System" notification
2. Click notification → Squad Builder Wizard appears
3. System detects current configuration and suggests matching squad
4. User confirms or changes → New system active

---

## Simplified Settings UI

After squad is chosen, the Settings panel becomes much simpler:

### Settings → AI Models Tab

```
┌─────────────────────────────────────────────┐
│ Your Active Squad: Hybrid                   │
├─────────────────────────────────────────────┤
│ Logic & Strategy: DeepSeek V3               │
│ Prose & Style: Magnum v4 12B (Local)        │
│ Coordination: Mistral 7B (Local)            │
│                                             │
│ [Change Squad]                              │
│                                             │
│ Advanced Options (Collapsed by default)     │
│ ▶ Override individual task models          │
│ ▶ Add custom models to tournaments          │
└─────────────────────────────────────────────┘
```

**Key Insight:** 95% of users never need to see the "Advanced Options". They just pick a squad and go.

---

## What This Solves

### Before (Current System):
- ❌ Writers see 9+ AI models and don't know which to use
- ❌ Need to understand "task-specific model assignment"
- ❌ Configure health checks, Foreman tasks, tournament strategies separately
- ❌ Story Bible quality limited by Mistral 7B intelligence
- ❌ No guidance on Local vs Cloud tradeoffs

### After (Squad System):
- ✅ Writers pick ONE squad that makes sense for their needs
- ✅ Story Bible uses smart AI (DeepSeek V3) automatically
- ✅ Tournament automatically uses squad models
- ✅ All task assignment happens behind the scenes
- ✅ Clear Local vs Hybrid vs Pro value proposition

---

## FAQ

**Q: Can I still customize individual models?**
A: Yes! The "Advanced Options" in Settings allows you to override any model. But 95% of users won't need this.

**Q: What if I want to try a new model mid-project?**
A: Click "Change Squad" in Settings. Your Story Bible and Voice Bundle are preserved.

**Q: Can I mix squad models in tournaments?**
A: Yes, in Advanced Options you can enable "Tournament Expansion" to include models from other squads.

**Q: What happens if my API key expires?**
A: The app automatically falls back to local models and shows a notification. Your work is never blocked.

**Q: Do I need to download Ollama manually?**
A: No. The app detects if Ollama is missing and offers to install it for you.

---

## Implementation Checklist

### Phase 1: Backend Foundation
- [ ] Create `backend/config/squad_presets.json`
- [ ] Build `SquadService` class
- [ ] Add hardware detection API endpoint (`/system/hardware`)
- [ ] Update `Foreman.__init__()` to use DeepSeek V3 by default
- [ ] Update `SceneWriterService` to respect squad settings

### Phase 2: Frontend UI
- [ ] Build `SquadBuilderWizard.svelte`
- [ ] Add squad selector to Settings panel
- [ ] Update `SettingsTournament.svelte` to show active squad
- [ ] Add "Change Squad" button to Settings

### Phase 3: Onboarding Flow
- [ ] Trigger wizard after Story Bible completion
- [ ] Add "Skip for now" option (keeps using defaults)
- [ ] Build migration flow for existing users

### Phase 4: Polish
- [ ] Add download progress indicators
- [ ] Add API key validation
- [ ] Build "System Health" dashboard widget
- [ ] Add model update notifications

---

*This architecture transforms a confusing 9-model configuration maze into a simple 3-choice system while preserving power-user flexibility.*
