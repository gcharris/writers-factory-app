<!--
  StudioPanel.svelte - Mode-aware action cards

  Shows different action cards based on the current Foreman mode:
  - ARCHITECT: Create Story Bible, Define Beats, Build Protagonist
  - VOICE_CALIBRATION: Launch Tournament, Review Variants, Generate Bundle
  - DIRECTOR: Create Scaffold, Generate Scene, Enhance Scene
  - EDITOR: Final polish tools
-->
<script>
  import { foremanMode, foremanActive } from '$lib/stores';

  // Card definitions by mode
  const modeCards = {
    ARCHITECT: [
      {
        id: 'create-story-bible',
        title: 'Create Story Bible',
        description: 'Define your novel\'s foundation: mindset, audience, premise, theme',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>`,
        action: () => console.log('Open Story Bible wizard'),
        status: 'ready'
      },
      {
        id: 'define-beats',
        title: 'Define Beat Sheet',
        description: '15-beat Save the Cat! structure with percentage targets',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>`,
        action: () => console.log('Open Beat Sheet editor'),
        status: 'locked'
      },
      {
        id: 'build-protagonist',
        title: 'Build Protagonist',
        description: 'Fatal Flaw, The Lie, character arc progression',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>`,
        action: () => console.log('Open Character builder'),
        status: 'locked'
      },
      {
        id: 'register-notebooks',
        title: 'Register NotebookLM',
        description: 'Connect World, Voice, and Craft notebooks',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
        </svg>`,
        action: () => console.log('Open NotebookLM registration'),
        status: 'optional'
      }
    ],
    VOICE_CALIBRATION: [
      {
        id: 'launch-tournament',
        title: 'Launch Voice Tournament',
        description: 'Run multi-model competition to discover your voice',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="23"></line>
        </svg>`,
        action: () => console.log('Open Voice Tournament'),
        status: 'ready'
      },
      {
        id: 'review-variants',
        title: 'Review Variants',
        description: 'Compare 15-25 voice variants in grid view',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>`,
        action: () => console.log('Open Variant Grid'),
        status: 'locked'
      },
      {
        id: 'generate-bundle',
        title: 'Generate Voice Bundle',
        description: 'Create Gold Standard, Anti-Patterns, Phase Evolution',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
        </svg>`,
        action: () => console.log('Generate Voice Bundle'),
        status: 'locked'
      }
    ],
    DIRECTOR: [
      {
        id: 'create-scaffold',
        title: 'Create Scaffold',
        description: 'Generate strategic context for your next scene',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>`,
        action: () => console.log('Open Scaffold Generator'),
        status: 'ready'
      },
      {
        id: 'generate-scene',
        title: 'Generate Scene',
        description: 'Run tournament with 15 variants (3 models x 5 strategies)',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="23 7 16 12 23 17 23 7"></polygon>
          <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
        </svg>`,
        action: () => console.log('Open Scene Generator'),
        status: 'ready'
      },
      {
        id: 'enhance-scene',
        title: 'Enhance Scene',
        description: 'Action Prompt (85+) or 6-Pass Enhancement (70-84)',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>`,
        action: () => console.log('Open Enhancement Panel'),
        status: 'locked'
      },
      {
        id: 'view-health',
        title: 'View Health',
        description: 'Check manuscript structure and pacing',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
        </svg>`,
        action: () => console.log('Open Health Dashboard'),
        status: 'ready'
      }
    ],
    EDITOR: [
      {
        id: 'final-review',
        title: 'Final Review',
        description: 'Full manuscript analysis and polish',
        icon: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>`,
        action: () => console.log('Open Final Review'),
        status: 'ready'
      }
    ]
  };

  // Get cards for current mode
  $: currentCards = $foremanMode ? modeCards[$foremanMode] || [] : [];

  // Status colors and labels
  const statusConfig = {
    ready: { color: 'var(--success, #3fb950)', label: 'Ready' },
    locked: { color: 'var(--text-muted, #6e7681)', label: 'Locked' },
    active: { color: 'var(--accent-cyan, #58a6ff)', label: 'In Progress' },
    optional: { color: 'var(--warning, #d29922)', label: 'Optional' }
  };
</script>

<div class="studio-panel">
  {#if !$foremanActive}
    <div class="welcome-state">
      <div class="welcome-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
        </svg>
      </div>
      <h3>Welcome to Writers Factory</h3>
      <p>Start a new project with the Foreman to begin your writing journey.</p>
      <p class="hint">Use the Foreman panel to create a new project.</p>
    </div>
  {:else if currentCards.length === 0}
    <div class="empty-state">
      <p>No actions available in this mode.</p>
    </div>
  {:else}
    <div class="card-grid">
      {#each currentCards as card}
        <button
          class="action-card {card.status}"
          on:click={card.action}
          disabled={card.status === 'locked'}
        >
          <div class="card-icon" style="color: {statusConfig[card.status].color}">
            {@html card.icon}
          </div>
          <div class="card-content">
            <h4 class="card-title">{card.title}</h4>
            <p class="card-description">{card.description}</p>
          </div>
          <div class="card-status">
            <span class="status-dot" style="background: {statusConfig[card.status].color}"></span>
            <span class="status-label">{statusConfig[card.status].label}</span>
          </div>
        </button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .studio-panel {
    padding: var(--space-4, 16px);
    height: 100%;
  }

  .welcome-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    height: 100%;
    padding: var(--space-4, 16px);
  }

  .welcome-icon {
    margin-bottom: var(--space-4, 16px);
    color: var(--accent-gold, #d4a574);
  }

  .welcome-state h3 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .welcome-state p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }

  .welcome-state .hint {
    margin-top: var(--space-4, 16px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .card-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .action-card {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    text-align: left;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .action-card:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .action-card:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .card-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-md, 6px);
  }

  .card-content {
    flex: 1;
    min-width: 0;
  }

  .card-title {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .card-description {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-normal, 1.5);
  }

  .card-status {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    flex-shrink: 0;
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  .status-label {
    font-size: 9px;
    font-weight: var(--font-medium, 500);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
  }
</style>
