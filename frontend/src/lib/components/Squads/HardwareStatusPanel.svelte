<!--
  HardwareStatusPanel.svelte - Compact hardware status widget for dashboard

  Features:
  - Displays RAM, CPU, GPU, Ollama status
  - Lists installed local models
  - Auto-refreshes every 30 seconds
  - "Install More Models" button for model management

  Usage:
    <HardwareStatusPanel />
-->
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { HardwareInfo } from '$lib/api_client';

  const BASE_URL = 'http://localhost:8000';

  // State
  let hardwareInfo: HardwareInfo | null = null;
  let loading = true;
  let error = '';
  let refreshInterval: ReturnType<typeof setInterval> | null = null;

  // Modal state
  let showModelModal = false;
  let availableModels: Array<{
    id: string;
    name: string;
    purpose: string;
    size_gb: number;
    tier: string;
    installed: boolean;
  }> = [];
  let loadingModels = false;

  onMount(() => {
    loadHardwareInfo();
    // Auto-refresh every 30 seconds
    refreshInterval = setInterval(loadHardwareInfo, 30000);
  });

  onDestroy(() => {
    if (refreshInterval) {
      clearInterval(refreshInterval);
    }
  });

  async function loadHardwareInfo() {
    try {
      loading = hardwareInfo === null; // Only show loading on first load
      error = '';

      const response = await fetch(`${BASE_URL}/system/hardware`);
      if (!response.ok) {
        throw new Error('Failed to load hardware info');
      }

      hardwareInfo = await response.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load hardware info';
    } finally {
      loading = false;
    }
  }

  async function openModelManager() {
    showModelModal = true;
    loadingModels = true;

    try {
      const response = await fetch(`${BASE_URL}/system/local-models`);
      if (response.ok) {
        const data = await response.json();
        availableModels = data.models || [];
      }
    } catch {
      // Silently fail - modal will show empty state
    } finally {
      loadingModels = false;
    }
  }

  function closeModelModal() {
    showModelModal = false;
  }

  function formatBytes(gb: number): string {
    if (gb >= 1) {
      return `${gb.toFixed(1)}GB`;
    }
    return `${Math.round(gb * 1024)}MB`;
  }

  function getModelSize(modelName: string): string {
    // Extract size from common model naming patterns
    const sizeMatch = modelName.match(/(\d+\.?\d*)([bB])/);
    if (sizeMatch) {
      return `${sizeMatch[1]}B`;
    }
    return '';
  }
</script>

