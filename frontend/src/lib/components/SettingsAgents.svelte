<!--
  SettingsAgents.svelte - API Key Configuration

  P0 CRITICAL: This component unblocks all cloud AI features.
  Without API keys configured, users cannot:
  - Run voice calibration tournaments
  - Use cloud models for scene generation
  - Enable premium quality tier
  - Access Graph Health with optimal models

  Supported Providers:
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Anthropic (Claude 3.5 Sonnet)
  - DeepSeek (DeepSeek V3)
  - Qwen (Qwen Plus, Qwen Turbo)
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';

  // API Key configuration
  let providers = [
    {
      id: 'openai',
      name: 'OpenAI',
      envVar: 'OPENAI_API_KEY',
      models: ['GPT-4o', 'GPT-4o-mini'],
      placeholder: 'sk-...',
      docsUrl: 'https://platform.openai.com/api-keys',
      value: '',
      status: 'unknown',  // unknown, valid, invalid, checking
      visible: false
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      envVar: 'ANTHROPIC_API_KEY',
      models: ['Claude 3.5 Sonnet'],
      placeholder: 'sk-ant-...',
      docsUrl: 'https://console.anthropic.com/settings/keys',
      value: '',
      status: 'unknown',
      visible: false
    },
    {
      id: 'deepseek',
      name: 'DeepSeek',
      envVar: 'DEEPSEEK_API_KEY',
      models: ['DeepSeek V3'],
      placeholder: 'sk-...',
      docsUrl: 'https://platform.deepseek.com/api_keys',
      value: '',
      status: 'unknown',
      visible: false
    },
    {
      id: 'qwen',
      name: 'Alibaba Qwen',
      envVar: 'QWEN_API_KEY',
      models: ['Qwen Plus', 'Qwen Turbo'],
      placeholder: 'sk-...',
      docsUrl: 'https://dashscope.console.aliyun.com/apiKey',
      value: '',
      status: 'unknown',
      visible: false
    },
  ];

  let isLoading = true;
  let isSaving = false;
  let availableProviders = {};
  let hasChanges = false;

  onMount(async () => {
    await loadApiKeyStatus();
  });

  async function loadApiKeyStatus() {
    isLoading = true;
    try {
      // Get available providers from orchestrator
      const caps = await apiClient.getModelCapabilities();
      availableProviders = caps.available_providers || {};

      // Update provider status based on backend detection
      providers = providers.map(p => ({
        ...p,
        status: availableProviders[p.id] ? 'valid' : 'unknown'
      }));
    } catch (e) {
      console.error('Failed to load API key status:', e);
      addToast({ type: 'error', message: 'Failed to load API key status' });
    } finally {
      isLoading = false;
    }
  }

  function toggleVisibility(providerId) {
    providers = providers.map(p =>
      p.id === providerId ? { ...p, visible: !p.visible } : p
    );
  }

  function handleInput(providerId, value) {
    providers = providers.map(p =>
      p.id === providerId ? { ...p, value, status: value ? 'unknown' : 'unknown' } : p
    );
    hasChanges = true;
  }

  async function saveApiKey(provider) {
    if (!provider.value.trim()) {
      addToast({ type: 'warning', message: 'Please enter an API key' });
      return;
    }

    isSaving = true;
    try {
      // Save to settings
      await apiClient.setSetting(`agents.${provider.id}_api_key`, provider.value);

      // Update status
      providers = providers.map(p =>
        p.id === provider.id ? { ...p, status: 'valid' } : p
      );

      addToast({ type: 'success', message: `${provider.name} API key saved!` });
      hasChanges = false;

      // Refresh capabilities to verify
      await loadApiKeyStatus();
    } catch (e) {
      console.error('Failed to save API key:', e);
      providers = providers.map(p =>
        p.id === provider.id ? { ...p, status: 'invalid' } : p
      );
      addToast({ type: 'error', message: `Failed to save ${provider.name} API key` });
    } finally {
      isSaving = false;
    }
  }

  async function testConnection(provider) {
    providers = providers.map(p =>
      p.id === provider.id ? { ...p, status: 'checking' } : p
    );

    try {
      // Use orchestrator to test the connection
      const caps = await apiClient.getModelCapabilities();
      const isAvailable = caps.available_providers[provider.id] || false;

      providers = providers.map(p =>
        p.id === provider.id ? { ...p, status: isAvailable ? 'valid' : 'invalid' } : p
      );

      if (isAvailable) {
        addToast({ type: 'success', message: `${provider.name} connection verified!` });
      } else {
        addToast({ type: 'error', message: `${provider.name} key not detected. Save the key and restart backend.` });
      }
    } catch (e) {
      providers = providers.map(p =>
        p.id === provider.id ? { ...p, status: 'invalid' } : p
      );
      addToast({ type: 'error', message: `Failed to test ${provider.name} connection` });
    }
  }

  // Status indicator colors
  function getStatusColor(status) {
    switch (status) {
      case 'valid': return 'var(--success, #3fb950)';
      case 'invalid': return 'var(--error, #f85149)';
      case 'checking': return 'var(--warning, #d29922)';
      default: return 'var(--text-muted, #6e7681)';
    }
  }

  function getStatusLabel(status) {
    switch (status) {
      case 'valid': return 'Connected';
      case 'invalid': return 'Invalid';
      case 'checking': return 'Checking...';
      default: return 'Not configured';
    }
  }
