# Onboarding Wizard Task

> A proper first-time setup flow for new writers using Writers Factory.

## Overview

This replaces the previous Squad-first approach with a clearer, step-by-step onboarding that:
1. Sets up local AI first (always available, even offline)
2. Explains cloud models honestly (free MVP models vs paid premium)
3. Guides users to add API keys if they want premium models
4. Names their assistant
5. Gets them writing

## The 4-Step Onboarding Flow

### Step 1: Local AI Setup

**Purpose:** Ensure every user has a working local AI before anything else.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: LOCAL AI SETUP                                         │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  "Let's set up your local AI assistant first"                   │
│                                                                 │
│  Scanning your computer...                                      │
│  • RAM: 32GB ✓                                                  │
│  • GPU: Apple M2 ✓                                              │
│  • Recommended model: Llama 3.2 (3B) for speed                  │
│    or Mistral (7B) for quality                                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Ollama Status: ○ Not installed                          │   │
│  │                                                         │   │
│  │ [Install Ollama] ← Opens installer/instructions         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Once Ollama is running:                                        │
│  • Download recommended model: [Install llama3.2:3b]            │
│  • Or choose larger model: [Install mistral:7b]                 │
│                                                                 │
│  Local AI ready: ✓                         [Continue →]         │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**
- Uses existing `/system/hardware` endpoint for scanning
- Uses existing Ollama detection logic
- Continue button disabled until Ollama + model installed
- Can skip if Ollama already configured

---

### Step 2: Cloud AI Models Overview

**Purpose:** Honest explanation of which models are free (MVP subsidized) vs require user keys.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: CLOUD AI MODELS                                        │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  "For serious writing, we recommend cloud AI models"            │
│                                                                 │
│  The first 4 require your own API keys (pay-per-use, no         │
│  monthly fee - you only pay for tokens you actually use).       │
│  All other models are FREE for MVP early users.                 │
│                                                                 │
│  ─── US ───                                                     │
│  OpenAI GPT-4o       $2.50/$10 per 1M tokens    [Key required]  │
│  Anthropic Claude    $3/$15 per 1M tokens       [Key required]  │
│  xAI Grok            $2/$10 per 1M tokens       [Key required]  │
│  Google Gemini       $0.075/$0.30 per 1M tokens [Key required]  │
│                                                                 │
│  ─── China / Asia ───                                           │
│  DeepSeek V3         $0.27/$1.10 per 1M tokens  [Free for MVP]  │
│  Alibaba Qwen        $0.50/$2 per 1M tokens     [Free for MVP]  │
│  Moonshot Kimi       $0.20/$0.80 per 1M tokens  [Free for MVP]  │
│  Zhipu ChatGLM       $0.30/$1.20 per 1M tokens  [Free for MVP]  │
│  Tencent Hunyuan     Free tier available        [Free for MVP]  │
│                                                                 │
│  ─── Europe ───                                                 │
│  Mistral AI          $0.15/$0.45 per 1M tokens  [Free for MVP]  │
│                                                                 │
│  ─── Russia ───                                                 │
│  Yandex AI           Variable pricing           [Free for MVP]  │
│                                                                 │
│  ─── Local ───                                                  │
│  Ollama              Free (runs on your machine)                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ WHY GET YOUR OWN KEYS?                                  │   │
│  │                                                         │   │
│  │ • No monthly subscription - pay only for what you use   │   │
│  │ • Premium models write better prose for final drafts    │   │
│  │ • Use cheap models for brainstorming, premium for       │   │
│  │   polishing                                             │   │
│  │ • Our "tournament" feature lets you compare outputs     │   │
│  │   from multiple models to find YOUR voice               │   │
│  │                                                         │   │
│  │ Even with all 4 US keys, your monthly cost will         │   │
│  │ probably not be more than you'd pay for one chatbot     │   │
│  │ subscription.                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [← Back]                                   [Continue →]        │
│  (You can add keys later in Settings)                           │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**
- This is an INFO screen - no configuration happens here
- Lists ALL models with honest pricing
- Clearly marks "Key required" vs "Free for MVP"
- Explains the value proposition for getting premium keys
- User can continue without doing anything

---

### Step 3: Add API Keys (Optional)

