# Task Spec: Director Mode UI Master Component

> **Priority**: High
> **Effort**: Large (2-3 days)
> **Dependencies**: Voice Calibration (Phase 2B), Story Bible completion
> **Branch**: TBD

---

## Overview

Create `DirectorMode.svelte` - a master orchestrator component that guides writers through scene-by-scene drafting with voice consistency and narrative coherence.

**The Pattern**: Like `VoiceCalibration.svelte`, this component ties together existing building blocks (SceneVariantGrid, SceneScoreBreakdown, SceneComparison) into a cohesive, stateful workflow.

---

## Current State

### ✅ Backend - Complete (16 endpoints)

All Director Mode services are implemented in `backend/services/`:

| Service | File | Endpoints |
|---------|------|-----------|
| Scaffold Generator | `scaffold_generator_service.py` | 3 (`draft-summary`, `enrich`, `generate`) |
| Scene Writer | `scene_writer_service.py` | 4 (`structure-variants`, `generate-variants`, `create-hybrid`, `quick-generate`) |
| Scene Analyzer | `scene_analyzer_service.py` | 4 (`analyze`, `compare`, `detect-patterns`, `analyze-metaphors`) |
| Scene Enhancement | `scene_enhancement_service.py` | 4 (`enhance`, `action-prompt`, `apply-fixes`, `six-pass`) |

### ✅ API Client - Complete

All methods implemented in `frontend/src/lib/api_client.ts`:
- `generateDraftSummary()` - Stage 1 scaffold
- `enrichScaffold()` - NotebookLM queries
- `generateScaffold()` - Full scaffold generation
- `generateStructureVariants()` - 5 layout options
- `generateSceneVariants()` - Multi-model tournament
- `createSceneHybrid()` - Combine best parts
- `quickGenerateScene()` - Fast single-model
- `analyzeScene()` - Full 100-point scoring
- `compareSceneVariants()` - Side-by-side comparison
- `detectPatterns()` - Real-time anti-pattern check
- `analyzeMetaphors()` - Domain usage analysis
- `enhanceScene()` - Auto-select enhancement
- `generateActionPrompt()` - Surgical fixes
- `applyFixes()` - Apply action prompt
- `runSixPass()` - Full 6-pass polish

### ✅ Stores - Complete

In `frontend/src/lib/stores.js`:
```javascript
// Scaffold state
export const currentScaffold = writable(null);
export const scaffoldLoading = writable(false);
export const scaffoldStep = writable(0);

// Structure variants
export const structureVariants = writable([]);
export const selectedStructure = writable(null);

// Scene variants
export const sceneVariants = writable([]);
export const sceneVariantsLoading = writable(false);
export const selectedSceneVariants = writable([]);

// Analysis
export const currentSceneAnalysis = writable(null);

// Director workflow step
export const directorStep = writable(0);
```

### ✅ Child Components - Complete

| Component | Purpose | Status |
|-----------|---------|--------|
| `SceneVariantGrid.svelte` | Model × Strategy matrix, score tiers | ✅ 733 lines |
| `SceneScoreBreakdown.svelte` | 5-category scoring display | ✅ 765 lines |
| `SceneComparison.svelte` | Side-by-side variant comparison | ✅ 552 lines |

### ❌ Missing: Master Orchestrator

No `DirectorMode.svelte` exists to:
1. Guide users through the 6-step workflow
2. Manage state transitions
3. Coordinate between child components
4. Provide navigation and progress indication

---

## Director Mode Workflow (6 Steps)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DIRECTOR MODE WORKFLOW                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌────────┐   ┌──────────┐  │
│  │  STEP 1 │   │  STEP 2 │   │  STEP 3  │   │ STEP 4 │   │  STEP 5  │  │
│  │SCAFFOLD │──▶│STRUCTURE│──▶│ GENERATE │──▶│COMPARE │──▶│ ENHANCE  │  │
│  │         │   │         │   │          │   │        │   │          │  │
│  │ Input   │   │ Choose  │   │ Run      │   │ Select │   │ Polish   │  │
│  │ scene   │   │ layout  │   │ tourney  │   │ winner │   │ based on │  │
│  │ details │   │ variant │   │ 3×5=15   │   │ or     │   │ score    │  │
│  └─────────┘   └─────────┘   └──────────┘   │ hybrid │   └──────────┘  │
│       │                                     └────────┘        │        │
│       │                                                       │        │
│       └───────────────────────────────────────────────────────┘        │
│                                  │                                      │
│                                  ▼                                      │
│                           ┌──────────┐                                  │
│                           │  STEP 6  │                                  │
│                           │ COMPLETE │                                  │
│                           │          │                                  │
│                           │ Save &   │                                  │
│                           │ continue │                                  │
│                           └──────────┘                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## UI/UX Design