</script>

<div class="settings-agents">
  <header class="section-header">
    <h2>API Keys</h2>
    <p class="section-description">
      Configure API keys to enable cloud AI models. At least one key is required for Voice Calibration and Premium features.
    </p>
  </header>

  {#if isLoading}
    <div class="loading-state">
      <div class="spinner"></div>
      <span>Loading API key status...</span>
    </div>
  {:else}
    <div class="providers-list">
      {#each providers as provider}
        <div class="provider-card">
          <div class="provider-header">
            <div class="provider-info">
              <h3 class="provider-name">{provider.name}</h3>
              <div class="provider-models">
                {#each provider.models as model}
                  <span class="model-badge">{model}</span>
                {/each}
              </div>
            </div>
            <div class="provider-status">
              <span
                class="status-dot"
                style="background: {getStatusColor(provider.status)}"
              ></span>
              <span class="status-label">{getStatusLabel(provider.status)}</span>
            </div>
          </div>

          <div class="api-key-input">
            <div class="input-wrapper">
              <input
                type={provider.visible ? 'text' : 'password'}
                placeholder={provider.placeholder}
                value={provider.value}
                on:input={(e) => handleInput(provider.id, e.target.value)}
                class="key-input"
              />
              <button
                class="toggle-visibility"
                on:click={() => toggleVisibility(provider.id)}
                title={provider.visible ? 'Hide' : 'Show'}
              >
                {#if provider.visible}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                {:else}
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                {/if}
              </button>
            </div>

            <div class="input-actions">
              <button
                class="btn btn-secondary"
                on:click={() => testConnection(provider)}
                disabled={provider.status === 'checking'}
              >
                Test
              </button>
              <button
                class="btn btn-primary"
                on:click={() => saveApiKey(provider)}
                disabled={isSaving || !provider.value.trim()}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>

          <div class="provider-footer">
            <a href={provider.docsUrl} target="_blank" rel="noopener noreferrer" class="docs-link">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                <polyline points="15 3 21 3 21 9"></polyline>
                <line x1="10" y1="14" x2="21" y2="3"></line>
              </svg>
              Get API Key
            </a>
            <span class="env-var">ENV: {provider.envVar}</span>
          </div>
        </div>
      {/each}
    </div>

    <div class="info-box">
      <div class="info-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      </div>
      <div class="info-content">
        <h4>Environment Variables</h4>
        <p>
          API keys can also be set via environment variables. The backend will automatically detect
          keys set in your environment. Restart the backend after setting environment variables.
        </p>
      </div>
    </div>
  {/if}
</div>

<style>
  .settings-agents {
    max-width: 700px;
  }

  .section-header {
    margin-bottom: var(--space-6, 24px);
  }

  .section-header h2 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .section-description {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }

  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3, 12px);
    padding: var(--space-8, 32px);
    color: var(--text-secondary, #8b949e);
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .providers-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  .provider-card {
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    padding: var(--space-4, 16px);
  }

  .provider-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: var(--space-3, 12px);
  }

  .provider-name {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .provider-models {
    display: flex;
    gap: var(--space-1, 4px);
    flex-wrap: wrap;
  }

  .model-badge {
    padding: 2px 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .provider-status {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .api-key-input {
    display: flex;
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-3, 12px);
  }

  .input-wrapper {
    flex: 1;
    position: relative;
  }

  .key-input {
    width: 100%;
    padding: var(--space-2, 8px) var(--space-10, 40px) var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-mono, monospace);
    font-size: var(--text-sm, 12px);
  }

  .key-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
    box-shadow: 0 0 0 2px var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
  }

  .key-input::placeholder {
    color: var(--text-muted, #6e7681);
  }

  .toggle-visibility {
    position: absolute;
    right: var(--space-2, 8px);
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .toggle-visibility:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .input-actions {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .btn {
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--bg-elevated, #2d3640);
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .btn-primary {
    background: var(--accent-cyan, #58a6ff);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--accent-cyan-hover, #79b8ff);
  }

  .provider-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--space-3, 12px);
    border-top: 1px solid var(--border-subtle, #21262d);
  }

  .docs-link {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--accent-cyan, #58a6ff);
    text-decoration: none;
    transition: color var(--transition-fast, 100ms ease);
  }

  .docs-link:hover {
    color: var(--accent-cyan-hover, #79b8ff);
  }

  .env-var {
    font-family: var(--font-mono, monospace);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .info-box {
    display: flex;
    gap: var(--space-3, 12px);
    margin-top: var(--space-6, 24px);
    padding: var(--space-4, 16px);
    background: var(--info-muted, rgba(88, 166, 255, 0.15));
    border: 1px solid var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-radius: var(--radius-md, 6px);
  }

  .info-icon {
    flex-shrink: 0;
    color: var(--accent-cyan, #58a6ff);
  }

  .info-content h4 {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .info-content p {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }
</style>
