<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Provider configuration - easily extensible
  const providers = [
    {
      id: 'deepseek',
      name: 'DeepSeek V3',
      tier: 'recommended',
      tierLabel: 'RECOMMENDED',
      description: 'Best value - $0.27/$1.10 per 1M tokens. Excellent quality.',
      placeholder: 'sk-...',
      docsUrl: 'https://platform.deepseek.com/api_keys',
      docsLabel: 'DeepSeek Platform',
      envVar: 'DEEPSEEK_API_KEY'
    },
    {
      id: 'openai',
      name: 'OpenAI (GPT-4o)',
      tier: 'premium',
      tierLabel: 'PREMIUM',
      description: 'High quality - $2.50/$10 per 1M tokens. Best for creative tasks.',
      placeholder: 'sk-...',
      docsUrl: 'https://platform.openai.com/api-keys',
      docsLabel: 'OpenAI Platform',
      envVar: 'OPENAI_API_KEY'
    },
    {
      id: 'anthropic',
      name: 'Anthropic (Claude)',
      tier: 'premium',
      tierLabel: 'PREMIUM',
      description: 'High quality - $3/$15 per 1M tokens. Best for narrative analysis.',
      placeholder: 'sk-ant-...',
      docsUrl: 'https://console.anthropic.com/settings/keys',
      docsLabel: 'Anthropic Console',
      envVar: 'ANTHROPIC_API_KEY'
    },
    {
      id: 'google',
      name: 'Google Gemini',
      tier: 'balanced',
      tierLabel: 'BALANCED',
      description: 'Good value - $0.075/$0.30 per 1M tokens. Fast and capable.',
      placeholder: 'AIza...',
      docsUrl: 'https://aistudio.google.com/apikey',
      docsLabel: 'Google AI Studio',
      envVar: 'GOOGLE_API_KEY'
    },
    {
      id: 'qwen',
      name: 'Alibaba Qwen',
      tier: 'budget',
      tierLabel: 'BUDGET',
      description: 'Low cost - $0.40/$1.20 per 1M tokens. Good for coordination.',
      placeholder: 'sk-...',
      docsUrl: 'https://dashscope.console.aliyun.com/apiKey',
      docsLabel: 'Qwen DashScope',
      envVar: 'QWEN_API_KEY'
    },
    {
      id: 'xai',
      name: 'xAI (Grok)',
      tier: 'premium',
      tierLabel: 'PREMIUM',
      description: 'Premium tier - Real-time knowledge. Great for research.',
      placeholder: 'xai-...',
      docsUrl: 'https://console.x.ai',
      docsLabel: 'xAI Console',
      envVar: 'XAI_API_KEY'
    },
    {
      id: 'mistral',
      name: 'Mistral API',
      tier: 'balanced',
      tierLabel: 'BALANCED',
      description: 'European provider - Good quality at reasonable cost.',
      placeholder: '...',
      docsUrl: 'https://console.mistral.ai/api-keys',
      docsLabel: 'Mistral Console',
      envVar: 'MISTRAL_API_KEY'
    }
  ];

  type ProviderId = 'deepseek' | 'openai' | 'anthropic' | 'google' | 'qwen' | 'xai' | 'mistral';

  // State for all providers
  let apiKeys: Record<ProviderId, string> = {
    deepseek: '', openai: '', anthropic: '', google: '', qwen: '', xai: '', mistral: ''
  };
  let savedKeys: Record<ProviderId, boolean> = {
    deepseek: false, openai: false, anthropic: false, google: false, qwen: false, xai: false, mistral: false
  };
  let testingKeys: Record<ProviderId, boolean> = {
    deepseek: false, openai: false, anthropic: false, google: false, qwen: false, xai: false, mistral: false
  };
  let testResults: Record<ProviderId, boolean | null> = {
    deepseek: null, openai: null, anthropic: null, google: null, qwen: null, xai: null, mistral: null
  };
  let showKeys: Record<ProviderId, boolean> = {
    deepseek: false, openai: false, anthropic: false, google: false, qwen: false, xai: false, mistral: false
  };

  let saveMessage = '';
  let isSaving = false;
  let showAllProviders = false;

  // Count configured keys
  $: configuredCount = Object.values(savedKeys).filter(Boolean).length;

  onMount(async () => {
    await loadApiKeys();
  });

  async function loadApiKeys() {
    try {
      const response = await fetch(`${BASE_URL}/settings/category/agents`);
      if (response.ok) {
        const data = await response.json();

        for (const provider of providers) {
          const keyName = `${provider.id}_api_key`;
          if (data[keyName]) {
            savedKeys[provider.id as ProviderId] = true;
            apiKeys[provider.id as ProviderId] = data[keyName] === '***' ? '' : data[keyName];
          }
        }
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  }

  async function saveApiKeys() {
    isSaving = true;
    saveMessage = '';

    try {
      const keysToSave: Record<string, string> = {};

      for (const provider of providers) {
        const key = apiKeys[provider.id as ProviderId];
        if (key) {
          keysToSave[`${provider.id}_api_key`] = key;
        }
      }

      const response = await fetch(`${BASE_URL}/settings/category/agents`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(keysToSave)
      });

      if (response.ok) {
        saveMessage = 'API keys saved successfully';

        for (const provider of providers) {
          savedKeys[provider.id as ProviderId] = !!apiKeys[provider.id as ProviderId];
        }

        setTimeout(() => { saveMessage = ''; }, 3000);
      } else {
        saveMessage = 'Failed to save API keys';
      }
    } catch (error) {
      console.error('Failed to save API keys:', error);
      saveMessage = 'Error saving API keys';
    } finally {
      isSaving = false;
    }
  }

  async function testApiKey(providerId: ProviderId) {
    testingKeys[providerId] = true;
    testResults[providerId] = null;

    try {
      const key = apiKeys[providerId];

      if (!key || key.trim() === '') {
        testResults[providerId] = false;
        testingKeys[providerId] = false;
        return;
      }

      const response = await fetch(`${BASE_URL}/api-keys/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: providerId,
          api_key: key
        })
      });

      if (response.ok) {
        const result = await response.json();
        testResults[providerId] = result.valid;

        if (!result.valid && result.error) {
          console.error(`${providerId} API key test failed:`, result.error);
        }
      } else {
        testResults[providerId] = false;
      }
    } catch (error) {
      console.error(`Failed to test ${providerId} API key:`, error);
      testResults[providerId] = false;
    } finally {
      testingKeys[providerId] = false;
    }
  }

  async function deleteApiKey(providerId: ProviderId) {
    if (!confirm(`Delete ${providerId} API key?`)) return;

    apiKeys[providerId] = '';
    savedKeys[providerId] = false;
    testResults[providerId] = null;

    await saveApiKeys();
  }

  function toggleShowKey(providerId: ProviderId) {
    showKeys[providerId] = !showKeys[providerId];
  }

  function getTierClass(tier: string): string {
    switch (tier) {
      case 'recommended': return 'tier-recommended';
      case 'premium': return 'tier-premium';
      case 'balanced': return 'tier-balanced';
      case 'budget': return 'tier-budget';
      default: return '';
    }
  }

  // Show primary providers by default, others in "More Providers" section
  $: primaryProviders = providers.slice(0, 4);
  $: additionalProviders = providers.slice(4);
</script>

<div class="settings-agents">
  <div class="header">
    <h2>API Keys & Providers</h2>
    <p class="description">
      Configure AI provider API keys. <strong>DeepSeek is recommended</strong> as the default - excellent quality at low cost.
    </p>
    <div class="status-bar">
      <span class="status-label">Configured:</span>
      <span class="status-count {configuredCount > 0 ? 'has-keys' : 'no-keys'}">
        {configuredCount} of {providers.length} providers
      </span>
    </div>
  </div>

  <!-- Primary Providers -->
  <div class="api-keys-grid">
    {#each primaryProviders as provider}
      <div class="api-key-card {provider.tier === 'recommended' ? 'recommended' : ''}">
        <div class="card-header">
          <div class="provider-info">
            <h3>{provider.name}</h3>
            <span class="tier-badge {getTierClass(provider.tier)}">{provider.tierLabel}</span>
          </div>
          {#if savedKeys[provider.id as ProviderId]}
            <span class="badge badge-success">Configured</span>
          {:else}
            <span class="badge badge-warning">Not set</span>
          {/if}
        </div>

        <p class="provider-desc">{provider.description}</p>

        <div class="key-input-group">
          <div class="input-wrapper">
            <input
              type={showKeys[provider.id as ProviderId] ? 'text' : 'password'}
              bind:value={apiKeys[provider.id as ProviderId]}
              placeholder={provider.placeholder}
              class="key-input"
            />
            <button
              type="button"
              class="toggle-visibility"
              on:click={() => toggleShowKey(provider.id as ProviderId)}
              title={showKeys[provider.id as ProviderId] ? 'Hide' : 'Show'}
            >
              {showKeys[provider.id as ProviderId] ? 'Hide' : 'Show'}
            </button>
          </div>

          <div class="button-group">
            <button
              type="button"
              class="btn-test"
              on:click={() => testApiKey(provider.id as ProviderId)}
              disabled={!apiKeys[provider.id as ProviderId] || testingKeys[provider.id as ProviderId]}
            >
              {testingKeys[provider.id as ProviderId] ? 'Testing...' : 'Test'}
            </button>

            {#if savedKeys[provider.id as ProviderId]}
              <button
                type="button"
                class="btn-delete"
                on:click={() => deleteApiKey(provider.id as ProviderId)}
              >
                Delete
              </button>
            {/if}
          </div>
        </div>

        {#if testResults[provider.id as ProviderId] !== null}
          <div class="test-result {testResults[provider.id as ProviderId] ? 'success' : 'error'}">
            {testResults[provider.id as ProviderId] ? 'Connection successful' : 'Connection failed'}
          </div>
        {/if}

        <p class="help-text">
          Get key from <a href={provider.docsUrl} target="_blank">{provider.docsLabel}</a>
          <span class="env-var">ENV: {provider.envVar}</span>
        </p>
      </div>
    {/each}
  </div>

  <!-- Additional Providers (Expandable) -->
  <div class="additional-section">
    <button class="toggle-additional" on:click={() => showAllProviders = !showAllProviders}>
      <span>{showAllProviders ? '&#9660;' : '&#9654;'} More Providers ({additionalProviders.length})</span>
    </button>

    {#if showAllProviders}
      <div class="api-keys-grid additional">
        {#each additionalProviders as provider}
          <div class="api-key-card">
            <div class="card-header">
              <div class="provider-info">
                <h3>{provider.name}</h3>
                <span class="tier-badge {getTierClass(provider.tier)}">{provider.tierLabel}</span>
              </div>
              {#if savedKeys[provider.id as ProviderId]}
                <span class="badge badge-success">Configured</span>
              {:else}
                <span class="badge badge-warning">Not set</span>
              {/if}
            </div>

            <p class="provider-desc">{provider.description}</p>

            <div class="key-input-group">
              <div class="input-wrapper">
                <input
                  type={showKeys[provider.id as ProviderId] ? 'text' : 'password'}
                  bind:value={apiKeys[provider.id as ProviderId]}
                  placeholder={provider.placeholder}
                  class="key-input"
                />
                <button
                  type="button"
                  class="toggle-visibility"
                  on:click={() => toggleShowKey(provider.id as ProviderId)}
                >
                  {showKeys[provider.id as ProviderId] ? 'Hide' : 'Show'}
                </button>
              </div>

              <div class="button-group">
                <button
                  type="button"
                  class="btn-test"
                  on:click={() => testApiKey(provider.id as ProviderId)}
                  disabled={!apiKeys[provider.id as ProviderId] || testingKeys[provider.id as ProviderId]}
                >
                  {testingKeys[provider.id as ProviderId] ? 'Testing...' : 'Test'}
                </button>

                {#if savedKeys[provider.id as ProviderId]}
                  <button
                    type="button"
                    class="btn-delete"
                    on:click={() => deleteApiKey(provider.id as ProviderId)}
                  >
                    Delete
                  </button>
                {/if}
              </div>
            </div>

            {#if testResults[provider.id as ProviderId] !== null}
              <div class="test-result {testResults[provider.id as ProviderId] ? 'success' : 'error'}">
                {testResults[provider.id as ProviderId] ? 'Connection successful' : 'Connection failed'}
              </div>
            {/if}

            <p class="help-text">
              Get key from <a href={provider.docsUrl} target="_blank">{provider.docsLabel}</a>
            </p>
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Save button -->
  <div class="actions">
    <button
      type="button"
      class="btn-save"
      on:click={saveApiKeys}
      disabled={isSaving}
    >
      {isSaving ? 'Saving...' : 'Save All API Keys'}
    </button>

    {#if saveMessage}
      <div class="save-message {saveMessage.includes('successfully') ? 'success' : 'error'}">
        {saveMessage}
      </div>
    {/if}
  </div>

  <!-- Info panel -->
  <div class="info-panel">
    <h4>Which keys do I need?</h4>
    <ul>
      <li><strong>Quick Start</strong>: Just DeepSeek - excellent quality at $0.27/$1.10 per 1M tokens</li>
      <li><strong>Balanced</strong>: DeepSeek + Google Gemini for variety</li>
      <li><strong>Premium</strong>: Add OpenAI or Anthropic for best-in-class quality</li>
      <li><strong>Offline</strong>: No keys needed - uses local Ollama models (free)</li>
    </ul>

    <div class="cost-note">
      <strong>Typical cost</strong>: $0.50-1/month for most writers (Balanced tier)
    </div>
  </div>
</div>

<style>
  .settings-agents {
    padding: 2rem;
    max-width: 1200px;
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

  .description {
    color: #b0b0b0;
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0 0 1rem 0;
  }

  .status-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #1a1a1a;
    border-radius: 4px;
    width: fit-content;
  }

  .status-label {
    color: #888888;
    font-size: 0.875rem;
  }

  .status-count {
    font-weight: 600;
    font-size: 0.875rem;
  }

  .status-count.has-keys {
    color: #00ff88;
  }

  .status-count.no-keys {
    color: #ffb000;
  }

  .api-keys-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .api-key-card {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 1.25rem;
    transition: border-color 0.2s;
  }

  .api-key-card.recommended {
    border-color: #00d9ff;
    background: linear-gradient(135deg, #2d2d2d 0%, #1a3a4a40 100%);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.5rem;
  }

  .provider-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .provider-info h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0;
  }

  .tier-badge {
    font-size: 0.6rem;
    padding: 0.15rem 0.4rem;
    border-radius: 3px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .tier-recommended {
    background: #00d9ff;
    color: #1a1a1a;
  }

  .tier-premium {
    background: #ffb000;
    color: #1a1a1a;
  }

  .tier-balanced {
    background: #00ff88;
    color: #1a1a1a;
  }

  .tier-budget {
    background: #888888;
    color: #1a1a1a;
  }

  .provider-desc {
    font-size: 0.75rem;
    color: #888888;
    margin: 0 0 1rem 0;
    line-height: 1.4;
  }

  .badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-weight: 500;
    white-space: nowrap;
  }

  .badge-success {
    background: #00ff8820;
    color: #00ff88;
  }

  .badge-warning {
    background: #ffb00020;
    color: #ffb000;
  }

  .key-input-group {
    margin-bottom: 0.75rem;
  }

  .input-wrapper {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .key-input {
    flex: 1;
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 0.5rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
  }

  .key-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .toggle-visibility {
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #888888;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.75rem;
    transition: all 0.2s;
  }

  .toggle-visibility:hover {
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .button-group {
    display: flex;
    gap: 0.5rem;
  }

  .btn-test, .btn-delete {
    padding: 0.4rem 0.75rem;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-test {
    background: #00d9ff20;
    border: 1px solid #00d9ff;
    color: #00d9ff;
  }

  .btn-test:hover:not(:disabled) {
    background: #00d9ff40;
  }

  .btn-test:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-delete {
    background: #ff336620;
    border: 1px solid #ff3366;
    color: #ff3366;
  }

  .btn-delete:hover {
    background: #ff336640;
  }

  .test-result {
    font-size: 0.8rem;
    padding: 0.4rem 0.75rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
  }

  .test-result.success {
    background: #00ff8820;
    color: #00ff88;
  }

  .test-result.error {
    background: #ff336620;
    color: #ff3366;
  }

  .help-text {
    font-size: 0.7rem;
    color: #666666;
    margin: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .help-text a {
    color: #00d9ff;
    text-decoration: none;
  }

  .help-text a:hover {
    text-decoration: underline;
  }

  .env-var {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #555555;
  }

  /* Additional providers section */
  .additional-section {
    margin-bottom: 2rem;
  }

  .toggle-additional {
    width: 100%;
    padding: 0.75rem 1rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #00d9ff;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
    margin-bottom: 1rem;
  }

  .toggle-additional:hover {
    background: #252525;
    border-color: #00d9ff;
  }

  .api-keys-grid.additional {
    margin-bottom: 0;
  }

  /* Actions */
  .actions {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .btn-save {
    background: #00d9ff;
    border: none;
    color: #1a1a1a;
    padding: 0.75rem 2rem;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-save:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .save-message {
    font-size: 0.875rem;
    font-weight: 500;
  }

  .save-message.success {
    color: #00ff88;
  }

  .save-message.error {
    color: #ff3366;
  }

  /* Info panel */
  .info-panel {
    padding: 1.5rem;
    background: #1a3a4a20;
    border: 1px solid #00d9ff40;
    border-radius: 8px;
  }

  .info-panel h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.75rem 0;
  }

  .info-panel ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem 0;
  }

  .info-panel li {
    color: #b0b0b0;
    font-size: 0.875rem;
    line-height: 1.8;
    padding-left: 1rem;
    position: relative;
  }

  .info-panel li::before {
    content: ">";
    position: absolute;
    left: 0;
    color: #00d9ff;
  }

  .info-panel li strong {
    color: #ffffff;
  }

  .cost-note {
    color: #b0b0b0;
    font-size: 0.875rem;
    padding-top: 1rem;
    border-top: 1px solid #404040;
  }

  .cost-note strong {
    color: #00d9ff;
  }
</style>