### Step 1: Scaffold Input

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 1/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Scene Setup ──────────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Chapter: [  3 ▼]    Scene: [  1 ▼]                                │ │
│  │                                                                     │ │
│  │  Scene Title: [The Casino Floor                              ]     │ │
│  │                                                                     │ │
│  │  Beat: [Catalyst - Beat 4: Something happens that...]            │ │
│  │                                                                     │ │
│  │  Characters in Scene:                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │ ☑ Mickey (protagonist)                                       │  │ │
│  │  │ ☐ Sarah                                                      │  │ │
│  │  │ ☑ The Woman                                                  │  │ │
│  │  │ ☐ Tony                                                       │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  │                                                                     │ │
│  │  Scene Description:                                                │ │
│  │  ┌─────────────────────────────────────────────────────────────┐  │ │
│  │  │ Mickey enters the casino for the first time since the       │  │ │
│  │  │ incident. The Woman is watching from the shadows. He needs  │  │ │
│  │  │ to find the mark without being recognized...                │  │ │
│  │  └─────────────────────────────────────────────────────────────┘  │ │
│  │                                                                     │ │
│  │  Target Word Count: [1500] words                                   │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌─ NotebookLM Enrichment (Optional) ─────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Suggested queries from draft summary:                             │ │
│  │  ☐ "What are the casino's security measures?" (World Notebook)     │ │
│  │  ☐ "How does The Woman typically approach targets?" (Character)    │ │
│  │                                                                     │ │
│  │  [ Query NotebookLM ]                                              │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│                                           [ Skip to Generation ] [ Next ]│
└──────────────────────────────────────────────────────────────────────────┘
```

### Step 2: Structure Variants

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 2/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Choose how you want to structure this scene:                           │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │ ○ A: Action-Forward                                                 ││
│  │   └─ 4 beats, fast pacing                                           ││
│  │   └─ Entry → Recognition → Pursuit → Escape                         ││
│  │   └─ ~1500 words                                                    ││
│  │                                                                      ││
│  │ ● B: Character-Driven (RECOMMENDED)                                 ││
│  │   └─ 3 beats, medium pacing                                         ││
│  │   └─ Internal Conflict → External Trigger → Decision                ││
│  │   └─ ~1400 words                                                    ││
│  │                                                                      ││
│  │ ○ C: Dialogue-Heavy                                                 ││
│  │   └─ 5 beats, slow pacing                                           ││
│  │   └─ Multiple conversations build tension                           ││
│  │   └─ ~1600 words                                                    ││
│  │                                                                      ││
│  │ ○ D: Atmospheric                                                    ││
│  │   └─ 2 beats, slow build                                            ││
│  │   └─ Setting description → Single dramatic moment                   ││
│  │   └─ ~1200 words                                                    ││
│  │                                                                      ││
│  │ ○ E: Balanced Mix                                                   ││
│  │   └─ 3 beats, varied pacing                                         ││
│  │   └─ Action + Character + Dialogue balanced                         ││
│  │   └─ ~1500 words                                                    ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                         [ Back ] [ Next ]│
└──────────────────────────────────────────────────────────────────────────┘
```

