<!--
  GraphRelationshipEditor.svelte - Create/Edit Relationships Modal

  Modal for:
  - Creating new relationships between nodes
  - Editing existing relationship properties
  - Deleting relationships
-->
<script>
  import { createEventDispatcher } from 'svelte';

  export let mode = 'create'; // 'create' or 'edit'
  export let edge = null; // Existing edge when editing
  export let nodes = [];

  const dispatch = createEventDispatcher();

  // Form state
  let sourceId = edge?.source_id || edge?.source?.id || edge?.source || '';
  let targetId = edge?.target_id || edge?.target?.id || edge?.target || '';
  let relationship = edge?.label || edge?.relationship || '';
  let weight = edge?.weight || 1;

  // UI state
  let saving = false;
  let deleting = false;
  let error = '';

  // Filter nodes for dropdowns
  $: sortedNodes = [...nodes].sort((a, b) => (a.name || '').localeCompare(b.name || ''));

  // Node type colors
  const typeColors = {
    CHARACTER: '#58a6ff',
    LOCATION: '#a371f7',
    THEME: '#d4a574',
    EVENT: '#3fb950',
    OBJECT: '#8b949e',
    CONCEPT: '#f85149'
  };

  function getTypeColor(type) {
    return typeColors[type?.toUpperCase()] || '#8b949e';
  }

  async function handleSubmit() {
    error = '';

    if (!sourceId || !targetId) {
      error = 'Please select both source and target nodes';
      return;
    }

    if (sourceId === targetId) {
      error = 'Source and target must be different nodes';
      return;
    }

    if (!relationship.trim()) {
      error = 'Please enter a relationship type';
      return;
    }

    saving = true;

    try {
      if (mode === 'create') {
        const response = await fetch('http://localhost:8000/graph/relationships', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            source_id: sourceId,
            target_id: targetId,
            relationship: relationship.trim(),
            weight: weight
          })
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to create relationship');
        }

        const newEdge = await response.json();
        dispatch('created', newEdge);
      } else {
        const response = await fetch(`http://localhost:8000/graph/relationships/${edge.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            relationship: relationship.trim(),
            weight: weight
          })
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to update relationship');
        }

        const updatedEdge = await response.json();
        dispatch('updated', updatedEdge);
      }
    } catch (e) {
      console.error('Save failed:', e);
      error = e.message || 'Failed to save relationship';
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!edge?.id) return;

    if (!confirm('Are you sure you want to delete this relationship?')) {
      return;
    }

    deleting = true;
    error = '';

    try {
      const response = await fetch(`http://localhost:8000/graph/relationships/${edge.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to delete relationship');
      }

      dispatch('deleted', { id: edge.id });
    } catch (e) {
      console.error('Delete failed:', e);
      error = e.message || 'Failed to delete relationship';
    } finally {
      deleting = false;
    }
  }

  function handleClose() {
    dispatch('close');
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  }

  // Common relationship types for quick selection
  const commonRelationships = [
    'knows',
    'loves',
    'hates',
    'works_with',
    'lives_in',
    'visits',
    'owns',
    'creates',
    'destroys',
    'influences',
    'fears',
    'protects',
    'betrays',
    'allied_with',
    'enemy_of',
    'parent_of',
    'child_of',
    'sibling_of',
    'mentor_of',
    'student_of'
  ];

  function selectRelationship(rel) {
    relationship = rel;
  }
</script>

