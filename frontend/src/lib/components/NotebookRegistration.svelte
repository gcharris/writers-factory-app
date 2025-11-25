<!--
  NotebookRegistration.svelte - Multi-notebook orchestration

  Allows writers to register NotebookLM notebooks with specific roles:
  - World: Setting, locations, factions, history
  - Voice: Character voice samples, dialogue patterns
  - Craft: Writing techniques, narrative craft reference

  Features:
  - Add notebook via URL or ID
  - Assign role to each notebook
  - Test query per notebook
  - View registered notebooks
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    notebookLMConnected,
    registeredNotebooks,
    showNotebookRegistration
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Form state
  let notebookId = '';
  let selectedRole = 'world';
  let isRegistering = false;
  let testQuery = '';
  let testResult = null;
  let isTesting = false;

  // Available roles
  const roles = [
    {
      id: 'world',
      name: 'World',
      description: 'Setting, locations, factions, world-building details',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="2" y1="12" x2="22" y2="12"></line>
        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
      </svg>`
    },
    {
      id: 'voice',
      name: 'Voice',
      description: 'Character voice samples, dialogue patterns, speech rhythms',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        <line x1="12" y1="19" x2="12" y2="23"></line>
      </svg>`
    },
    {
      id: 'craft',
      name: 'Craft',
      description: 'Writing techniques, narrative craft, story structure reference',
      icon: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
      </svg>`
    }
  ];

  // Check connection status on mount
  async function checkConnection() {
    try {
      const status = await apiClient.getNotebookLMStatus();
      $notebookLMConnected = status.connected;
    } catch (error) {
      console.error('Failed to check NotebookLM status:', error);
      $notebookLMConnected = false;
    }
  }

  // Load registered notebooks
  async function loadNotebooks() {
    try {
      const result = await apiClient.getNotebookLMList();
      $registeredNotebooks = result.notebooks || [];
    } catch (error) {
      console.error('Failed to load notebooks:', error);
    }
  }

  // Register a new notebook
  async function handleRegister() {
    if (!notebookId.trim()) {
      addToast('Please enter a notebook ID or URL', 'error');
      return;
    }

    isRegistering = true;
    try {
      // Extract ID from URL if needed
      let id = notebookId.trim();
      if (id.includes('notebooklm.google.com')) {
        const match = id.match(/notebook\/([^/?]+)/);
        if (match) id = match[1];
      }

      await apiClient.foremanRegisterNotebook(id, selectedRole);
      addToast(`Notebook registered as ${selectedRole}`, 'success');

      // Refresh notebook list
      await loadNotebooks();

      // Clear form
      notebookId = '';

      dispatch('registered', { id, role: selectedRole });
    } catch (error) {
      console.error('Failed to register notebook:', error);
      addToast(`Failed to register notebook: ${error.message}`, 'error');
    } finally {
      isRegistering = false;
    }
  }

  // Test query a notebook
  async function handleTestQuery(notebook) {
    if (!testQuery.trim()) {
      addToast('Please enter a test query', 'error');
      return;
    }

    isTesting = true;
    testResult = null;
    try {
      const result = await apiClient.queryNotebook(notebook.id, testQuery);
      testResult = {
        notebookId: notebook.id,
        answer: result.answer,
        sources: result.sources
      };
      addToast('Query successful', 'success');
    } catch (error) {
      console.error('Failed to query notebook:', error);
      addToast(`Query failed: ${error.message}`, 'error');
    } finally {
      isTesting = false;
    }
  }

  // Remove a notebook
  function handleRemove(notebook) {
    $registeredNotebooks = $registeredNotebooks.filter(n => n.id !== notebook.id);
    addToast(`Removed ${notebook.name || notebook.id}`, 'info');
  }

  function handleClose() {
    $showNotebookRegistration = false;
    dispatch('close');
  }

  onMount(() => {
    checkConnection();
    loadNotebooks();
  });
</script>

<div class="notebook-registration">
  <div class="section-header">
    <h3 class="section-title">NotebookLM Integration</h3>
    <div class="connection-status" class:connected={$notebookLMConnected}>
      <span class="status-dot"></span>
      <span>{$notebookLMConnected ? 'Connected' : 'Not Connected'}</span>
    </div>
  </div>

  {#if !$notebookLMConnected}
    <div class="connection-notice">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <path d="M12 16v-4"></path>
        <path d="M12 8h.01"></path>
      </svg>
      <p>NotebookLM is not connected. Please ensure the MCP bridge is running.</p>
    </div>
  {:else}
    <!-- Register new notebook -->
    <div class="register-section">
      <h4 class="subsection-title">Add Notebook</h4>
      <div class="register-form">
        <div class="input-group">
          <label for="notebook-id">Notebook ID or URL</label>
          <input
            id="notebook-id"
            type="text"
            placeholder="Paste NotebookLM URL or ID..."
            bind:value={notebookId}
            disabled={isRegistering}
          />
        </div>

        <div class="input-group">
          <label>Role</label>
          <div class="role-selector">
            {#each roles as role}
              <button
                class="role-option {selectedRole === role.id ? 'selected' : ''}"
                on:click={() => selectedRole = role.id}
                disabled={isRegistering}
              >
                <span class="role-icon">{@html role.icon}</span>
                <span class="role-name">{role.name}</span>
              </button>
            {/each}
          </div>
          <p class="role-description">{roles.find(r => r.id === selectedRole)?.description}</p>
        </div>

        <button
          class="register-btn"
          on:click={handleRegister}
          disabled={!notebookId.trim() || isRegistering}
        >
          {#if isRegistering}
            <span class="spinner"></span>
            Registering...
          {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Add Notebook
          {/if}
        </button>
      </div>
    </div>

    <!-- Registered notebooks -->
    {#if $registeredNotebooks.length > 0}
      <div class="notebooks-section">
        <h4 class="subsection-title">Registered Notebooks</h4>
        <div class="notebook-list">
          {#each $registeredNotebooks as notebook}
            <div class="notebook-item">
              <div class="notebook-info">
                <span class="notebook-role-badge">{notebook.role || 'unassigned'}</span>
                <span class="notebook-name">{notebook.name || notebook.id}</span>
              </div>
              <div class="notebook-actions">
                <button
                  class="test-btn"
                  on:click={() => handleTestQuery(notebook)}
                  disabled={isTesting}
                  title="Test query"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                </button>
                <button
                  class="remove-btn"
                  on:click={() => handleRemove(notebook)}
                  title="Remove"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Test query section -->
    <div class="test-section">
      <h4 class="subsection-title">Test Query</h4>
      <div class="test-form">
        <input
          type="text"
          placeholder="Enter a test query..."
          bind:value={testQuery}
          disabled={isTesting || $registeredNotebooks.length === 0}
        />
      </div>

      {#if testResult}
        <div class="test-result">
          <h5>Result from {testResult.notebookId}</h5>
          <p class="answer">{testResult.answer}</p>
          {#if testResult.sources?.length > 0}
            <div class="sources">
              <span class="sources-label">Sources:</span>
              {#each testResult.sources as source}
                <span class="source">{source}</span>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .notebook-registration {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .section-title {
    margin: 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .connection-status {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .connection-status.connected {
    color: var(--success, #3fb950);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-muted, #6e7681);
  }

  .connection-status.connected .status-dot {
    background: var(--success, #3fb950);
  }

  .connection-notice {
    display: flex;
    align-items: flex-start;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    color: var(--warning, #d29922);
  }

  .connection-notice p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .register-section,
  .notebooks-section,
  .test-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .subsection-title {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .register-form {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .input-group label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .input-group input {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .input-group input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .input-group input:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .role-selector {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .role-option {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .role-option:hover:not(:disabled) {
    border-color: var(--accent-cyan, #58a6ff);
  }

  .role-option.selected {
    background: color-mix(in srgb, var(--accent-cyan, #58a6ff) 15%, transparent);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .role-icon {
    display: flex;
    color: var(--text-muted, #6e7681);
  }

  .role-option.selected .role-icon {
    color: var(--accent-cyan, #58a6ff);
  }

  .role-name {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .role-option.selected .role-name {
    color: var(--accent-cyan, #58a6ff);
  }

  .role-description {
    margin: 0;
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .register-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--accent-cyan, #58a6ff);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--bg-primary, #0f1419);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .register-btn:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .register-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .notebook-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .notebook-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .notebook-info {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .notebook-role-badge {
    padding: 2px 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--accent-cyan, #58a6ff);
    text-transform: uppercase;
  }

  .notebook-name {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .notebook-actions {
    display: flex;
    gap: var(--space-1, 4px);
  }

  .test-btn,
  .remove-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .test-btn {
    color: var(--success, #3fb950);
  }

  .remove-btn {
    color: var(--error, #f85149);
  }

  .test-btn:hover:not(:disabled),
  .remove-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
  }

  .test-form {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .test-form input {
    flex: 1;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .test-form input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .test-result {
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .test-result h5 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .test-result .answer {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    line-height: var(--leading-relaxed, 1.7);
  }

  .sources {
    margin-top: var(--space-2, 8px);
    padding-top: var(--space-2, 8px);
    border-top: 1px solid var(--border, #2d3a47);
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
    align-items: center;
  }

  .sources-label {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .source {
    padding: 2px 6px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    font-size: 10px;
    color: var(--text-secondary, #8b949e);
  }
</style>
