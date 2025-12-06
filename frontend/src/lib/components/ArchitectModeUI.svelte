<!--
  ArchitectModeUI.svelte - Mode-specific context panel for ARCHITECT mode

  Displayed in the Foreman panel when mode is ARCHITECT.
  Shows:
  - Work Order progress tracker
  - Quick links to templates
  - NotebookLM registration summary
  - Mode transition guidance
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import {
    foremanMode,
    foremanProjectTitle,
    foremanProtagonist,
    storyBibleStatus,
    registeredNotebooks,
    showStoryBibleWizard,
    showNotebookRegistration,
    activeModal
  } from '$lib/stores';
  import WorkOrderTracker from './WorkOrderTracker.svelte';

  const dispatch = createEventDispatcher();

  // Quick actions
  function openStoryBibleWizard() {
    $showStoryBibleWizard = true;
    $activeModal = 'story-bible';
    dispatch('action', { type: 'open-wizard' });
  }

  function openNotebookRegistration() {
    $showNotebookRegistration = true;
    $activeModal = 'notebook-registration';
    dispatch('action', { type: 'open-notebooks' });
  }

  function handleTemplateEdit(event) {
    dispatch('edit-template', event.detail);
  }

  function handleAdvanceMode(event) {
    dispatch('advance-mode', event.detail);
  }

  // Computed values
  $: hasNotebooks = $registeredNotebooks.length > 0;
  $: notebookSummary = $registeredNotebooks.length > 0
    ? `${$registeredNotebooks.length} notebook${$registeredNotebooks.length > 1 ? 's' : ''} registered`
    : 'No notebooks registered';
</script>

<div class="architect-mode-ui">
  <!-- Project Header -->
  {#if $foremanProjectTitle}
    <div class="project-header">
      <div class="project-info">
        <h4 class="project-title">{$foremanProjectTitle}</h4>
        {#if $foremanProtagonist}
          <span class="protagonist-name">Protagonist: {$foremanProtagonist}</span>
        {/if}
      </div>
      <button class="edit-btn" on:click={openStoryBibleWizard} title="Edit Story Bible">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
        </svg>
      </button>
    </div>
  {:else}
    {#if !hasNotebooks}
      <div class="welcome-banner" style="border-color: var(--accent-cyan, #58a6ff);">
        <div class="welcome-content">
          <h4 style="color: var(--accent-cyan, #58a6ff);">Step 1: Connect Research</h4>
          <p>Before building your Story Bible, connect your NotebookLM research to ground your story in facts.</p>
          <button class="start-btn" on:click={openNotebookRegistration} style="background: var(--accent-cyan, #58a6ff);">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
            Connect Research Notebooks
          </button>
        </div>
      </div>
    {:else}
      <div class="welcome-banner">
        <div class="welcome-content">
          <h4>Welcome to ARCHITECT Mode</h4>
          <p>Create your Story Bible to define the foundation of your novel.</p>
          <button class="start-btn" on:click={openStoryBibleWizard}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Create Story Bible
          </button>
        </div>
      </div>
    {/if}
  {/if}

  <!-- Work Order Tracker -->
  <div class="section">
    <WorkOrderTracker
      on:edit={handleTemplateEdit}
      on:advance={handleAdvanceMode}
    />
  </div>

  <!-- NotebookLM Section -->
  <div class="section">
    <div class="section-header">
      <h5 class="section-title">Research Notebooks</h5>
      <button class="section-action" on:click={openNotebookRegistration}>
        {hasNotebooks ? 'Manage' : 'Add'}
      </button>
    </div>

    {#if hasNotebooks}
      <div class="notebook-list">
        {#each $registeredNotebooks as notebook}
          <div class="notebook-item">
            <span class="notebook-role">{notebook.role || '?'}</span>
            <span class="notebook-name">{notebook.name || notebook.id}</span>
          </div>
        {/each}
      </div>
    {:else}
      <div class="empty-state">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
        <p>Connect NotebookLM for AI-powered research integration</p>
        <button class="link-btn" on:click={openNotebookRegistration}>
          Add Notebook
        </button>
      </div>
    {/if}
  </div>

  <!-- Mode Guidance -->
  <div class="section guidance">
    <h5 class="section-title">ARCHITECT Mode</h5>
    <div class="guidance-content">
      <p>Build the foundation of your story:</p>
      <ul>
        <li>Define your protagonist's Fatal Flaw and The Lie</li>
        <li>Map the 15-beat Save the Cat! structure</li>
        <li>Establish theme and world rules</li>
        <li>Complete 80% to unlock Voice Calibration</li>
      </ul>
    </div>
  </div>
</div>

<style>
  .architect-mode-ui {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
    padding: var(--space-3, 12px);
  }

  .project-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: var(--space-3, 12px);
    background: linear-gradient(135deg, var(--mode-architect, #2f81f7) 0%, color-mix(in srgb, var(--mode-architect, #2f81f7) 60%, var(--bg-secondary)) 100%);
    border-radius: var(--radius-md, 6px);
  }

  .project-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .project-title {
    margin: 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .protagonist-name {
    font-size: var(--text-xs, 11px);
    color: rgba(255, 255, 255, 0.8);
  }

  .edit-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: rgba(255, 255, 255, 0.15);
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: white;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .edit-btn:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  .welcome-banner {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px dashed var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    text-align: center;
  }

  .welcome-content h4 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .welcome-content p {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .start-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--mode-architect, #2f81f7);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: white;
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .start-btn:hover {
    filter: brightness(1.1);
  }

  .section {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .section-title {
    margin: 0;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .section-action {
    background: transparent;
    border: none;
    font-size: var(--text-xs, 11px);
    color: var(--accent-cyan, #58a6ff);
    cursor: pointer;
    text-decoration: underline;
  }

  .notebook-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .notebook-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-sm, 4px);
  }

  .notebook-role {
    padding: 2px 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--accent-cyan, #58a6ff);
    text-transform: uppercase;
  }

  .notebook-name {
    font-size: var(--text-xs, 11px);
    color: var(--text-primary, #e6edf3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    text-align: center;
  }

  .empty-state svg {
    color: var(--text-muted, #6e7681);
  }

  .empty-state p {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .link-btn {
    background: transparent;
    border: none;
    font-size: var(--text-xs, 11px);
    color: var(--accent-cyan, #58a6ff);
    cursor: pointer;
    text-decoration: underline;
  }

  .guidance {
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    border-left: 3px solid var(--mode-architect, #2f81f7);
  }

  .guidance-content p {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .guidance-content ul {
    margin: 0;
    padding-left: var(--space-4, 16px);
  }

  .guidance-content li {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
    line-height: 1.6;
  }
</style>