### Step 3: Scene Generation (Tournament)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 3/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Running Tournament...                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Models: Claude Sonnet • GPT-4o • DeepSeek                          ││
│  │ Strategies: Action • Character • Dialogue • Brainstorm • Balanced  ││
│  │ Total variants: 15                                                  ││
│  │                                                                      ││
│  │ Progress: ████████████░░░░░░░░ 12/15                               ││
│  │                                                                      ││
│  │ Claude Sonnet - Action    ✓  Score: 87                             ││
│  │ Claude Sonnet - Character ✓  Score: 91                             ││
│  │ Claude Sonnet - Dialogue  ✓  Score: 84                             ││
│  │ Claude Sonnet - Brainstorm ✓ Score: 79                             ││
│  │ Claude Sonnet - Balanced  ✓  Score: 88                             ││
│  │ GPT-4o - Action           ✓  Score: 85                             ││
│  │ GPT-4o - Character        ✓  Score: 89                             ││
│  │ GPT-4o - Dialogue         ✓  Score: 86                             ││
│  │ GPT-4o - Brainstorm       ✓  Score: 81                             ││
│  │ GPT-4o - Balanced         ✓  Score: 87                             ││
│  │ DeepSeek - Action         ✓  Score: 83                             ││
│  │ DeepSeek - Character      ⌛ Generating...                         ││
│  │ DeepSeek - Dialogue       ○                                        ││
│  │ DeepSeek - Brainstorm     ○                                        ││
│  │ DeepSeek - Balanced       ○                                        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  Tournament will complete in ~30 seconds                                │
│                                                                          │
│                                                                [ Cancel ]│
└──────────────────────────────────────────────────────────────────────────┘
```

### Step 4: Compare & Select (uses SceneVariantGrid)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 4/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Tournament Complete! 15 variants scored.                               │
│                                                                          │
│  ┌─ SceneVariantGrid ─────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │        │ Action   │ Character │ Dialogue │ Brainstorm │ Balanced  │ │
│  │ ───────┼──────────┼───────────┼──────────┼────────────┼────────── │ │
│  │ Claude │ 87       │ ★ 91     │ 84       │ 79         │ 88        │ │
│  │ GPT-4o │ 85       │ 89       │ 86       │ 81         │ 87        │ │
│  │ Deep   │ 83       │ 86       │ 82       │ 78         │ 84        │ │
│  │                                                                     │ │
│  │ ★ = Best variant (Claude Sonnet - Character: 91/100)               │ │
│  │                                                                     │ │
│  │ [ 2 selected ]  [ Compare ]  [ Create Hybrid ]  [ Use Best (91) ] │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  [ View Score Breakdown ]                          [ Back ] [ Continue ] │
└──────────────────────────────────────────────────────────────────────────┘
```

### Step 5: Enhancement

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 5/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Selected: Claude Sonnet - Character (Score: 91/100)                    │
│                                                                          │
│  ┌─ Enhancement Recommendation ───────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  Score: 91/100 - "Strong"                                          │ │
│  │                                                                     │ │
│  │  ✓ Above 85 threshold → Action Prompt (surgical fixes)             │ │
│  │                                                                     │ │
│  │  3 issues found:                                                   │ │
│  │  • Line 42: "with practiced precision" → Zero-tolerance violation  │ │
│  │  • Line 78: Gambling metaphors at 38% → Approaching saturation     │ │
│  │  • Line 156: Character trusted without reading angles → Flaw miss  │ │
│  │                                                                     │ │
│  │  [ Preview Fixes ]                                                 │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  Enhancement Options:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ ● Apply Action Prompt (recommended for 85+ scores)                 ││
│  │   └─ Quick surgical fixes, preserves 95% of content                ││
│  │                                                                      ││
│  │ ○ Run 6-Pass Enhancement (for 70-84 scores)                        ││
│  │   └─ Full polish pipeline, may significantly alter prose           ││
│  │                                                                      ││
│  │ ○ Skip Enhancement                                                 ││
│  │   └─ Keep current draft as-is                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                 [ Back ] [ Run & Continue ]│
└──────────────────────────────────────────────────────────────────────────┘
```

### Step 6: Complete

```
┌──────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR MODE                                                    Step 6/6│
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─ Scene Complete! ──────────────────────────────────────────────────┐ │
│  │                                                                     │ │
│  │  ✓ Chapter 3, Scene 1: "The Casino Floor"                         │ │
│  │                                                                     │ │
│  │  Final Score: 94/100 (Gold Standard)                               │ │
│  │  Word Count: 1,487                                                 │ │
│  │  Model: Claude Sonnet (Character strategy)                         │ │
│  │  Enhancement: Action Prompt applied (+3 points)                    │ │
│  │                                                                     │ │
│  │  ┌─ Score Breakdown ──────────────────────────────────────────┐   │ │
│  │  │ Voice Authenticity:      28/30 ████████████████████░░      │   │ │
│  │  │ Character Consistency:   19/20 ████████████████████████░   │   │ │
│  │  │ Metaphor Discipline:     18/20 ██████████████████████░░░   │   │ │
│  │  │ Anti-Pattern Compliance: 15/15 ██████████████████████████  │   │ │
│  │  │ Phase Appropriateness:   14/15 ████████████████████████░░  │   │ │
│  │  └────────────────────────────────────────────────────────────┘   │ │
│  │                                                                     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  What's next?                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ ● Save and start next scene (Chapter 3, Scene 2)                   ││
│  │ ○ Save and review full chapter                                     ││
│  │ ○ Save and return to dashboard                                     ││
│  │ ○ Edit in Monaco editor                                            ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│                                                              [ Complete ]│
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### File: `frontend/src/lib/components/DirectorMode.svelte`

