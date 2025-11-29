<!--
  Step1LocalAI.svelte - Local AI Setup Step (Simplified)

  Purpose: Ensure every user has Ollama + llama3.2:3b installed.
  This is a lightweight model sufficient for The Foreman's casual chat.
  All heavy lifting uses cloud APIs.

  3-State Flow:
  1. Install Ollama (if not installed)
  2. Install llama3.2:3b model
  3. Ready - continue to next step
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import type { HardwareInfo } from '$lib/api_client';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // The only model we need
  const requiredModel = {
    id: 'llama3.2:3b',
    name: 'Llama 3.2',
    description: 'Fast, lightweight AI for your writing assistant',
    size: '2GB'
  };

  // State
  let hardwareInfo: HardwareInfo | null = null;
  let scanning = true;
  let error = '';

  // Model installation state
  let installing = false;
  let installProgress = 0;
  let installError = '';

  // Check if required model is installed
  $: hasRequiredModel = hardwareInfo?.ollama_models?.some(m =>
    m.includes('llama3.2') || m.includes('llama3.2:3b')
  ) ?? false;

  $: isReady = hardwareInfo?.ollama_installed && hasRequiredModel;

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
        new Promise(resolve => setTimeout(resolve, 800))
      ]);

      if (!response.ok) {
        throw new Error('Failed to detect hardware');
      }

      hardwareInfo = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Hardware detection failed';
    } finally {
      scanning = false;
    }
  }

  async function installModel() {
    installing = true;
    installProgress = 0;
    installError = '';

    try {
      // Start the model pull
      const response = await fetch(`${BASE_URL}/system/ollama/pull`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: requiredModel.id })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to start model download');
      }

      // Poll for progress
      const pollProgress = async () => {
        try {
          const statusResp = await fetch(`${BASE_URL}/system/ollama/pull-status?model=${requiredModel.id}`);
          if (statusResp.ok) {
            const status = await statusResp.json();
            installProgress = status.progress || 0;

            if (status.status === 'complete') {
              installing = false;
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
          installing = false;
        }
      };

      // Start polling after a short delay
      setTimeout(pollProgress, 500);
    } catch (e) {
      installError = e instanceof Error ? e.message : 'Failed to install model';
      installing = false;
    }
  }

  function openOllamaWebsite() {
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
      Your writing assistant needs a small AI model for offline help. This takes about 2 minutes.
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
      <p>Checking your system...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{error}</p>
      <button class="btn-secondary" on:click={scanHardware}>Try Again</button>
    </div>
  {:else if hardwareInfo}
    <div class="setup-content">
      <!-- State 1: Ollama Not Installed -->
      {#if !hardwareInfo.ollama_installed}
        <div class="status-card warning">
          <div class="status-icon">⚠️</div>
          <div class="status-content">
            <h3>Ollama Required</h3>
            <p>Ollama runs AI models locally on your computer. It's free and takes just a minute to install.</p>
            <div class="status-actions">
              <button class="btn-primary" on:click={openOllamaWebsite}>
                Install Ollama
                <span class="external-icon">↗</span>
              </button>
              <button class="btn-secondary" on:click={scanHardware}>Rescan</button>
            </div>
          </div>
        </div>

      <!-- State 2: Ollama Installed, Model Missing -->
      {:else if !hasRequiredModel}
        <div class="status-card">
          <div class="status-row success">
            <span class="check-icon">✓</span>
            <span>Ollama v{hardwareInfo.ollama_version}</span>
          </div>

          <div class="model-install-section">
            <div class="model-info">
              <span class="model-icon">📦</span>
              <div class="model-details">
                <span class="model-name">{requiredModel.name}</span>
                <span class="model-size">({requiredModel.size})</span>
              </div>
            </div>
            <p class="model-desc">{requiredModel.description}</p>

            {#if installing}
              <div class="install-progress">
                <div class="progress-bar">
                  <div class="progress-fill" style="width: {installProgress}%"></div>
                </div>
                <span class="progress-text">{installProgress}%</span>
              </div>
            {:else}
              <button class="btn-primary install-btn" on:click={installModel}>
                Install Model
              </button>
            {/if}

            {#if installError}
              <div class="error-message">{installError}</div>
            {/if}
          </div>
        </div>

      <!-- State 3: Ready -->
      {:else}
        <div class="status-card ready">
          <div class="status-row success">
            <span class="check-icon">✓</span>
            <span>Ollama v{hardwareInfo.ollama_version}</span>
          </div>
          <div class="status-row success">
            <span class="check-icon">✓</span>
            <span>{requiredModel.name} installed</span>
          </div>
          <div class="ready-message">
            <span class="ready-icon">🎉</span>
            <span>Your local AI is ready!</span>
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Navigation -->
  <div class="step-actions">
    <div></div> <!-- Spacer for alignment -->
    <button
      class="btn-primary"
      on:click={handleContinue}
      disabled={!isReady}
    >
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<style>
  .step-local-ai {
    max-width: 500px;
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

  /* Setup Content */
  .setup-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  /* Status Card */
  .status-card {
    padding: 1.5rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 12px;
    border: 1px solid var(--border, #2d3a47);
  }

  .status-card.warning {
    border-color: var(--warning, #d29922);
    background: rgba(210, 153, 34, 0.05);
    display: flex;
    gap: 1rem;
    align-items: flex-start;
  }

  .status-card.ready {
    border-color: var(--success, #3fb950);
    background: rgba(63, 185, 80, 0.05);
  }

  .status-icon {
    font-size: 2rem;
    flex-shrink: 0;
  }

  .status-content h3 {
    margin: 0 0 0.5rem 0;
    color: var(--warning, #d29922);
    font-size: 1.125rem;
  }

  .status-content p {
    margin: 0 0 1rem 0;
    color: var(--text-secondary, #8b949e);
    font-size: 0.9375rem;
    line-height: 1.5;
  }

  .status-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .status-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
  }

  .status-row.success {
    color: var(--success, #3fb950);
  }

  .check-icon {
    font-size: 1.125rem;
  }

  /* Model Install Section */
  .model-install-section {
    margin-top: 1.25rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .model-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  .model-icon {
    font-size: 1.5rem;
  }

  .model-details {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
  }

  .model-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 1.0625rem;
  }

  .model-size {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
  }

  .model-desc {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 1rem 0;
  }

  .install-btn {
    width: 100%;
  }

  /* Progress Bar */
  .install-progress {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .progress-bar {
    flex: 1;
    height: 8px;
    background: var(--border, #2d3a47);
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent-cyan, #00d9ff);
    transition: width 0.3s;
  }

  .progress-text {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--accent-cyan, #00d9ff);
    min-width: 40px;
    text-align: right;
  }

  /* Ready Message */
  .ready-message {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(63, 185, 80, 0.1);
    border-radius: 8px;
  }

  .ready-icon {
    font-size: 1.25rem;
  }

  .ready-message span:last-child {
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
