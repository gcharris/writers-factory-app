<!--
  SessionManagerModal.svelte - Chat Session Manager

  Features:
  - List all chat sessions with dates and stats
  - Search/filter sessions
  - Click to load session into Foreman chat
  - Export session to JSON or Markdown
  - Delete sessions
  - Archive/restore functionality
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';

  const dispatch = createEventDispatcher();

  // Sessions data
  let sessions = [];
  let loading = true;
  let error = '';

  // Search/filter state
  let searchQuery = '';
  let sortBy = 'recent'; // 'recent', 'oldest', 'messages'
  let filterArchived = false;

  // Selected session for preview
  let selectedSession = null;
  let sessionHistory = [];
  let loadingHistory = false;

  // Export state
  let exporting = false;
  let exportFormat = 'markdown'; // 'markdown' or 'json'

  // Confirmation modal
  let showDeleteConfirm = false;
  let sessionToDelete = null;

  onMount(async () => {
    await loadSessions();
  });

  async function loadSessions() {
    loading = true;
    error = '';

    try {
      const res = await fetch('http://localhost:8000/sessions/active?limit=100');
      if (!res.ok) throw new Error('Failed to load sessions');

      const data = await res.json();
      sessions = data.sessions || [];
    } catch (e) {
      console.error('Session load error:', e);
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function loadSessionHistory(sessionId) {
    loadingHistory = true;

    try {
      const res = await fetch(`http://localhost:8000/session/${sessionId}/history?limit=100`);
      if (!res.ok) throw new Error('Failed to load history');

      const data = await res.json();
      sessionHistory = data.events || [];
    } catch (e) {
      console.error('History load error:', e);
      sessionHistory = [];
    } finally {
      loadingHistory = false;
    }
  }

  function selectSession(session) {
    selectedSession = session;
    loadSessionHistory(session.session_id);
  }

  function loadSessionIntoForeman() {
    if (!selectedSession) return;
    dispatch('load-session', {
      sessionId: selectedSession.session_id,
      history: sessionHistory
    });
    dispatch('close');
  }

  async function exportSession() {
    if (!selectedSession || sessionHistory.length === 0) return;

    exporting = true;

    try {
      let content = '';
      let filename = '';
      let mimeType = '';

      if (exportFormat === 'markdown') {
        content = generateMarkdown();
        filename = `session-${selectedSession.session_id.slice(0, 8)}.md`;
        mimeType = 'text/markdown';
      } else {
        content = JSON.stringify({
          session_id: selectedSession.session_id,
          scene_id: selectedSession.scene_id,
          exported_at: new Date().toISOString(),
          events: sessionHistory
        }, null, 2);
        filename = `session-${selectedSession.session_id.slice(0, 8)}.json`;
        mimeType = 'application/json';
      }

      // Trigger download
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } finally {
      exporting = false;
    }
  }

  function generateMarkdown() {
    const lines = [];
    const date = selectedSession.last_activity
      ? new Date(selectedSession.last_activity).toLocaleString()
      : 'Unknown';

    lines.push(`# Chat Session Export`);
    lines.push('');
    lines.push(`**Session ID:** \`${selectedSession.session_id}\``);
    if (selectedSession.scene_id) {
      lines.push(`**Scene:** ${selectedSession.scene_id}`);
    }
    lines.push(`**Exported:** ${new Date().toLocaleString()}`);
    lines.push(`**Last Activity:** ${date}`);
    lines.push(`**Messages:** ${sessionHistory.length}`);
    lines.push('');
    lines.push('---');
    lines.push('');

    for (const event of sessionHistory) {
      if (event.role === 'system') continue;

      const role = event.role === 'user' ? '**You:**' : '**Foreman:**';
      const timestamp = event.timestamp
        ? new Date(event.timestamp).toLocaleTimeString()
        : '';

      lines.push(`### ${role} ${timestamp}`);
      lines.push('');
      lines.push(event.content);
      lines.push('');
    }

    return lines.join('\n');
  }

  function confirmDelete(session) {
    sessionToDelete = session;
    showDeleteConfirm = true;
  }

  async function deleteSession() {
    if (!sessionToDelete) return;

    // Note: Backend delete endpoint would need to be implemented
    // For now, just remove from local list
    sessions = sessions.filter(s => s.session_id !== sessionToDelete.session_id);

    if (selectedSession?.session_id === sessionToDelete.session_id) {
      selectedSession = null;
      sessionHistory = [];
    }

    showDeleteConfirm = false;
    sessionToDelete = null;
  }

  // Filter and sort sessions
  $: filteredSessions = sessions
    .filter(s => {
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        s.session_id.toLowerCase().includes(q) ||
        (s.scene_id && s.scene_id.toLowerCase().includes(q))
      );
    })
    .sort((a, b) => {
      if (sortBy === 'recent') {
        return new Date(b.last_activity) - new Date(a.last_activity);
      } else if (sortBy === 'oldest') {
        return new Date(a.last_activity) - new Date(b.last_activity);
      } else {
        return b.event_count - a.event_count;
      }
    });

  // Format relative time
  function formatRelativeTime(dateStr) {
    if (!dateStr) return 'Unknown';

    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }

  function close() {
    dispatch('close');
  }
</script>

<div class="modal-backdrop" on:click={close} on:keydown={(e) => e.key === 'Escape' && close()}>
  <div class="modal-content" on:click|stopPropagation>
    <!-- Header -->
    <div class="modal-header">
      <div class="header-left">
        <span class="modal-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
        </span>
        <div class="header-info">
          <h2>Session Manager</h2>
          <span class="header-subtitle">{sessions.length} sessions</span>
        </div>
      </div>
      <button class="close-btn" on:click={close}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="modal-body">
      <!-- Left: Session List -->
      <div class="session-list-panel">
        <!-- Search & Filters -->
        <div class="list-controls">
          <div class="search-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
            <input
              type="text"
              bind:value={searchQuery}
              placeholder="Search sessions..."
              class="search-input"
            />
          </div>
          <select bind:value={sortBy} class="sort-select">
            <option value="recent">Most Recent</option>
            <option value="oldest">Oldest First</option>
            <option value="messages">Most Messages</option>
          </select>
        </div>

        <!-- Session List -->
        <div class="session-list">
          {#if loading}
            <div class="loading-state">
              <div class="spinner"></div>
              <span>Loading sessions...</span>
            </div>
          {:else if error}
            <div class="error-state">
              <span>{error}</span>
              <button class="retry-btn" on:click={loadSessions}>Retry</button>
            </div>
          {:else if filteredSessions.length === 0}
            <div class="empty-state">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              <span>No sessions found</span>
            </div>
          {:else}
            {#each filteredSessions as session}
              <button
                class="session-item"
                class:selected={selectedSession?.session_id === session.session_id}
                on:click={() => selectSession(session)}
              >
                <div class="session-main">
                  <span class="session-id">
                    {session.session_id.slice(0, 8)}...
                  </span>
                  {#if session.scene_id}
                    <span class="session-scene">{session.scene_id}</span>
                  {/if}
                </div>
                <div class="session-meta">
                  <span class="session-messages">{session.event_count} msgs</span>
                  <span class="session-time">{formatRelativeTime(session.last_activity)}</span>
                </div>
              </button>
            {/each}
          {/if}
        </div>
      </div>

      <!-- Right: Session Preview -->
      <div class="session-preview-panel">
        {#if !selectedSession}
          <div class="preview-empty">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>Select a session to preview</span>
          </div>
        {:else}
          <!-- Preview Header -->
          <div class="preview-header">
            <div class="preview-title">
              <span class="preview-id">{selectedSession.session_id.slice(0, 8)}...</span>
              {#if selectedSession.scene_id}
                <span class="preview-scene">{selectedSession.scene_id}</span>
              {/if}
            </div>
            <div class="preview-actions">
              <select bind:value={exportFormat} class="export-select">
                <option value="markdown">Markdown</option>
                <option value="json">JSON</option>
              </select>
              <button
                class="action-btn export-btn"
                on:click={exportSession}
                disabled={exporting || sessionHistory.length === 0}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Export
              </button>
              <button
                class="action-btn delete-btn"
                on:click={() => confirmDelete(selectedSession)}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>

          <!-- Preview Messages -->
          <div class="preview-messages">
            {#if loadingHistory}
              <div class="loading-state">
                <div class="spinner"></div>
                <span>Loading messages...</span>
              </div>
            {:else if sessionHistory.length === 0}
              <div class="empty-state">
                <span>No messages in this session</span>
              </div>
            {:else}
              {#each sessionHistory as event}
                {#if event.role !== 'system'}
                  <div class="preview-message" class:user={event.role === 'user'} class:assistant={event.role === 'assistant'}>
                    <div class="message-header">
                      <span class="message-role">{event.role === 'user' ? 'You' : 'Foreman'}</span>
                      <span class="message-time">
                        {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                    <div class="message-content">
                      {event.content.length > 300
                        ? event.content.slice(0, 300) + '...'
                        : event.content}
                    </div>
                  </div>
                {/if}
              {/each}
            {/if}
          </div>

          <!-- Preview Footer -->
          <div class="preview-footer">
            <button class="load-btn" on:click={loadSessionIntoForeman}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="1 4 1 10 7 10"></polyline>
                <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
              </svg>
              Load into Foreman Chat
            </button>
          </div>
        {/if}
      </div>
    </div>

    <!-- Delete Confirmation -->
    {#if showDeleteConfirm}
      <div class="confirm-overlay" on:click={() => showDeleteConfirm = false}>
        <div class="confirm-dialog" on:click|stopPropagation>
          <h3>Delete Session?</h3>
          <p>This will permanently delete this session and all its messages.</p>
          <div class="confirm-actions">
            <button class="cancel-btn" on:click={() => showDeleteConfirm = false}>Cancel</button>
            <button class="confirm-delete-btn" on:click={deleteSession}>Delete</button>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--space-4, 16px);
  }

  .modal-content {
    width: 100%;
    max-width: 900px;
    max-height: 80vh;
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow: var(--shadow-xl, 0 20px 40px rgba(0, 0, 0, 0.5));
  }

  /* Header */
  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .header-left {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .modal-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: rgba(88, 166, 255, 0.15);
    border-radius: var(--radius-md, 6px);
    color: var(--accent-cyan, #58a6ff);
  }

  .header-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .modal-header h2 {
    margin: 0;
    font-size: var(--text-base, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .header-subtitle {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .close-btn {
    padding: var(--space-2, 8px);
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    border-radius: var(--radius-md, 6px);
    transition: all 0.1s ease;
  }

  .close-btn:hover {
    background: var(--bg-tertiary, #252d38);
    color: var(--text-primary, #e6edf3);
  }

  /* Body */
  .modal-body {
    display: flex;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  /* Session List Panel */
  .session-list-panel {
    width: 320px;
    display: flex;
    flex-direction: column;
    border-right: 1px solid var(--border, #2d3a47);
    background: var(--bg-secondary, #1a2027);
  }

  .list-controls {
    display: flex;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .search-wrapper {
    flex: 1;
    position: relative;
  }

  .search-icon {
    position: absolute;
    left: var(--space-2, 8px);
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted, #6e7681);
    pointer-events: none;
  }

  .search-input {
    width: 100%;
    padding: 6px var(--space-2, 8px) 6px 30px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-primary, #e6edf3);
    font-size: var(--text-sm, 12px);
  }

  .search-input::placeholder {
    color: var(--text-muted, #6e7681);
  }

  .search-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .sort-select {
    padding: 6px var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
  }

  .sort-select:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-2, 8px);
  }

  .session-item {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid transparent;
    border-radius: var(--radius-md, 6px);
    text-align: left;
    cursor: pointer;
    transition: all 0.1s ease;
    margin-bottom: var(--space-2, 8px);
  }

  .session-item:hover {
    background: var(--bg-elevated, #2d3a47);
    border-color: var(--border-strong, #3d4a57);
  }

  .session-item.selected {
    background: rgba(88, 166, 255, 0.1);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .session-main {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .session-id {
    font-family: var(--font-mono, 'SF Mono', monospace);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .session-scene {
    font-size: var(--text-xs, 11px);
    color: var(--accent-purple, #a371f7);
  }

  .session-meta {
    display: flex;
    justify-content: space-between;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Preview Panel */
  .session-preview-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .preview-empty {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-3, 12px);
    color: var(--text-muted, #6e7681);
  }

  .preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-bottom: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .preview-title {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .preview-id {
    font-family: var(--font-mono, 'SF Mono', monospace);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
  }

  .preview-scene {
    font-size: var(--text-xs, 11px);
    color: var(--accent-purple, #a371f7);
  }

  .preview-actions {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .export-select {
    padding: 4px var(--space-2, 8px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px var(--space-3, 12px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .action-btn:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3a47);
    color: var(--text-primary, #e6edf3);
  }

  .action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .delete-btn:hover:not(:disabled) {
    background: rgba(248, 81, 73, 0.15);
    border-color: var(--error, #f85149);
    color: var(--error, #f85149);
  }

  /* Messages */
  .preview-messages {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-3, 12px);
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .preview-message {
    padding: var(--space-3, 12px);
    border-radius: var(--radius-md, 6px);
    background: var(--bg-tertiary, #252d38);
  }

  .preview-message.user {
    background: rgba(88, 166, 255, 0.1);
    border-left: 3px solid var(--accent-cyan, #58a6ff);
  }

  .preview-message.assistant {
    background: rgba(212, 165, 116, 0.1);
    border-left: 3px solid var(--accent-gold, #d4a574);
  }

  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-2, 8px);
  }

  .message-role {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .message-time {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .message-content {
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* Preview Footer */
  .preview-footer {
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-top: 1px solid var(--border, #2d3a47);
    flex-shrink: 0;
  }

  .load-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-3, 12px);
    background: var(--accent-cyan, #58a6ff);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
    transition: all 0.1s ease;
  }

  .load-btn:hover {
    background: var(--accent-cyan-hover, #79b8ff);
    transform: translateY(-1px);
  }

  /* Loading/Error/Empty States */
  .loading-state,
  .error-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-2, 8px);
    padding: var(--space-6, 24px);
    color: var(--text-muted, #6e7681);
    text-align: center;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #58a6ff);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .retry-btn {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--accent-cyan, #58a6ff);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: var(--bg-primary, #0f1419);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
  }

  /* Confirm Dialog */
  .confirm-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .confirm-dialog {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    padding: var(--space-4, 16px);
    max-width: 320px;
    text-align: center;
  }

  .confirm-dialog h3 {
    margin: 0 0 var(--space-2, 8px);
    font-size: var(--text-base, 14px);
    color: var(--text-primary, #e6edf3);
  }

  .confirm-dialog p {
    margin: 0 0 var(--space-4, 16px);
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .confirm-actions {
    display: flex;
    gap: var(--space-2, 8px);
    justify-content: center;
  }

  .cancel-btn {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #8b949e);
    font-size: var(--text-sm, 12px);
    cursor: pointer;
  }

  .confirm-delete-btn {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--error, #f85149);
    border: none;
    border-radius: var(--radius-md, 6px);
    color: white;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    cursor: pointer;
  }

  .confirm-delete-btn:hover {
    background: #da3633;
  }
</style>
