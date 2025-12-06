<!--
  NotebookLMPanel.svelte - NotebookLM Integration Modal (Tabbed Interface)

  Provides writers with research capabilities grounded in their source materials:
  - Research: Query notebooks with natural language, see results with citations
  - Notebooks: Register/manage notebooks with roles (World, Voice, Craft)
  - Characters: Extract character profiles from research
  - World: Extract world-building details
  - Status: Connection health, authentication
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { get } from 'svelte/store';
  import {
    notebookStatus,
    notebookList,
    selectedNotebookId,
    notebookLoading,
    notebookError,
    notebookResult,
    notebookLMConnected,
    registeredNotebooks
  } from '$lib/stores';

  export let activeTab = 'research';

  const dispatch = createEventDispatcher();
  const API_URL = 'http://127.0.0.1:8000';

  // Form state
  let queryText = '';
  let characterName = '';
  let worldAspect = '';
  let notebookIdInput = '';
  let notebookLabelInput = '';  // Custom label for new notebooks
  let selectedRole = 'character';
  let isRegistering = false;
  let isSaving = false;

  // Saved notes state
  let savedNotes = [];
  let isLoadingNotes = false;
  let isDeletingNote = null;  // ID of note being deleted

  // Load state on mount
  onMount(async () => {
    await Promise.all([fetchStatus(), fetchConfiguredNotebooks()]);
  });

  async function fetchStatus() {
    try {
      const res = await fetch(`${API_URL}/notebooklm/status`);
      const data = await res.json();
      notebookStatus.set(data.status || 'unknown');
      notebookLMConnected.set(data.status === 'ready');
    } catch (err) {
      notebookStatus.set('offline');
      notebookLMConnected.set(false);
      notebookError.set('NotebookLM backend offline');
    }
  }

  async function fetchConfiguredNotebooks() {
    try {
      const res = await fetch(`${API_URL}/notebooklm/notebooks`);
      const data = await res.json();
      const list = data.configured || [];
      notebookList.set(list);
      if (list.length > 0 && !get(selectedNotebookId)) {
        selectedNotebookId.set(list[0].id);
      }
    } catch (err) {
      notebookError.set('Failed to load notebooks');
    }
  }

  async function triggerAuth() {
    try {
      notebookError.set('');
      notebookLoading.set(true);
      const res = await fetch(`${API_URL}/notebooklm/auth`);
      if (!res.ok) throw new Error('Auth trigger failed');
      // Browser will open for Google login
    } catch (err) {
      notebookError.set(err.message);
    } finally {
      notebookLoading.set(false);
    }
  }

  function selectNotebook(event) {
    selectedNotebookId.set(event.target.value);
  }

  async function runQuery(endpoint, payloadBuilder) {
    const currentNotebook = get(selectedNotebookId);
    if (!currentNotebook) {
      notebookError.set('Select a notebook first.');
      return;
    }

    notebookError.set('');
    notebookLoading.set(true);
    notebookResult.set(null);

    try {
      const body = payloadBuilder();
      body.notebook_id = currentNotebook;
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      if (!res.ok) throw new Error(`Request failed (${res.status})`);

      const data = await res.json();
      notebookResult.set(data);
    } catch (err) {
      notebookError.set(err.message);
    } finally {
      notebookLoading.set(false);
    }
  }

  async function handleRegisterNotebook() {
    if (!notebookIdInput.trim()) return;

    isRegistering = true;
    notebookError.set('');
    try {
      // Extract ID from URL if needed
      let id = notebookIdInput.trim();
      if (id.includes('notebooklm.google.com')) {
        const match = id.match(/notebook\/([^/?]+)/);
        if (match) id = match[1];
      }

      // Use the direct config endpoint (no project required)
      const res = await fetch(`${API_URL}/notebooklm/notebooks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notebook_id: id,
          label: notebookLabelInput.trim() || '',  // Use custom label if provided
          description: '',
          category: selectedRole
        })
      });

      if (res.ok) {
        await fetchConfiguredNotebooks();
        notebookIdInput = '';
        notebookLabelInput = '';
      } else {
        const data = await res.json();
        notebookError.set(data.detail || 'Failed to register notebook');
      }
    } catch (err) {
      notebookError.set('Failed to register notebook: ' + err.message);
    } finally {
      isRegistering = false;
    }
  }

  async function handleDeleteNotebook(notebookId) {
    try {
      notebookError.set('');
      const res = await fetch(`${API_URL}/notebooklm/notebooks/${encodeURIComponent(notebookId)}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        await fetchConfiguredNotebooks();
      } else {
        const data = await res.json();
        notebookError.set(data.detail || 'Failed to delete notebook');
      }
    } catch (err) {
      notebookError.set('Failed to delete notebook: ' + err.message);
    }
  }

  async function handleSaveToKB() {
    if (!result) return;

    isSaving = true;
    notebookError.set('');

    try {
      // Determine category and key based on active tab and content
      let category = 'world';
      let key = '';
      let content = '';

      if (activeTab === 'characters' && characterName) {
        category = 'character';
        key = characterName.toLowerCase().replace(/\s+/g, '_');
        content = result.profile || result.answer || JSON.stringify(result);
      } else if (activeTab === 'world' && worldAspect) {
        category = 'world';
        key = worldAspect.toLowerCase().replace(/\s+/g, '_');
        content = result.details || result.answer || JSON.stringify(result);
      } else if (activeTab === 'research' && queryText) {
        category = 'research';
        key = `research_${Date.now()}`;
        content = result.answer || JSON.stringify(result);
      } else {
        notebookError.set('Cannot determine what to save. Please use Characters or World tabs.');
        isSaving = false;
        return;
      }

      const currentNb = notebooks.find(nb => nb.id === currentNotebook);
      const sourceNotebook = currentNb?.label || currentNotebook;

      const res = await fetch(`${API_URL}/notebooklm/save-to-kb`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category,
          key,
          content,
          source_notebook: sourceNotebook
        })
      });

      if (res.ok) {
        const data = await res.json();
        // Show success briefly by updating the result
        const savedMessage = `Saved to Knowledge Base as "${key}"`;
        notebookError.set(''); // Clear any error
        // Flash a success indicator (we'll add a saved state)
        alert(savedMessage); // Simple feedback for now
      } else {
        const data = await res.json();
        notebookError.set(data.detail || 'Failed to save to KB');
      }
    } catch (err) {
      notebookError.set('Failed to save: ' + err.message);
    } finally {
      isSaving = false;
    }
  }

  async function fetchSavedNotes() {
    isLoadingNotes = true;
    try {
      const res = await fetch(`${API_URL}/notebooklm/research-notes`);
      if (res.ok) {
        const data = await res.json();
        savedNotes = data.notes || [];
      } else {
        notebookError.set('Failed to load saved notes');
      }
    } catch (err) {
      notebookError.set('Failed to load saved notes: ' + err.message);
    } finally {
      isLoadingNotes = false;
    }
  }

  async function deleteNote(noteId) {
    isDeletingNote = noteId;
    try {
      const res = await fetch(`${API_URL}/notebooklm/research-notes/${noteId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        savedNotes = savedNotes.filter(n => n.id !== noteId);
      } else {
        const data = await res.json();
        notebookError.set(data.detail || 'Failed to delete note');
      }
    } catch (err) {
      notebookError.set('Failed to delete note: ' + err.message);
    } finally {
      isDeletingNote = null;
    }
  }

  // Tab definitions
  const tabs = [
    { id: 'research', label: 'Research', icon: 'search' },
    { id: 'notebooks', label: 'Notebooks', icon: 'book' },
    { id: 'characters', label: 'Characters', icon: 'user' },
    { id: 'world', label: 'World', icon: 'globe' },
    { id: 'saved', label: 'Saved Notes', icon: 'folder' },
    { id: 'status', label: 'Status', icon: 'activity' }
  ];

  // Role definitions
  const roles = [
    { id: 'character', name: 'Character', description: 'Character research, backstory, psychology' },
    { id: 'world', name: 'World', description: 'Setting, locations, factions, world-building' },
    { id: 'voice', name: 'Voice', description: 'Voice samples, dialogue patterns, prose style' },
    { id: 'theme', name: 'Theme', description: 'Themes, philosophy, symbolism research' },
    { id: 'craft', name: 'Craft', description: 'Writing techniques, narrative craft reference' }
  ];

  // Icons
  const tabIcons = {
    search: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"></circle>
      <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
    </svg>`,
    book: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
    </svg>`,
    user: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    </svg>`,
    globe: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="2" y1="12" x2="22" y2="12"></line>
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
    </svg>`,
    activity: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
    </svg>`,
    folder: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
    </svg>`
  };

  // Reactive state
  $: status = $notebookStatus;
  $: notebooks = $notebookList;
  $: currentNotebook = $selectedNotebookId;
  $: isLoading = $notebookLoading;
  $: errorMsg = $notebookError;
  $: result = $notebookResult;

  // Clear results when switching tabs (prevents stale data confusion)
  // and load saved notes when switching to saved tab
  let previousTab = activeTab;
  $: if (activeTab !== previousTab) {
    const switchingToSaved = activeTab === 'saved';
    notebookResult.set(null);
    notebookError.set('');
    previousTab = activeTab;
    // Load saved notes when switching to saved tab
    if (switchingToSaved) {
      fetchSavedNotes();
    }
  }

  // Clear results when switching notebooks
  let previousNotebook = currentNotebook;
  $: if (currentNotebook !== previousNotebook) {
    notebookResult.set(null);
    notebookError.set('');
    previousNotebook = currentNotebook;
  }
</script>

<div class="notebooklm-panel">
  <!-- Sidebar Navigation -->
  <nav class="panel-nav">
    <div class="nav-header">
      <h3>NotebookLM</h3>
      <div class="connection-badge {status === 'ready' ? 'connected' : 'offline'}">
        <span class="status-dot"></span>
        <span>{status === 'ready' ? 'Connected' : 'Offline'}</span>
      </div>
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
          </button>
        </li>
      {/each}
    </ul>
  </nav>

  <!-- Content Area -->
  <div class="panel-content">
    {#if activeTab === 'research'}
      <div class="tab-content">
        <h2>Research Query</h2>
        <p class="tab-description">Ask questions grounded in your uploaded research materials.</p>

        {#if notebooks.length === 0}
          <div class="empty-state">
            <div class="empty-icon">{@html tabIcons.book}</div>
            <p>No notebooks configured</p>
            <p class="empty-hint">Go to the Notebooks tab to add your first notebook</p>
          </div>
        {:else}
          <div class="form-group">
            <label for="notebook-select">Select Notebook</label>
            <select id="notebook-select" on:change={selectNotebook} value={currentNotebook}>
              {#each notebooks as nb}
                <option value={nb.id}>{nb.label} ({nb.category})</option>
              {/each}
            </select>
            {#if notebooks.find(nb => nb.id === currentNotebook)?.description}
              <p class="field-hint">{notebooks.find(nb => nb.id === currentNotebook)?.description}</p>
            {/if}
          </div>

          <div class="form-group">
            <label for="query-input">Research Question</label>
            <textarea
              id="query-input"
              bind:value={queryText}
              placeholder="What would you like to know from your research?"
              rows="3"
            ></textarea>
          </div>

          <button
            class="action-btn primary"
            disabled={isLoading || !queryText.trim()}
            on:click={() => runQuery('/notebooklm/query', () => ({ query: queryText }))}
          >
            {#if isLoading}
              <span class="spinner"></span>
              Searching...
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              Search Research
            {/if}
          </button>
        {/if}
      </div>

    {:else if activeTab === 'notebooks'}
      <div class="tab-content">
        <h2>Manage Notebooks</h2>
        <p class="tab-description">Register NotebookLM notebooks and assign roles for The Foreman.</p>

        <!-- Add Notebook Form -->
        <div class="card">
          <h3 class="card-title">Add Notebook</h3>
          <div class="form-group">
            <label for="notebook-id">Notebook ID or URL</label>
            <input
              id="notebook-id"
              type="text"
              placeholder="Paste NotebookLM URL or ID..."
              bind:value={notebookIdInput}
              disabled={isRegistering}
            />
          </div>

          <div class="form-group">
            <label for="notebook-label">Label (optional)</label>
            <input
              id="notebook-label"
              type="text"
              placeholder="e.g., Character Research, World Building Notes..."
              bind:value={notebookLabelInput}
              disabled={isRegistering}
            />
            <p class="field-hint">A friendly name to identify this notebook</p>
          </div>

          <div class="form-group">
            <label>Role</label>
            <div class="role-selector">
              {#each roles as role}
                <button
                  class="role-option {selectedRole === role.id ? 'selected' : ''}"
                  on:click={() => selectedRole = role.id}
                  disabled={isRegistering}
                >
                  <span class="role-name">{role.name}</span>
                </button>
              {/each}
            </div>
            <p class="field-hint">{roles.find(r => r.id === selectedRole)?.description}</p>
          </div>

          <button
            class="action-btn primary"
            on:click={handleRegisterNotebook}
            disabled={!notebookIdInput.trim() || isRegistering}
          >
            {#if isRegistering}
              <span class="spinner"></span>
              Registering...
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Add Notebook
            {/if}
          </button>
        </div>

        <!-- Registered Notebooks -->
        {#if notebooks.length > 0}
          <div class="card">
            <h3 class="card-title">Registered Notebooks</h3>
            <div class="notebook-list">
              {#each notebooks as nb}
                <div class="notebook-item">
                  <div class="notebook-info">
                    <span class="notebook-category">{nb.category}</span>
                    <span class="notebook-label">{nb.label}</span>
                  </div>
                  <div class="notebook-actions">
                    <span class="notebook-id">{nb.id.slice(0, 8)}...</span>
                    <button
                      class="delete-btn"
                      on:click={() => handleDeleteNotebook(nb.id)}
                      title="Remove notebook"
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
      </div>

    {:else if activeTab === 'characters'}
      <div class="tab-content">
        <h2>Character Profiles</h2>
        <p class="tab-description">Extract character details from your research notebooks.</p>

        {#if notebooks.length === 0}
          <div class="empty-state">
            <div class="empty-icon">{@html tabIcons.user}</div>
            <p>No notebooks configured</p>
          </div>
        {:else}
          <div class="form-group">
            <label for="char-notebook">Select Notebook</label>
            <select id="char-notebook" on:change={selectNotebook} value={currentNotebook}>
              {#each notebooks as nb}
                <option value={nb.id}>{nb.label}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="char-name">Character Name</label>
            <input
              id="char-name"
              type="text"
              bind:value={characterName}
              placeholder="e.g., Detective Sarah Chen"
            />
          </div>

          <button
            class="action-btn primary"
            disabled={isLoading || !characterName.trim()}
            on:click={() => runQuery('/notebooklm/character-profile', () => ({ character_name: characterName }))}
          >
            {#if isLoading}
              <span class="spinner"></span>
              Extracting...
            {:else}
              Extract Character Profile
            {/if}
          </button>
        {/if}
      </div>

    {:else if activeTab === 'world'}
      <div class="tab-content">
        <h2>World Building</h2>
        <p class="tab-description">Extract world-building details from your research.</p>

        {#if notebooks.length === 0}
          <div class="empty-state">
            <div class="empty-icon">{@html tabIcons.globe}</div>
            <p>No notebooks configured</p>
          </div>
        {:else}
          <div class="form-group">
            <label for="world-notebook">Select Notebook</label>
            <select id="world-notebook" on:change={selectNotebook} value={currentNotebook}>
              {#each notebooks as nb}
                <option value={nb.id}>{nb.label}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="world-aspect">World Aspect</label>
            <input
              id="world-aspect"
              type="text"
              bind:value={worldAspect}
              placeholder="e.g., AI regulation in 2035"
            />
          </div>

          <button
            class="action-btn primary"
            disabled={isLoading || !worldAspect.trim()}
            on:click={() => runQuery('/notebooklm/world-building', () => ({ aspect: worldAspect }))}
          >
            {#if isLoading}
              <span class="spinner"></span>
              Extracting...
            {:else}
              Extract World Details
            {/if}
          </button>
        {/if}
      </div>

    {:else if activeTab === 'saved'}
      <div class="tab-content">
        <h2>Saved Research Notes</h2>
        <p class="tab-description">Review and manage notes saved from NotebookLM extractions. Delete irrelevant ones before Foreman uses them.</p>

        {#if isLoadingNotes}
          <div class="loading-state">
            <span class="spinner"></span>
            Loading saved notes...
          </div>
        {:else if savedNotes.length === 0}
          <div class="empty-state">
            <div class="empty-icon">{@html tabIcons.folder}</div>
            <p>No saved research notes yet</p>
            <p class="empty-hint">Use the Characters or World tabs to extract and save notes</p>
          </div>
        {:else}
          <div class="saved-notes-list">
            {#each savedNotes as note}
              <div class="saved-note-card">
                <div class="note-header">
                  <span class="note-category">{note.category}</span>
                  <span class="note-key">{note.key}</span>
                  <button
                    class="delete-btn"
                    on:click={() => deleteNote(note.id)}
                    disabled={isDeletingNote === note.id}
                    title="Delete this note"
                  >
                    {#if isDeletingNote === note.id}
                      <span class="spinner small"></span>
                    {:else}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                      </svg>
                    {/if}
                  </button>
                </div>
                <div class="note-content">
                  {note.content.length > 300 ? note.content.slice(0, 300) + '...' : note.content}
                </div>
                <div class="note-footer">
                  <span class="note-source">{note.source || 'Unknown source'}</span>
                  {#if note.is_promoted}
                    <span class="note-status promoted">Promoted to Graph</span>
                  {/if}
                </div>
              </div>
            {/each}
          </div>
          <p class="notes-count">{savedNotes.length} note{savedNotes.length !== 1 ? 's' : ''} saved</p>
        {/if}
      </div>

    {:else if activeTab === 'status'}
      <div class="tab-content">
        <h2>Connection Status</h2>
        <p class="tab-description">Check NotebookLM connection and authentication.</p>

        <div class="status-card">
          <div class="status-row">
            <span class="status-label">MCP Bridge</span>
            <span class="status-value {status === 'ready' ? 'success' : 'error'}">
              {status === 'ready' ? 'Connected' : 'Offline'}
            </span>
          </div>
          <div class="status-row">
            <span class="status-label">Notebooks Loaded</span>
            <span class="status-value">{notebooks.length}</span>
          </div>
          <div class="status-row">
            <span class="status-label">Selected Notebook</span>
            <span class="status-value">{currentNotebook ? currentNotebook.slice(0, 12) + '...' : 'None'}</span>
          </div>
        </div>

        <div class="action-buttons">
          <button class="action-btn" on:click={() => { fetchStatus(); fetchConfiguredNotebooks(); }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Refresh Status
          </button>

          <button class="action-btn" on:click={triggerAuth} disabled={isLoading}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"></path>
            </svg>
            Authenticate with Google
          </button>
        </div>
      </div>
    {/if}

    <!-- Error Display -->
    {#if errorMsg}
      <div class="error-banner">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        {errorMsg}
      </div>
    {/if}

    <!-- Results Display - only show on extraction tabs -->
    {#if result && (activeTab === 'research' || activeTab === 'characters' || activeTab === 'world')}
      <div class="results-card">
        <h3 class="results-title">Response</h3>
        <div class="results-content">
          {#if result.answer}
            <p class="answer-text">{result.answer}</p>
          {:else if result.profile}
            <p class="answer-text">{result.profile}</p>
          {:else if result.details}
            <p class="answer-text">{result.details}</p>
          {/if}

          {#if result.sources && result.sources.length > 0}
            <div class="sources-section">
              <h4 class="sources-title">Sources</h4>
              <div class="sources-list">
                {#each result.sources as src}
                  <span class="source-badge">{src.title || src.notebook_id || JSON.stringify(src).slice(0, 30)}</span>
                {/each}
              </div>
            </div>
          {/if}
        </div>

        <!-- Save to KB Button -->
        {#if activeTab === 'characters' || activeTab === 'world'}
          <div class="results-actions">
            <button
              class="action-btn save-btn"
              on:click={handleSaveToKB}
              disabled={isSaving}
            >
              {#if isSaving}
                <span class="spinner"></span>
                Saving...
              {:else}
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                  <polyline points="17 21 17 13 7 13 7 21"></polyline>
                  <polyline points="7 3 7 8 15 8"></polyline>
                </svg>
                Save to Research Notes
              {/if}
            </button>
            <p class="save-hint">Save for Foreman to use when building your Story Bible</p>
          </div>
        {/if}

        <details class="debug-section">
          <summary>Raw JSON</summary>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </details>
      </div>
    {/if}
  </div>
</div>

<style>
  .notebooklm-panel {
    display: flex;
    height: 100%;
    min-height: 500px;
    background: var(--bg-secondary, #1a2027);
  }

  /* Navigation Sidebar */
  .panel-nav {
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
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .connection-badge {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .connection-badge.connected {
    color: var(--success, #3fb950);
  }

  .connection-badge .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
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
    background: var(--accent-purple-muted, rgba(163, 113, 247, 0.2));
    color: var(--accent-purple, #a371f7);
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

  /* Content Area */
  .panel-content {
    flex: 1;
    padding: var(--space-6, 24px);
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
  }

  .tab-content h2 {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .tab-description {
    margin: 0 0 var(--space-4, 16px) 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  /* Form Elements */
  .form-group {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
    margin-bottom: var(--space-3, 12px);
  }

  .form-group label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
  }

  .form-group input,
  .form-group select,
  .form-group textarea {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-ui);
  }

  .form-group input:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-purple, #a371f7);
  }

  .form-group textarea {
    resize: vertical;
    min-height: 80px;
  }

  .field-hint {
    margin: var(--space-1, 4px) 0 0 0;
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  /* Role Selector */
  .role-selector {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .role-option {
    flex: 1;
    padding: var(--space-2, 8px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .role-option:hover:not(:disabled) {
    border-color: var(--accent-purple, #a371f7);
  }

  .role-option.selected {
    background: var(--accent-purple-muted, rgba(163, 113, 247, 0.2));
    border-color: var(--accent-purple, #a371f7);
    color: var(--accent-purple, #a371f7);
  }

  /* Action Buttons */
  .action-btn {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .action-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--border-strong, #3d4752);
    color: var(--text-primary, #e6edf3);
  }

  .action-btn.primary {
    background: var(--accent-purple, #a371f7);
    border-color: var(--accent-purple, #a371f7);
    color: white;
  }

  .action-btn.primary:hover:not(:disabled) {
    background: var(--accent-purple-hover, #b689f9);
    border-color: var(--accent-purple-hover, #b689f9);
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-buttons {
    display: flex;
    gap: var(--space-2, 8px);
    flex-wrap: wrap;
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

  /* Cards */
  .card {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
  }

  .card-title {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  /* Notebook List */
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
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-md, 6px);
  }

  .notebook-info {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .notebook-category {
    padding: 2px 6px;
    background: var(--accent-purple-muted, rgba(163, 113, 247, 0.2));
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--accent-purple, #a371f7);
    text-transform: uppercase;
  }

  .notebook-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .notebook-id {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono);
    color: var(--text-muted, #6e7681);
  }

  .notebook-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    padding: 0;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .delete-btn:hover {
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    color: var(--error, #f85149);
  }

  /* Status Card */
  .status-card {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-lg, 8px);
    margin-bottom: var(--space-4, 16px);
  }

  .status-row {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2, 8px) 0;
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .status-row:last-child {
    border-bottom: none;
  }

  .status-label {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .status-value {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .status-value.success {
    color: var(--success, #3fb950);
  }

  .status-value.error {
    color: var(--error, #f85149);
  }

  /* Empty State */
  .empty-state {
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

  .empty-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    margin-bottom: var(--space-3, 12px);
    background: var(--bg-primary, #0f1419);
    border-radius: var(--radius-full, 9999px);
    color: var(--text-muted, #6e7681);
  }

  .empty-icon :global(svg) {
    width: 24px;
    height: 24px;
  }

  .empty-state p {
    margin: 0;
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
  }

  .empty-hint {
    margin-top: var(--space-1, 4px) !important;
    font-size: var(--text-xs, 11px) !important;
    color: var(--text-muted, #6e7681) !important;
  }

  /* Error Banner */
  .error-banner {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    background: var(--error-muted, rgba(248, 81, 73, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--error, #f85149);
    font-size: var(--text-sm, 12px);
  }

  /* Results */
  .results-card {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--accent-purple-muted, rgba(163, 113, 247, 0.3));
    border-radius: var(--radius-lg, 8px);
  }

  .results-title {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--accent-purple, #a371f7);
  }

  .results-content {
    margin-bottom: var(--space-3, 12px);
  }

  .answer-text {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    line-height: var(--leading-relaxed, 1.7);
    white-space: pre-wrap;
  }

  .sources-section {
    margin-top: var(--space-3, 12px);
    padding-top: var(--space-3, 12px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .sources-title {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    color: var(--text-muted, #6e7681);
  }

  .sources-list {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
  }

  .source-badge {
    padding: 2px 8px;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-sm, 4px);
    font-size: 10px;
    color: var(--text-secondary, #8b949e);
  }

  /* Save to KB section */
  .results-actions {
    margin-top: var(--space-4, 16px);
    padding-top: var(--space-3, 12px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .save-btn {
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    border-color: var(--success, #3fb950);
    color: var(--success, #3fb950);
  }

  .save-btn:hover:not(:disabled) {
    background: var(--success, #3fb950);
    color: white;
  }

  .save-hint {
    margin: var(--space-2, 8px) 0 0 0;
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .debug-section {
    margin-top: var(--space-2, 8px);
  }

  .debug-section summary {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .debug-section pre {
    margin-top: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    background: var(--bg-primary, #0f1419);
    border-radius: var(--radius-md, 6px);
    font-size: 10px;
    font-family: var(--font-mono);
    color: var(--text-secondary, #8b949e);
    overflow-x: auto;
  }

  /* Loading State */
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-3, 12px);
    padding: var(--space-10, 40px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-lg, 8px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
  }

  /* Saved Notes List */
  .saved-notes-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .saved-note-card {
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    transition: border-color var(--transition-fast, 100ms ease);
  }

  .saved-note-card:hover {
    border-color: var(--border-strong, #3d4752);
  }

  .note-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    margin-bottom: var(--space-3, 12px);
  }

  .note-category {
    padding: 2px 8px;
    background: var(--accent-purple-muted, rgba(163, 113, 247, 0.2));
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    color: var(--accent-purple, #a371f7);
    text-transform: uppercase;
    flex-shrink: 0;
  }

  .note-key {
    flex: 1;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .note-content {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
    white-space: pre-wrap;
    margin-bottom: var(--space-3, 12px);
  }

  .note-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: var(--space-2, 8px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .note-source {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .note-status {
    padding: 2px 6px;
    border-radius: var(--radius-sm, 4px);
    font-size: 9px;
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
  }

  .note-status.promoted {
    background: var(--success-muted, rgba(63, 185, 80, 0.2));
    color: var(--success, #3fb950);
  }

  .notes-count {
    margin-top: var(--space-4, 16px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    text-align: center;
  }

  .spinner.small {
    width: 12px;
    height: 12px;
    border-width: 1.5px;
  }
</style>
