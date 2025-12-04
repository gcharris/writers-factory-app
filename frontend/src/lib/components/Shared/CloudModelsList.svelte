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
  let testResults: Record<string, TestResult> = {};
  let subscriptionStatus: 'none' | 'active' = 'none';

  // Model data organized by region
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
        { id: 'kimi', provider: 'Moonshot', model: 'Kimi', pricing: '$0.20/$0.80 per 1M tokens', tier: 'embedded' },
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

  // Count stats
  $: readyCount = keyStatus
    ? Object.values(keyStatus.providers).filter(p => p.available).length
    : 0;
  $: totalCount = keyStatus
    ? Object.keys(keyStatus.providers).length
    : 0;

  onMount(async () => {
    // Load subscription status
    const savedStatus = localStorage.getItem('writers_factory_subscription');
    if (savedStatus === 'active') {
      subscriptionStatus = 'active';
    }
    await loadKeyStatus();
  });

  export async function loadKeyStatus() {
    loading = true;
    error = '';

    try {
      const response = await fetch(`${BASE_URL}/api-keys/status?t=${Date.now()}`);
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
      // HACK: For the Desktop App MVP, we want to pretend .env keys don't exist for premium providers
      // so the user sees the "Configure" flow.
      const isUserTier = ['openai', 'anthropic', 'xai', 'gemini'].includes(modelId);
      if (isUserTier && status.source === 'env') {
        return { available: false, source: null };
      }

      // GATING LOGIC: Check subscription for embedded providers
      if (!isUserTier && status.source === 'embedded' && subscriptionStatus !== 'active') {
        return { available: false, source: 'locked' };
      }

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

  function handleConfigure() {
    dispatch('configure');
  }
</script>

<div class="cloud-models-list">
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
      <button class="btn-configure" on:click={handleConfigure}>
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
                    {:else if status.source === 'locked'}
                       <button class="btn-configure-small locked" on:click={handleConfigure}>
                        Unlock
                      </button>
                    {:else if model.tier === 'user'}
                      <button class="btn-configure-small" on:click={handleConfigure}>
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
    </div>
  {/if}
</div>

<style>
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

  .btn-configure-small.locked {
    background: rgba(248, 81, 73, 0.1);
    border-color: var(--error, #f85149);
    color: var(--error, #f85149);
  }

  .btn-configure-small.locked:hover {
    background: rgba(248, 81, 73, 0.2);
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
  
  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border, #30363d);
    color: #ffffff;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #21262d);
  }
</style>
