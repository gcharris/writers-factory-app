<!--
  ForemanAction.svelte - Rich Display for Foreman Actions

  Renders Foreman actions with appropriate styling:
  - save_decision: Shows category, key, value saved
  - advance_to_voice_calibration: Mode transition notification
  - query_notebook: NotebookLM query with loading state
  - start_voice_tournament: Tournament initiation
  - save_template: Template creation/update

  Part of Track A: Minimal Testing Path
-->
<script>
  /**
   * @typedef {Object} ForemanAction
   * @property {string} action - Action type
   * @property {string} [category] - For save_decision
   * @property {string} [key] - For save_decision
   * @property {*} [value] - For save_decision
   * @property {string} [notebook_id] - For query_notebook
   * @property {string} [query] - For query_notebook
   * @property {string} [template_name] - For save_template
   */

  /** @type {ForemanAction} */
  export let action;

  /** @type {boolean} Show compact version */
  export let compact = false;

  // Action configuration
  const ACTION_CONFIG = {
    save_decision: {
      icon: '💾',
      label: 'Decision Saved',
      color: 'var(--success, #3fb950)',
      bgColor: 'rgba(63, 185, 80, 0.1)'
    },
    advance_to_voice_calibration: {
      icon: '🎭',
      label: 'Advancing to Voice Calibration',
      color: 'var(--accent-purple, #a371f7)',
      bgColor: 'rgba(163, 113, 247, 0.1)'
    },
    advance_to_director: {
      icon: '🎬',
      label: 'Advancing to Director Mode',
      color: 'var(--success, #3fb950)',
      bgColor: 'rgba(63, 185, 80, 0.1)'
    },
    advance_to_editor: {
      icon: '✨',
      label: 'Advancing to Editor Mode',
      color: 'var(--accent-gold, #d4a574)',
      bgColor: 'rgba(212, 165, 116, 0.1)'
    },
    query_notebook: {
      icon: '📓',
      label: 'Querying NotebookLM',
      color: 'var(--accent-cyan, #58a6ff)',
      bgColor: 'rgba(88, 166, 255, 0.1)'
    },
    start_voice_tournament: {
      icon: '🏆',
      label: 'Starting Voice Tournament',
      color: 'var(--accent-purple, #a371f7)',
      bgColor: 'rgba(163, 113, 247, 0.1)'
    },
    save_template: {
      icon: '📄',
      label: 'Template Updated',
      color: 'var(--accent-cyan, #58a6ff)',
      bgColor: 'rgba(88, 166, 255, 0.1)'
    },
    run_health_check: {
      icon: '🏥',
      label: 'Running Health Check',
      color: 'var(--warning, #d29922)',
      bgColor: 'rgba(210, 153, 34, 0.1)'
    }
  };

  // Get category icon
  function getCategoryIcon(category) {
    const icons = {
      character: '👤',
      constraint: '⚠️',
      world: '🌍',
      theme: '📖',
      plot: '📊',
      voice: '🎤',
      structure: '🏗️'
    };
    return icons[category?.toLowerCase()] || '📌';
  }

  $: config = ACTION_CONFIG[action?.action] || {
    icon: '⚡',
    label: action?.action?.replace(/_/g, ' ') || 'Action',
    color: 'var(--text-secondary)',
    bgColor: 'var(--bg-tertiary)'
  };
</script>

{#if action}
  <div
    class="foreman-action"
    class:compact
    style="--action-color: {config.color}; --action-bg: {config.bgColor}"
  >
    <div class="action-header">
      <span class="action-icon">{config.icon}</span>
      <span class="action-label">{config.label}</span>
    </div>

    <!-- Action-specific content -->
    {#if action.action === 'save_decision' && !compact}
      <div class="action-details">
        <div class="decision-item">
          <span class="decision-category">
            <span class="cat-icon">{getCategoryIcon(action.category)}</span>
            {action.category}
          </span>
          <span class="decision-arrow">→</span>
          <span class="decision-key">{action.key}</span>
        </div>
        {#if action.value}
          <div class="decision-value">
            "{typeof action.value === 'string' ? action.value : JSON.stringify(action.value)}"
          </div>
        {/if}
      </div>

    {:else if action.action === 'query_notebook' && !compact}
      <div class="action-details">
        <div class="notebook-query">
          <span class="query-label">Query:</span>
          <span class="query-text">"{action.query}"</span>
        </div>
        {#if action.notebook_id}
          <div class="notebook-id">
            Notebook: {action.notebook_id}
          </div>
        {/if}
      </div>

    {:else if action.action === 'save_template' && !compact}
      <div class="action-details">
        <div class="template-info">
          <span class="template-icon">📄</span>
          <span class="template-name">{action.template_name}</span>
        </div>
      </div>

    {:else if action.action?.startsWith('advance_to')}
      <div class="action-details mode-transition">
        <span class="transition-text">Story Bible Complete! Moving to next phase...</span>
      </div>
    {/if}
  </div>
{/if}

<style>
  .foreman-action {
    background: var(--action-bg);
    border: 1px solid var(--action-color);
    border-left: 3px solid var(--action-color);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    margin: var(--space-2, 8px) 0;
  }

  .foreman-action.compact {
    padding: var(--space-1, 4px) var(--space-2, 8px);
    margin: var(--space-1, 4px) 0;
  }

  .action-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .action-icon {
    font-size: 14px;
  }

  .compact .action-icon {
    font-size: 12px;
  }

  .action-label {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--action-color);
  }

  .compact .action-label {
    font-size: var(--text-xs, 11px);
  }

  .action-details {
    margin-top: var(--space-2, 8px);
    padding-top: var(--space-2, 8px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  /* Decision styling */
  .decision-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #c9d1d9);
  }

  .decision-category {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    text-transform: capitalize;
    color: var(--text-muted, #8b949e);
  }

  .cat-icon {
    font-size: 12px;
  }

  .decision-arrow {
    color: var(--text-muted, #8b949e);
  }

  .decision-key {
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .decision-value {
    margin-top: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #c9d1d9);
    font-style: italic;
    padding-left: var(--space-3, 12px);
    border-left: 2px solid var(--border, #2d3a47);
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Notebook query styling */
  .notebook-query {
    font-size: var(--text-xs, 11px);
  }

  .query-label {
    color: var(--text-muted, #8b949e);
    margin-right: var(--space-1, 4px);
  }

  .query-text {
    color: var(--text-secondary, #c9d1d9);
    font-style: italic;
  }

  .notebook-id {
    margin-top: var(--space-1, 4px);
    font-size: 10px;
    color: var(--text-muted, #8b949e);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  /* Template styling */
  .template-info {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
  }

  .template-icon {
    font-size: 12px;
  }

  .template-name {
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  /* Mode transition */
  .mode-transition {
    text-align: center;
  }

  .transition-text {
    font-size: var(--text-xs, 11px);
    color: var(--action-color);
    font-weight: var(--font-medium, 500);
  }
</style>