```svelte
<!--
  DirectorMode.svelte - Scene Creation Pipeline Orchestrator

  Guides writers through 6-step scene creation:
  1. Scaffold Input - Scene details, characters, optional NotebookLM enrichment
  2. Structure Selection - Choose from 5 structural approaches
  3. Generation - Multi-model tournament (3 models × 5 strategies = 15 variants)
  4. Comparison - Review variants, select winner or create hybrid
  5. Enhancement - Apply Action Prompt (85+) or 6-Pass (70-84) polish
  6. Complete - Save scene, continue to next

  Uses existing child components:
  - SceneVariantGrid.svelte
  - SceneScoreBreakdown.svelte
  - SceneComparison.svelte
-->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    currentScaffold,
    scaffoldLoading,
    scaffoldStep,
    structureVariants,
    selectedStructure,
    sceneVariants,
    sceneVariantsLoading,
    selectedSceneVariants,
    currentSceneAnalysis,
    directorStep,
    currentProject
  } from '$lib/stores';

  // Child components
  import SceneVariantGrid from './SceneVariantGrid.svelte';
  import SceneScoreBreakdown from './SceneScoreBreakdown.svelte';
  import SceneComparison from './SceneComparison.svelte';

  const dispatch = createEventDispatcher();

  // ============================================
  // State Machine
  // ============================================

  const STEPS = {
    SCAFFOLD: 0,
    STRUCTURE: 1,
    GENERATE: 2,
    COMPARE: 3,
    ENHANCE: 4,
    COMPLETE: 5
  };

  const STEP_LABELS = [
    'Scene Setup',
    'Structure',
    'Generate',
    'Compare',
    'Enhance',
    'Complete'
  ];

  // ============================================
  // Step 1: Scaffold Input State
  // ============================================

  let chapterNumber = 1;
  let sceneNumber = 1;
  let sceneTitle = '';
  let beatInfo = '';
  let selectedCharacters = [];
  let sceneDescription = '';
  let targetWordCount = 1500;

  // NotebookLM enrichment
  let enrichmentSuggestions = [];
  let enrichmentData = [];
  let enrichmentLoading = false;

  // Available characters (loaded from Story Bible)
  let availableCharacters = [];

  // Available beats (loaded from Beat Sheet)
  let availableBeats = [];

  // ============================================
  // Step 2: Structure State
  // ============================================

  let structureLoading = false;

  // ============================================
  // Step 3: Generation State
  // ============================================

  let tournamentProgress = 0;
  let tournamentTotal = 15;
  let tournamentId = null;
  let generationStatus = []; // Track each variant's status

  // ============================================
  // Step 4: Comparison State
  // ============================================

  let showComparison = false;
  let showScoreBreakdown = false;
  let selectedForComparison = [];

  // ============================================
  // Step 5: Enhancement State
  // ============================================

  let selectedVariant = null;
  let enhancementMode = 'action_prompt'; // 'action_prompt' | 'six_pass' | 'skip'
  let enhancementLoading = false;
  let enhancementResult = null;
  let actionPromptFixes = [];

  // ============================================
  // Step 6: Complete State
  // ============================================

  let finalScene = null;
  let nextAction = 'next_scene'; // 'next_scene' | 'review_chapter' | 'dashboard' | 'edit'

  // ============================================
  // Lifecycle
  // ============================================

  onMount(async () => {
    // Load available characters from Story Bible
    await loadCharacters();
    // Load available beats from Beat Sheet
    await loadBeats();
  });

  async function loadCharacters() {
    try {
      const response = await apiClient.getStoryBibleStatus();
      if (response.characters) {
        availableCharacters = response.characters.map(c => ({
          name: c.name,
          role: c.role || 'supporting',
          isProtagonist: c.is_protagonist || false
        }));
      }
    } catch (error) {
      console.error('Failed to load characters:', error);
    }
  }

  async function loadBeats() {
    try {
      const response = await apiClient.getStoryBibleStatus();
      if (response.beat_sheet?.beats) {
        availableBeats = response.beat_sheet.beats;
      }
    } catch (error) {
      console.error('Failed to load beats:', error);
    }
  }

  // ============================================
  // Step Navigation
  // ============================================

  function canProceed() {
    switch ($directorStep) {
      case STEPS.SCAFFOLD:
        return sceneTitle && beatInfo && selectedCharacters.length > 0 && sceneDescription;
      case STEPS.STRUCTURE:
        return $selectedStructure !== null;
      case STEPS.GENERATE:
        return $sceneVariants.length > 0 && !$sceneVariantsLoading;
      case STEPS.COMPARE:
        return selectedVariant !== null;
      case STEPS.ENHANCE:
        return enhancementResult !== null || enhancementMode === 'skip';
      default:
        return true;
    }
  }

  function goBack() {
    if ($directorStep > 0) {
      $directorStep -= 1;
    }
  }

  async function goNext() {
    if (!canProceed()) return;

    switch ($directorStep) {
      case STEPS.SCAFFOLD:
        await generateDraftSummary();
        break;
      case STEPS.STRUCTURE:
        await startTournament();
        break;
      case STEPS.GENERATE:
        $directorStep = STEPS.COMPARE;
        break;
      case STEPS.COMPARE:
        $directorStep = STEPS.ENHANCE;
        break;
      case STEPS.ENHANCE:
        await runEnhancement();
        break;
      case STEPS.COMPLETE:
        await completeScene();
        break;
    }
  }

  // ============================================
  // Step 1: Scaffold Generation
  // ============================================

  async function generateDraftSummary() {
    $scaffoldLoading = true;

    try {
      // Stage 1: Generate draft summary
      const response = await apiClient.generateDraftSummary(
        $currentProject?.id || 'default',
        chapterNumber,
        sceneNumber,
        beatInfo,
        selectedCharacters.map(c => c.name),
        sceneDescription
      );

      enrichmentSuggestions = response.enrichment_suggestions || [];

      // If no enrichment needed, generate full scaffold
      if (enrichmentSuggestions.length === 0 || !$currentProject?.notebookLMEnabled) {
        await generateFullScaffold();
      } else {
        // Show enrichment options
        $scaffoldStep = 1;
      }
    } catch (error) {
      console.error('Failed to generate draft summary:', error);
    } finally {
      $scaffoldLoading = false;
    }
  }

  async function queryNotebookLM(suggestion) {
    enrichmentLoading = true;
    try {
      const response = await apiClient.enrichScaffold(
        suggestion.notebook_id,
        suggestion.query
      );
      enrichmentData = [...enrichmentData, {
        query: suggestion.query,
        answer: response.answer
      }];
    } catch (error) {
      console.error('NotebookLM query failed:', error);
    } finally {
      enrichmentLoading = false;
    }
  }

  async function generateFullScaffold() {
    $scaffoldLoading = true;

    try {
      const response = await apiClient.generateScaffold(
        $currentProject?.id || 'default',
        chapterNumber,
        sceneNumber,
        sceneTitle,
        beatInfo,
        selectedCharacters.map(c => c.name),
        sceneDescription,
        enrichmentData.length > 0 ? enrichmentData : undefined
      );

      $currentScaffold = {
        scene_id: response.scene_id,
        scaffold: response.scaffold,
        enrichment_used: response.enrichment_used
      };

      // Move to structure selection
      await generateStructureVariants();
      $directorStep = STEPS.STRUCTURE;
    } catch (error) {
      console.error('Failed to generate scaffold:', error);
    } finally {
      $scaffoldLoading = false;
    }
  }

  // ============================================
  // Step 2: Structure Variants
  // ============================================

  async function generateStructureVariants() {
    structureLoading = true;

    try {
      const response = await apiClient.generateStructureVariants(
        $currentScaffold.scene_id,
        beatInfo,
        selectedCharacters.find(c => c.isProtagonist)?.name || selectedCharacters[0]?.name,
        targetWordCount,
        $currentScaffold.scaffold
      );

      $structureVariants = response.variants;

      // Auto-select recommended (first one usually)
      if ($structureVariants.length > 0) {
        $selectedStructure = $structureVariants[0];
      }
    } catch (error) {
      console.error('Failed to generate structure variants:', error);
    } finally {
      structureLoading = false;
    }
  }

  // ============================================
  // Step 3: Scene Generation Tournament
  // ============================================

  async function startTournament() {
    $sceneVariantsLoading = true;
    $directorStep = STEPS.GENERATE;
    tournamentProgress = 0;
    generationStatus = [];

    try {
      const response = await apiClient.generateSceneVariants(
        $currentScaffold.scene_id,
        $currentScaffold.scaffold,
        $selectedStructure.id,
        $currentProject?.voiceBundlePath
      );

      tournamentId = response.tournament_id;
      $sceneVariants = response.variants;
      tournamentTotal = response.total_variants;

      // All variants generated and scored
      tournamentProgress = tournamentTotal;

    } catch (error) {
      console.error('Tournament failed:', error);
    } finally {
      $sceneVariantsLoading = false;
    }
  }

  // ============================================
  // Step 4: Comparison & Selection
  // ============================================

  function handleVariantSelect(event) {
    selectedVariant = event.detail.variant;
  }

  function handleCompare(event) {
    selectedForComparison = event.detail.variants;
    showComparison = true;
  }

  function handleHybrid(event) {
    // Open hybrid creation modal
    dispatch('createHybrid', { variants: event.detail.variants });
  }

  function handleViewBreakdown(variant) {
    $currentSceneAnalysis = variant.analysis;
    showScoreBreakdown = true;
  }

  function selectWinner(variant) {
    selectedVariant = variant;
    showComparison = false;
    $directorStep = STEPS.ENHANCE;
  }

  // ============================================
  // Step 5: Enhancement
  // ============================================

  async function runEnhancement() {
    if (enhancementMode === 'skip') {
      enhancementResult = {
        content: selectedVariant.content,
        original_score: selectedVariant.score,
        enhanced_score: selectedVariant.score,
        mode_used: 'none'
      };
      $directorStep = STEPS.COMPLETE;
      return;
    }

    enhancementLoading = true;

    try {
      if (enhancementMode === 'action_prompt') {
        // First get the fixes preview
        const promptResponse = await apiClient.generateActionPrompt(
          $currentScaffold.scene_id,
          selectedVariant.content,
          getCurrentPhase()
        );
        actionPromptFixes = promptResponse.fixes;

        // Then apply them
        const applyResponse = await apiClient.applyFixes(
          $currentScaffold.scene_id,
          selectedVariant.content,
          promptResponse.fixes.map(f => f.id)
        );

        enhancementResult = {
          content: applyResponse.enhanced_content,
          original_score: selectedVariant.score,
          enhanced_score: applyResponse.new_score,
          mode_used: 'action_prompt',
          fixes_applied: applyResponse.fixes_applied
        };
      } else {
        // 6-pass enhancement
        const response = await apiClient.runSixPass(
          $currentScaffold.scene_id,
          selectedVariant.content,
          getCurrentPhase()
        );

        enhancementResult = {
          content: response.enhanced_content,
          original_score: selectedVariant.score,
          enhanced_score: response.final_score,
          mode_used: 'six_pass',
          passes: response.pass_results
        };
      }

      $directorStep = STEPS.COMPLETE;
    } catch (error) {
      console.error('Enhancement failed:', error);
    } finally {
      enhancementLoading = false;
    }
  }

  function getCurrentPhase() {
    // Determine story phase from beat
    if (beatInfo.includes('Opening') || beatInfo.includes('Setup')) return 'act1';
    if (beatInfo.includes('Midpoint')) return 'midpoint';
    if (beatInfo.includes('Climax') || beatInfo.includes('Finale')) return 'climax';
    return 'act2';
  }

  // ============================================
  // Step 6: Completion
  // ============================================

  async function completeScene() {
    finalScene = {
      chapter: chapterNumber,
      scene: sceneNumber,
      title: sceneTitle,
      content: enhancementResult?.content || selectedVariant.content,
      word_count: (enhancementResult?.content || selectedVariant.content).split(/\s+/).length,
      score: enhancementResult?.enhanced_score || selectedVariant.score,
      model: selectedVariant.model,
      strategy: selectedVariant.strategy,
      enhancement: enhancementResult?.mode_used || 'none'
    };

    // Save to file system
    try {
      await apiClient.writeFile(
        `content/Chapters/Chapter_${chapterNumber}/Scene_${sceneNumber}.md`,
        finalScene.content
      );
    } catch (error) {
      console.error('Failed to save scene:', error);
    }

    // Handle next action
    switch (nextAction) {
      case 'next_scene':
        resetForNextScene();
        break;
      case 'review_chapter':
        dispatch('reviewChapter', { chapter: chapterNumber });
        break;
      case 'dashboard':
        dispatch('returnToDashboard');
        break;
      case 'edit':
        dispatch('openEditor', { path: `content/Chapters/Chapter_${chapterNumber}/Scene_${sceneNumber}.md` });
        break;
    }
  }

  function resetForNextScene() {
    // Increment scene number
    sceneNumber += 1;

    // Reset state
    sceneTitle = '';
    sceneDescription = '';
    enrichmentData = [];
    enrichmentSuggestions = [];
    $currentScaffold = null;
    $structureVariants = [];
    $selectedStructure = null;
    $sceneVariants = [];
    $selectedSceneVariants = [];
    selectedVariant = null;
    enhancementResult = null;

    // Go back to step 1
    $directorStep = STEPS.SCAFFOLD;
  }

  // ============================================
  // Utility Functions
  // ============================================

  function toggleCharacter(character) {
    if (selectedCharacters.find(c => c.name === character.name)) {
      selectedCharacters = selectedCharacters.filter(c => c.name !== character.name);
    } else {
      selectedCharacters = [...selectedCharacters, character];
    }
  }

  function getScoreTier(score) {
    if (score >= 95) return { label: 'Gold Standard', color: '#d4a574' };
    if (score >= 90) return { label: 'Excellent', color: '#3fb950' };
    if (score >= 85) return { label: 'Strong', color: '#58a6ff' };
    if (score >= 80) return { label: 'Good', color: '#d29922' };
    if (score >= 75) return { label: 'Acceptable', color: '#8b949e' };
    return { label: 'Needs Work', color: '#f85149' };
  }
</script>

<!-- Template continues with full UI implementation... -->
<!-- See UI/UX Design section above for detailed layouts -->

<div class="director-mode">
  <!-- Progress Header -->
  <header class="director-header">
    <h1>Director Mode</h1>
    <div class="step-indicator">
      {#each STEP_LABELS as label, i}
        <div
          class="step"
          class:active={$directorStep === i}
          class:completed={$directorStep > i}
        >
          <span class="step-number">{i + 1}</span>
          <span class="step-label">{label}</span>
        </div>
        {#if i < STEP_LABELS.length - 1}
          <div class="step-connector" class:completed={$directorStep > i}></div>
        {/if}
      {/each}
    </div>
  </header>

  <!-- Step Content -->
  <main class="director-content">
    {#if $directorStep === STEPS.SCAFFOLD}
      <!-- Step 1: Scaffold Input -->
      <div class="step-scaffold">
        <!-- ... scaffold input form ... -->
      </div>
    {:else if $directorStep === STEPS.STRUCTURE}
      <!-- Step 2: Structure Selection -->
      <div class="step-structure">
        <!-- ... structure variant selection ... -->
      </div>
    {:else if $directorStep === STEPS.GENERATE}
      <!-- Step 3: Tournament Progress -->
      <div class="step-generate">
        <!-- ... tournament progress display ... -->
      </div>
    {:else if $directorStep === STEPS.COMPARE}
      <!-- Step 4: Compare & Select -->
      <div class="step-compare">
        <SceneVariantGrid
          variants={$sceneVariants}
          on:select={handleVariantSelect}
          on:compare={handleCompare}
          on:hybrid={handleHybrid}
        />
      </div>
    {:else if $directorStep === STEPS.ENHANCE}
      <!-- Step 5: Enhancement -->
      <div class="step-enhance">
        <!-- ... enhancement options ... -->
      </div>
    {:else if $directorStep === STEPS.COMPLETE}
      <!-- Step 6: Complete -->
      <div class="step-complete">
        <!-- ... completion summary ... -->
      </div>
    {/if}
  </main>

  <!-- Navigation Footer -->
  <footer class="director-footer">
    {#if $directorStep > 0 && $directorStep < STEPS.COMPLETE}
      <button class="btn-secondary" on:click={goBack}>Back</button>
    {/if}
    <div class="spacer"></div>
    {#if $directorStep < STEPS.COMPLETE}
      <button
        class="btn-primary"
        on:click={goNext}
        disabled={!canProceed()}
      >
        {$directorStep === STEPS.ENHANCE ? 'Run & Continue' : 'Next'}
      </button>
    {:else}
      <button class="btn-primary" on:click={completeScene}>
        Complete
      </button>
    {/if}
  </footer>

  <!-- Modals -->
  {#if showComparison}
    <div class="modal-overlay" on:click={() => showComparison = false}>
      <div class="modal-content" on:click|stopPropagation>
        <SceneComparison
          variants={selectedForComparison}
          on:selectWinner={(e) => selectWinner(e.detail.variant)}
          on:close={() => showComparison = false}
        />
      </div>
    </div>
  {/if}

  {#if showScoreBreakdown}
    <div class="modal-overlay" on:click={() => showScoreBreakdown = false}>
      <div class="modal-content" on:click|stopPropagation>
        <SceneScoreBreakdown
          on:close={() => showScoreBreakdown = false}
          on:enhance={(e) => {
            enhancementMode = e.detail.mode;
            showScoreBreakdown = false;
          }}
        />
      </div>
    </div>
  {/if}
</div>

<style>
  .director-mode {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary, #0f1419);
  }

  /* Header with step indicator */
  .director-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .director-header h1 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .step-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
  }

  .step {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: var(--space-1, 4px) var(--space-2, 8px);
    border-radius: var(--radius-full, 9999px);
    background: var(--bg-tertiary, #242d38);
    opacity: 0.5;
    transition: all 0.2s ease;
  }

  .step.active {
    opacity: 1;
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
  }

  .step.completed {
    opacity: 0.8;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
  }

  .step-number {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--bg-elevated, #2d3640);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
  }

  .step.active .step-number {
    background: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
  }

  .step.completed .step-number {
    background: var(--success, #3fb950);
    color: var(--bg-primary, #0f1419);
  }

  .step-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .step.active .step-label {
    color: var(--accent-gold, #d4a574);
  }

  .step-connector {
    width: 16px;
    height: 2px;
    background: var(--border, #2d3a47);
  }

  .step-connector.completed {
    background: var(--success, #3fb950);
  }

  /* Main content area */
  .director-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  /* Footer with navigation */
  .director-footer {
    display: flex;
    align-items: center;
    padding: var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .spacer {
    flex: 1;
  }

  .btn-primary,
  .btn-secondary {
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-primary {
    background: var(--accent-gold, #d4a574);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--accent-gold-hover, #e0b585);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  /* Modal overlay */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    overflow: hidden;
    border-radius: var(--radius-lg, 8px);
  }
</style>
```

