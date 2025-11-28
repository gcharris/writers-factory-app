<!--
  Step1LocalAI.svelte - Local AI Setup Step

  Purpose: Ensure every user has a working local AI before anything else.
  - Scans hardware capabilities
  - Checks Ollama installation
  - Helps install recommended local models
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { HardwareInfo } from '$lib/api_client';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // State
  let hardwareInfo: HardwareInfo | null = null;
  let scanning = true;
  let error = '';

  // Model installation state
  let installingModel = '';
  let installProgress = 0;
  let installError = '';

  // Recommended models based on RAM
  const modelRecommendations = {
    low: { id: 'llama3.2:3b', name: 'Llama 3.2 (3B)', description: 'Fast, lightweight - good for low-end systems', size: '2GB' },
    medium: { id: 'mistral:7b', name: 'Mistral 7B', description: 'Balanced quality and speed', size: '4GB' },
    high: { id: 'deepseek-r1:7b', name: 'DeepSeek R1 (7B)', description: 'High quality reasoning', size: '4.5GB' }
  };

  $: recommendedModel = getRecommendedModel(hardwareInfo);
  $: isReady = hardwareInfo?.ollama_installed && hardwareInfo.ollama_models.length > 0;

  onMount(async () => {
    await scanHardware();
  });

  async function scanHardware() {
    scanning = true;
    error = '';

    try {
      // Minimum delay for UX
      const [response] = await Promise.all([
        fetch(`${BASE_URL}/system/hardware`),
        new Promise(resolve => setTimeout(resolve, 1000))
      ]);

      if (!response.ok) {
        throw new Error('Failed to detect hardware');
      }

      hardwareInfo = await response.json();
      dispatch('complete', { complete: isReady });
    } catch (e) {
      error = e instanceof Error ? e.message : 'Hardware detection failed';
    } finally {
      scanning = false;
    }
  }

  function getRecommendedModel(info: HardwareInfo | null) {
    if (!info) return modelRecommendations.low;

    if (info.ram_gb >= 16) {
      return modelRecommendations.high;
    } else if (info.ram_gb >= 8) {
      return modelRecommendations.medium;
    }
    return modelRecommendations.low;
  }

  async function installModel(modelId: string) {
    installingModel = modelId;
    installProgress = 0;
    installError = '';

    try {
      // Start the model pull
      const response = await fetch(`${BASE_URL}/system/ollama/pull`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: modelId })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start model download');
      }

      // Poll for progress
      const pollProgress = async () => {
        try {
          const statusResp = await fetch(`${BASE_URL}/system/ollama/pull-status?model=${modelId}`);
          if (statusResp.ok) {
            const status = await statusResp.json();
            installProgress = status.progress || 0;

            if (status.status === 'complete') {
              installingModel = '';
              await scanHardware(); // Refresh hardware info
              return;
            } else if (status.status === 'error') {
              throw new Error(status.error || 'Installation failed');
            }
          }
          // Continue polling
          setTimeout(pollProgress, 1000);
        } catch (e) {
          installError = e instanceof Error ? e.message : 'Installation failed';
          installingModel = '';
        }
      };

      // Start polling after a short delay
      setTimeout(pollProgress, 500);
    } catch (e) {
      installError = e instanceof Error ? e.message : 'Failed to install model';
      installingModel = '';
    }
  }

  function openOllamaWebsite() {
    // In Tauri, this would open the URL in the default browser
    window.open('https://ollama.ai', '_blank');
  }

  function handleContinue() {
    dispatch('next');
  }
</script>

