<!--
  StudioToolsPanel.svelte - Studio tools modal with tabbed navigation

  Contains all creative tools organized as tabs:
  - Voice Tournament: Compare AI voice variants
  - Scaffold Generator: Generate story structure
  - Health Dashboard: Check narrative health
  - Metabolism: Consolidate sessions to graph
  - Scene Multiplier: Generate scene variants

  UPDATED: Now wires existing orphaned components instead of placeholders
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';

  // Import existing components that were orphaned
  import VoiceTournamentLauncher from './VoiceTournamentLauncher.svelte';
  import ScaffoldGenerator from './ScaffoldGenerator.svelte';
  import HealthDashboard from './HealthDashboard.svelte';
  import SceneVariantGrid from './SceneVariantGrid.svelte';

  export let activeTab = 'voice-tournament';

  const dispatch = createEventDispatcher();

  // Tool status state
  let healthStatus = { conflicts: 0, warnings: 0 };
  let metabolismStatus = { uncommitted: 0, digesting: false };

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

  const tabs = [
    { id: 'voice-tournament', label: 'Voice Tournament', icon: 'mic', status: 'Ready' },
    { id: 'scaffold-generator', label: 'Scaffold Generator', icon: 'compass', status: 'Active' },
    { id: 'health-dashboard', label: 'Health Dashboard', icon: 'activity', status: null },
    { id: 'metabolism', label: 'Metabolism', icon: 'zap', status: null },
    { id: 'scene-multiplier', label: 'Scene Multiplier', icon: 'layers', status: 'Ready' }
  ];

  // Get dynamic status for tabs
  function getTabStatus(tab) {
    if (tab.id === 'health-dashboard') {
      if (healthStatus.conflicts > 0) {
        return `${healthStatus.conflicts} Conflicts`;
      }
      return 'All Clear';
    }
    if (tab.id === 'metabolism') {
      if (metabolismStatus.digesting) {
        return 'Digesting...';
      }
      if (metabolismStatus.uncommitted > 0) {
        return `${metabolismStatus.uncommitted} Pending`;
      }
      return 'Idle';
    }
    return tab.status;
  }

  function getStatusColor(tab) {
    if (tab.id === 'health-dashboard') {
      return healthStatus.conflicts > 0 ? 'var(--warning)' : 'var(--success)';
    }
    if (tab.id === 'metabolism') {
      if (metabolismStatus.digesting) return 'var(--accent-cyan)';
      if (metabolismStatus.uncommitted > 0) return 'var(--accent-gold)';
      return 'var(--text-muted)';
    }
    return 'var(--text-secondary)';
  }

  // Icons for each tab
  const tabIcons = {
    mic: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`,
    compass: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
    </svg>`,
    activity: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
    </svg>`,
    zap: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
    </svg>`,
    layers: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
      <polyline points="2 17 12 22 22 17"></polyline>
      <polyline points="2 12 12 17 22 12"></polyline>
    </svg>`
  };
</script>

<div class="studio-panel">
  <!-- Sidebar Navigation -->
  <nav class="studio-nav">
    <div class="nav-header">
      <h3>Studio Tools</h3>
    </div>
    <ul class="nav-list">
      {#each tabs as tab}
        <li>
          <button
            class="nav-item {activeTab === tab.id ? 'active' : ''}"
            on:click={() => activeTab = tab.id}
          >
            <span class="nav-icon">{@html tabIcons[tab.icon]}</span>
            <span class="nav-label">{tab.label}</span>
            {#if getTabStatus(tab)}
              <span class="status-badge" style="color: {getStatusColor(tab)}">
                {getTabStatus(tab)}
              </span>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <!-- Content Area -->
  <div class="studio-content">
    {#if activeTab === 'voice-tournament'}
      <!-- Voice Tournament - full component -->
      <VoiceTournamentLauncher />

    {:else if activeTab === 'scaffold-generator'}
      <!-- Scaffold Generator - full component -->
      <ScaffoldGenerator />

    {:else if activeTab === 'health-dashboard'}
      <!-- Health Dashboard - full component -->
      <HealthDashboard />

    {:else if activeTab === 'metabolism'}
      <div class="tool-content">
        <h2>Metabolism</h2>
        <p class="tool-description">Digest chat sessions into the knowledge graph.</p>

        <div class="metabolism-status">
          <div class="status-indicator {metabolismStatus.digesting ? 'active' : ''}">
            <span class="indicator-dot"></span>
            <span class="indicator-label">
              {metabolismStatus.digesting ? 'Digesting...' : metabolismStatus.uncommitted > 0 ? `${metabolismStatus.uncommitted} sessions pending` : 'All caught up'}
            </span>
          </div>
        </div>

        <button
          class="action-btn {metabolismStatus.digesting ? 'digesting' : ''}"
          on:click={runMetabolism}
          disabled={metabolismStatus.digesting || metabolismStatus.uncommitted === 0}
        >
          {#if metabolismStatus.digesting}
            <svg class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            Digesting...
          {:else}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
            </svg>
            Run Metabolism
          {/if}
        </button>
      </div>

    {:else if activeTab === 'scene-multiplier'}
      <!-- Scene Multiplier - full component -->
      <SceneVariantGrid />
    {/if}
  </div>
</div>

<style>
  .studio-panel {
    display: flex;
    height: 100%;
    min-height: 500px;
    background: var(--bg-secondary, #1a2027);
  }

  /* Navigation Sidebar */
  .studio-nav {
    width: 220px;
    flex-shrink: 0;
    background: var(--bg-primary, #0f1419);
    border-right: 1px solid var(--border, #2d3a47);
    display: flex;
    flex-direction: column;
  }

  .nav-header {
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .nav-header h3 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .nav-list {
    list-style: none;
    margin: 0;
    padding: var(--space-2, 8px);
    flex: 1;
    overflow-y: auto;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    width: 100%;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: transparent;
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
    text-align: left;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .nav-item:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .nav-item.active {
    background: var(--accent-gold-muted, rgba(212, 165, 116, 0.2));
    color: var(--accent-gold, #d4a574);
  }

  .nav-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .nav-label {
    flex: 1;
  }

  .status-badge {
    font-size: 9px;
    font-weight: var(--font-medium, 500);
    white-space: nowrap;
  }

  /* Content Area */
  .studio-content {
    flex: 1;
    padding: var(--space-6, 24px);
    overflow-y: auto;
  }

  .tool-content h2 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .tool-description {
    margin: 0 0 var(--space-6, 24px) 0;
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
  }

  /* Placeholder for unimplemented tools */
  .tool-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--space-10, 40px);
    background: var(--bg-tertiary, #242d38);
    border: 1px dashed var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    text-align: center;
  }

  .placeholder-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    margin-bottom: var(--space-4, 16px);
    background: var(--bg-primary, #0f1419);
    border-radius: var(--radius-full, 9999px);
    color: var(--text-muted, #6e7681);
  }

  .placeholder-icon :global(svg) {
    width: 24px;
    height: 24px;
  }

  .tool-placeholder p {
    margin: 0;
    color: var(--text-secondary, #8b949e);
  }

  .placeholder-hint {
    margin-top: var(--space-2, 8px) !important;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Health Dashboard */
  .health-summary {
    display: flex;
    gap: var(--space-4, 16px);
    margin-bottom: var(--space-6, 24px);
  }

  .health-stat {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-lg, 8px);
    border: 1px solid var(--border, #2d3a47);
  }

  .health-stat.warning {
    border-color: var(--warning, #d29922);
  }

  .health-stat.success {
    border-color: var(--success, #3fb950);
  }

  .stat-value {
    font-size: var(--text-2xl, 24px);
    font-weight: var(--font-bold, 700);
    color: var(--text-primary, #e6edf3);
  }

  .health-stat.warning .stat-value {
    color: var(--warning, #d29922);
  }

  .health-stat.success .stat-value {
    color: var(--success, #3fb950);
  }

  .stat-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  /* Metabolism */
  .metabolism-status {
    margin-bottom: var(--space-6, 24px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-lg, 8px);
    border: 1px solid var(--border, #2d3a47);
  }

  .status-indicator {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .indicator-dot {
    width: 8px;
    height: 8px;
    border-radius: var(--radius-full, 9999px);
    background: var(--text-muted, #6e7681);
  }

  .status-indicator.active .indicator-dot {
    background: var(--accent-cyan, #58a6ff);
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  .indicator-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  /* Action button */
  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--accent-gold, #d4a574);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .action-btn:hover:not(:disabled) {
    background: var(--accent-gold-hover, #e0b585);
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-btn.digesting {
    background: var(--accent-cyan, #58a6ff);
  }

  .action-btn .spin {
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
