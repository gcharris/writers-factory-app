<!--
  StudioPanel.svelte - Tool Card Grid (Cyber-Noir Theme)

  Matching the mockup with:
  - 2x2 card grid layout
  - Icons with status indicators
  - Run buttons
  - Mode-aware cards (Voice Tournament, Scaffold Generator, Health Check, Metabolism)
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import {
    foremanMode,
    foremanActive,
    showStoryBibleWizard,
    showNotebookRegistration,
    activeModal,
    storyBibleStatus
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Health status
  let healthStatus = { conflicts: 0, warnings: 0 };
  let metabolismStatus = { uncommitted: 0, digesting: false };

  // Fetch status on mount
  onMount(async () => {
    await fetchHealthStatus();
    await fetchMetabolismStatus();
  });

  async function fetchHealthStatus() {
    try {
      const res = await fetch('http://localhost:8000/health/status');
      if (res.ok) {
        const data = await res.json();
        healthStatus = {
          conflicts: data.conflicts?.length || 0,
          warnings: data.warnings?.length || 0
        };
      }
    } catch (e) {
      console.warn('Failed to fetch health status:', e);
    }
  }

  async function fetchMetabolismStatus() {
    try {
      const res = await fetch('http://localhost:8000/health/status');
      if (res.ok) {
        const data = await res.json();
        metabolismStatus = {
          uncommitted: data.uncommitted_count || 0,
          digesting: false
        };
      }
    } catch (e) {
      console.warn('Failed to fetch metabolism status:', e);
    }
  }

  // Card actions
  function openVoiceTournament() {
    dispatch('open-modal', { modal: 'voice-tournament' });
  }

  function openScaffoldGenerator() {
    dispatch('open-modal', { modal: 'scaffold-generator' });
  }

  function runHealthCheck() {
    dispatch('open-modal', { modal: 'health-dashboard' });
  }

  async function runMetabolism() {
    if (metabolismStatus.digesting) return;

    metabolismStatus.digesting = true;
    try {
      const res = await fetch('http://localhost:8000/graph/consolidate', {
        method: 'POST'
      });
      if (res.ok) {
        await fetchMetabolismStatus();
      }
    } catch (e) {
      console.error('Metabolism failed:', e);
    } finally {
      metabolismStatus.digesting = false;
    }
  }

  // Card definitions matching the mockup
  const cards = [
    {
      id: 'voice-tournament',
      title: 'Voice Tournament',
      icon: 'mic',
      status: 'Ready',
      statusType: 'ready',
      action: openVoiceTournament,
      hasRunButton: true
    },
    {
      id: 'scaffold-generator',
      title: 'Scaffold Generator',
      icon: 'compass',
      status: 'Active',
      statusType: 'active',
      action: openScaffoldGenerator,
      hasRunButton: true
    },
    {
      id: 'health-check',
      title: 'Health Check',
      icon: 'activity',
      statusType: 'warning',
      action: runHealthCheck,
      hasRunButton: true,
      dynamic: true
    },
    {
      id: 'metabolism',
      title: 'Metabolism',
      icon: 'zap',
      statusType: 'info',
      action: runMetabolism,
      hasStopButton: true,
      dynamic: true
    }
  ];

  // Icon SVGs
  const icons = {
    mic: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`,
    compass: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
    </svg>`,
    activity: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
    </svg>`,
    zap: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
    </svg>`
  };

  // Get dynamic status for cards
  function getCardStatus(card) {
    if (card.id === 'health-check') {
      if (healthStatus.conflicts > 0) {
        return `${healthStatus.conflicts} Conflicts`;
      }
      return 'All Clear';
    }
    if (card.id === 'metabolism') {
      if (metabolismStatus.digesting) {
        return 'Digesting...';
      }
      if (metabolismStatus.uncommitted > 0) {
        return `${metabolismStatus.uncommitted} Pending`;
      }
      return 'Idle';
    }
    return card.status;
  }

  function getStatusType(card) {
    if (card.id === 'health-check') {
      return healthStatus.conflicts > 0 ? 'warning' : 'success';
    }
    if (card.id === 'metabolism') {
      if (metabolismStatus.digesting) return 'active';
      if (metabolismStatus.uncommitted > 0) return 'info';
      return 'muted';
    }
    return card.statusType;
  }

  // Status colors
  const statusColors = {
    ready: 'var(--text-secondary)',
    active: 'var(--accent-cyan)',
    warning: 'var(--warning)',
    success: 'var(--success)',
    info: 'var(--accent-gold)',
    muted: 'var(--text-muted)'
  };
</script>

<div class="studio-panel">
  <div class="card-grid">
    {#each cards as card}
      <div class="studio-card" on:click={card.action}>
        <!-- Card Icon -->
        <div class="card-icon" style="color: {statusColors[getStatusType(card)]}">
          {@html icons[card.icon]}
        </div>

        <!-- Card Content -->
        <div class="card-content">
          <div class="card-title">{card.title}</div>
          <div class="card-status" style="color: {statusColors[getStatusType(card)]}">
            {getCardStatus(card)}
          </div>
        </div>

        <!-- Card Action -->
        <div class="card-action">
          {#if card.hasRunButton}
            <button
              class="action-btn run"
              on:click|stopPropagation={card.action}
              disabled={card.id === 'metabolism' && metabolismStatus.digesting}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              Run
            </button>
          {:else if card.hasStopButton && metabolismStatus.digesting}
            <button class="action-btn stop" on:click|stopPropagation={() => {}}>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="6" width="12" height="12"></rect>
              </svg>
              Stop
            </button>
          {:else if card.hasStopButton}
            <button
              class="action-btn run"
              on:click|stopPropagation={card.action}
              disabled={metabolismStatus.uncommitted === 0}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              Run
            </button>
          {/if}
        </div>
      </div>
    {/each}
  </div>

  <!-- Writers Factory / Settings footer -->
  <div class="studio-footer">
    <span class="footer-label">Writers Factory</span>
    <span class="footer-sep">·</span>
    <button class="footer-link" on:click={() => dispatch('open-settings')}>Settings</button>
  </div>
</div>

<style>
  .studio-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    padding: var(--space-3);
    background: linear-gradient(180deg, var(--bg-secondary) 0%, #1e2530 100%);
  }

  .card-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3);
    flex: 1;
  }

  .studio-card {
    display: flex;
    flex-direction: column;
    padding: var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .studio-card:hover {
    background: var(--bg-elevated);
    border-color: var(--border-strong);
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }

  .card-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    margin-bottom: var(--space-2);
    background: var(--bg-primary);
    border-radius: var(--radius-md);
  }

  .card-content {
    flex: 1;
    margin-bottom: var(--space-2);
  }

  .card-title {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-primary);
    margin-bottom: 2px;
  }

  .card-status {
    font-size: var(--text-xs);
    font-weight: var(--font-medium);
  }

  .card-action {
    display: flex;
    justify-content: flex-end;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: var(--space-1);
    padding: var(--space-1) var(--space-3);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    cursor: pointer;
    transition: all var(--transition-fast);
  }

  .action-btn.run {
    background: var(--success);
    color: var(--bg-primary);
  }

  .action-btn.run:hover:not(:disabled) {
    background: var(--success-hover);
  }

  .action-btn.stop {
    background: var(--error);
    color: white;
  }

  .action-btn.stop:hover {
    background: var(--error-hover);
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Footer */
  .studio-footer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2);
    padding-top: var(--space-3);
    margin-top: auto;
    border-top: 1px solid var(--border);
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  .footer-label {
    font-style: italic;
  }

  .footer-sep {
    opacity: 0.5;
  }

  .footer-link {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: var(--text-xs);
    cursor: pointer;
    transition: color var(--transition-fast);
  }

  .footer-link:hover {
    color: var(--accent-cyan);
  }
</style>
