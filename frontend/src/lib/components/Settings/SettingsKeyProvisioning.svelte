<!--
  SettingsKeyProvisioning.svelte - Key provisioning status and controls

  Features:
  - Shows provisioning status (active, needs refresh, expired)
  - Lists baked-in providers vs user-provided
  - Provision/refresh button
  - License ID input (optional)

  Usage:
    <SettingsKeyProvisioning />
-->
<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Status state
  let provisioningStatus: {
    status: string;
    provisioned_providers: string[];
    missing_providers: string[];
    last_provisioned: string | null;
    next_refresh: string | null;
    offline_days_remaining: number | null;
  } | null = null;

  // Provider categories
  let bakedInProviders: Record<string, string> = {};
  let userProviders: Record<string, string> = {};

  // UI state
  let loading = true;
  let provisioning = false;
  let error = '';
  let successMessage = '';
  let licenseId = '';
  let showLicenseInput = false;

  // Provider display names
  const providerNames: Record<string, string> = {
    deepseek: 'DeepSeek',
    qwen: 'Qwen (Alibaba)',
    mistral: 'Mistral',
    zhipu: 'Zhipu (GLM-4)',
    kimi: 'Kimi (Moonshot)',
    yandex: 'Yandex GPT',
    anthropic: 'Anthropic (Claude)',
    openai: 'OpenAI (GPT-4)',
    google: 'Google (Gemini)',
    xai: 'xAI (Grok)',
  };

  // Status display
  const statusDisplay: Record<string, { label: string; color: string; icon: string }> = {
    active: { label: 'Active', color: '#00ff88', icon: '&#10003;' },
    needs_refresh: { label: 'Needs Refresh', color: '#ffbb00', icon: '&#8635;' },
    offline_grace: { label: 'Offline Mode', color: '#ffbb00', icon: '&#9888;' },
    expired: { label: 'Expired', color: '#ff4444', icon: '&#10007;' },
    not_provisioned: { label: 'Not Set Up', color: '#888888', icon: '&#8226;' },
    error: { label: 'Error', color: '#ff4444', icon: '&#10007;' },
  };

  onMount(() => {
    loadStatus();
    loadProviders();
  });

  async function loadStatus() {
    try {
      const response = await fetch(`${BASE_URL}/keys/status`);
      if (!response.ok) throw new Error('Failed to load status');

      const data = await response.json();
      provisioningStatus = data.provisioning;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load status';
    } finally {
      loading = false;
    }
  }

  async function loadProviders() {
    try {
      const response = await fetch(`${BASE_URL}/keys/providers`);
      if (!response.ok) return;

      const data = await response.json();
      bakedInProviders = data.categories?.baked_in || {};
      userProviders = data.categories?.user_provided || {};
    } catch {
      // Silently fail - not critical
    }
  }

  async function provisionKeys() {
    provisioning = true;
    error = '';
    successMessage = '';

    try {
      const response = await fetch(`${BASE_URL}/keys/provision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          license_id: licenseId || null,
          force_refresh: true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Provisioning failed');
      }

      const data = await response.json();
      const result = data.result;

      if (result.success) {
        successMessage = `Successfully provisioned ${result.providers_provisioned.length} providers`;
        await loadStatus();
        await loadProviders();
      } else {
        error = result.error_message || 'Provisioning failed';
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Provisioning failed';
    } finally {
      provisioning = false;
    }
  }

  function formatDate(isoString: string | null): string {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function getStatusInfo() {
    if (!provisioningStatus) return statusDisplay.not_provisioned;
    return statusDisplay[provisioningStatus.status] || statusDisplay.error;
  }

  function getSourceIcon(source: string): string {
    switch (source) {
      case 'provisioned': return '&#10003;';  // Checkmark
      case 'env': return '&#128273;';  // Key
      case 'none': return '&#10007;';  // X
      default: return '&#8226;';  // Bullet
    }
  }

  function getSourceColor(source: string): string {
    switch (source) {
      case 'provisioned': return '#00ff88';
      case 'env': return '#00d9ff';
      case 'none': return '#666666';
      default: return '#888888';
    }
  }

  function getSourceLabel(source: string): string {
    switch (source) {
      case 'provisioned': return 'Included';
      case 'env': return 'Your Key';
      case 'none': return 'Not Available';
      default: return source;
    }
  }
</script>

<div class="key-provisioning">
  <div class="header">
    <h2>API Key Provisioning</h2>
    <p class="subtitle">
      Writers Factory includes API keys for affordable AI providers.
      Premium providers (Claude, GPT-4) require your own keys.
    </p>
  </div>

  <!-- Status Card -->
  <div class="status-card">
    {#if loading}
      <div class="loading-state">
        <div class="spinner"></div>
        <span>Loading status...</span>
      </div>
    {:else}
      <div class="status-header">
        <div class="status-badge" style="--status-color: {getStatusInfo().color}">
          <span class="status-icon">{@html getStatusInfo().icon}</span>
          <span class="status-label">{getStatusInfo().label}</span>
        </div>

        <button
          class="btn-refresh"
          on:click={provisionKeys}
          disabled={provisioning}
        >
          {#if provisioning}
            <span class="btn-spinner"></span>
            Provisioning...
          {:else}
            <span class="btn-icon">&#8635;</span>
            {provisioningStatus?.status === 'not_provisioned' ? 'Set Up Keys' : 'Refresh Keys'}
          {/if}
        </button>
      </div>

      {#if provisioningStatus}
        <div class="status-details">
          <div class="detail-row">
            <span class="detail-label">Providers Active</span>
            <span class="detail-value">{provisioningStatus.provisioned_providers.length} / 6</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Last Provisioned</span>
            <span class="detail-value">{formatDate(provisioningStatus.last_provisioned)}</span>
          </div>
          {#if provisioningStatus.next_refresh}
            <div class="detail-row">
              <span class="detail-label">Next Refresh</span>
              <span class="detail-value">{formatDate(provisioningStatus.next_refresh)}</span>
            </div>
          {/if}
          {#if provisioningStatus.offline_days_remaining !== null}
            <div class="detail-row warning">
              <span class="detail-label">Offline Grace Period</span>
              <span class="detail-value">{provisioningStatus.offline_days_remaining} days remaining</span>
            </div>
          {/if}
        </div>
      {/if}
    {/if}
  </div>

  <!-- License Input (expandable) -->
  <div class="license-section">
    <button class="license-toggle" on:click={() => showLicenseInput = !showLicenseInput}>
      <span class="toggle-icon">{showLicenseInput ? '&#9660;' : '&#9654;'}</span>
      Have a license key?
    </button>

    {#if showLicenseInput}
      <div class="license-input-wrapper">
        <input
          type="text"
          bind:value={licenseId}
          placeholder="Enter your license key..."
          class="license-input"
        />
        <p class="license-help">
          MVP course participants receive a license key for extended access.
        </p>
      </div>
    {/if}
  </div>

  <!-- Provider Lists -->
  <div class="providers-section">
    <!-- Included Providers -->
    <div class="provider-group">
      <h3>
        <span class="group-icon">&#127873;</span>
        Included Providers
      </h3>
      <p class="group-description">These providers are included at no extra cost</p>

      <div class="provider-list">
        {#each Object.entries(bakedInProviders) as [provider, source]}
          <div class="provider-item">
            <span class="provider-icon" style="color: {getSourceColor(source)}">{@html getSourceIcon(source)}</span>
            <span class="provider-name">{providerNames[provider] || provider}</span>
            <span class="provider-source" style="color: {getSourceColor(source)}">{getSourceLabel(source)}</span>
          </div>
        {/each}
      </div>
    </div>

    <!-- User Providers -->
    <div class="provider-group">
      <h3>
        <span class="group-icon">&#128273;</span>
        Your API Keys
      </h3>
      <p class="group-description">Premium providers require your own API keys</p>

      <div class="provider-list">
        {#each Object.entries(userProviders) as [provider, source]}
          <div class="provider-item">
            <span class="provider-icon" style="color: {getSourceColor(source)}">{@html getSourceIcon(source)}</span>
            <span class="provider-name">{providerNames[provider] || provider}</span>
            <span class="provider-source" style="color: {getSourceColor(source)}">{getSourceLabel(source)}</span>
          </div>
        {/each}
      </div>

      <a href="#settings-agents" class="configure-link">
        Configure your API keys &#8594;
      </a>
    </div>
  </div>

  <!-- Info Box -->
  <div class="info-box">
    <h4>How Key Provisioning Works</h4>
    <ul>
      <li><strong>Included keys</strong> are provided by Writers Factory for affordable providers</li>
      <li>Keys are <strong>encrypted</strong> and stored locally on your machine</li>
      <li>Keys <strong>refresh automatically</strong> every 7 days</li>
      <li><strong>Offline mode</strong> allows 30 days without internet</li>
      <li>Premium providers (Claude, GPT-4) always require your own keys</li>
    </ul>
  </div>

  <!-- Messages -->
  {#if successMessage}
    <div class="message success">{successMessage}</div>
  {/if}
  {#if error}
    <div class="message error">{error}</div>
  {/if}
</div>

<style>
  .key-provisioning {
    padding: 2rem;
    max-width: 800px;
    color: #ffffff;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    color: #b0b0b0;
    margin: 0;
    line-height: 1.5;
  }

  /* Status Card */
  .status-card {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 1rem;
    color: #888;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #404040;
    border-top-color: #00d9ff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .status-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--status-color);
    border-radius: 6px;
    color: var(--status-color);
  }

  .status-icon {
    font-size: 1rem;
  }

  .status-label {
    font-weight: 600;
    font-size: 0.9rem;
  }

  .btn-refresh {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-refresh:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-refresh:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .btn-icon {
    font-size: 1rem;
  }

  .btn-spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(0, 0, 0, 0.2);
    border-top-color: #1a1a1a;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  .status-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding-top: 1rem;
    border-top: 1px solid #404040;
  }

  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.875rem;
  }

  .detail-label {
    color: #888;
  }

  .detail-value {
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
  }

  .detail-row.warning .detail-value {
    color: #ffbb00;
  }

  /* License Section */
  .license-section {
    margin-bottom: 1.5rem;
  }

  .license-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: transparent;
    border: none;
    color: #888;
    font-size: 0.875rem;
    cursor: pointer;
    padding: 0.5rem 0;
    transition: color 0.2s;
  }

  .license-toggle:hover {
    color: #00d9ff;
  }

  .toggle-icon {
    font-size: 0.75rem;
  }

  .license-input-wrapper {
    margin-top: 0.75rem;
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .license-input {
    width: 100%;
    padding: 0.75rem 1rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
  }

  .license-input:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .license-help {
    margin: 0.5rem 0 0 0;
    font-size: 0.75rem;
    color: #888;
  }

  /* Provider Groups */
  .providers-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .provider-group {
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
    padding: 1.25rem;
  }

  .provider-group h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 0.25rem 0;
  }

  .group-icon {
    font-size: 1.125rem;
  }

  .group-description {
    font-size: 0.8rem;
    color: #888;
    margin: 0 0 1rem 0;
  }

  .provider-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .provider-item {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.75rem;
    align-items: center;
    padding: 0.5rem;
    background: #1a1a1a;
    border-radius: 4px;
  }

  .provider-icon {
    font-size: 1rem;
    width: 20px;
    text-align: center;
  }

  .provider-name {
    font-size: 0.875rem;
    color: #ffffff;
  }

  .provider-source {
    font-size: 0.75rem;
    font-weight: 500;
  }

  .configure-link {
    display: inline-block;
    margin-top: 1rem;
    font-size: 0.8rem;
    color: #00d9ff;
    text-decoration: none;
    transition: opacity 0.2s;
  }

  .configure-link:hover {
    opacity: 0.8;
  }

  /* Info Box */
  .info-box {
    background: #1a3a4a20;
    border: 1px solid #00d9ff40;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .info-box h4 {
    font-size: 0.9rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.75rem 0;
  }

  .info-box ul {
    margin: 0;
    padding-left: 1.25rem;
  }

  .info-box li {
    color: #b0b0b0;
    font-size: 0.8rem;
    line-height: 1.6;
    margin-bottom: 0.25rem;
  }

  .info-box li strong {
    color: #ffffff;
  }

  /* Messages */
  .message {
    padding: 0.75rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .message.success {
    background: #00ff8820;
    border: 1px solid #00ff88;
    color: #00ff88;
  }

  .message.error {
    background: #ff444420;
    border: 1px solid #ff4444;
    color: #ff4444;
  }

  /* Responsive */
  @media (max-width: 640px) {
    .key-provisioning {
      padding: 1rem;
    }

    .status-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .btn-refresh {
      width: 100%;
      justify-content: center;
    }

    .providers-section {
      grid-template-columns: 1fr;
    }
  }
</style>