<div class="hardware-panel">
  <div class="panel-header">
    <h3>System Status</h3>
    <button class="refresh-btn" on:click={loadHardwareInfo} title="Refresh">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M23 4v6h-6"></path>
        <path d="M1 20v-6h6"></path>
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
      </svg>
    </button>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <span>Detecting hardware...</span>
    </div>
  {:else if error}
    <div class="error-state">
      <span class="error-icon">&#9888;</span>
      <span>{error}</span>
    </div>
  {:else if hardwareInfo}
    <div class="hardware-stats">
      <div class="stat-row">
        <span class="stat-icon">&#128190;</span>
        <span class="stat-label">RAM</span>
        <span class="stat-value">{hardwareInfo.ram_gb}GB</span>
        <span class="stat-detail">({hardwareInfo.available_ram_gb}GB free)</span>
      </div>

      <div class="stat-row">
        <span class="stat-icon">&#128187;</span>
        <span class="stat-label">CPU</span>
        <span class="stat-value">{hardwareInfo.cpu_cores} cores</span>
      </div>

      <div class="stat-row">
        <span class="stat-icon">&#127912;</span>
        <span class="stat-label">GPU</span>
        <span class="stat-value {hardwareInfo.gpu_available ? '' : 'muted'}">
          {hardwareInfo.gpu_available ? (hardwareInfo.gpu_name || 'Available') : 'None'}
        </span>
        {#if hardwareInfo.gpu_vram_gb}
          <span class="stat-detail">({hardwareInfo.gpu_vram_gb}GB VRAM)</span>
        {/if}
      </div>

      <div class="stat-row">
        <span class="stat-icon">&#129433;</span>
        <span class="stat-label">Ollama</span>
        {#if hardwareInfo.ollama_installed}
          <span class="stat-value status-ok">&#10003; v{hardwareInfo.ollama_version}</span>
        {:else}
          <span class="stat-value status-warn">&#9888; Not installed</span>
        {/if}
      </div>
    </div>

    {#if hardwareInfo.ollama_installed && hardwareInfo.ollama_models.length > 0}
      <div class="models-section">
        <div class="models-header">
          <span class="models-label">Local Models ({hardwareInfo.ollama_models.length})</span>
        </div>
        <div class="models-list">
          {#each hardwareInfo.ollama_models as model}
            <div class="model-item">
              <span class="model-name">{model}</span>
              {#if getModelSize(model)}
                <span class="model-size">{getModelSize(model)}</span>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {:else if hardwareInfo.ollama_installed}
      <div class="no-models">
        <span class="no-models-text">No local models installed</span>
      </div>
    {/if}

    <button class="install-btn" on:click={openModelManager}>
      Install More Models
    </button>
  {/if}
</div>

<!-- Model Manager Modal -->
{#if showModelModal}
  <div class="modal-overlay" on:click={closeModelModal} on:keydown={(e) => e.key === 'Escape' && closeModelModal()} role="button" tabindex="0">
    <div class="modal-content" on:click|stopPropagation role="dialog" aria-modal="true">
      <div class="modal-header">
        <h3>Available Local Models</h3>
        <button class="close-btn" on:click={closeModelModal}>&#10005;</button>
      </div>

      <div class="modal-body">
        {#if loadingModels}
          <div class="loading-state">
            <div class="spinner"></div>
            <span>Loading models...</span>
          </div>
        {:else if availableModels.length > 0}
          <div class="available-models">
            {#each availableModels as model}
              <div class="available-model-item">
                <div class="model-info">
                  <span class="model-name">{model.name}</span>
                  <span class="model-purpose">{model.purpose}</span>
                </div>
                <div class="model-meta">
                  <span class="model-size">{formatBytes(model.size_gb)}</span>
                  <span class="model-tier tier-{model.tier}">{model.tier}</span>
                </div>
                <div class="model-action">
                  {#if model.installed}
                    <span class="installed-badge">&#10003; Installed</span>
                  {:else}
                    <button class="install-model-btn">
                      Install
                    </button>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <div class="empty-state">
            <p>No additional models available.</p>
            <p class="help-text">Make sure Ollama is running to see available models.</p>
          </div>
        {/if}
      </div>

      <div class="modal-footer">
        <a href="https://ollama.ai/library" target="_blank" rel="noopener" class="ollama-link">
          Browse Ollama Library &#8599;
        </a>
        <button class="btn-secondary" on:click={closeModelModal}>Close</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .hardware-panel {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 8px;
    padding: 1rem;
    color: #ffffff;
  }

  .panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .panel-header h3 {
    margin: 0;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .refresh-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .refresh-btn:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Loading & Error States */
  .loading-state,
  .error-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1.5rem;
    color: var(--text-secondary, #8b949e);
  }

  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-state {
    color: var(--error, #f85149);
  }

  .error-icon {
    font-size: 1rem;
  }

  /* Hardware Stats */
  .hardware-stats {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .stat-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 4px;
  }

  .stat-icon {
    font-size: 1rem;
    width: 24px;
    text-align: center;
  }

  .stat-label {
    width: 50px;
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
  }

  .stat-value {
    flex: 1;
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-primary, #e6edf3);
  }

  .stat-value.muted {
    color: var(--text-secondary, #8b949e);
  }

  .stat-value.status-ok {
    color: var(--success, #3fb950);
  }

  .stat-value.status-warn {
    color: var(--warning, #d29922);
  }

  .stat-detail {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  /* Models Section */
  .models-section {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 4px;
  }

  .models-header {
    margin-bottom: 0.5rem;
  }

  .models-label {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
  }

  .models-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .model-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
  }

  .model-name {
    font-size: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-cyan, #58a6ff);
  }

  .model-size {
    font-size: 0.7rem;
    color: var(--text-secondary, #8b949e);
    padding: 0.125rem 0.375rem;
    background: var(--bg-secondary, #1a2027);
    border-radius: 3px;
  }

  .no-models {
    padding: 0.75rem;
    text-align: center;
  }

  .no-models-text {
    font-size: 0.8rem;
    color: var(--text-secondary, #8b949e);
  }

  /* Install Button */
  .install-btn {
    width: 100%;
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: 4px;
    color: var(--text-secondary, #8b949e);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .install-btn:hover {
    background: var(--bg-tertiary, #242d38);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Modal */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary, #e6edf3);
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary, #8b949e);
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.25rem;
    line-height: 1;
    transition: color 0.2s;
  }

  .close-btn:hover {
    color: var(--text-primary, #e6edf3);
  }

  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 1.25rem;
  }

  .available-models {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .available-model-item {
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 0.75rem;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg-primary, #0f1419);
    border-radius: 6px;
  }

  .model-info {
    display: flex;
    flex-direction: column;
    gap: 0.125rem;
  }

  .model-purpose {
    font-size: 0.7rem;
    color: var(--text-secondary, #8b949e);
  }

  .model-meta {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .model-tier {
    font-size: 0.65rem;
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
    text-transform: uppercase;
    font-weight: 600;
  }

  .model-tier.tier-budget {
    background: var(--success, #3fb950);
    color: #000;
  }

  .model-tier.tier-balanced {
    background: var(--accent-cyan, #58a6ff);
    color: #000;
  }

  .model-tier.tier-premium {
    background: #a371f7;
    color: #000;
  }

  .installed-badge {
    font-size: 0.75rem;
    color: var(--success, #3fb950);
  }

  .install-model-btn {
    padding: 0.375rem 0.75rem;
    background: var(--accent-cyan, #58a6ff);
    color: #000;
    border: none;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .install-model-btn:hover {
    background: #79b8ff;
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary, #8b949e);
  }

  .empty-state p {
    margin: 0 0 0.5rem 0;
  }

  .help-text {
    font-size: 0.8rem;
  }

  .modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .ollama-link {
    font-size: 0.8rem;
    color: var(--accent-cyan, #58a6ff);
    text-decoration: none;
    transition: opacity 0.2s;
  }

  .ollama-link:hover {
    opacity: 0.8;
  }

  .btn-secondary {
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: 4px;
    color: var(--text-secondary, #8b949e);
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }
</style>
