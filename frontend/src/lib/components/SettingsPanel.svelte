<!--
  SettingsPanel.svelte - Main settings modal with tabbed navigation

  Tab order (simplified for writers):
  - Assistant (personalization)
  - AI Model (quality tier selection)
  - API Keys (advanced - for power users)
  - Voice (style settings)
  - Advanced (power user options)

  Setup wizard can be re-run via wand icon in header
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import SettingsAgents from './Settings/SettingsAgents.svelte';
  import SettingsOrchestrator from './Settings/SettingsOrchestrator.svelte';
  import SettingsVoice from './Settings/SettingsVoice.svelte';
  import SettingsAdvanced from './Settings/SettingsAdvanced.svelte';
  import SettingsAssistant from './Settings/SettingsAssistant.svelte';
  import OnboardingWizard from './Onboarding/OnboardingWizard.svelte';
  import { hasCompletedOnboarding } from '$lib/stores';

  export let activeTab = 'assistant';

  const dispatch = createEventDispatcher();

  let showSetupWizard = false;

  // Tab order for writers
  const tabs = [
    { id: 'assistant', label: 'Assistant', icon: 'sparkles' },
    { id: 'orchestrator', label: 'AI Model', icon: 'cpu' },
    { id: 'agents', label: 'API Keys', icon: 'key', sublabel: 'Advanced' },
    { id: 'voice', label: 'Voice', icon: 'mic' },
    { id: 'advanced', label: 'Advanced', icon: 'settings' },
    { id: 'setup', label: 'Re-run Setup Wizard', icon: 'wand', action: 'openSetupWizard' },
  ];

  // Icons for each tab (only icons used in simplified tabs)
  const tabIcons = {
    sparkles: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
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
    mic: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
      <line x1="12" y1="19" x2="12" y2="23"></line>
      <line x1="8" y1="23" x2="16" y2="23"></line>
    </svg>`,
    settings: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="3"></circle>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
    </svg>`,
    users: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
      <circle cx="9" cy="7" r="4"></circle>
      <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
      <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
    </svg>`,
    wand: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M15 4V2"></path>
      <path d="M15 16v-2"></path>
      <path d="M8 9h2"></path>
      <path d="M20 9h2"></path>
      <path d="M17.8 11.8L19 13"></path>
      <path d="M15 9h0"></path>
      <path d="M17.8 6.2L19 5"></path>
      <path d="m3 21 9-9"></path>
      <path d="M12.2 6.2L11 5"></path>
    </svg>`
  };

  function openSetupWizard() {
    showSetupWizard = true;
  }

  function closeSetupWizard() {
    showSetupWizard = false;
  }
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
            class="nav-item {activeTab === tab.id && !tab.action ? 'active' : ''}"
            on:click={() => {
              if (tab.action === 'openSetupWizard') {
                openSetupWizard();
              } else {
                activeTab = tab.id;
              }
            }}
          >
            <span class="nav-icon">{@html tabIcons[tab.icon]}</span>
            <span class="nav-label">{tab.label}</span>
            {#if tab.sublabel}
              <span class="sublabel">{tab.sublabel}</span>
            {/if}
            {#if tab.id === 'setup' && $hasCompletedOnboarding}
              <span class="checkmark-inline">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </span>
            {/if}
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <!-- Content Area -->
  <div class="settings-content">
    {#if activeTab === 'assistant'}
      <SettingsAssistant />
    {:else if activeTab === 'orchestrator'}
      <SettingsOrchestrator />
    {:else if activeTab === 'agents'}
      <SettingsAgents />
    {:else if activeTab === 'voice'}
      <SettingsVoice />
    {:else if activeTab === 'advanced'}
      <SettingsAdvanced />
    {/if}
  </div>
</div>

<!-- Setup Wizard Modal -->
{#if showSetupWizard}
  <div class="wizard-overlay" on:click={closeSetupWizard} on:keydown={(e) => e.key === 'Escape' && closeSetupWizard()} role="button" tabindex="0">
    <div class="wizard-container" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true">
      <OnboardingWizard on:close={closeSetupWizard} on:complete={closeSetupWizard} />
    </div>
  </div>
{/if}

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
    padding: var(--space-3, 12px) var(--space-4, 16px);
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

  .sublabel {
    padding: 2px 6px;
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-medium, 500);
    color: var(--text-muted, #6e7681);
  }

  .checkmark-inline {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent-green, #3fb950);
    margin-left: auto;
  }

  /* Content Area */
  .settings-content {
    flex: 1;
    padding: var(--space-6, 24px);
    overflow-y: auto;
  }

  /* Wizard Overlay */
  .wizard-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .wizard-container {
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 12px);
    border: 1px solid var(--border, #2d3a47);
    max-width: 900px;
    max-height: 90vh;
    width: 90%;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  }

</style>
