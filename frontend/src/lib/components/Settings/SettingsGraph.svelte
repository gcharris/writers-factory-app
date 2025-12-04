<!--
  SettingsGraph.svelte - Knowledge Graph configuration settings

  Controls:
  - Narrative edge type extraction (MOTIVATES, HINDERS, etc.)
  - Extraction triggers (on promotion, before chat, periodic)
  - Verification level (minimal, standard, thorough)
  - Embedding provider (ollama, openai, none)
-->
<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Edge type toggles
  let edgeTypes: Record<string, boolean> = {
    MOTIVATES: true,
    HINDERS: true,
    CHALLENGES: true,
    CAUSES: true,
    FORESHADOWS: true,
    CALLBACKS: true,
    KNOWS: true,
    CONTRADICTS: false,
  };

  // Extraction trigger settings
  let extractionTriggers = {
    on_manuscript_promote: true,
    before_foreman_chat: true,
    periodic_minutes: 0,
  };

  // Verification and embedding settings
  let verificationLevel: 'minimal' | 'standard' | 'thorough' = 'standard';
  let embeddingProvider: 'ollama' | 'openai' | 'none' = 'ollama';

  // UI state
  let isLoading = true;
  let saveMessage = '';
  let errorMessage = '';

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

  // Group edge types by category
  $: coreEdgeTypes = edgeTypeInfo.filter(e => e.category === 'core');
  $: threadingEdgeTypes = edgeTypeInfo.filter(e => e.category === 'threading');
  $: otherEdgeTypes = edgeTypeInfo.filter(e => e.category === 'state' || e.category === 'experimental');

  onMount(() => {
    loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/graph`);
      if (response.ok) {
        const data = await response.json();

        // Merge with defaults in case some keys are missing
        if (data.edge_types) {
          edgeTypes = { ...edgeTypes, ...data.edge_types };
        }
        if (data.extraction_triggers) {
          extractionTriggers = { ...extractionTriggers, ...data.extraction_triggers };
        }
        verificationLevel = data.verification_level || 'standard';
        embeddingProvider = data.embedding_provider || 'ollama';
      }
    } catch (error) {
      console.error('Failed to load graph settings:', error);
      errorMessage = 'Failed to load settings';
    } finally {
      isLoading = false;
    }
  }

  async function saveSettings() {
    saveMessage = '';
    errorMessage = '';

    try {
      const settings = {
        edge_types: edgeTypes,
        extraction_triggers: extractionTriggers,
        verification_level: verificationLevel,
        embedding_provider: embeddingProvider,
      };

      const response = await fetch(`${BASE_URL}/settings/category/graph`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        saveMessage = 'Graph settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save graph settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefaults() {
    edgeTypes = {
      MOTIVATES: true,
      HINDERS: true,
      CHALLENGES: true,
      CAUSES: true,
      FORESHADOWS: true,
      CALLBACKS: true,
      KNOWS: true,
      CONTRADICTS: false,
    };
    extractionTriggers = {
      on_manuscript_promote: true,
      before_foreman_chat: true,
      periodic_minutes: 0,
    };
    verificationLevel = 'standard';
    embeddingProvider = 'ollama';
  }
</script>

<div class="settings-graph">
  <div class="header">
    <h2>Knowledge Graph</h2>
    <p class="subtitle">Configure how story information is extracted, stored, and verified.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Section 1: Narrative Edge Types -->
    <div class="section">
      <h3>Narrative Edge Types</h3>
      <p class="section-desc">Control which relationship types are extracted from your scenes.</p>

      <!-- Core Relationships -->
      <div class="edge-group">
        <h4>Core Relationships</h4>
        <div class="edge-list">
          {#each coreEdgeTypes as et}
            <label class="edge-item">
              <input
                type="checkbox"
                bind:checked={edgeTypes[et.key]}
              />
              <span class="edge-label">{et.label}</span>
              <span class="edge-desc">— {et.desc}</span>
            </label>
          {/each}
        </div>
      </div>

      <!-- Narrative Threading -->
      <div class="edge-group">
        <h4>Narrative Threading</h4>
        <div class="edge-list">
          {#each threadingEdgeTypes as et}
            <label class="edge-item">
              <input
                type="checkbox"
                bind:checked={edgeTypes[et.key]}
              />
              <span class="edge-label">{et.label}</span>
              <span class="edge-desc">— {et.desc}</span>
            </label>
          {/each}
        </div>
      </div>

      <!-- Additional -->
      <div class="edge-group">
        <h4>Additional</h4>
        <div class="edge-list">
          {#each otherEdgeTypes as et}
            <label class="edge-item {et.category === 'experimental' ? 'experimental' : ''}">
              <input
                type="checkbox"
                bind:checked={edgeTypes[et.key]}
              />
              <span class="edge-label">{et.label}</span>
              <span class="edge-desc">— {et.desc}</span>
              {#if et.category === 'experimental'}
                <span class="badge-experimental">experimental</span>
              {/if}
            </label>
          {/each}
        </div>
      </div>
    </div>

    <!-- Section 2: Extraction Behavior -->
    <div class="section">
      <h3>Extraction Behavior</h3>
      <p class="section-desc">Control when story facts are extracted and added to the knowledge graph.</p>

      <div class="trigger-list">
        <label class="trigger-item">
          <div class="trigger-info">
            <span class="trigger-label">Extract on manuscript promotion</span>
            <span class="trigger-desc">When you finalize a scene from Working to Manuscript</span>
          </div>
          <input
            type="checkbox"
            bind:checked={extractionTriggers.on_manuscript_promote}
          />
        </label>

        <label class="trigger-item">
          <div class="trigger-info">
            <span class="trigger-label">Extract before Foreman chat</span>
            <span class="trigger-desc">Process recent edits before the Foreman responds</span>
          </div>
          <input
            type="checkbox"
            bind:checked={extractionTriggers.before_foreman_chat}
          />
        </label>

        <div class="trigger-item">
          <div class="trigger-info">
            <span class="trigger-label">Periodic extraction (minutes)</span>
            <span class="trigger-desc">Automatically extract every N minutes (0 = disabled)</span>
          </div>
          <input
            type="number"
            min="0"
            max="120"
            bind:value={extractionTriggers.periodic_minutes}
            class="number-input"
          />
        </div>
      </div>
    </div>

    <!-- Section 3: Verification Level -->
    <div class="section">
      <h3>Verification Level</h3>
      <p class="section-desc">How thoroughly should generated content be checked for consistency?</p>

      <div class="radio-list">
        {#each verificationLevels as level}
          <label class="radio-item {verificationLevel === level.value ? 'selected' : ''}">
            <input
              type="radio"
              name="verification_level"
              value={level.value}
              bind:group={verificationLevel}
            />
            <div class="radio-content">
              <span class="radio-label">{level.label}</span>
              <span class="radio-desc">{level.desc}</span>
            </div>
          </label>
        {/each}
      </div>

      <!-- Verification explainer -->
      <div class="info-box">
        {#if verificationLevel === 'minimal'}
          <p><strong>Fast checks only:</strong> Dead character detection, known contradictions. No delay to generation.</p>
        {:else if verificationLevel === 'thorough'}
          <p><strong>All checks:</strong> Fast + medium + full LLM semantic analysis. Includes voice consistency, pacing, and beat alignment. May add 5-10 seconds.</p>
        {:else}
          <p><strong>Balanced:</strong> Fast checks inline (~500ms), medium checks run in background. You'll see notifications for any issues found.</p>
        {/if}
      </div>
    </div>

    <!-- Section 4: Embedding Provider -->
    <div class="section">
      <h3>Semantic Search</h3>
      <p class="section-desc">Embeddings enable intelligent search across your knowledge graph.</p>

      <div class="radio-list">
        {#each embeddingProviders as provider}
          <label class="radio-item {embeddingProvider === provider.value ? 'selected' : ''}">
            <input
              type="radio"
              name="embedding_provider"
              value={provider.value}
              bind:group={embeddingProvider}
            />
            <div class="radio-content">
              <span class="radio-label">{provider.label}</span>
              <span class="radio-desc">{provider.desc}</span>
            </div>
          </label>
        {/each}
      </div>

      {#if embeddingProvider === 'ollama'}
        <div class="info-box tip">
          <p><strong>Tip:</strong> For best results, install the dedicated embedding model: <code>ollama pull nomic-embed-text</code></p>
        </div>
      {/if}

      {#if embeddingProvider === 'none'}
        <div class="info-box warning">
          <p><strong>Note:</strong> Without embeddings, the system falls back to keyword matching. Semantic queries like "characters similar to Mickey" won't work.</p>
        </div>
      {/if}
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefaults}>
        Reset to Defaults
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Graph Settings
      </button>
    </div>

    {#if saveMessage}
      <div class="message success">{saveMessage}</div>
    {/if}
    {#if errorMessage}
      <div class="message error">{errorMessage}</div>
    {/if}
  {/if}
</div>

<style>
  .settings-graph {
    padding: 2rem;
    max-width: 900px;
    color: #ffffff;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    color: #b0b0b0;
    margin: 0;
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: #b0b0b0;
  }

  .section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
  }

  .section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.5rem 0;
  }

  .section-desc {
    color: #888888;
    font-size: 0.875rem;
    margin: 0 0 1.5rem 0;
  }

  /* Edge Types */
  .edge-group {
    margin-bottom: 1.5rem;
  }

  .edge-group:last-child {
    margin-bottom: 0;
  }

  .edge-group h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: #b0b0b0;
    margin: 0 0 0.75rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .edge-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .edge-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: #1a1a1a;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
  }

  .edge-item:hover {
    background: #252525;
  }

  .edge-item.experimental {
    border: 1px solid #a8620080;
  }

  .edge-item input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: #00d9ff;
    cursor: pointer;
  }

  .edge-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
    color: #ffffff;
    font-weight: 500;
  }

  .edge-desc {
    color: #888888;
    font-size: 0.875rem;
  }

  .badge-experimental {
    margin-left: auto;
    padding: 0.125rem 0.5rem;
    font-size: 0.75rem;
    background: #a8620040;
    color: #ffc107;
    border-radius: 4px;
  }

  /* Trigger List */
  .trigger-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .trigger-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .trigger-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .trigger-label {
    color: #ffffff;
    font-weight: 500;
  }

  .trigger-desc {
    color: #888888;
    font-size: 0.875rem;
  }

  .trigger-item input[type="checkbox"] {
    width: 20px;
    height: 20px;
    accent-color: #00d9ff;
    cursor: pointer;
  }

  .number-input {
    width: 80px;
    padding: 0.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-size: 0.875rem;
    text-align: center;
  }

  .number-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  /* Radio List */
  .radio-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .radio-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s;
  }

  .radio-item:hover {
    background: #252525;
  }

  .radio-item.selected {
    background: #00d9ff15;
    border-color: #00d9ff40;
  }

  .radio-item input[type="radio"] {
    width: 18px;
    height: 18px;
    margin-top: 2px;
    accent-color: #00d9ff;
    cursor: pointer;
  }

  .radio-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .radio-label {
    color: #ffffff;
    font-weight: 500;
  }

  .radio-desc {
    color: #888888;
    font-size: 0.875rem;
  }

  /* Info Boxes */
  .info-box {
    margin-top: 1rem;
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
    border-left: 3px solid #00d9ff;
  }

  .info-box p {
    margin: 0;
    color: #b0b0b0;
    font-size: 0.875rem;
  }

  .info-box strong {
    color: #ffffff;
  }

  .info-box.tip {
    border-left-color: #00d9ff;
    background: #00d9ff10;
  }

  .info-box.tip p {
    color: #00d9ff;
  }

  .info-box.warning {
    border-left-color: #ffc107;
    background: #ffc10710;
  }

  .info-box.warning p {
    color: #ffc107;
  }

  .info-box code {
    background: #2d2d2d;
    padding: 0.125rem 0.375rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8125rem;
  }

  /* Actions */
  .actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
  }

  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: #b0b0b0;
    border: 1px solid #404040;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .btn-save {
    padding: 0.75rem 2rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-save:hover {
    background: #00b8d9;
  }

  .message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    font-weight: 500;
  }

  .message.success {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  .message.error {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff4444;
  }
</style>