---

## Integration Points

### 1. Store Updates

The existing stores in `stores.js` are sufficient. The component uses:
- `directorStep` - Current step (0-5)
- `currentScaffold` - Scene scaffold data
- `scaffoldLoading` / `scaffoldStep` - Scaffold generation state
- `structureVariants` / `selectedStructure` - Structure selection
- `sceneVariants` / `sceneVariantsLoading` - Tournament results
- `selectedSceneVariants` - Multi-select for comparison
- `currentSceneAnalysis` - Detailed score breakdown

### 2. API Client

All necessary methods already exist in `api_client.ts`. No additions needed.

### 3. MainLayout Integration

Add Director Mode as a tab/mode in the main layout:

```svelte
<!-- In MainLayout.svelte -->
{#if currentMode === 'director'}
  <DirectorMode
    on:returnToDashboard={() => currentMode = 'dashboard'}
    on:reviewChapter={handleReviewChapter}
    on:openEditor={handleOpenEditor}
  />
{/if}
```

### 4. Foreman Integration

The Foreman can trigger Director Mode when Story Bible is complete:

```javascript
// In Foreman conversation handler
if (foremanMode === 'DIRECTOR' && storyBibleComplete && voiceBundleExists) {
  dispatch('enterDirectorMode');
}
```

---

