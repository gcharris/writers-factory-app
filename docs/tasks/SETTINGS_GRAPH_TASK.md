# Settings Panel: Graph Configuration

**Related To**: Squad Management Enhancement Plan (in progress)
**Parent Spec**: `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md` (Part 6)
**Status**: Ready for Implementation
**Coordination**: This can be built alongside or after SettingsSquad.svelte enhancements

---

## Context

The GraphRAG implementation plan defines new settings that need UI controls. This task creates a `SettingsGraph.svelte` component for the Settings panel.

**Important**: Before starting, read `docs/specs/GRAPHRAG_IMPLEMENTATION_PLAN.md`, especially:
- Part 0.4: Settings Integration Points
- Part 6: Settings Panel Integration

---

## Goal

Create a new Settings panel section for Knowledge Graph configuration with:
1. Narrative edge type toggles
2. Extraction behavior controls
3. Verification level selector
4. Embedding provider choice

---

## Component: SettingsGraph.svelte

**File**: `frontend/src/lib/components/settings/SettingsGraph.svelte`

### Full Component Code

```svelte
<!-- frontend/src/lib/components/settings/SettingsGraph.svelte -->

<script>
    import { onMount } from 'svelte';
    import { settingsStore, saveSettings } from '$lib/stores';

    // Local state bound to settings
    let edgeTypes = {
        MOTIVATES: true,
        HINDERS: true,
        CHALLENGES: true,
        CAUSES: true,
        FORESHADOWS: true,
        CALLBACKS: true,
        KNOWS: true,
        CONTRADICTS: false,
    };

    let extractionTriggers = {
        on_manuscript_promote: true,
        before_foreman_chat: true,
        periodic_minutes: 0,
    };

    let verificationLevel = 'standard';
    let embeddingProvider = 'ollama';

    // Edge type metadata for display
    const edgeTypeInfo = [
        { key: 'MOTIVATES', label: 'MOTIVATES', desc: 'Character → Goal', category: 'core' },
        { key: 'HINDERS', label: 'HINDERS', desc: 'Obstacle → Goal', category: 'core' },
        { key: 'CHALLENGES', label: 'CHALLENGES', desc: 'Scene → Fatal Flaw', category: 'core' },
        { key: 'CAUSES', label: 'CAUSES', desc: 'Event → Event', category: 'core' },
        { key: 'FORESHADOWS', label: 'FORESHADOWS', desc: 'Scene → Future Event', category: 'threading' },
        { key: 'CALLBACKS', label: 'CALLBACKS', desc: 'Scene → Past Event', category: 'threading' },
        { key: 'KNOWS', label: 'KNOWS', desc: 'Character → Fact', category: 'state' },
        { key: 'CONTRADICTS', label: 'CONTRADICTS', desc: 'Fact → Fact (experimental)', category: 'experimental' },
    ];

    const verificationLevels = [
        { value: 'minimal', label: 'Minimal', desc: 'Critical contradictions only. Fastest.' },
        { value: 'standard', label: 'Standard', desc: 'Fast checks inline (~500ms). Medium checks in background.' },
        { value: 'thorough', label: 'Thorough', desc: 'All checks including LLM analysis. May add 5-10s.' },
    ];

    const embeddingProviders = [
        { value: 'ollama', label: 'Ollama (Local)', desc: 'Free, uses local llama3.2 or nomic-embed-text' },
        { value: 'openai', label: 'OpenAI', desc: 'Best quality, requires API key' },
        { value: 'none', label: 'Disabled', desc: 'No semantic search capabilities' },
    ];

    // Load settings on mount
    onMount(() => {
        const unsubscribe = settingsStore.subscribe(settings => {
            if (settings?.graph) {
                edgeTypes = { ...edgeTypes, ...settings.graph.edge_types };
                extractionTriggers = { ...extractionTriggers, ...settings.graph.extraction_triggers };
                verificationLevel = settings.graph.verification_level || 'standard';
                embeddingProvider = settings.graph.embedding_provider || 'ollama';
            }
        });
        return unsubscribe;
    });

    // Save on any change
    async function handleChange() {
        const graphSettings = {
            edge_types: edgeTypes,
            extraction_triggers: extractionTriggers,
            verification_level: verificationLevel,
            embedding_provider: embeddingProvider,
        };

        settingsStore.update(current => ({
            ...current,
            graph: graphSettings
        }));

        await saveSettings({ graph: graphSettings });
    }

    // Group edge types by category
    $: coreEdgeTypes = edgeTypeInfo.filter(e => e.category === 'core');
    $: threadingEdgeTypes = edgeTypeInfo.filter(e => e.category === 'threading');
    $: otherEdgeTypes = edgeTypeInfo.filter(e => e.category === 'state' || e.category === 'experimental');
</script>

<div class="space-y-8">
    <!-- Header -->
    <div>
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Knowledge Graph</h2>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Configure how story information is extracted, stored, and verified.
        </p>
    </div>

    <!-- Section 1: Narrative Edge Types -->
    <section class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Narrative Edge Types</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Control which relationship types are extracted from your scenes. These capture the dramatic forces that drive your plot.
        </p>

        <!-- Core Relationships -->
        <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Core Relationships</h4>
            <div class="space-y-2">
                {#each coreEdgeTypes as et}
                    <label class="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-900 rounded">
                        <div class="flex items-center gap-3">
                            <input
                                type="checkbox"
                                bind:checked={edgeTypes[et.key]}
                                on:change={handleChange}
                                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <div>
                                <span class="font-mono text-sm text-gray-900 dark:text-white">{et.label}</span>
                                <span class="text-gray-500 dark:text-gray-400 text-sm ml-2">— {et.desc}</span>
                            </div>
                        </div>
                    </label>
                {/each}
            </div>
        </div>

        <!-- Narrative Threading -->
        <div class="mb-4">
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Narrative Threading</h4>
            <div class="space-y-2">
                {#each threadingEdgeTypes as et}
                    <label class="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-900 rounded">
                        <div class="flex items-center gap-3">
                            <input
                                type="checkbox"
                                bind:checked={edgeTypes[et.key]}
                                on:change={handleChange}
                                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <div>
                                <span class="font-mono text-sm text-gray-900 dark:text-white">{et.label}</span>
                                <span class="text-gray-500 dark:text-gray-400 text-sm ml-2">— {et.desc}</span>
                            </div>
                        </div>
                    </label>
                {/each}
            </div>
        </div>

        <!-- Other/Experimental -->
        <div>
            <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Additional</h4>
            <div class="space-y-2">
                {#each otherEdgeTypes as et}
                    <label class="flex items-center justify-between py-2 px-3 bg-gray-50 dark:bg-gray-900 rounded {et.category === 'experimental' ? 'border border-yellow-300 dark:border-yellow-700' : ''}">
                        <div class="flex items-center gap-3">
                            <input
                                type="checkbox"
                                bind:checked={edgeTypes[et.key]}
                                on:change={handleChange}
                                class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                            />
                            <div>
                                <span class="font-mono text-sm text-gray-900 dark:text-white">{et.label}</span>
                                <span class="text-gray-500 dark:text-gray-400 text-sm ml-2">— {et.desc}</span>
                                {#if et.category === 'experimental'}
                                    <span class="ml-2 px-1.5 py-0.5 text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 rounded">experimental</span>
                                {/if}
                            </div>
                        </div>
                    </label>
                {/each}
            </div>
        </div>
    </section>

    <!-- Section 2: Extraction Behavior -->
    <section class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Extraction Behavior</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Control when story facts are extracted and added to the knowledge graph.
        </p>

        <div class="space-y-4">
            <label class="flex items-center justify-between">
                <div>
                    <span class="text-gray-900 dark:text-white">Extract on manuscript promotion</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">When you finalize a scene from Working to Manuscript</p>
                </div>
                <input
                    type="checkbox"
                    bind:checked={extractionTriggers.on_manuscript_promote}
                    on:change={handleChange}
                    class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
            </label>

            <label class="flex items-center justify-between">
                <div>
                    <span class="text-gray-900 dark:text-white">Extract before Foreman chat</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Process recent edits before the Foreman responds</p>
                </div>
                <input
                    type="checkbox"
                    bind:checked={extractionTriggers.before_foreman_chat}
                    on:change={handleChange}
                    class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
            </label>

            <div class="flex items-center justify-between">
                <div>
                    <span class="text-gray-900 dark:text-white">Periodic extraction</span>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Automatically extract every N minutes (0 = disabled)</p>
                </div>
                <input
                    type="number"
                    min="0"
                    max="120"
                    bind:value={extractionTriggers.periodic_minutes}
                    on:change={handleChange}
                    class="w-20 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900 text-gray-900 dark:text-white"
                />
            </div>
        </div>
    </section>

    <!-- Section 3: Verification Level -->
    <section class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Verification Level</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            How thoroughly should generated content be checked for consistency?
        </p>

        <div class="space-y-2">
            {#each verificationLevels as level}
                <label class="flex items-start gap-3 p-3 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900 {verificationLevel === level.value ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' : 'bg-gray-50 dark:bg-gray-900'}">
                    <input
                        type="radio"
                        name="verification_level"
                        value={level.value}
                        bind:group={verificationLevel}
                        on:change={handleChange}
                        class="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                        <span class="font-medium text-gray-900 dark:text-white">{level.label}</span>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{level.desc}</p>
                    </div>
                </label>
            {/each}
        </div>

        <!-- Verification level explainer -->
        <div class="mt-4 p-3 bg-gray-100 dark:bg-gray-900 rounded text-sm">
            {#if verificationLevel === 'minimal'}
                <p class="text-gray-700 dark:text-gray-300">
                    <strong>Fast checks only:</strong> Dead character detection, known contradictions.
                    No delay to generation.
                </p>
            {:else if verificationLevel === 'thorough'}
                <p class="text-gray-700 dark:text-gray-300">
                    <strong>All checks:</strong> Fast + medium + full LLM semantic analysis.
                    Includes voice consistency, pacing, and beat alignment. May add 5-10 seconds.
                </p>
            {:else}
                <p class="text-gray-700 dark:text-gray-300">
                    <strong>Balanced:</strong> Fast checks inline (~500ms), medium checks run in background.
                    You'll see notifications for any issues found.
                </p>
            {/if}
        </div>
    </section>

    <!-- Section 4: Embedding Provider -->
    <section class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">Semantic Search</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Embeddings enable intelligent search across your knowledge graph (e.g., "find characters with similar motivations").
        </p>

        <div class="space-y-2">
            {#each embeddingProviders as provider}
                <label class="flex items-start gap-3 p-3 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900 {embeddingProvider === provider.value ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' : 'bg-gray-50 dark:bg-gray-900'}">
                    <input
                        type="radio"
                        name="embedding_provider"
                        value={provider.value}
                        bind:group={embeddingProvider}
                        on:change={handleChange}
                        class="mt-1 w-4 h-4 text-blue-600 focus:ring-blue-500"
                    />
                    <div>
                        <span class="font-medium text-gray-900 dark:text-white">{provider.label}</span>
                        <p class="text-sm text-gray-500 dark:text-gray-400">{provider.desc}</p>
                    </div>
                </label>
            {/each}
        </div>

        {#if embeddingProvider === 'ollama'}
            <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded text-sm">
                <p class="text-blue-800 dark:text-blue-200">
                    <strong>Tip:</strong> For best results, install the dedicated embedding model:
                    <code class="bg-blue-100 dark:bg-blue-800 px-1 rounded">ollama pull nomic-embed-text</code>
                </p>
            </div>
        {/if}

        {#if embeddingProvider === 'none'}
            <div class="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded text-sm">
                <p class="text-yellow-800 dark:text-yellow-200">
                    <strong>Note:</strong> Without embeddings, the system falls back to keyword matching.
                    Semantic queries like "characters similar to Mickey" won't work.
                </p>
            </div>
        {/if}
    </section>
</div>
```

