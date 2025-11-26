<!--
  GraphNodeDetails.svelte - Node Properties Panel

  Slide-in panel showing:
  - Node type and name
  - Editable properties
  - Connected nodes list
  - Metadata (ID, timestamps)
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { selectedNode } from '$lib/stores';

  export let edges = [];
  export let nodes = [];

  const dispatch = createEventDispatcher();

  let node = null;
  let editing = false;
  let editedName = '';
  let editedProperties = {};
  let saving = false;
  let error = '';

  // Subscribe to selected node
  const unsubscribe = selectedNode.subscribe(n => {
    node = n;
    if (node) {
      editedName = node.name || '';
      editedProperties = { ...(node.properties || {}) };
      editing = false;
      error = '';
    }
  });

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

  // Get connected nodes
  $: connectedNodes = node ? getConnectedNodes(node.id) : [];

  function getConnectedNodes(nodeId) {
    const connected = [];

    edges.forEach(edge => {
      const sourceId = edge.source_id || edge.source?.id || edge.source;
      const targetId = edge.target_id || edge.target?.id || edge.target;

      if (sourceId === nodeId) {
        const targetNode = nodes.find(n => n.id === targetId);
        if (targetNode) {
          connected.push({
            node: targetNode,
            relationship: edge.label || edge.relationship || 'connected to',
            direction: 'outgoing'
          });
        }
      } else if (targetId === nodeId) {
        const sourceNode = nodes.find(n => n.id === sourceId);
        if (sourceNode) {
          connected.push({
            node: sourceNode,
            relationship: edge.label || edge.relationship || 'connected from',
            direction: 'incoming'
          });
        }
      }
    });

    return connected;
  }

  function startEditing() {
    editing = true;
    error = '';
  }

  async function saveChanges() {
    if (!node) return;

    saving = true;
    error = '';

    try {
      const response = await fetch(`http://localhost:8000/graph/nodes/${node.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: editedName,
          properties: editedProperties
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update node');
      }

      const updatedNode = await response.json();

      // Update the local node
      node = { ...node, name: editedName, properties: editedProperties };
      selectedNode.set(node);

      dispatch('node-updated', updatedNode);
      editing = false;
    } catch (e) {
      console.error('Save failed:', e);
      error = e.message || 'Failed to save changes';
    } finally {
      saving = false;
    }
  }

  function cancelEdit() {
    editedName = node?.name || '';
    editedProperties = { ...(node?.properties || {}) };
    editing = false;
    error = '';
  }

  function close() {
    dispatch('close');
  }

  function selectConnectedNode(connectedNode) {
    selectedNode.set(connectedNode);
  }

  function addProperty() {
    const key = prompt('Property name:');
    if (key && !editedProperties.hasOwnProperty(key)) {
      editedProperties[key] = '';
      editedProperties = editedProperties; // Trigger reactivity
    }
  }

  function removeProperty(key) {
    delete editedProperties[key];
    editedProperties = editedProperties; // Trigger reactivity
  }

  // Cleanup
  import { onDestroy } from 'svelte';
  onDestroy(() => unsubscribe());
</script>

{#if node}
  <div class="node-details-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-content">
        <span class="node-type-badge" style="background: {getTypeColor(node.type)}">{node.type || 'UNKNOWN'}</span>
        {#if editing}
          <input
            type="text"
            bind:value={editedName}
            class="name-input"
            placeholder="Node name"
          />
        {:else}
          <h3 class="node-name">{node.name || 'Unnamed'}</h3>
        {/if}
      </div>
      <button class="close-btn" on:click={close} title="Close">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="panel-content">
      {#if error}
        <div class="error-message">{error}</div>
      {/if}

      <!-- Properties Section -->
      <div class="section">
        <div class="section-header">
          <h4 class="section-title">Properties</h4>
          {#if !editing}
            <button class="edit-btn" on:click={startEditing}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
              Edit
            </button>
          {/if}
        </div>

        <div class="properties-list">
          {#if Object.keys(editedProperties).length > 0}
            {#each Object.entries(editedProperties) as [key, value]}
              <div class="property-item">
                <div class="property-key-row">
                  <span class="property-key">{key}</span>
                  {#if editing}
                    <button class="remove-property-btn" on:click={() => removeProperty(key)} title="Remove property">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    </button>
                  {/if}
                </div>
                {#if editing}
                  <textarea
                    bind:value={editedProperties[key]}
                    class="property-value-input"
                    rows="2"
                  ></textarea>
                {:else}
                  <div class="property-value">{value || '—'}</div>
                {/if}
              </div>
            {/each}
          {:else}
            <p class="empty-message">No properties defined</p>
          {/if}

          {#if editing}
            <button class="add-property-btn" on:click={addProperty}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add Property
            </button>
          {/if}
        </div>

        {#if editing}
          <div class="edit-actions">
            <button class="save-btn" on:click={saveChanges} disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button class="cancel-btn" on:click={cancelEdit} disabled={saving}>Cancel</button>
          </div>
        {/if}
      </div>

      <!-- Connected Nodes Section -->
      <div class="section">
        <h4 class="section-title">Connections ({connectedNodes.length})</h4>
        {#if connectedNodes.length > 0}
          <div class="connected-list">
            {#each connectedNodes as { node: connNode, relationship, direction }}
              <button class="connected-item" on:click={() => selectConnectedNode(connNode)}>
                <span class="direction-icon">{direction === 'outgoing' ? '→' : '←'}</span>
                <span class="connected-type-dot" style="background: {getTypeColor(connNode.type)}"></span>
                <span class="connected-name">{connNode.name}</span>
                <span class="connected-relationship">{relationship}</span>
              </button>
            {/each}
          </div>
        {:else}
          <p class="empty-message">No connections</p>
        {/if}
      </div>

      <!-- Metadata Section -->
      <div class="section">
        <h4 class="section-title">Metadata</h4>
        <div class="metadata-grid">
          <div class="metadata-item">
            <span class="metadata-label">ID</span>
            <span class="metadata-value">{node.id}</span>
          </div>
          {#if node.created_at}
            <div class="metadata-item">
              <span class="metadata-label">Created</span>
              <span class="metadata-value">{new Date(node.created_at).toLocaleDateString()}</span>
            </div>
          {/if}
          {#if node.updated_at}
            <div class="metadata-item">
              <span class="metadata-label">Updated</span>
              <span class="metadata-value">{new Date(node.updated_at).toLocaleDateString()}</span>
            </div>
          {/if}
          {#if node.source_file}
            <div class="metadata-item">
              <span class="metadata-label">Source</span>
              <span class="metadata-value file">{node.source_file.split('/').pop()}</span>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .node-details-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
  }

  /* Header */
  .panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
    gap: var(--space-2, 8px);
  }

  .header-content {
    flex: 1;
    min-width: 0;
  }

  .node-type-badge {
    display: inline-block;
    padding: 2px var(--space-2, 8px);
    border-radius: var(--radius-sm, 4px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-bold, 700);
    text-transform: uppercase;
    margin-bottom: var(--space-2, 8px);
  }

  .node-name {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
    margin: 0;
    word-break: break-word;
  }

  .name-input {
    width: 100%;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--accent-cyan, #58a6ff);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
  }

  .name-input:focus {
    outline: none;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3);
  }

  .close-btn {
    padding: var(--space-1, 4px);
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: color 0.1s ease;
    flex-shrink: 0;
  }

  .close-btn:hover {
    color: var(--text-primary, #e6edf3);
  }

  /* Content */
  .panel-content {
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

  .section {
    margin-bottom: var(--space-6, 24px);
  }

  .section:last-child {
    margin-bottom: 0;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-3, 12px);
  }

  .section-title {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0;
  }

  .edit-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px var(--space-2, 8px);
    background: none;
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .edit-btn:hover {
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  /* Properties */
  .properties-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .property-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .property-key-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .property-key {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .remove-property-btn {
    padding: 2px;
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    opacity: 0.6;
    transition: all 0.1s ease;
  }

  .remove-property-btn:hover {
    color: var(--error, #f85149);
    opacity: 1;
  }

  .property-value {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    line-height: 1.5;
  }

  .property-value-input {
    width: 100%;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-sm, 12px);
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
  }

  .property-value-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .add-property-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-1, 4px);
    width: 100%;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px dashed var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-muted, #6e7681);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .add-property-btn:hover {
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--accent-cyan, #58a6ff);
  }

  .edit-actions {
    display: flex;
    gap: var(--space-2, 8px);
    margin-top: var(--space-4, 16px);
  }

  .save-btn,
  .cancel-btn {
    flex: 1;
    padding: var(--space-2, 8px) var(--space-3, 12px);
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

  /* Connected Nodes */
  .connected-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .connected-item {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    width: 100%;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid transparent;
    border-radius: var(--radius-md, 6px);
    cursor: pointer;
    transition: all 0.1s ease;
    text-align: left;
  }

  .connected-item:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border, #2d3a47);
  }

  .direction-icon {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    flex-shrink: 0;
  }

  .connected-type-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .connected-name {
    flex: 1;
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .connected-relationship {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    font-style: italic;
    flex-shrink: 0;
  }

  .empty-message {
    font-size: var(--text-sm, 12px);
    color: var(--text-muted, #6e7681);
    font-style: italic;
    margin: 0;
  }

  /* Metadata */
  .metadata-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .metadata-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
  }

  .metadata-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    font-weight: var(--font-semibold, 600);
  }

  .metadata-value {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    font-family: var(--font-mono, 'SF Mono', monospace);
    text-align: right;
    word-break: break-all;
  }

  .metadata-value.file {
    color: var(--accent-cyan, #58a6ff);
  }

  /* Scrollbar */
  .panel-content::-webkit-scrollbar {
    width: 6px;
  }

  .panel-content::-webkit-scrollbar-track {
    background: transparent;
  }

  .panel-content::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 3px;
  }

  .panel-content::-webkit-scrollbar-thumb:hover {
    background: var(--border-strong, #3d4a57);
  }
</style>
