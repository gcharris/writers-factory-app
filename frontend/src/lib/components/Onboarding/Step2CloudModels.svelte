<!--
  Step2CloudModels.svelte - Comprehensive Cloud AI Models Setup

  Features:
  - Shows all models organized by region
  - Real-time status from /api-keys/status endpoint
  - [Configure Keys] button opens modal for premium providers
  - [Test] button beside each model
  - Clear status indicators (Ready, Not Configured, Testing, Failed)
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Types
  type ProviderStatus = {
    available: boolean;
    source: 'embedded' | 'env' | null;
    tier: 'embedded' | 'user';
  };

  type KeyStatusResponse = {
    providers: Record<string, ProviderStatus>;
    embedded_providers: string[];
    user_providers: string[];
  };

  type TestResult = 'untested' | 'testing' | 'success' | 'failed';

  // State
  let keyStatus: KeyStatusResponse | null = null;
  let loading = true;
  let error = '';
  let showConfigureModal = false;
  let testResults: Record<string, TestResult> = {};

  // Premium provider keys (for modal input)
  let premiumKeys: Record<string, string> = {
    openai: '',
    anthropic: '',
    xai: '',
    gemini: ''
  };
  let showKeys: Record<string, boolean> = {
    openai: false,
    anthropic: false,
    xai: false,
    gemini: false
  };
  let savingKeys = false;
  let saveMessage = '';

  // Model data organized by region
  const regions = [
    {
      name: 'US',
      subtitle: 'Premium',
      badgeClass: 'key-required',
      models: [
        { id: 'openai', provider: 'OpenAI', model: 'GPT-4o', pricing: '$2.50/$10 per 1M tokens', tier: 'user' },
        { id: 'anthropic', provider: 'Anthropic', model: 'Claude', pricing: '$3/$15 per 1M tokens', tier: 'user' },
        { id: 'xai', provider: 'xAI', model: 'Grok', pricing: '$2/$10 per 1M tokens', tier: 'user' },
        { id: 'gemini', provider: 'Google', model: 'Gemini', pricing: '$0.075/$0.30 per 1M tokens', tier: 'user' }
      ]
    },
    {
      name: 'China / Asia',
      subtitle: 'Included Free',
      badgeClass: 'free-mvp',
      models: [
        { id: 'deepseek', provider: 'DeepSeek', model: 'V3', pricing: '$0.27/$1.10 per 1M tokens', tier: 'embedded' },
        { id: 'qwen', provider: 'Alibaba', model: 'Qwen', pricing: '$0.50/$2 per 1M tokens', tier: 'embedded' },
        { id: 'moonshot', provider: 'Moonshot', model: 'Kimi', pricing: '$0.20/$0.80 per 1M tokens', tier: 'embedded' },
        { id: 'zhipu', provider: 'Zhipu AI', model: 'ChatGLM', pricing: '$0.30/$1.20 per 1M tokens', tier: 'embedded' }
      ]
    },
    {
      name: 'Europe',
      subtitle: 'Included Free',
      badgeClass: 'free-mvp',
      models: [
        { id: 'mistral', provider: 'Mistral AI', model: 'Mistral Large', pricing: '$0.15/$0.45 per 1M tokens', tier: 'embedded' }
      ]
    },
    {
      name: 'Russia',
      subtitle: 'Included Free',
      badgeClass: 'free-mvp',
      models: [
        { id: 'yandex', provider: 'Yandex', model: 'YandexGPT', pricing: 'Variable pricing', tier: 'embedded' }
      ]
    },
    {
      name: 'Local',
      subtitle: 'Always Free',
      badgeClass: 'local',
      models: [
        { id: 'ollama', provider: 'Ollama', model: 'Llama 3.2', pricing: 'Free (runs locally)', tier: 'local' }
      ]
    }
  ];

  // Premium providers for the modal
  const premiumProviders = [
    {
      id: 'openai',
      name: 'OpenAI (GPT-4o)',
      description: 'Best for creative writing and complex narratives',
      placeholder: 'sk-...',
      docsUrl: 'https://platform.openai.com/api-keys'
    },
    {
      id: 'anthropic',
      name: 'Anthropic (Claude)',
      description: 'Excellent for character development and narrative analysis',
      placeholder: 'sk-ant-...',
      docsUrl: 'https://console.anthropic.com/settings/keys'
    },
    {
      id: 'xai',
      name: 'xAI (Grok)',
      description: 'Real-time knowledge for research and world-building',
      placeholder: 'xai-...',
      docsUrl: 'https://console.x.ai'
    },
    {
      id: 'gemini',
      name: 'Google Gemini',
      description: 'Fast and capable with generous free tier',
      placeholder: 'AIza...',
      docsUrl: 'https://aistudio.google.com/apikey'
    }
  ];

  // Count stats
  $: readyCount = keyStatus
    ? Object.values(keyStatus.providers).filter(p => p.available).length
    : 0;
  $: totalCount = keyStatus
    ? Object.keys(keyStatus.providers).length
    : 0;

  onMount(async () => {
    await loadKeyStatus();
  });

  async function loadKeyStatus() {
    loading = true;
    error = '';

    try {
      const response = await fetch(`${BASE_URL}/api-keys/status`);
      if (response.ok) {
        keyStatus = await response.json();
        // Initialize test results
        if (keyStatus) {
          for (const provider of Object.keys(keyStatus.providers)) {
            testResults[provider] = 'untested';
          }
        }
      } else {
        throw new Error('Failed to load key status');
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to check API keys';
    } finally {
      loading = false;
    }
  }

  function getModelStatus(modelId: string): { available: boolean; source: string | null } {
    if (!keyStatus) return { available: false, source: null };

    // Special case for Ollama - check if it was detected
    if (modelId === 'ollama') {
      return { available: true, source: 'local' };
    }

    const status = keyStatus.providers[modelId];
    if (status) {
      return { available: status.available, source: status.source };
    }
    return { available: false, source: null };
  }

  async function testModel(modelId: string) {
    testResults[modelId] = 'testing';
    testResults = testResults; // Trigger reactivity

    try {
      const response = await fetch(`${BASE_URL}/api-keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: modelId })
      });

      if (response.ok) {
        const result = await response.json();
        testResults[modelId] = result.valid ? 'success' : 'failed';
      } else {
        testResults[modelId] = 'failed';
      }
    } catch (e) {
      testResults[modelId] = 'failed';
    }
    testResults = testResults; // Trigger reactivity
  }

  function openConfigureModal() {
    showConfigureModal = true;
  }

  function closeConfigureModal() {
    showConfigureModal = false;
    saveMessage = '';
  }

  async function saveApiKeys() {
    savingKeys = true;
    saveMessage = '';

    try {
      // Save keys via the settings endpoint
      const keysToSave: Record<string, string> = {};
      for (const [provider, key] of Object.entries(premiumKeys)) {
        if (key.trim()) {
          keysToSave[`${provider}_api_key`] = key.trim();
        }
      }

      if (Object.keys(keysToSave).length === 0) {
        saveMessage = 'No keys to save';
        savingKeys = false;
        return;
      }

      const response = await fetch(`${BASE_URL}/settings/category/agents`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keysToSave)
      });

      if (response.ok) {
        saveMessage = 'Keys saved! Refreshing status...';
        // Clear inputs
        for (const provider of Object.keys(premiumKeys)) {
          premiumKeys[provider] = '';
        }
        // Reload status
        await loadKeyStatus();
        saveMessage = 'Keys saved successfully!';
        setTimeout(() => {
          closeConfigureModal();
        }, 1500);
      } else {
        saveMessage = 'Failed to save keys';
      }
    } catch (e) {
      saveMessage = 'Error saving keys';
    } finally {
      savingKeys = false;
    }
  }

  function toggleShowKey(provider: string) {
    showKeys[provider] = !showKeys[provider];
    showKeys = showKeys;
  }

  function openDocs(url: string) {
    window.open(url, '_blank');
  }

  function handleBack() {
    dispatch('back');
  }

  function handleContinue() {
    dispatch('next');
  }
</script>

<div class="step-cloud-models">
  <div class="step-header">
    <h2>Cloud AI Models</h2>
    <p class="step-description">
      Configure your AI models. Some are included free, others require your own API keys.
    </p>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Checking AI model status...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <p>{error}</p>
      <button class="btn-secondary" on:click={loadKeyStatus}>Retry</button>
    </div>
  {:else}
    <!-- Status Summary -->
    <div class="status-summary">
      <div class="summary-stat">
        <span class="stat-number">{readyCount}</span>
        <span class="stat-label">Ready</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-stat">
        <span class="stat-number">{totalCount - readyCount}</span>
        <span class="stat-label">Not Configured</span>
      </div>
      <button class="btn-configure" on:click={openConfigureModal}>
        Configure Premium Keys
      </button>
    </div>

    <!-- Model Regions -->
    <div class="regions-container">
      {#each regions as region}
        <div class="region-section">
          <div class="region-header">
            <h3 class="region-name">{region.name}</h3>
            <span class="region-subtitle {region.badgeClass}">{region.subtitle}</span>
          </div>

          <div class="models-list">
            {#each region.models as model}
              {@const status = getModelStatus(model.id)}
              {@const testResult = testResults[model.id] || 'untested'}
              <div class="model-row {status.available ? 'available' : 'unavailable'}">
                <div class="model-info">
                  <span class="provider-name">{model.provider}</span>
                  <span class="model-name">{model.model}</span>
                </div>
                <div class="model-pricing">{model.pricing}</div>
                <div class="model-status-col">
                  {#if status.available}
                    <span class="status-badge ready">Ready</span>
                  {:else}
                    <span class="status-badge not-configured">Not Configured</span>
                  {/if}
                </div>
                <div class="model-actions">
                  {#if model.tier !== 'local'}
                    {#if status.available}
                      <button
                        class="btn-test {testResult}"
                        on:click={() => testModel(model.id)}
                        disabled={testResult === 'testing'}
                      >
                        {#if testResult === 'testing'}
                          Testing...
                        {:else if testResult === 'success'}
                          Passed
                        {:else if testResult === 'failed'}
                          Failed
                        {:else}
                          Test
                        {/if}
                      </button>
                    {:else if model.tier === 'user'}
                      <button class="btn-configure-small" on:click={openConfigureModal}>
                        Configure
                      </button>
                    {:else}
                      <span class="status-note">Not available</span>
                    {/if}
                  {:else}
                    <span class="status-note local">Local</span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>

    <!-- Info Note -->
    <div class="info-note">
      <p>
        <strong>Included models</strong> (DeepSeek, Qwen, Mistral) work immediately.
        Premium US models require your own API keys - you only pay for tokens you use.
      </p>
      <p class="skip-text">You can configure keys later in Settings.</p>
    </div>
  {/if}

  <!-- Navigation -->
  <div class="step-actions">
    <button class="btn-secondary" on:click={handleBack}>
      <span class="arrow">←</span>
      Back
    </button>
    <button class="btn-primary" on:click={handleContinue}>
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<!-- Configure Keys Modal -->
{#if showConfigureModal}
  <div class="modal-overlay" on:click={closeConfigureModal} on:keydown={(e) => e.key === 'Escape' && closeConfigureModal()} role="button" tabindex="0">
    <div class="modal-content" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true" tabindex="-1">
      <div class="modal-header">
        <h3>Configure Premium API Keys</h3>
        <button class="modal-close" on:click={closeConfigureModal}>×</button>
      </div>

      <div class="modal-body">
        <p class="modal-intro">
          Enter your API keys for premium providers. These are optional - you only pay for tokens you use.
        </p>

        <div class="key-inputs">
          {#each premiumProviders as provider}
            {@const status = getModelStatus(provider.id)}
            <div class="key-input-card {status.available ? 'configured' : ''}">
              <div class="key-header">
                <span class="key-name">{provider.name}</span>
                {#if status.available}
                  <span class="key-badge configured">Configured</span>
                {/if}
              </div>
              <p class="key-desc">{provider.description}</p>

              <div class="input-row">
                <input
                  type={showKeys[provider.id] ? 'text' : 'password'}
                  bind:value={premiumKeys[provider.id]}
                  placeholder={status.available ? '(already configured)' : provider.placeholder}
                  class="key-input"
                />
                <button
                  type="button"
                  class="btn-toggle-vis"
                  on:click={() => toggleShowKey(provider.id)}
                >
                  {showKeys[provider.id] ? 'Hide' : 'Show'}
                </button>
              </div>

              <button class="btn-link" on:click={() => openDocs(provider.docsUrl)}>
                Get API Key →
              </button>
            </div>
          {/each}
        </div>

        {#if saveMessage}
          <div class="save-message {saveMessage.includes('success') ? 'success' : 'error'}">
            {saveMessage}
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeConfigureModal}>Cancel</button>
        <button class="btn-primary" on:click={saveApiKeys} disabled={savingKeys}>
          {savingKeys ? 'Saving...' : 'Save Keys'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .step-cloud-models {
    max-width: 900px;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .step-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .step-description {
    color: var(--text-secondary, #8b949e);
    margin: 0;
    font-size: 1rem;
  }

  /* Loading/Error States */
  .loading-state, .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3rem;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #00d9ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-state p, .error-state p {
    margin-top: 1rem;
    color: var(--text-secondary, #8b949e);
  }

  /* Status Summary */
  .status-summary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    padding: 1rem 1.5rem;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }

  .summary-stat {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .stat-number {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent-cyan, #00d9ff);
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
  }

  .summary-divider {
    width: 1px;
    height: 32px;
    background: var(--border, #2d3a47);
  }

  .btn-configure {
    margin-left: auto;
    padding: 0.5rem 1rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-configure:hover {
    background: #00b8d9;
  }

  /* Regions Container */
  .regions-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .region-section {
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    overflow: hidden;
  }

  .region-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .region-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .region-subtitle {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
  }

  .region-subtitle.key-required {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
  }

  .region-subtitle.free-mvp {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .region-subtitle.local {
    background: rgba(88, 166, 255, 0.2);
    color: #58a6ff;
  }

  /* Models List */
  .models-list {
    padding: 0.5rem;
  }

  .model-row {
    display: grid;
    grid-template-columns: 1.5fr 1fr auto auto;
    gap: 1rem;
    align-items: center;
    padding: 0.75rem 0.5rem;
    border-radius: 4px;
    transition: background 0.2s;
  }

  .model-row:hover {
    background: var(--bg-secondary, #1a2027);
  }

  .model-row.unavailable {
    opacity: 0.7;
  }

  .model-info {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .provider-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.875rem;
  }

  .model-name {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  .model-pricing {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    font-family: 'JetBrains Mono', monospace;
  }

  .model-status-col {
    min-width: 100px;
    text-align: center;
  }

  .status-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .status-badge.ready {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .status-badge.not-configured {
    background: rgba(210, 153, 34, 0.2);
    color: var(--warning, #d29922);
  }

  .model-actions {
    min-width: 80px;
    text-align: right;
  }

  .btn-test {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    background: rgba(0, 217, 255, 0.1);
    border: 1px solid var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .btn-test:hover:not(:disabled) {
    background: rgba(0, 217, 255, 0.2);
  }

  .btn-test:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-test.success {
    background: rgba(63, 185, 80, 0.2);
    border-color: var(--success, #3fb950);
    color: var(--success, #3fb950);
  }

  .btn-test.failed {
    background: rgba(248, 81, 73, 0.2);
    border-color: var(--error, #f85149);
    color: var(--error, #f85149);
  }

  .btn-configure-small {
    padding: 0.25rem 0.5rem;
    font-size: 0.7rem;
    font-weight: 600;
    border-radius: 4px;
    cursor: pointer;
    background: rgba(210, 153, 34, 0.1);
    border: 1px solid var(--warning, #d29922);
    color: var(--warning, #d29922);
    transition: all 0.2s;
  }

  .btn-configure-small:hover {
    background: rgba(210, 153, 34, 0.2);
  }

  .status-note {
    font-size: 0.7rem;
    color: var(--text-secondary, #8b949e);
  }

  .status-note.local {
    color: #58a6ff;
  }

  /* Info Note */
  .info-note {
    padding: 1rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 8px;
    border: 1px solid var(--border, #2d3a47);
    margin-bottom: 1.5rem;
  }

  .info-note p {
    margin: 0 0 0.5rem 0;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    line-height: 1.6;
  }

  .info-note p:last-child {
    margin-bottom: 0;
  }

  .info-note strong {
    color: var(--success, #3fb950);
  }

  .skip-text {
    font-style: italic;
    font-size: 0.8rem !important;
    opacity: 0.8;
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .arrow {
    font-size: 1.25rem;
  }

  /* Modal Overlay */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: var(--bg-secondary, #1a2027);
    border-radius: 12px;
    border: 1px solid var(--border, #2d3a47);
    max-width: 600px;
    max-height: 90vh;
    width: 90%;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
  }

  .modal-close {
    background: transparent;
    border: none;
    color: var(--text-secondary, #8b949e);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .modal-close:hover {
    color: #ffffff;
  }

  .modal-body {
    padding: 1.5rem;
    overflow-y: auto;
    max-height: 60vh;
  }

  .modal-intro {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 1.5rem 0;
    line-height: 1.5;
  }

  .key-inputs {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .key-input-card {
    padding: 1rem;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
  }

  .key-input-card.configured {
    border-color: var(--success, #3fb950);
    background: rgba(63, 185, 80, 0.05);
  }

  .key-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }

  .key-name {
    font-weight: 600;
    color: #ffffff;
  }

  .key-badge.configured {
    font-size: 0.65rem;
    padding: 0.15rem 0.4rem;
    background: var(--success, #3fb950);
    color: var(--bg-primary, #0f1419);
    border-radius: 4px;
    font-weight: 600;
  }

  .key-desc {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    margin: 0 0 0.75rem 0;
  }

  .input-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .key-input {
    flex: 1;
    padding: 0.5rem 0.75rem;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 4px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
  }

  .key-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #00d9ff);
  }

  .key-input::placeholder {
    color: var(--text-secondary, #8b949e);
  }

  .btn-toggle-vis {
    padding: 0.5rem 0.75rem;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 4px;
    color: var(--text-secondary, #8b949e);
    font-size: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-toggle-vis:hover {
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .btn-link {
    background: none;
    border: none;
    color: var(--accent-cyan, #00d9ff);
    font-size: 0.75rem;
    padding: 0;
    cursor: pointer;
    text-decoration: none;
  }

  .btn-link:hover {
    text-decoration: underline;
  }

  .save-message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.875rem;
    text-align: center;
  }

  .save-message.success {
    background: rgba(63, 185, 80, 0.2);
    color: var(--success, #3fb950);
  }

  .save-message.error {
    background: rgba(248, 81, 73, 0.2);
    color: var(--error, #f85149);
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  /* Responsive */
  @media (max-width: 700px) {
    .model-row {
      grid-template-columns: 1fr auto;
      gap: 0.5rem;
    }

    .model-pricing {
      display: none;
    }

    .status-summary {
      flex-wrap: wrap;
    }

    .btn-configure {
      margin-left: 0;
      width: 100%;
      margin-top: 0.5rem;
    }

    .step-actions {
      flex-direction: column;
      gap: 1rem;
    }

    .btn-primary, .btn-secondary {
      width: 100%;
      justify-content: center;
    }
  }
</style>
