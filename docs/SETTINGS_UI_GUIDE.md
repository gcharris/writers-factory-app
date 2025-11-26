# Settings UI Guide - Writers Factory

**Last Updated:** November 26, 2025
**Version:** Phase 3E Complete

Complete guide to the Writers Factory Settings interface. All 8 settings panels explained with screenshots, defaults, and best practices.

---

## Quick Navigation

1. [**API Keys**](#1-api-keys-p0-critical) (P0 Critical) - Configure AI providers
2. [**AI Model**](#2-ai-model-p0-critical) (P0 Critical) - Choose quality tiers
3. [**Scoring**](#3-scoring-p2) - Adjust rubric weights
4. [**Voice**](#4-voice-p2) - Voice strictness settings
5. [**Enhancement**](#5-enhancement-p2) - Enhancement thresholds
6. [**Foreman**](#6-foreman-p2) - AI behavior settings
7. [**Health**](#7-health-p2) - Graph health checks
8. [**Advanced**](#8-advanced-p3) - Expert options

---

## 1. API Keys (P0 Critical)

**Purpose:** Configure your AI provider API keys to enable cloud models.

### Recommended Provider: DeepSeek (⭐ Highlighted)

**Why DeepSeek?**
- GPT-4 level quality at 10% of the cost
- Input: $0.27/1M tokens | Output: $1.10/1M tokens
- Excellent for Story Bible, Voice Calibration, and Scene Generation
- Full Story Bible costs ~$0.01 to generate

### Supported Providers (7 Total)

#### Tier 1: RECOMMENDED
- **DeepSeek V3** (⭐ Default)
  - Best value-to-quality ratio
  - API Key: Get at https://platform.deepseek.com
  - Use for: Story Bible, Scene Logic, Strategic Planning

#### Tier 2: PREMIUM
- **OpenAI (GPT-4o)**
  - Excellent thematic analysis
  - Input: $2.50/1M | Output: $10.00/1M
  - Use for: Complex reasoning, creative tasks

- **Anthropic (Claude 3.7 Sonnet)**
  - Best prose quality
  - Input: $3.00/1M | Output: $15.00/1M
  - Use for: Voice matching, character nuance

#### Tier 3: BALANCED
- **Google Gemini 2.0 Flash**
  - 1M token context window
  - Free during experimental period
  - Use for: Long-context analysis, multimodal

- **xAI (Grok 2)**
  - Unconventional thinking
  - Use for: Brainstorming, humor

#### Tier 4: BUDGET
- **Qwen Plus** (Alibaba)
  - Input: $0.40/1M | Output: $1.20/1M
  - Use for: Supporting character tracking

- **Mistral Large**
  - Excellent prose polish
  - Use for: Final enhancement passes

### Local Models (Zero Cost)

**Ollama Required:** Download at https://ollama.com

**Mistral 7B** (Default for Foreman)
- Size: 4.4 GB
- Quality: ⭐⭐⭐⭐☆
- Use for: Story Bible coordination, quick drafts

**Llama 3.2 3B**
- Size: 2.0 GB
- Quality: ⭐⭐⭐☆☆
- Use for: Ultra-fast brainstorming

### Setup Instructions

1. **Get API Key** from provider website
2. **Paste into field** (masked with •••)
3. **Click "Test Key"** to validate
4. **Save** when green checkmark appears

**Status Indicators:**
- ✅ Green: Key validated, ready to use
- ❌ Red: Invalid key or connection error
- ⚠️ Yellow: Key works but rate-limited

### Cost Tracking

The UI shows estimated monthly cost based on:
- Average novel: 100K words = ~150K tokens
- Story Bible: 50K tokens
- Voice Calibration: 20K tokens
- 50 scene generations: 500K tokens

**Example Budget (Hybrid Approach):**
- DeepSeek (Story Bible + Logic): $0.30/month
- Mistral 7B Local (Coordination): $0.00
- Total: **$0.30/month** for full novel

---

## 2. AI Model (P0 Critical)

**Purpose:** Choose quality tiers for different tasks.

### Orchestrator Presets

The app offers 4 preset configurations optimized for different workflows:

#### Preset 1: Flagship (Best Quality)
```
Story Bible: DeepSeek V3
Scene Logic: Claude 3.7 Sonnet
Prose: Claude 3.7 Sonnet
Cost: ~$3-5/month
```
**Best For:** Professional writers, publishers, final drafts

#### Preset 2: Balanced (Recommended ⭐)
```
Story Bible: DeepSeek V3
Scene Logic: DeepSeek V3
Prose: GPT-4o
Cost: ~$1-2/month
```
**Best For:** Most writers, excellent quality at reasonable cost

#### Preset 3: Economy
```
Story Bible: Mistral 7B (Local)
Scene Logic: DeepSeek V3
Prose: Qwen Plus
Cost: ~$0.30/month
```
**Best For:** Budget-conscious writers, frequent iteration

#### Preset 4: Local Only
```
Story Bible: Mistral 7B (Local)
Scene Logic: Mistral 7B (Local)
Prose: Mistral 7B (Local)
Cost: $0/month
```
**Best For:** Privacy, offline work, zero cost

### Task-Specific Assignments

**Expert Mode:** Click "Advanced Options" to override individual tasks:

**Story Bible Tasks:**
- World Building
- Character Profiles
- Theme Analysis
- 15-Beat Structure

**Scene Tasks:**
- Logic & Reasoning
- Prose & Style
- Dialogue
- Action Sequences

**Health Checks:**
- Timeline Consistency
- Theme Resonance
- Character Arcs

### Model Capabilities Reference

| Model | Reasoning | Prose | Speed | Cost/1M | Context |
|-------|-----------|-------|-------|---------|---------|
| Claude 3.7 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 1.8s | $3.00 | 200K |
| GPT-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | 1.2s | $2.50 | 128K |
| DeepSeek V3 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐☆ | 1.5s | $0.27 | 64K |
| Mistral 7B | ⭐⭐⭐☆☆ | ⭐⭐⭐☆☆ | 0.3s | $0.00 | 33K |
| Gemini 2.0 | ⭐⭐⭐⭐☆ | ⭐⭐⭐⭐☆ | 0.9s | $0.08 | 1M |

---

## 3. Scoring (P2)

**Purpose:** Adjust how scenes are scored by the Scene Analyzer.

### The Five Rubric Categories

Scores must sum to **100 points total**.

1. **Voice Authenticity** (Default: 30)
   - Does the prose match the target voice bundle?
   - Checks diction, rhythm, sentence structure
   - High = strict voice matching

2. **Character Consistency** (Default: 20)
   - Are characters acting true to their profiles?
   - Checks Fatal Flaw manifestation, dialogue patterns
   - High = character-driven stories

3. **Metaphor Discipline** (Default: 20)
   - Are extended metaphors maintained?
   - Checks for metaphor breaks, mixed imagery
   - High = literary fiction, symbolism-heavy

4. **Anti-Pattern Compliance** (Default: 15)
   - Are prose anti-patterns avoided?
   - Checks for purple prose, filter words, telling vs showing
   - High = clean, tight prose

5. **Phase Beat Appropriateness** (Default: 15)
   - Does scene hit the right 15-beat phase?
   - Checks for premature reveals, pacing issues
   - High = structure-conscious writing

### Genre Presets

Click a preset button to auto-configure weights:

#### Literary Fiction
```
Voice: 40 | Character: 25 | Metaphor: 15 | Anti-Pattern: 10 | Phase: 10
```
**Focus:** Voice and character depth over structure

#### Thriller
```
Voice: 20 | Character: 25 | Metaphor: 10 | Anti-Pattern: 20 | Phase: 25
```
**Focus:** Pacing and structure, clean prose

#### Romance
```
Voice: 25 | Character: 35 | Metaphor: 15 | Anti-Pattern: 15 | Phase: 10
```
**Focus:** Character relationships and emotional depth

#### Balanced (Default)
```
Voice: 30 | Character: 20 | Metaphor: 20 | Anti-Pattern: 15 | Phase: 15
```
**Focus:** Balanced across all categories

### Custom Weights

**Sliders:** Drag to adjust (step: 5 points)
**Input:** Type exact value
**Visual Bar:** See weight distribution at a glance

**Tips:**
- Total must equal 100 (enforced)
- Minimum per category: 5
- Changes apply to next scene generation
- Save presets for different projects

---

## 4. Voice (P2)

**Purpose:** Control how strictly the app enforces your target voice.

### Voice Strictness Levels

#### Authenticity (Default: Medium)

**What it controls:** How closely scenes must match your voice bundle

- **Relaxed (30):** Allow creative variation, looser interpretation
- **Medium (50):** ⭐ Balanced - match tone but allow flexibility
- **Strict (70):** Tight adherence, minimal deviation
- **Exact (90):** Near-perfect match, very rigid

**Use Relaxed When:**
- Experimenting with new styles
- Generating multiple voice variants
- Brainstorming phase

**Use Strict When:**
- Final draft polish
- Matching established series voice
- Professional consistency required

#### Purpose (Default: Medium)

**What it controls:** How much "artistic license" vs "functional prose"

- **Functional (30):** Clear, direct, story-first
- **Medium (50):** ⭐ Balance clarity and style
- **Stylistic (70):** Prose as art, more flourishes
- **Experimental (90):** Push voice boundaries

#### Fusion (Default: Medium)

**What it controls:** How much voice blending occurs in tournaments

- **Pure (30):** Each model stays in its own style
- **Medium (50):** ⭐ Subtle cross-model influence
- **Blended (70):** Active style mixing
- **Hybrid (90):** Create entirely new voice

### Extended Metaphor Discipline

**What it does:** Enforces consistency in extended metaphors across a scene.

**Example:**
```
Opening: "The city was a hungry beast, its neon teeth..."
Later: "...steel claws raked the night sky"  ← Consistent
Bad: "...the tranquil gardens offered peace" ← Breaks metaphor
```

**Settings:**

- **Off:** No metaphor tracking
- **Warn:** Flag breaks but allow them
- **Enforce:** ⭐ Reject scenes with broken metaphors
- **Strict:** Require metaphor evolution, not just consistency

**Metaphor Categories:**

Toggle which types to track:
- ☑️ Visual (colors, shapes, light/dark)
- ☑️ Natural (weather, seasons, animals)
- ☑️ Mechanical (machines, industry)
- ☑️ Abstract (time, space, concepts)

---

## 5. Enhancement (P2)

**Purpose:** Set thresholds for the enhancement pipeline.

### The Enhancement Pipeline

Scenes flow through enhancement based on their initial score:

```
Score 85+ → Action Prompt Polish → Done
Score 70-84 → Six-Pass Enhancement → Done
Score < 70 → Reject / Regenerate
```

### Threshold Settings

#### Action Prompt Threshold (Default: 85)

**What it means:** Scenes scoring 85+ get light polish

**Action Prompt Enhancement:**
- Single-pass targeted fixes
- Preserves voice and structure
- Takes ~10 seconds
- Cost: ~$0.01 per scene

**When to raise (90+):**
- You want tighter quality gate
- Only best variants get through
- More regenerations, higher standards

**When to lower (80):**
- Accept "good enough" faster
- Reduce API costs
- High iteration speed

#### Six-Pass Threshold (Default: 70)

**What it means:** Scenes scoring 70-84 get deep enhancement

**Six-Pass Enhancement:**
1. **Voice Calibration:** Match target voice
2. **Character Consistency:** Align with profiles
3. **Metaphor Discipline:** Strengthen imagery
4. **Anti-Pattern Removal:** Clean prose issues
5. **Pacing Adjustment:** Fix rhythm problems
6. **Final Polish:** Overall quality pass

**Cost:** ~$0.05 per scene (6x single pass)
**Time:** ~60 seconds

**When to raise (75):**
- Reserve deep work for edge cases
- Reduce enhancement costs
- Trust initial generation more

**When to lower (65):**
- More aggressive improvement
- Accept lower-scoring variants
- Fine-tune everything

#### Reject Threshold (Default: 60)

**What it means:** Scenes below this are rejected outright

**Options:**
- **Regenerate:** Request new variant from same model
- **Try Different Model:** Switch to another agent
- **Manual Edit:** Accept and edit yourself

**When to raise (65-70):**
- Strict quality standards
- Willing to regenerate often
- API costs not a concern

**When to lower (50-55):**
- Willing to heavily edit
- Exploration/brainstorming mode
- Limited API budget

### Visual Threshold Bar

The UI shows a color-coded bar:

```
[   Reject   |   Six-Pass   |   Action   |   Perfect   ]
0           60            70          85             100
```

**Live Preview:** As you drag sliders, see which zone example scores fall into.

---

## 6. Foreman (P2)

**Purpose:** Control The Foreman's personality and behavior.

### The Foreman's Role

The Foreman guides you through:
- Story Bible creation (ARCHITECT mode)
- Voice calibration (VOICE_CALIBRATION mode)
- Scene generation (DIRECTOR mode)
- Revision (EDITOR mode)

### Behavior Settings

#### Proactiveness (Default: Medium)

**What it controls:** How much the Foreman suggests vs waits for requests

- **Passive (Low):** Only responds when asked, minimal suggestions
- **Medium:** ⭐ Offers ideas when relevant, respects silence
- **Active (High):** Regularly suggests next steps, anticipates needs
- **Aggressive:** Constantly pushing forward, assumes goals

**Use Passive When:**
- You have a clear vision
- Exploring at your own pace
- Don't want interruptions

**Use Active When:**
- Need structure and guidance
- First-time novel writing
- Want accountability

#### Challenge Intensity (Default: Questioning)

**What it controls:** How much the Foreman pushes back on ideas

- **Supportive:** Accepts all ideas, cheerleader mode
- **Questioning:** ⭐ Asks "why" and suggests alternatives
- **Critical:** Points out flaws, demands justification
- **Adversarial:** Devil's advocate, stress-tests everything

**Use Supportive When:**
- Brainstorming freely
- Building confidence
- Overcoming writer's block

**Use Critical When:**
- Finalizing Story Bible
- Checking narrative logic
- Professional quality standards

#### Verbosity (Default: Balanced)

**What it controls:** Length and detail of Foreman responses

- **Terse:** Short answers, bullet points, minimal explanation
- **Balanced:** ⭐ Concise but complete, examples when needed
- **Detailed:** Thorough explanations, multiple examples
- **Comprehensive:** Essay-length responses, deep dives

**Affects:**
- Token usage (higher verbosity = higher cost)
- Reading time
- Level of hand-holding

#### Auto-Knowledge Base Writes (Default: On)

**What it does:** Automatically save important decisions to Knowledge Base

**When ON (Recommended):**
- Foreman writes KB entries after key decisions
- Example: "Character: Alice's Fatal Flaw is pride"
- No manual tracking needed

**When OFF:**
- You manually review before KB writes
- More control, less automation
- Useful for experimental Story Bibles

**KB Entry Types:**
- Character traits
- World building rules
- Theme decisions
- Plot constraints
- Voice guidelines

---

## 7. Health (P2)

**Purpose:** Configure graph health check validations.

### The 7 Health Check Categories

Each checks a different aspect of narrative consistency:

#### 1. Timeline Consistency

**What it checks:** No contradictions in time/sequence

**Examples Caught:**
- "She was 12 in Chapter 1, but 15 in Chapter 3 (only 1 week later)"
- "The necklace was destroyed in Chapter 5 but worn in Chapter 8"

**Settings:**
- Enable/Disable toggle
- Threshold: How strict (0-100)
- Default: 70 (catches major issues)

**Recommended Model:** Claude 3.7 Sonnet (best at narrative reasoning)

#### 2. Theme Resonance

**What it checks:** Themes appear at correct 15-beat phases

**Examples Caught:**
- "Redemption theme should peak at Climax (Beat 13), currently absent"
- "Fatal Flaw not challenged in Dark Night (Beat 9)"

**Settings:**
- Per-theme toggles
- Required vs Optional themes
- Default: 60 (flexible interpretation)

**Recommended Model:** GPT-4o (excellent thematic analysis)

#### 3. Fatal Flaw Challenges

**What it checks:** Protagonist's Fatal Flaw is tested appropriately

**Examples Caught:**
- "Alice's pride not challenged since Inciting Incident (Beat 3)"
- "Flaw challenge missing in Midpoint False Victory (Beat 8)"

**Settings:**
- Minimum challenges per act
- Escalation required (Yes/No)
- Default: 65 (moderate enforcement)

**Recommended Model:** DeepSeek V3 (deep character psychology)

#### 4. Supporting Cast Function

**What it checks:** Supporting characters serve clear narrative purpose

**Examples Caught:**
- "Bob appears in 3 scenes but has no arc or function"
- "Mentor character absent during Key Moment (Beat 5)"

**Settings:**
- Minimum appearances per character
- Require functional tags (Mentor, Antagonist, etc.)
- Default: 50 (lenient)

**Recommended Model:** Qwen Plus (fast, good enough, cheap)

#### 5. Pacing Analysis

**What it checks:** Scene density matches genre expectations

**Examples Caught:**
- "Act 2 has 15 scenes, Act 1 has 3 (imbalanced)"
- "7 dialogue scenes in a row (pacing plateau)"

**Settings:**
- Scenes per beat target (Flexible, Moderate, Strict)
- Allow pacing violations (Yes/No)
- Default: Medium (warns but allows)

**Recommended Model:** Mistral 7B (local, fast, structural)

#### 6. Beat Progress Validation

**What it checks:** 15-beat structure is followed correctly

**Examples Caught:**
- "Midpoint (Beat 8) occurs at 30% instead of 50%"
- "No Inciting Incident detected (Beat 3 missing)"

**Settings:**
- Strict percentage windows (Yes/No)
- Allow beat skipping (Never, Rarely, Sometimes)
- Default: 70 (enforces structure)

**Recommended Model:** Mistral 7B (structural validation, local)

#### 7. Symbolic Layering

**What it checks:** Symbols evolve consistently across story

**Examples Caught:**
- "The red scarf symbolizes oppression in Act 1, freedom in Act 3 (unexplained shift)"
- "Symbol introduced but never paid off"

**Settings:**
- Track symbols (On/Off)
- Require resolution (Yes/No)
- Default: 55 (flexible)

**Recommended Model:** GPT-4o (pattern recognition)

### Health Check Frequency

**When are checks run?**
- After each scene is written
- On-demand via "Run Health Check" button
- Automatically before major milestones (Midpoint, Climax)

**Performance:**
- Each check: ~5 seconds
- Full suite (all 7): ~35 seconds
- Cost: ~$0.02 total (with DeepSeek)

### Health Score Interpretation

```
90-100: Excellent - No issues detected
75-89:  Good - Minor issues, easily fixed
60-74:  Fair - Notable problems, revision recommended
< 60:   Poor - Significant structural issues
```

**UI Indicators:**
- ✅ Green: Passed
- ⚠️ Yellow: Warning (non-critical)
- ❌ Red: Failed (critical issue)

---

## 8. Advanced (P3)

**Purpose:** Expert settings for power users.

### Expert Mode Toggle

**When OFF (Default):**
- Simple interface
- Preset configurations
- Beginner-friendly

**When ON:**
- Per-task model assignment
- Advanced tournament controls
- Context window tuning
- Token budget management

**Warning:** Expert mode can break presets. Only enable if you understand model capabilities and task routing.

### Default Model Selection

**Override the system default for all tasks.**

**System Defaults (as of Phase 3E):**
- Story Bible: Mistral 7B (local)
- Scene Logic: DeepSeek V3 (cloud)
- Enhancement: Claude 3.7 Sonnet (cloud)

**DeepSeek Recommended:** ⭐
- Best value-to-quality ratio
- Use for Story Bible, Logic, Strategy tasks
- Fall back to Mistral 7B if offline

**When to Change:**
- You have unlimited API budget → Use GPT-4o or Claude everywhere
- You want 100% local → Use Mistral 7B everywhere
- You're optimizing for speed → Use Gemini 2.0 Flash

### Context Window Settings

**Max Conversation Messages (Default: 20)**

How many messages The Foreman remembers in chat history.

- **Low (10):** Fast, cheap, may forget context
- **Medium (20):** ⭐ Balanced for most workflows
- **High (50):** Long conversations, higher token cost
- **Unlimited:** Full history (expensive!)

**Max Knowledge Base Size (Default: 1000 KB)**

How much Story Bible data to inject into prompts.

- **Small (500 KB):** ~10 characters, basic world
- **Medium (1000 KB):** ⭐ ~25 characters, full world
- **Large (2000 KB):** Complex worlds, many characters
- **Unlimited:** Everything (may hit model limits)

**Context Trimming Strategy:**

When context exceeds limits:
- **Oldest First:** Drop earliest messages
- **Least Relevant:** ⭐ Drop by semantic similarity
- **Summarize:** Compress old messages into summary
- **None:** Fail with error (forces manual cleanup)

### Tournament Controls (Expert Mode Only)

**Variant Count (Default: 5 per model)**

How many variants each model generates.

- **3:** Fast, less choice
- **5:** ⭐ Good variety
- **7:** More options, slower
- **10:** Excessive (diminishing returns)

**Strategy Selection:**

Which strategies to include:
- ☑️ Action (visceral, immediate)
- ☑️ Dialogue (character-driven)
- ☑️ Logic (plot-focused)
- ☑️ Brainstorming (experimental)
- ☑️ Integration (balanced)

**Hybrid Generation (On/Off):**

Allow creating hybrids from top variants.

**Cost:** 2x token usage (re-generation of combined variant)

### Fallback Model Configuration

**What it does:** If primary model fails, use backup

**Example:**
```
Primary: Claude 3.7 Sonnet
Fallback: DeepSeek V3
Local Fallback: Mistral 7B
```

**Fallback Triggers:**
- API rate limit hit
- Network error
- Model unavailable (maintenance)

**Behavior:**
- Automatic retry with fallback
- Notification shown to user
- Logged for debugging

---

## Common Workflows

### Workflow 1: First Novel (Local-First)

**Goal:** Write your first novel with zero cost.

1. **API Keys:** Skip all cloud providers
2. **AI Model:** Select "Local Only" preset
3. **Scoring:** Use "Balanced" preset
4. **Voice:** Medium strictness across the board
5. **Enhancement:** Lower thresholds (60/65) to accept more variants
6. **Foreman:** Active proactiveness, Questioning challenge
7. **Health:** Enable Beat Progress and Pacing only (fast checks)
8. **Advanced:** Keep Expert Mode OFF

**Expected Cost:** $0/month
**Quality:** ⭐⭐⭐☆☆ (Good for first draft)

---

### Workflow 2: Professional Author (Quality-First)

**Goal:** Best possible quality, cost is secondary.

1. **API Keys:** Add Claude, GPT-4o, DeepSeek
2. **AI Model:** "Flagship" preset
3. **Scoring:** Genre-specific preset (Literary, Thriller, etc.)
4. **Voice:** Strict authenticity, Stylistic purpose
5. **Enhancement:** High thresholds (90/75), only accept excellence
6. **Foreman:** Passive proactiveness, Critical challenge
7. **Health:** Enable all 7 checks, strict thresholds (80+)
8. **Advanced:** Expert Mode ON, fine-tune per task

**Expected Cost:** $3-5/month
**Quality:** ⭐⭐⭐⭐⭐ (Professional grade)

---

### Workflow 3: Budget-Conscious Writer (Best Value)

**Goal:** High quality at minimal cost.

1. **API Keys:** DeepSeek only
2. **AI Model:** "Balanced" preset (DeepSeek + local)
3. **Scoring:** "Balanced" preset
4. **Voice:** Medium everything
5. **Enhancement:** Medium thresholds (85/70/60)
6. **Foreman:** Medium proactiveness, Questioning
7. **Health:** Enable 4 most important checks (Timeline, Theme, Flaw, Beat)
8. **Advanced:** Keep OFF

**Expected Cost:** $0.30-0.50/month
**Quality:** ⭐⭐⭐⭐☆ (Excellent value)

---

## Troubleshooting

### "Settings Not Saving"

**Cause:** Backend API not responding
**Fix:**
1. Check backend is running (`http://localhost:8000/health`)
2. Clear browser cache
3. Check browser console for errors

### "API Key Invalid"

**Cause:** Wrong key format or expired key
**Fix:**
1. Regenerate key at provider website
2. Check for extra spaces when pasting
3. Test key with provider's official tools first

### "Scores Don't Add to 100"

**Cause:** Rubric weights misconfigured
**Fix:**
1. Use a preset button to reset
2. The UI enforces sum=100 automatically
3. If stuck, reload page

### "Foreman Too Chatty / Too Quiet"

**Cause:** Verbosity setting mismatch
**Fix:**
1. Adjust Verbosity slider in Foreman settings
2. Lower = shorter responses
3. Or modify system prompt in Advanced (experts only)

### "Health Checks Take Forever"

**Cause:** Too many checks enabled with slow models
**Fix:**
1. Disable less critical checks (Symbolic Layering, Cast Function)
2. Use faster models (Mistral 7B local for structural checks)
3. Run checks manually instead of auto

---

## Keyboard Shortcuts

**Settings Panel:**
- `Cmd/Ctrl + ,` - Open Settings
- `Esc` - Close Settings
- `Tab` - Navigate tabs
- `Enter` - Save changes

**Within Tabs:**
- `↑↓` - Adjust slider values
- `Space` - Toggle checkboxes
- `Cmd/Ctrl + R` - Reset to defaults

---

## API Reference

For programmatic access to settings, see:
- [SETTINGS_SYSTEM.md](./SETTINGS_SYSTEM.md) - Backend architecture
- [SETTINGS_QUICK_START.md](./SETTINGS_QUICK_START.md) - API examples
- [API_REFERENCE.md](./API_REFERENCE.md) - Full endpoint documentation

---

*Last Updated: November 26, 2025 - Phase 3E Complete*