<div class="step-local-ai">
  <div class="step-header">
    <h2>Local AI Setup</h2>
    <p class="step-description">
      Let's set up your local AI assistant first. This ensures you can always write, even offline.
    </p>
  </div>

  {#if scanning}
    <div class="scanning-state">
      <div class="scanner-animation">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
          <rect x="9" y="9" width="6" height="6"></rect>
          <line x1="9" y1="1" x2="9" y2="4"></line>
          <line x1="15" y1="1" x2="15" y2="4"></line>
          <line x1="9" y1="20" x2="9" y2="23"></line>
          <line x1="15" y1="20" x2="15" y2="23"></line>
        </svg>
      </div>
      <p>Scanning your computer...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{error}</p>
      <button class="btn-secondary" on:click={scanHardware}>Try Again</button>
    </div>
  {:else if hardwareInfo}
    <!-- Hardware Results -->
    <div class="hardware-results">
      <div class="hardware-grid">
        <div class="hardware-item">
          <span class="hw-icon">💾</span>
          <span class="hw-label">RAM</span>
          <span class="hw-value">{hardwareInfo.ram_gb}GB</span>
          <span class="hw-status success">✓</span>
        </div>
        <div class="hardware-item">
          <span class="hw-icon">💻</span>
          <span class="hw-label">CPU</span>
          <span class="hw-value">{hardwareInfo.cpu_cores} cores</span>
          <span class="hw-status success">✓</span>
        </div>
        <div class="hardware-item">
          <span class="hw-icon">🎨</span>
          <span class="hw-label">GPU</span>
          <span class="hw-value">{hardwareInfo.gpu_available ? (hardwareInfo.gpu_name || 'Available') : 'Not detected'}</span>
          <span class="hw-status {hardwareInfo.gpu_available ? 'success' : 'warning'}">{hardwareInfo.gpu_available ? '✓' : '⚠'}</span>
        </div>
        <div class="hardware-item">
          <span class="hw-icon">🦙</span>
          <span class="hw-label">Ollama</span>
          <span class="hw-value">{hardwareInfo.ollama_installed ? `v${hardwareInfo.ollama_version}` : 'Not installed'}</span>
          <span class="hw-status {hardwareInfo.ollama_installed ? 'success' : 'warning'}">{hardwareInfo.ollama_installed ? '✓' : '⚠'}</span>
        </div>
      </div>

      <!-- Recommendation Box -->
      <div class="recommendation-box">
        <span class="rec-icon">💡</span>
        <span class="rec-text">
          Recommended model size: <strong>{hardwareInfo.recommended_max_params || '7B or smaller'}</strong>
        </span>
      </div>

      <!-- Ollama Setup Section -->
      {#if !hardwareInfo.ollama_installed}
        <div class="ollama-setup">
          <div class="setup-card warning">
            <h3>Ollama Not Installed</h3>
            <p>Ollama is required to run local AI models. It's free and easy to install.</p>
            <button class="btn-primary" on:click={openOllamaWebsite}>
              Install Ollama
              <span class="external-icon">↗</span>
            </button>
            <p class="help-text">After installing, restart this wizard or click "Rescan" below.</p>
            <button class="btn-secondary" on:click={scanHardware}>Rescan System</button>
          </div>
        </div>
      {:else}
        <!-- Model Installation Section -->
        <div class="model-section">
          {#if hardwareInfo.ollama_models.length > 0}
            <div class="installed-models">
              <h4>Installed Models</h4>
              <div class="model-tags">
                {#each hardwareInfo.ollama_models as model}
                  <span class="model-tag">✓ {model}</span>
                {/each}
              </div>
            </div>
          {/if}

          <div class="install-models">
            <h4>Install a Model</h4>
            <p class="section-desc">Choose a model to install. You can install more later.</p>

            <div class="model-options">
              <!-- Recommended Model -->
              <div class="model-option recommended">
                <div class="model-info">
                  <span class="model-name">{recommendedModel.name}</span>
                  <span class="recommended-badge">Recommended</span>
                </div>
                <p class="model-desc">{recommendedModel.description}</p>
                <div class="model-meta">
                  <span class="model-size">{recommendedModel.size}</span>
                  {#if hardwareInfo.ollama_models.includes(recommendedModel.id.split(':')[0]) || hardwareInfo.ollama_models.some(m => m.includes(recommendedModel.id.split(':')[0]))}
                    <span class="installed-badge">✓ Installed</span>
                  {:else if installingModel === recommendedModel.id}
                    <div class="install-progress">
                      <div class="progress-bar">
                        <div class="progress-fill" style="width: {installProgress}%"></div>
                      </div>
                      <span class="progress-text">{installProgress}%</span>
                    </div>
                  {:else}
                    <button class="btn-install" on:click={() => installModel(recommendedModel.id)}>
                      Install
                    </button>
                  {/if}
                </div>
              </div>

              <!-- Alternative Models -->
              {#each Object.entries(modelRecommendations).filter(([key]) => modelRecommendations[key].id !== recommendedModel.id) as [tier, model]}
                <div class="model-option">
                  <div class="model-info">
                    <span class="model-name">{model.name}</span>
                    <span class="tier-badge tier-{tier}">{tier}</span>
                  </div>
                  <p class="model-desc">{model.description}</p>
                  <div class="model-meta">
                    <span class="model-size">{model.size}</span>
                    {#if hardwareInfo.ollama_models.includes(model.id.split(':')[0]) || hardwareInfo.ollama_models.some(m => m.includes(model.id.split(':')[0]))}
                      <span class="installed-badge">✓ Installed</span>
                    {:else if installingModel === model.id}
                      <div class="install-progress">
                        <div class="progress-bar">
                          <div class="progress-fill" style="width: {installProgress}%"></div>
                        </div>
                        <span class="progress-text">{installProgress}%</span>
                      </div>
                    {:else}
                      <button class="btn-install" on:click={() => installModel(model.id)}>
                        Install
                      </button>
                    {/if}
                  </div>
                </div>
              {/each}
            </div>

            {#if installError}
              <div class="error-message">{installError}</div>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <!-- Ready Status -->
    {#if isReady}
      <div class="ready-status">
        <span class="ready-icon">✓</span>
        <span class="ready-text">Local AI ready!</span>
      </div>
    {/if}
  {/if}

  <!-- Navigation -->
  <div class="step-actions">
    <div></div> <!-- Spacer -->
    <button
      class="btn-primary"
      on:click={handleContinue}
      disabled={!isReady && !hardwareInfo?.ollama_installed}
    >
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<style>
  .step-local-ai {
    max-width: 700px;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 2rem;
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

  /* Scanning State */
  .scanning-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3rem;
    text-align: center;
  }

  .scanner-animation {
    color: var(--accent-cyan, #00d9ff);
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }

  .scanning-state p {
    margin-top: 1rem;
    color: var(--accent-cyan, #00d9ff);
    font-weight: 500;
  }

  /* Error State */
  .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    text-align: center;
  }

  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .error-state p {
    color: var(--error, #f85149);
    margin-bottom: 1rem;
  }

  /* Hardware Results */
  .hardware-results {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .hardware-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }

  .hardware-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 8px;
    border: 1px solid var(--border, #2d3a47);
  }

  .hw-icon {
    font-size: 1.25rem;
  }

  .hw-label {
    flex: 1;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
  }

  .hw-value {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.875rem;
  }

  .hw-status {
    font-size: 1rem;
  }

  .hw-status.success {
    color: var(--success, #3fb950);
  }

  .hw-status.warning {
    color: var(--warning, #d29922);
  }

  /* Recommendation Box */
  .recommendation-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(0, 217, 255, 0.1);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 8px;
  }

  .rec-icon {
    font-size: 1.25rem;
  }

  .rec-text {
    color: var(--text-secondary, #8b949e);
  }

  .rec-text strong {
    color: var(--accent-cyan, #00d9ff);
  }

  /* Ollama Setup */
  .ollama-setup {
    margin-top: 1rem;
  }

  .setup-card {
    padding: 1.5rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 8px;
    border: 1px solid var(--border, #2d3a47);
    text-align: center;
  }

  .setup-card.warning {
    border-color: var(--warning, #d29922);
    background: rgba(210, 153, 34, 0.1);
  }

  .setup-card h3 {
    margin: 0 0 0.5rem 0;
    color: var(--warning, #d29922);
  }

  .setup-card p {
    color: var(--text-secondary, #8b949e);
    margin: 0 0 1rem 0;
  }

  .help-text {
    font-size: 0.875rem;
    margin-top: 1rem !important;
  }

  /* Model Section */
  .model-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .installed-models h4,
  .install-models h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 0.75rem 0;
  }

  .section-desc {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 1rem 0;
  }

  .model-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .model-tag {
    padding: 0.375rem 0.75rem;
    background: var(--bg-secondary, #1a2027);
    border-radius: 4px;
    font-size: 0.875rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--success, #3fb950);
  }

  /* Model Options */
  .model-options {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .model-option {
    padding: 1rem;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    transition: border-color 0.2s;
  }

  .model-option.recommended {
    border-color: var(--accent-cyan, #00d9ff);
    background: rgba(0, 217, 255, 0.05);
  }

  .model-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .model-name {
    font-weight: 600;
    color: #ffffff;
  }

  .recommended-badge {
    font-size: 0.65rem;
    padding: 0.125rem 0.375rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border-radius: 3px;
    font-weight: 700;
    text-transform: uppercase;
  }

  .tier-badge {
    font-size: 0.65rem;
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .tier-badge.tier-low {
    background: var(--success, #3fb950);
    color: #000;
  }

  .tier-badge.tier-medium {
    background: #58a6ff;
    color: #000;
  }

  .tier-badge.tier-high {
    background: #a371f7;
    color: #000;
  }

  .model-desc {
    font-size: 0.875rem;
    color: var(--text-secondary, #8b949e);
    margin: 0 0 0.75rem 0;
  }

  .model-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .model-size {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    padding: 0.25rem 0.5rem;
    background: var(--bg-secondary, #1a2027);
    border-radius: 4px;
  }

  .installed-badge {
    font-size: 0.75rem;
    color: var(--success, #3fb950);
  }

  .btn-install {
    padding: 0.375rem 1rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-install:hover {
    background: #00b8d9;
  }

  /* Install Progress */
  .install-progress {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 120px;
  }

  .progress-bar {
    flex: 1;
    height: 6px;
    background: var(--border, #2d3a47);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent-cyan, #00d9ff);
    transition: width 0.3s;
  }

  .progress-text {
    font-size: 0.75rem;
    color: var(--accent-cyan, #00d9ff);
    min-width: 35px;
  }

  /* Ready Status */
  .ready-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    border-radius: 8px;
    margin-top: 1.5rem;
  }

  .ready-icon {
    font-size: 1.25rem;
    color: var(--success, #3fb950);
  }

  .ready-text {
    font-weight: 600;
    color: var(--success, #3fb950);
  }

  /* Error Message */
  .error-message {
    padding: 0.75rem;
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 6px;
    color: var(--error, #f85149);
    font-size: 0.875rem;
    margin-top: 1rem;
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
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

  .btn-primary:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
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

  .external-icon {
    font-size: 0.875rem;
    margin-left: 0.25rem;
  }
</style>