---

## Integration with Settings Panel

The Settings panel should have tabs or sections. Add "Knowledge Graph" as a new section/tab.

**Option A: Tab-based** (if Settings uses tabs)
```svelte
<!-- In Settings.svelte or similar -->
<script>
    import SettingsSquad from './settings/SettingsSquad.svelte';
    import SettingsGraph from './settings/SettingsGraph.svelte';

    let activeTab = 'squad';
</script>

<div class="tabs">
    <button class:active={activeTab === 'squad'} on:click={() => activeTab = 'squad'}>
        Squad
    </button>
    <button class:active={activeTab === 'graph'} on:click={() => activeTab = 'graph'}>
        Knowledge Graph
    </button>
</div>

{#if activeTab === 'squad'}
    <SettingsSquad />
{:else if activeTab === 'graph'}
    <SettingsGraph />
{/if}
```

**Option B: Accordion/Section-based**
```svelte
<details>
    <summary>Squad Configuration</summary>
    <SettingsSquad />
</details>

<details>
    <summary>Knowledge Graph</summary>
    <SettingsGraph />
</details>
```

---

## Backend Settings Schema

Ensure the backend `settings_service.py` can handle the graph settings. Add to the settings schema:

```python
# In backend/services/settings_service.py

# Add graph settings schema
GRAPH_SETTINGS_DEFAULT = {
    "edge_types": {
        "MOTIVATES": True,
        "HINDERS": True,
        "CHALLENGES": True,
        "CAUSES": True,
        "FORESHADOWS": True,
        "CALLBACKS": True,
        "KNOWS": True,
        "CONTRADICTS": False,
    },
    "extraction_triggers": {
        "on_manuscript_promote": True,
        "before_foreman_chat": True,
        "periodic_minutes": 0,
    },
    "verification_level": "standard",
    "embedding_provider": "ollama",
}

# In get_all_settings or equivalent
def get_all_settings(self) -> dict:
    settings = self._load_settings()
    # Ensure graph settings exist with defaults
    if "graph" not in settings:
        settings["graph"] = GRAPH_SETTINGS_DEFAULT.copy()
    return settings
```

