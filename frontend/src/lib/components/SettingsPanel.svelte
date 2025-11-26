<!--
  SettingsPanel.svelte - Main settings modal with tabbed navigation

  Contains all settings sub-components organized by category:
  - Squad (AI Model Squad) - P0 Critical
  - Agents (API Keys) - P0 Critical
  - Orchestrator (Quality Tiers) - P0 Critical
  - Scoring (Rubric Weights) - P2
  - Voice (Strictness) - P2
  - Enhancement (Thresholds) - P2
  - Foreman (Behavior) - P2
  - Health Checks (Validation) - P2
  - Advanced - P3
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import SettingsSquad from './Settings/SettingsSquad.svelte';
  import SettingsAgents from './Settings/SettingsAgents.svelte';
  import SettingsOrchestrator from './Settings/SettingsOrchestrator.svelte';
  import SettingsScoring from './Settings/SettingsScoring.svelte';
  import SettingsVoice from './Settings/SettingsVoice.svelte';
  import SettingsEnhancement from './Settings/SettingsEnhancement.svelte';
  import SettingsForeman from './Settings/SettingsForeman.svelte';
  import SettingsHealth from './Settings/SettingsHealth.svelte';
  import SettingsAdvanced from './Settings/SettingsAdvanced.svelte';

  export let activeTab = 'squad';

  const dispatch = createEventDispatcher();

  const tabs = [
    { id: 'squad', label: 'Squad', icon: 'users', priority: 'P0' },
    { id: 'agents', label: 'API Keys', icon: 'key', priority: 'P0' },
    { id: 'orchestrator', label: 'AI Model', icon: 'cpu', priority: 'P0' },
    { id: 'scoring', label: 'Scoring', icon: 'chart', priority: 'P2' },
    { id: 'voice', label: 'Voice', icon: 'mic', priority: 'P2' },
    { id: 'enhancement', label: 'Enhancement', icon: 'wand', priority: 'P2' },
    { id: 'foreman', label: 'Foreman', icon: 'bot', priority: 'P2' },
    { id: 'health', label: 'Health Checks', icon: 'heart', priority: 'P2' },
    { id: 'advanced', label: 'Advanced', icon: 'settings', priority: 'P3' },
  ];

  // Icons for each tab
  const tabIcons = {
    users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
      <circle cx="9" cy="7" r="4"></circle>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
    </svg>`,
    key: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
    </svg>`,
    cpu: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
      <rect x="9" y="9" width="6" height="6"></rect>
      <line x1="9" y1="1" x2="9" y2="4"></line>
      <line x1="15" y1="1" x2="15" y2="4"></line>
      <line x1="9" y1="20" x2="9" y2="23"></line>
      <line x1="15" y1="20" x2="15" y2="23"></line>
      <line x1="20" y1="9" x2="23" y2="9"></line>
      <line x1="20" y1="14" x2="23" y2="14"></line>
      <line x1="1" y1="9" x2="4" y2="9"></line>
      <line x1="1" y1="14" x2="4" y2="14"></line>
    </svg>`,
    chart: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <line x1="18" y1="20" x2="18" y2="10"></line>
      <line x1="12" y1="20" x2="12" y2="4"></line>
      <line x1="6" y1="20" x2="6" y2="14"></line>
    </svg>`,
    mic: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`,
    wand: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M15 4V2"></path>
      <path d="M15 16v-2"></path>
      <path d="M8 9h2"></path>
      <path d="M20 9h2"></path>
      <path d="M17.8 11.8 19 13"></path>
      <path d="M15 9h0"></path>
      <path d="M17.8 6.2 19 5"></path>
      <path d="m3 21 9-9"></path>
      <path d="M12.2 6.2 11 5"></path>
    </svg>`,
    bot: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <rect x="3" y="11" width="18" height="10" rx="2"></rect>
      <circle cx="12" cy="5" r="2"></circle>
      <path d="M12 7v4"></path>
      <line x1="8" y1="16" x2="8" y2="16"></line>
      <line x1="16" y1="16" x2="16" y2="16"></line>
    </svg>`,
    heart: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
    </svg>`,
    settings: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
    </svg>`
  };
</script>

<div class="settings-panel">
  <!-- Sidebar Navigation -->
  <nav class="settings-nav">
    <div class="nav-header">
      <h3>Settings</h3>
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
            {#if tab.priority === 'P0'}
              <span class="priority-badge critical">Required</span>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <!-- Content Area -->
  <div class="settings-content">
    {#if activeTab === 'squad'}
      <SettingsSquad />
    {:else if activeTab === 'agents'}
      <SettingsAgents />
    {:else if activeTab === 'orchestrator'}
      <SettingsOrchestrator />
    {:else if activeTab === 'scoring'}
      <SettingsScoring />
    {:else if activeTab === 'voice'}
      <SettingsVoice />
    {:else if activeTab === 'enhancement'}
      <SettingsEnhancement />
    {:else if activeTab === 'foreman'}
      <SettingsForeman />
    {:else if activeTab === 'health'}
      <SettingsHealth />
    {:else if activeTab === 'advanced'}
      <SettingsAdvanced />
    {/if}
  </div>
</div>

<style>
  .settings-panel {
    display: flex;
    height: 100%;
    min-height: 500px;
    background: var(--bg-secondary, #1a2027);
  }

  /* Navigation Sidebar */
  .settings-nav {
    width: 200px;
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
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    color: var(--accent-cyan, #58a6ff);
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

  .priority-badge {
    padding: 2px 6px;
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
  }

  .priority-badge.critical {
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    color: var(--error, #f85149);
  }

  /* Content Area */
  .settings-content {
    flex: 1;
    padding: var(--space-6, 24px);
    overflow-y: auto;
  }

</style>