<div class="modal-backdrop" on:click={handleBackdropClick} role="dialog" aria-modal="true">
  <div class="modal-container">
    <!-- Header -->
    <div class="modal-header">
      <h2 class="modal-title">{mode === 'create' ? 'Create Relationship' : 'Edit Relationship'}</h2>
      <button class="close-btn" on:click={handleClose} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="modal-content">
      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      <form on:submit|preventDefault={handleSubmit}>
        <!-- Source Node -->
        <div class="form-group">
          <label class="form-label" for="source-node">Source Node</label>
          <select
            id="source-node"
            bind:value={sourceId}
            class="form-select"
            disabled={mode === 'edit'}
          >
            <option value="">Select source node...</option>
            {#each sortedNodes as node}
              <option value={node.id}>
                {node.name} ({node.type})
              </option>
            {/each}
          </select>
          {#if sourceId}
            {@const sourceNode = nodes.find(n => n.id === sourceId)}
            {#if sourceNode}
              <div class="node-preview">
                <span class="preview-dot" style="background: {getTypeColor(sourceNode.type)}"></span>
                <span class="preview-name">{sourceNode.name}</span>
                <span class="preview-type">{sourceNode.type}</span>
              </div>
            {/if}
          {/if}
        </div>

        <!-- Relationship Type -->
        <div class="form-group">
          <label class="form-label" for="relationship">Relationship</label>
          <div class="relationship-input-row">
            <input
              id="relationship"
              type="text"
              bind:value={relationship}
              class="form-input"
              placeholder="e.g., knows, loves, works_with"
            />
          </div>
          <div class="quick-relationships">
            {#each commonRelationships as rel}
              <button
                type="button"
                class="quick-rel-btn"
                class:active={relationship === rel}
                on:click={() => selectRelationship(rel)}
              >
                {rel}
              </button>
            {/each}
          </div>
        </div>

        <!-- Target Node -->
        <div class="form-group">
          <label class="form-label" for="target-node">Target Node</label>
          <select
            id="target-node"
            bind:value={targetId}
            class="form-select"
            disabled={mode === 'edit'}
          >
            <option value="">Select target node...</option>
            {#each sortedNodes as node}
              <option value={node.id}>
                {node.name} ({node.type})
              </option>
            {/each}
          </select>
          {#if targetId}
            {@const targetNode = nodes.find(n => n.id === targetId)}
            {#if targetNode}
              <div class="node-preview">
                <span class="preview-dot" style="background: {getTypeColor(targetNode.type)}"></span>
                <span class="preview-name">{targetNode.name}</span>
                <span class="preview-type">{targetNode.type}</span>
              </div>
            {/if}
          {/if}
        </div>

        <!-- Weight (Optional) -->
        <div class="form-group">
          <label class="form-label" for="weight">Strength (1-10)</label>
          <input
            id="weight"
            type="range"
            bind:value={weight}
            min="1"
            max="10"
            class="form-range"
          />
          <div class="range-labels">
            <span>Weak</span>
            <span class="range-value">{weight}</span>
            <span>Strong</span>
          </div>
        </div>

        <!-- Preview -->
        {#if sourceId && targetId && relationship}
          <div class="relationship-preview">
            <span class="preview-source">{nodes.find(n => n.id === sourceId)?.name || 'Source'}</span>
            <span class="preview-arrow">—[{relationship}]→</span>
            <span class="preview-target">{nodes.find(n => n.id === targetId)?.name || 'Target'}</span>
          </div>
        {/if}
      </form>
    </div>

    <!-- Footer -->
    <div class="modal-footer">
      {#if mode === 'edit'}
        <button
          type="button"
          class="delete-btn"
          on:click={handleDelete}
          disabled={deleting || saving}
        >
          {deleting ? 'Deleting...' : 'Delete'}
        </button>
      {/if}
      <div class="footer-right">
        <button
          type="button"
          class="cancel-btn"
          on:click={handleClose}
          disabled={saving || deleting}
        >
          Cancel
        </button>
        <button
          type="submit"
          class="save-btn"
          on:click={handleSubmit}
          disabled={saving || deleting || !sourceId || !targetId || !relationship.trim()}
        >
          {saving ? 'Saving...' : mode === 'create' ? 'Create' : 'Update'}
        </button>
      </div>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 500;
    animation: fadeIn 0.15s ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal-container {
    width: 500px;
    max-width: calc(100vw - 32px);
    max-height: calc(100vh - 32px);
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.5));
    display: flex;
    flex-direction: column;
    animation: slideIn 0.2s ease-out;
  }

  @keyframes slideIn {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  /* Header */
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .modal-title {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
    margin: 0;
  }

  .close-btn {
    padding: var(--space-1, 4px);
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: color 0.1s ease;
  }

  .close-btn:hover {
    color: var(--text-primary, #e6edf3);
  }

  /* Content */
  .modal-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .error-message {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--error, #f85149);
    border-radius: var(--radius-md, 6px);
    color: var(--error, #f85149);
    font-size: var(--text-sm, 12px);
    margin-bottom: var(--space-4, 16px);
  }

  .form-group {
    margin-bottom: var(--space-4, 16px);
  }

  .form-label {
    display: block;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-2, 8px);
  }

  .form-select,
  .form-input {
    width: 100%;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-sm, 12px);
    transition: all 0.1s ease;
  }

  .form-select:focus,
  .form-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .form-select:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .node-preview {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin-top: var(--space-2, 8px);
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
  }

  .preview-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .preview-name {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    flex: 1;
  }

  .preview-type {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Quick Relationships */
  .quick-relationships {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
    margin-top: var(--space-2, 8px);
  }

  .quick-rel-btn {
    padding: 2px var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .quick-rel-btn:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border-strong, #3d4a57);
    color: var(--text-secondary, #8b949e);
  }

  .quick-rel-btn.active {
    background: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  /* Range Input */
  .form-range {
    width: 100%;
    height: 6px;
    -webkit-appearance: none;
    appearance: none;
    background: var(--bg-tertiary, #252d38);
    border-radius: 3px;
    outline: none;
  }

  .form-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 16px;
    height: 16px;
    background: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    cursor: pointer;
    transition: background 0.1s ease;
  }

  .form-range::-webkit-slider-thumb:hover {
    background: var(--accent-cyan-hover, #79b8ff);
  }

  .range-labels {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .range-value {
    font-weight: var(--font-semibold, 600);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Relationship Preview */
  .relationship-preview {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    margin-top: var(--space-4, 16px);
  }

  .preview-source,
  .preview-target {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .preview-arrow {
    font-size: var(--text-xs, 11px);
    color: var(--accent-cyan, #58a6ff);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  /* Footer */
  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .footer-right {
    display: flex;
    gap: var(--space-2, 8px);
    margin-left: auto;
  }

  .save-btn,
  .cancel-btn,
  .delete-btn {
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .save-btn {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .save-btn:hover:not(:disabled) {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .cancel-btn {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-secondary, #8b949e);
  }

  .cancel-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3a47);
  }

  .delete-btn {
    background: transparent;
    border: 1px solid var(--error, #f85149);
    color: var(--error, #f85149);
  }

  .delete-btn:hover:not(:disabled) {
    background: rgba(248, 81, 73, 0.15);
  }

  .delete-btn:disabled,
  .cancel-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