## Testing Checklist

### Step 1: Scaffold
- [ ] Chapter/scene dropdowns populate correctly
- [ ] Character list loads from Story Bible
- [ ] Beat list loads from Beat Sheet
- [ ] Scene description accepts multiline input
- [ ] NotebookLM enrichment queries work
- [ ] Scaffold generates correctly
- [ ] Skip to generation bypasses enrichment

### Step 2: Structure
- [ ] 5 structure variants display
- [ ] Radio selection works
- [ ] Recommended variant highlighted
- [ ] Word count estimates shown
- [ ] Back button returns to scaffold

### Step 3: Generate
- [ ] Tournament starts correctly
- [ ] Progress indicator updates
- [ ] All 15 variants generate
- [ ] Scores display in real-time
- [ ] Cancel button works
- [ ] Error handling for API failures

### Step 4: Compare
- [ ] SceneVariantGrid displays correctly
- [ ] Multi-select works (max 4)
- [ ] Compare modal opens
- [ ] Score breakdown modal opens
- [ ] Best variant highlighted
- [ ] Hybrid creation triggers event
- [ ] Single selection proceeds to enhancement

### Step 5: Enhance
- [ ] Correct mode recommended based on score
- [ ] Action prompt shows fixes
- [ ] 6-pass option available
- [ ] Skip option available
- [ ] Enhancement runs correctly
- [ ] Score improvement shown

### Step 6: Complete
- [ ] Final score displayed
- [ ] Scene saved to file system
- [ ] Next scene option works
- [ ] Review chapter option works
- [ ] Return to dashboard works
- [ ] Edit in Monaco works

---

## Definition of Done

1. [ ] `DirectorMode.svelte` created with full 6-step workflow
2. [ ] All 6 steps have complete UI implementation
3. [ ] Integrates with existing child components
4. [ ] Uses existing stores and API client
5. [ ] Step navigation with validation
6. [ ] Loading states and error handling
7. [ ] Modal overlays for comparison/breakdown
8. [ ] Scene saved to file system on completion
9. [ ] TypeScript types pass `npm run check`
10. [ ] Manual testing of full workflow
11. [ ] Documentation updated

---

*Task spec created: December 5, 2025*
*Branch: nifty-antonelli*
