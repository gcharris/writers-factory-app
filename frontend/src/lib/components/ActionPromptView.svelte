<!--
  ActionPromptView.svelte - Surgical Fix Display

  Displays Action Prompt fixes for high-scoring scenes (85+):
  - OLD → NEW text replacements
  - Reason for each fix
  - Priority levels (critical, high, medium)
  - Accept/reject individual fixes
  - Preview changes before applying
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import {
    actionPromptFixes,
    selectedFixes,
    currentSceneContent,
    enhancementLoading
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let fixes = [];
  export let currentScore = 0;
  export let estimatedScore = 0;
  export let sceneId = '';
  export let sceneContent = '';

  // Local state
  let selectedFixIds = [];
  let applying = false;
  let previewContent = '';
  let showPreview = false;
  let error = null;

  // Use props or store
  $: displayFixes = fixes.length > 0 ? fixes : $actionPromptFixes;
  $: content = sceneContent || $currentSceneContent;

  // Priority configuration
  const priorities = {
    critical: { label: 'Critical', color: '#f85149', icon: '!!' },
    high: { label: 'High', color: '#d29922', icon: '!' },
    medium: { label: 'Medium', color: '#58a6ff', icon: '-' }
  };

  // Category icons
  const categories = {
    voice: { label: 'Voice', color: '#d4a574' },
    character: { label: 'Character', color: '#a371f7' },
    metaphor: { label: 'Metaphor', color: '#58a6ff' },
    anti_pattern: { label: 'Anti-Pattern', color: '#3fb950' },
    phase: { label: 'Phase', color: '#d29922' }
  };

  // Toggle fix selection
  function toggleFix(fixId) {
    if (selectedFixIds.includes(fixId)) {
      selectedFixIds = selectedFixIds.filter(id => id !== fixId);
    } else {
      selectedFixIds = [...selectedFixIds, fixId];
    }
    $selectedFixes = displayFixes.filter(f => selectedFixIds.includes(f.id));
  }

  // Select all fixes
  function selectAll() {
    selectedFixIds = displayFixes.map(f => f.id);
    $selectedFixes = displayFixes;
  }

  // Clear selection
  function clearSelection() {
    selectedFixIds = [];
    $selectedFixes = [];
  }

  // Preview changes
  function previewChanges() {
    const selectedFixesData = displayFixes.filter(f => selectedFixIds.includes(f.id));
    previewContent = content;

    // Apply fixes in reverse order of line number to preserve positions
    const sortedFixes = [...selectedFixesData].sort((a, b) => b.line - a.line);
    for (const fix of sortedFixes) {
      previewContent = previewContent.replace(fix.old_text, fix.new_text);
    }

    showPreview = true;
  }

  // Apply selected fixes
  async function applyFixes() {
    if (selectedFixIds.length === 0) return;

    applying = true;
    $enhancementLoading = true;
    error = null;

    try {
      const fixesToApply = displayFixes
        .filter(f => selectedFixIds.includes(f.id))
        .map(f => ({ old_text: f.old_text, new_text: f.new_text }));

      const result = await apiClient.applyFixes(
        sceneId || 'scene_1',
        content,
        fixesToApply
      );

      $currentSceneContent = result.updated_content;
      dispatch('applied', {
        content: result.updated_content,
        fixesApplied: result.fixes_applied,
        newScore: result.new_score
      });
    } catch (err) {
      error = err.message || 'Failed to apply fixes';
    } finally {
      applying = false;
      $enhancementLoading = false;
    }
  }

  // Close handler
  function close() {
    dispatch('close');
  }

  // Close preview
  function closePreview() {
    showPreview = false;
    previewContent = '';
  }

  // Get category config
  function getCategoryConfig(category) {
    return categories[category] || { label: category, color: '#8b949e' };
  }

  // Get priority config
  function getPriorityConfig(priority) {
    return priorities[priority] || priorities.medium;
  }
</script>

<div class="action-prompt-view">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
      </div>
      <div>
        <h2>Action Prompt</h2>
        <p class="subtitle">{displayFixes.length} surgical fixes available</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  <!-- Score Improvement -->
  <div class="score-improvement">
    <div class="score-item">
      <span class="score-label">Current</span>
      <span class="score-value current">{currentScore}</span>
    </div>
    <div class="score-arrow">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="5" y1="12" x2="19" y2="12"></line>
        <polyline points="12 5 19 12 12 19"></polyline>
      </svg>
    </div>
    <div class="score-item">
      <span class="score-label">Estimated</span>
      <span class="score-value estimated">{estimatedScore}</span>
    </div>
    <div class="score-diff">
      +{estimatedScore - currentScore} points
    </div>
  </div>

  <!-- Error display -->
  {#if error}
    <div class="error-banner">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
      </svg>
      <span>{error}</span>
      <button on:click={() => error = null}>Dismiss</button>
    </div>
  {/if}

  <!-- Selection Controls -->
  <div class="selection-controls">
    <div class="selection-info">
      <span>{selectedFixIds.length} of {displayFixes.length} selected</span>
    </div>
    <div class="selection-actions">
      <button class="link-btn" on:click={selectAll}>Select All</button>
      <button class="link-btn" on:click={clearSelection}>Clear</button>
    </div>
  </div>

  <!-- Fixes List -->
  <div class="fixes-list">
    {#each displayFixes as fix}
      {@const priority = getPriorityConfig(fix.priority)}
      {@const category = getCategoryConfig(fix.category)}
      <div
        class="fix-card"
        class:selected={selectedFixIds.includes(fix.id)}
        on:click={() => toggleFix(fix.id)}
        on:keydown={(e) => e.key === 'Enter' && toggleFix(fix.id)}
        role="button"
        tabindex="0"
      >
        <div class="fix-header">
          <div class="fix-checkbox">
            {#if selectedFixIds.includes(fix.id)}
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            {/if}
          </div>
          <div class="fix-meta">
            <span class="priority-badge" style="--priority-color: {priority.color}">
              {priority.label}
            </span>
            <span class="category-badge" style="--category-color: {category.color}">
              {category.label}
            </span>
            <span class="line-number">Line {fix.line}</span>
          </div>
        </div>

        <div class="fix-content">
          <div class="fix-old">
            <span class="fix-label">OLD:</span>
            <span class="fix-text">{fix.old_text}</span>
          </div>
          <div class="fix-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <polyline points="19 12 12 19 5 12"></polyline>
            </svg>
          </div>
          <div class="fix-new">
            <span class="fix-label">NEW:</span>
            <span class="fix-text">{fix.new_text}</span>
          </div>
        </div>

        <div class="fix-reason">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span>{fix.reason}</span>
        </div>
      </div>
    {/each}
  </div>

  <!-- Actions -->
  <div class="actions">
    <button class="secondary-btn" on:click={previewChanges} disabled={selectedFixIds.length === 0}>
      Preview Changes
    </button>
    <button
      class="primary-btn"
      on:click={applyFixes}
      disabled={selectedFixIds.length === 0 || applying}
    >
      {#if applying}
        <span class="spinner"></span>
        Applying...
      {:else}
        Apply {selectedFixIds.length} Fix{selectedFixIds.length !== 1 ? 'es' : ''}
      {/if}
    </button>
  </div>

  <!-- Preview Modal -->
  {#if showPreview}
    <div class="preview-overlay" on:click={closePreview} on:keydown={(e) => e.key === 'Escape' && closePreview()} role="button" tabindex="0">
      <div class="preview-modal" on:click|stopPropagation role="dialog">
        <div class="preview-header">
          <h3>Preview Changes</h3>
          <button class="close-preview" on:click={closePreview}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="preview-content">
          <pre>{previewContent}</pre>
        </div>
        <div class="preview-actions">
          <button class="secondary-btn" on:click={closePreview}>Close</button>
          <button class="primary-btn" on:click={() => { closePreview(); applyFixes(); }}>
            Apply Changes
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .action-prompt-view {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 85vh;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .header-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--success, #3fb950);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .subtitle {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Score Improvement */
  .score-improvement {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .score-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .score-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .score-value {
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-bold, 700);
  }

  .score-value.current {
    color: var(--text-secondary, #8b949e);
  }

  .score-value.estimated {
    color: var(--success, #3fb950);
  }

  .score-arrow {
    color: var(--text-muted, #6e7681);
  }

  .score-arrow svg {
    width: 20px;
    height: 20px;
  }

  .score-diff {
    padding: 4px 12px;
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-radius: var(--radius-full, 9999px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--success, #3fb950);
  }

  /* Error Banner */
  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    border-bottom: 1px solid var(--error, #f85149);
    color: var(--error, #f85149);
    font-size: var(--text-sm, 12px);
  }

  .error-banner svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .error-banner span {
    flex: 1;
  }

  .error-banner button {
    padding: 4px 8px;
    background: transparent;
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-sm, 4px);
    color: var(--error, #f85149);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
  }

  /* Selection Controls */
  .selection-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .selection-info {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .selection-actions {
    display: flex;
    gap: var(--space-3, 12px);
  }

  .link-btn {
    background: transparent;
    border: none;
    font-size: var(--text-xs, 11px);
    color: var(--accent-cyan, #58a6ff);
    cursor: pointer;
  }

  .link-btn:hover {
    text-decoration: underline;
  }

  /* Fixes List */
  .fixes-list {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .fix-card {
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-3, 12px);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .fix-card:hover {
    border-color: var(--accent-cyan, #58a6ff);
  }

  .fix-card.selected {
    border-color: var(--success, #3fb950);
    background: var(--success-muted, rgba(63, 185, 80, 0.1));
  }

  .fix-header {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .fix-checkbox {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-input, #161b22);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    flex-shrink: 0;
  }

  .fix-card.selected .fix-checkbox {
    background: var(--success, #3fb950);
    border-color: var(--success, #3fb950);
  }

  .fix-checkbox svg {
    width: 12px;
    height: 12px;
    color: var(--bg-primary, #0f1419);
  }

  .fix-meta {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    flex-wrap: wrap;
  }

  .priority-badge,
  .category-badge {
    padding: 2px 6px;
    border-radius: var(--radius-full, 9999px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
  }

  .priority-badge {
    background: color-mix(in srgb, var(--priority-color) 20%, transparent);
    color: var(--priority-color);
  }

  .category-badge {
    background: color-mix(in srgb, var(--category-color) 20%, transparent);
    color: var(--category-color);
  }

  .line-number {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .fix-content {
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-sm, 4px);
    padding: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .fix-old,
  .fix-new {
    display: flex;
    gap: var(--space-2, 8px);
    align-items: flex-start;
  }

  .fix-old {
    margin-bottom: var(--space-2, 8px);
  }

  .fix-label {
    font-size: 10px;
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
    flex-shrink: 0;
    width: 36px;
  }

  .fix-old .fix-label {
    color: var(--error, #f85149);
  }

  .fix-new .fix-label {
    color: var(--success, #3fb950);
  }

  .fix-text {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono);
    color: var(--text-secondary, #8b949e);
    line-height: 1.5;
  }

  .fix-old .fix-text {
    text-decoration: line-through;
    opacity: 0.7;
  }

  .fix-arrow {
    display: flex;
    justify-content: center;
    padding: var(--space-1, 4px) 0;
    color: var(--text-muted, #6e7681);
  }

  .fix-arrow svg {
    width: 14px;
    height: 14px;
  }

  .fix-reason {
    display: flex;
    align-items: flex-start;
    gap: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .fix-reason svg {
    width: 14px;
    height: 14px;
    flex-shrink: 0;
    margin-top: 1px;
  }

  /* Actions */
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3, 12px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .secondary-btn,
  .primary-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .secondary-btn {
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .secondary-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .secondary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .primary-btn {
    background: var(--success, #3fb950);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .primary-btn:hover:not(:disabled) {
    background: var(--success-hover, #56d364);
  }

  .primary-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Spinner */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Preview Modal */
  .preview-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: var(--z-modal, 400);
  }

  .preview-modal {
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .preview-header h3 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .close-preview {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .close-preview svg {
    width: 16px;
    height: 16px;
  }

  .preview-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .preview-content pre {
    margin: 0;
    font-family: var(--font-ui);
    font-size: var(--text-sm, 12px);
    line-height: 1.7;
    color: var(--text-secondary, #8b949e);
    white-space: pre-wrap;
  }

  .preview-actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3, 12px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }
</style>