**Purpose:** Let users add their own API keys for premium models.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: ADD API KEYS (Optional)                                │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  Re-uses the EXISTING SettingsAgents.svelte component           │
│  which already has the excellent format:                        │
│                                                                 │
│  API Keys & Providers                                           │
│  Configure AI provider API keys.                                │
│  Configured: 0 of 12 providers                                  │
│                                                                 │
│  DeepSeek V3                                    RECOMMENDED     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [Not set]  Best value - $0.27/$1.10 per 1M tokens       │  │
│  │ [Show] [Test] [Get key from platform.deepseek.com →]    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  OpenAI                                         KEY REQUIRED    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ [_______________]  GPT-4o - $2.50/$10 per 1M tokens     │  │
│  │ [Show] [Test] [Get key from platform.openai.com →]      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ... (same format for all 12 providers)                         │
│                                                                 │
│  [← Back]                                   [Continue →]        │
│  [Skip for now - I'll add keys later]                           │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**
- Embeds existing `SettingsAgents.svelte` component
- No new UI needed - just wrap it in wizard step
- Add "Skip for now" option
- Keys are optional at this stage

---

### Step 4: Name Your Assistant

**Purpose:** Personalization - give the assistant a name.

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: NAME YOUR ASSISTANT                                    │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  "What would you like to call your writing assistant?"          │
│                                                                 │
│  [Muse] [Scribe] [Quill] [Ghost] [Custom: ________]             │
│                                                                 │
│  Preview: "Hey Quill, help me brainstorm..."                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Your default model: DeepSeek V3                         │   │
│  │                                                         │   │
│  │ You can choose any available model at each prompt       │   │
│  │ using the dropdown in the chat input.                   │   │
│  │ (Agent selector coming soon)                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  [← Back]                               [Get Started →]         │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**
- Re-uses name selection from `SettingsAssistant.svelte`
- Shows which model is default (DeepSeek)
- Mentions agent selector dropdown (future feature)
- "Get Started" completes onboarding

---

## After Onboarding: Main App

User lands in the 3-panel layout with their assistant ready:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MAIN APP                                    │
│  ─────────────────────────────────────────────────────────────  │
│  3-panel layout: Binder | Canvas | Chat                         │
│                                                                 │
│  First message from assistant:                                  │
│  "Hi! I'm Quill. What would you like to work on today?"         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Settings (Separate from Onboarding)

For returning users who want to change things:

```
┌─────────────────────────────────────────────────────────────────┐
│  SETTINGS                                                       │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│ API Keys     │  ← First! This is what enables everything        │
│ AI Models    │  ← Select which models to use for what           │
│ Squad        │  ← Pre-configured team setups                    │
│ Assistant    │  ← Name, behavior preferences                    │
│ Voice        │  ← Writing style settings                        │
│ Advanced     │  ← Power user options                            │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

**Note:** Settings tab order should be: API Keys → AI Models → Squad → Assistant → Voice → Advanced

---

## AI Providers Reference

### US (Key Required)
| Provider | Model | Input/Output per 1M tokens | Status |
|----------|-------|---------------------------|--------|
| OpenAI | GPT-4o | $2.50 / $10 | Key required |
| Anthropic | Claude 3.5 Sonnet | $3 / $15 | Key required |
| xAI | Grok | $2 / $10 | Key required |
| Google | Gemini 1.5 Pro | $0.075 / $0.30 | Key required |

### China / Asia (Free for MVP)
| Provider | Model | Input/Output per 1M tokens | Status |
|----------|-------|---------------------------|--------|
| DeepSeek | V3 | $0.27 / $1.10 | Free for MVP |
| Alibaba | Qwen | $0.50 / $2 | Free for MVP |
| Moonshot | Kimi | $0.20 / $0.80 | Free for MVP |
| Zhipu | ChatGLM | $0.30 / $1.20 | Free for MVP |
| Tencent | Hunyuan | Free tier | Free for MVP |

### Europe (Free for MVP)
| Provider | Model | Input/Output per 1M tokens | Status |
|----------|-------|---------------------------|--------|
| Mistral | Mistral Large | $0.15 / $0.45 | Free for MVP |

### Russia (Free for MVP)
| Provider | Model | Input/Output per 1M tokens | Status |
|----------|-------|---------------------------|--------|
| Yandex | YandexGPT | Variable | Free for MVP |

### Local (Always Free)
| Provider | Model | Cost | Status |
|----------|-------|------|--------|
| Ollama | Various | Free | Runs locally |

---

## Implementation Phases

### Phase 1: Create OnboardingWizard Component
- [ ] Create `OnboardingWizard.svelte` with 4-step flow
- [ ] Step navigation (back/next/skip)
- [ ] Progress indicator
- [ ] Proper close button (X) on each step

### Phase 2: Step 1 - Local AI Setup
- [ ] Hardware scan display (re-use existing)
- [ ] Ollama status detection
- [ ] Model installation buttons
- [ ] "Continue" enabled only when ready

### Phase 3: Step 2 - Cloud Models Info
- [ ] Create model list UI grouped by region
- [ ] Show pricing and "Key required" / "Free for MVP" badges
- [ ] Info box explaining value proposition

### Phase 4: Step 3 - API Keys
- [ ] Embed existing `SettingsAgents.svelte`
- [ ] Add "Skip for now" button
- [ ] Update SettingsAgents to show all 12 providers

### Phase 5: Step 4 - Name Assistant
- [ ] Re-use name selection from `SettingsAssistant.svelte`
- [ ] Show default model info
- [ ] "Get Started" completes onboarding

### Phase 6: Settings Reorganization
- [ ] Reorder tabs: API Keys → AI Models → Squad → Assistant → Voice → Advanced
- [ ] Remove "Change Squad" button from top (make it a regular tab)
- [ ] Ensure all overlays have close (X) buttons

### Phase 7: Fix Existing Issues
- [ ] Squad wizard needs X close button
- [ ] Squad wizard needs to scroll
- [ ] Remove auto-launch of old Squad wizard on first run

---

## Files to Modify/Create

**New Files:**
- `frontend/src/lib/components/Onboarding/OnboardingWizard.svelte`
- `frontend/src/lib/components/Onboarding/Step1LocalAI.svelte`
- `frontend/src/lib/components/Onboarding/Step2CloudModels.svelte`
- `frontend/src/lib/components/Onboarding/Step3ApiKeys.svelte`
- `frontend/src/lib/components/Onboarding/Step4NameAssistant.svelte`

**Modify:**
- `frontend/src/routes/+page.svelte` - Replace old wizard with new OnboardingWizard
- `frontend/src/lib/components/SettingsPanel.svelte` - Reorder tabs, fix Squad button
- `frontend/src/lib/components/Settings/SettingsAgents.svelte` - Add all 12 providers
- `frontend/src/lib/components/Squads/SquadWizard.svelte` - Add X button, scrolling

---

## Supersedes

This task supersedes `SETTINGS_SQUAD_REDESIGN.md` which had an outdated approach focused on Squad-first onboarding with baked-in keys.

---

*Created: November 2025*
*Status: Ready for Implementation*
*Priority: High - Critical for user onboarding*
