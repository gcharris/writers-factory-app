<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Props
  export let keyStatus: any = null;

  // Premium providers
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

  // State
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

  // Subscription State
  let subscriptionCode = '';
  let subscriptionStatus: 'none' | 'active' | 'invalid' = 'none';

  onMount(() => {
    // Load subscription status
    const savedStatus = localStorage.getItem('writers_factory_subscription');
    if (savedStatus === 'active') {
      subscriptionStatus = 'active';
      subscriptionCode = 'skoltech2026'; // Pre-fill for UX
    }
  });

  function checkSubscription() {
    if (subscriptionCode.trim() === 'skoltech2026') {
      subscriptionStatus = 'active';
      localStorage.setItem('writers_factory_subscription', 'active');
      // In a real app, we would save this to the backend
    } else {
      subscriptionStatus = 'invalid';
    }
  }

  function getModelStatus(modelId: string): { available: boolean; source: string | null } {
    if (!keyStatus) return { available: false, source: null };

    const status = keyStatus.providers[modelId];
    if (status) {
      // HACK: For the Desktop App MVP, we want to pretend .env keys don't exist for premium providers
      // so the user sees the "Configure" flow.
      const isUserTier = premiumProviders.some(p => p.id === modelId);
      if (isUserTier && status.source === 'env') {
        return { available: false, source: null };
      }

      return { available: status.available, source: status.source };
    }
    return { available: false, source: null };
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
        dispatch('saved');
        saveMessage = 'Keys saved successfully!';
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

  function openDocs(url: string, event: Event) {
    event.preventDefault();
    window.open(url, '_blank');
  }

  function handleCancel() {
    dispatch('cancel');
  }
</script>

<div class="premium-key-form">
  <div class="modal-header">
    <h3>Key Configuration</h3>
    <button class="modal-close" on:click={handleCancel}>×</button>
  </div>

  <div class="modal-body">
    <!-- Subscription Section -->
    <div class="subscription-section">
      <h4>Writers Factory Subscription</h4>
      <p class="sub-desc">If your subscription includes free keys, enter your code here.</p>
      
      <div class="sub-input-row">
        <input 
          type="text" 
          bind:value={subscriptionCode} 
          placeholder="Enter subscription code"
          class="sub-input"
          disabled={subscriptionStatus === 'active'}
        />
        <button 
          class="btn-apply {subscriptionStatus === 'active' ? 'success' : ''}" 
          on:click={checkSubscription}
          disabled={subscriptionStatus === 'active'}
        >
          {subscriptionStatus === 'active' ? 'Active' : 'Apply'}
        </button>
      </div>
      
      {#if subscriptionStatus === 'active'}
        <div class="sub-message success">
          ✓ Subscription active! Free keys enabled.
        </div>
      {:else if subscriptionStatus === 'invalid'}
        <div class="sub-message error">
          Invalid code. Please try again.
        </div>
      {/if}
    </div>

    <div class="divider"></div>

    <h4>Configure Premium API Keys</h4>
    <p class="modal-intro">
      Enter your own API keys for premium providers. These are optional - you only pay for tokens you use.
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
    <button class="btn-secondary" on:click={handleCancel}>Cancel</button>
    <button class="btn-primary" on:click={saveApiKeys} disabled={savingKeys}>
      {savingKeys ? 'Saving...' : 'Save Keys'}
    </button>
  </div>
</div>

<style>
  .premium-key-form {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 100%;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid var(--border, #30363d);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    color: #ffffff;
  }

  .modal-close {
    background: none;
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
    flex: 1;
  }

  .modal-intro {
    color: var(--text-secondary, #8b949e);
    margin: 0 0 1.5rem 0;
    font-size: 0.9rem;
  }

  .key-inputs {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .key-input-card {
    background: var(--bg-primary, #0d1117);
    border: 1px solid var(--border, #30363d);
    border-radius: 8px;
    padding: 1rem;
    transition: border-color 0.2s;
  }

  .key-input-card.configured {
    border-color: var(--success, #238636);
  }

  .key-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .key-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 1rem;
  }

  .key-badge {
    font-size: 0.7rem;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .key-badge.configured {
    background: rgba(35, 134, 54, 0.2);
    color: var(--success, #3fb950);
  }

  .key-desc {
    font-size: 0.8rem;
    color: var(--text-secondary, #8b949e);
    margin: 0 0 1rem 0;
  }

  .input-row {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }

  .key-input {
    flex: 1;
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border, #30363d);
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    color: #ffffff;
    font-family: monospace;
    font-size: 0.9rem;
  }

  .key-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #00d9ff);
  }

  .btn-toggle-vis {
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border, #30363d);
    color: var(--text-secondary, #8b949e);
    padding: 0 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
  }

  .btn-toggle-vis:hover {
    border-color: var(--text-secondary, #8b949e);
    color: #ffffff;
  }

  .btn-link {
    background: none;
    border: none;
    color: var(--accent-cyan, #00d9ff);
    font-size: 0.8rem;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .btn-link:hover {
    text-decoration: underline;
  }

  .save-message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 6px;
    font-size: 0.9rem;
    text-align: center;
  }

  .save-message.success {
    background: rgba(35, 134, 54, 0.2);
    color: var(--success, #3fb950);
  }

  .save-message.error {
    background: rgba(248, 81, 73, 0.2);
    color: var(--error, #f85149);
  }

  .modal-footer {
    padding: 1.25rem 1.5rem;
    border-top: 1px solid var(--border, #30363d);
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  .btn-primary {
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    padding: 0.5rem 1.5rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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

  /* Subscription Section */
  .subscription-section {
    background: var(--bg-primary, #0d1117);
    border: 1px solid var(--border, #30363d);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1.5rem;
  }

  .subscription-section h4 {
    margin: 0 0 0.5rem 0;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
  }

  .modal-body h4 {
    margin: 0 0 0.5rem 0;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 600;
  }

  .sub-desc {
    font-size: 0.85rem;
    color: var(--text-secondary, #8b949e);
    margin: 0 0 1rem 0;
  }

  .sub-input-row {
    display: flex;
    gap: 0.5rem;
  }

  .sub-input {
    flex: 1;
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border, #30363d);
    border-radius: 6px;
    padding: 0.5rem 0.75rem;
    color: #ffffff;
    font-size: 0.9rem;
  }

  .sub-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #00d9ff);
  }

  .btn-apply {
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    padding: 0 1rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-apply:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-apply.success {
    background: var(--success, #238636);
    color: #ffffff;
    cursor: default;
  }

  .btn-apply:disabled:not(.success) {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .sub-message {
    margin-top: 0.75rem;
    font-size: 0.85rem;
    font-weight: 500;
  }

  .sub-message.success {
    color: var(--success, #3fb950);
  }

  .sub-message.error {
    color: var(--error, #f85149);
  }

  .divider {
    height: 1px;
    background: var(--border, #30363d);
    margin: 1.5rem 0;
  }
</style>