---

## Files Checklist

**Create**:
- [ ] `frontend/src/lib/components/settings/SettingsGraph.svelte`

**Modify**:
- [ ] Settings panel parent component (add SettingsGraph as tab/section)
- [ ] `backend/services/settings_service.py` (add graph settings defaults)
- [ ] `frontend/src/lib/stores.js` (ensure settingsStore handles graph namespace)

---

## Verification

### Visual Check
1. Open Settings panel
2. Navigate to Knowledge Graph section
3. Verify all 4 sections render:
   - Narrative Edge Types (with 8 toggles)
   - Extraction Behavior (with 3 controls)
   - Verification Level (with 3 radio options)
   - Embedding Provider (with 3 radio options)

### Functional Check
1. Toggle an edge type → verify it persists after page refresh
2. Change verification level → verify selection persists
3. Change embedding provider → verify info message updates

### Dark Mode Check
1. Toggle dark mode
2. Verify all sections have proper contrast
3. Verify experimental badge is visible in both modes

---

## Coordination with Squad Settings Task

The original Squad settings task remains valid. The two tasks can be done:
- **In parallel**: Different agents work on SettingsSquad.svelte and SettingsGraph.svelte
- **Sequentially**: Same agent does both

If done by the same agent, suggest this order:
1. Complete Squad settings (Role Assignments, Health Check Configuration)
2. Create SettingsGraph.svelte
3. Wire both into the Settings panel parent

---

## Success Criteria

- [ ] SettingsGraph.svelte renders all 4 sections
- [ ] All settings persist correctly via settingsStore
- [ ] Backend returns graph settings with proper defaults
- [ ] Dark mode support
- [ ] No TypeScript/Svelte warnings
- [ ] Settings panel navigation works (tab or section)

---

## Handoff

When complete, provide:
1. Branch name and commit hash
2. Screenshot of the Settings Graph panel
3. Confirmation that settings persist correctly
4. Note any deviations from spec
