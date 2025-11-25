<!--
  StatusBar.svelte - Application status bar

  Shows:
  - Current Foreman mode
  - Graph node count
  - Current model / quality tier
  - Backend connection status
-->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { foremanMode, foremanActive } from '$lib/stores';

  let graphNodeCount = 0;
  let backendStatus = 'checking';
  let qualityTier = 'budget';
  let currentSpend = 0;
  let budgetLimit = null;

  // Mode colors
  const modeColors = {
    ARCHITECT: 'var(--mode-architect, #2f81f7)',
    VOICE_CALIBRATION: 'var(--mode-voice, #a371f7)',
    DIRECTOR: 'var(--mode-director, #d4a574)',
    EDITOR: 'var(--mode-editor, #3fb950)'
  };

  async function checkBackendStatus() {
    try {
      const status = await apiClient.foremanStatus();
      backendStatus = 'online';
    } catch (e) {
      backendStatus = 'offline';
    }
  }

  async function loadOrchestratorInfo() {
    try {
      const settings = await apiClient.getSettingsCategory('orchestrator');
      qualityTier = settings.quality_tier || 'budget';

      const spend = await apiClient.getCurrentSpend();
      currentSpend = spend.total_spend_usd || 0;
      budgetLimit = spend.budget_usd;
    } catch (e) {
      // Silently fail - orchestrator may not be available
    }
  }

  let interval;

  onMount(async () => {
    await checkBackendStatus();
    await loadOrchestratorInfo();

    // Refresh every 30 seconds
    interval = setInterval(async () => {
      await checkBackendStatus();
      await loadOrchestratorInfo();
    }, 30000);
  });

  onDestroy(() => {
    if (interval) clearInterval(interval);
  });
</script>

<footer class="status-bar">
  <div class="status-left">
    <!-- Backend Status -->
    <div class="status-item">
      <span class="status-dot {backendStatus}"></span>
      <span class="status-label">{backendStatus === 'online' ? 'Backend Online' : 'Backend Offline'}</span>
    </div>

    <!-- Foreman Mode -->
    {#if $foremanActive && $foremanMode}
      <div class="status-item">
        <span class="mode-indicator" style="--mode-color: {modeColors[$foremanMode] || modeColors.ARCHITECT}">
          {$foremanMode.replace('_', ' ')}
        </span>
      </div>
    {/if}
  </div>

  <div class="status-right">
    <!-- Quality Tier -->
    <div class="status-item">
      <span class="tier-badge tier-{qualityTier}">
        {qualityTier.charAt(0).toUpperCase() + qualityTier.slice(1)}
      </span>
    </div>

    <!-- Spend Tracker -->
    {#if budgetLimit !== null}
      <div class="status-item spend-tracker">
        <span class="spend-amount">${currentSpend.toFixed(2)}</span>
        <span class="spend-separator">/</span>
        <span class="spend-budget">${budgetLimit.toFixed(2)}</span>
      </div>
    {/if}
  </div>
</footer>

<style>
  .status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--status-bar-height, 32px);
    padding: 0 var(--space-4, 16px);
    background: var(--bg-primary, #0f1419);
    border-top: 1px solid var(--border, #2d3a47);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .status-left,
  .status-right {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-dot.online {
    background: var(--success, #3fb950);
    box-shadow: 0 0 6px var(--success, #3fb950);
  }

  .status-dot.offline {
    background: var(--error, #f85149);
  }

  .status-dot.checking {
    background: var(--warning, #d29922);
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .status-label {
    color: var(--text-secondary, #8b949e);
  }

  .mode-indicator {
    padding: 2px 8px;
    background: color-mix(in srgb, var(--mode-color) 20%, transparent);
    border: 1px solid var(--mode-color);
    border-radius: var(--radius-sm, 4px);
    color: var(--mode-color);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .tier-badge {
    padding: 2px 8px;
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
  }

  .tier-budget {
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    color: var(--success, #3fb950);
  }

  .tier-balanced {
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    color: var(--accent-cyan, #58a6ff);
  }

  .tier-premium {
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    color: var(--accent-gold, #d4a574);
  }

  .spend-tracker {
    font-family: var(--font-mono, monospace);
    font-size: var(--text-xs, 11px);
  }

  .spend-amount {
    color: var(--text-primary, #e6edf3);
  }

  .spend-separator {
    color: var(--text-muted, #6e7681);
  }

  .spend-budget {
    color: var(--text-secondary, #8b949e);
  }
</style>
