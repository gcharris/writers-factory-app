<!--
  ModeIndicator.svelte - Foreman Mode Status Display

  Shows the current Foreman mode in a compact, colorful indicator:
  - ARCHITECT (Blue): Building Story Bible
  - VOICE_CALIBRATION (Purple): Finding narrative voice
  - DIRECTOR (Green): Drafting scenes
  - EDITOR (Amber): Polish & revision

  Part of Track A: Minimal Testing Path
-->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { foremanMode, foremanActive, foremanProjectTitle } from '$lib/stores';

  // Poll interval for status updates (5 seconds)
  const POLL_INTERVAL = 5000;
  let pollTimer = null;
  let isLoading = false;
  let lastError = null;

  // Mode configuration
  const MODE_CONFIG = {
    architect: {
      icon: '🏗️',
      label: 'ARCHITECT',
      description: 'Building Story Bible',
      color: '#3B82F6',
      bgColor: 'rgba(59, 130, 246, 0.15)'
    },
    voice_calibration: {
      icon: '🎭',
      label: 'VOICE',
      description: 'Calibrating Voice',
      color: '#8B5CF6',
      bgColor: 'rgba(139, 92, 246, 0.15)'
    },
    director: {
      icon: '🎬',
      label: 'DIRECTOR',
      description: 'Drafting Scenes',
      color: '#10B981',
      bgColor: 'rgba(16, 185, 129, 0.15)'
    },
    editor: {
      icon: '✨',
      label: 'EDITOR',
      description: 'Polish & Revision',
      color: '#F59E0B',
      bgColor: 'rgba(245, 158, 11, 0.15)'
    }
  };

  // Normalize mode key (handle uppercase from API)
  function normalizeMode(mode) {
    if (!mode) return null;
    return mode.toLowerCase();
  }

  $: currentMode = normalizeMode($foremanMode);
  $: config = currentMode ? MODE_CONFIG[currentMode] : null;

  // Fetch Foreman status
  async function fetchStatus() {
    if (isLoading) return;

    try {
      isLoading = true;
      const response = await fetch('http://localhost:8000/foreman/status');

      if (!response.ok) {
        throw new Error(`Status check failed: ${response.status}`);
      }

      const data = await response.json();

      // Update stores
      if (data.mode) {
        foremanMode.set(data.mode);
        foremanActive.set(true);
      } else {
        foremanActive.set(false);
      }

      if (data.project_title) {
        foremanProjectTitle.set(data.project_title);
      }

      lastError = null;
    } catch (e) {
      console.warn('ModeIndicator: Failed to fetch status:', e.message);
      lastError = e.message;
      // Don't clear the mode on error - keep showing last known state
    } finally {
      isLoading = false;
    }
  }

  // Start polling on mount
  onMount(() => {
    fetchStatus();
    pollTimer = setInterval(fetchStatus, POLL_INTERVAL);
  });

  // Cleanup on destroy
  onDestroy(() => {
    if (pollTimer) {
      clearInterval(pollTimer);
    }
  });

  // Manual refresh
  function handleClick() {
    fetchStatus();
  }
</script>

<button
  class="mode-indicator"
  class:active={$foremanActive}
  class:loading={isLoading}
  style="--mode-color: {config?.color || 'var(--text-muted)'}; --mode-bg: {config?.bgColor || 'transparent'}"
  on:click={handleClick}
  title={config ? `${config.description}\nClick to refresh` : 'Foreman not active\nClick to check status'}
>
  {#if $foremanActive && config}
    <span class="mode-icon">{config.icon}</span>
    <span class="mode-label">{config.label}</span>
    {#if isLoading}
      <span class="loading-dot"></span>
    {/if}
  {:else}
    <span class="mode-icon inactive">💤</span>
    <span class="mode-label inactive">IDLE</span>
  {/if}
</button>

<style>
  .mode-indicator {
    display: inline-flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: var(--space-1, 4px) var(--space-2, 8px);
    background: var(--mode-bg);
    border: 1px solid var(--mode-color);
    border-radius: var(--radius-md, 6px);
    color: var(--mode-color);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;
  }

  .mode-indicator:hover {
    filter: brightness(1.1);
    transform: translateY(-1px);
  }

  .mode-indicator:active {
    transform: translateY(0);
  }

  .mode-indicator.loading {
    opacity: 0.7;
  }

  .mode-indicator:not(.active) {
    border-color: var(--border, #2d3a47);
    background: var(--bg-tertiary, #252d38);
    color: var(--text-muted, #8b949e);
  }

  .mode-icon {
    font-size: 12px;
    line-height: 1;
  }

  .mode-icon.inactive {
    opacity: 0.5;
  }

  .mode-label {
    letter-spacing: 0.05em;
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .mode-label.inactive {
    opacity: 0.7;
  }

  .loading-dot {
    width: 6px;
    height: 6px;
    background: var(--mode-color);
    border-radius: 50%;
    animation: pulse 1s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 0.3; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1); }
  }
</style>
