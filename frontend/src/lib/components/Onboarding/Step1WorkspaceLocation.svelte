<!--
  Step1WorkspaceLocation.svelte - Workspace Location Setup Step

  Purpose: Let users choose where their writing projects will be stored.

  Redesigned Flow:
  1. Present a clear choice: Use default location OR choose custom
  2. Default option is prominent with "Use Default" button
  3. Custom option via "Choose Your Own" button
  4. Only show confirmation after user makes a choice
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { workspacePath } from '$lib/stores';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Tauri dialog (loaded dynamically)
  let tauriDialog: any = null;
  let isTauriAvailable = false;

  // State
  type ViewState = 'choosing' | 'confirming';
  let viewState: ViewState = 'choosing';
  let selectedPath: string = '';
  let validating = false;
  let pathValid = false;
  let error = '';
  let defaultPath = '';

  // Check if ready to continue
  $: isReady = selectedPath && pathValid && !validating;

  onMount(async () => {
    // Try to load Tauri dialog API
    try {
      tauriDialog = await import('@tauri-apps/plugin-dialog');
      isTauriAvailable = true;
    } catch (e) {
      console.log('Tauri dialog not available');
      isTauriAvailable = false;
    }

    // Get the default workspace path from backend
    await getDefaultPath();

    // If we already have a saved workspace path, go to confirm state
    if ($workspacePath) {
      selectedPath = $workspacePath;
      await validatePath(selectedPath);
      viewState = 'confirming';
    }
  });

  async function getDefaultPath() {
    try {
      const response = await fetch(`${BASE_URL}/system/workspace/default`);
      if (response.ok) {
        const data = await response.json();
        defaultPath = data.path;
      }
    } catch (e) {
      console.warn('Failed to get default workspace path:', e);
      // Fallback
      defaultPath = '~/Documents/Writers Factory';
    }
  }

  async function validatePath(path: string) {
    if (!path) {
      pathValid = false;
      return;
    }

    validating = true;
    error = '';

    try {
      const response = await fetch(`${BASE_URL}/system/workspace/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Invalid path');
      }

      const result = await response.json();
      pathValid = result.valid;

      if (!result.valid) {
        error = result.error || 'This location cannot be used';
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to validate path';
      pathValid = false;
    } finally {
      validating = false;
    }
  }

  async function useDefaultLocation() {
    if (defaultPath) {
      selectedPath = defaultPath;
      await validatePath(defaultPath);
      viewState = 'confirming';
    }
  }

  async function browseFolder() {
    if (!isTauriAvailable || !tauriDialog) {
      error = 'Folder picker requires the desktop app';
      return;
    }

    try {
      const selected = await tauriDialog.open({
        directory: true,
        multiple: false,
        title: 'Choose Workspace Location'
      });

      if (selected && typeof selected === 'string') {
        selectedPath = selected;
        await validatePath(selected);
        viewState = 'confirming';
      }
    } catch (e) {
      console.error('Failed to open folder dialog:', e);
      error = 'Could not open folder picker';
    }
  }

  function changeLocation() {
    viewState = 'choosing';
    error = '';
  }

  async function handleContinue() {
    if (!isReady) return;

    // Create the directory if it doesn't exist yet
    validating = true;
    error = '';

    try {
      const response = await fetch(`${BASE_URL}/system/workspace/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: selectedPath, create_if_missing: true })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create workspace');
      }

      const result = await response.json();
      if (!result.valid) {
        error = result.error || 'Failed to create workspace directory';
        return;
      }

      // Success - save the workspace path and proceed
      workspacePath.set(selectedPath);
      dispatch('complete', { path: selectedPath });
      dispatch('next');
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to create workspace';
    } finally {
      validating = false;
    }
  }

  function formatPath(path: string): string {
    // Shorten home directory for display
    if (path.startsWith('/Users/')) {
      const parts = path.split('/');
      if (parts.length >= 3) {
        return '~/' + parts.slice(3).join('/');
      }
    }
    return path;
  }
</script>

<div class="step-workspace">
  <div class="step-header">
    <h2>Where should we store your writing projects?</h2>
    <p class="step-description">
      Choose a folder on your computer. You can use cloud-synced folders like Dropbox or iCloud.
    </p>
  </div>

  <div class="workspace-content">
    {#if viewState === 'choosing'}
      <!-- Choice View: Two clear options -->
      <div class="choice-section">
        <!-- Default Location Option -->
        <button class="choice-card primary" on:click={useDefaultLocation}>
          <div class="choice-icon">📁</div>
          <div class="choice-content">
            <h3>Use Default Location</h3>
            <p class="choice-path">{formatPath(defaultPath || '~/Documents/Writers Factory')}</p>
            <p class="choice-hint">Recommended - we'll create this folder for you</p>
          </div>
          <div class="choice-arrow">→</div>
        </button>

        <!-- Custom Location Option -->
        <button class="choice-card secondary" on:click={browseFolder} disabled={!isTauriAvailable}>
          <div class="choice-icon">🔍</div>
          <div class="choice-content">
            <h3>Choose Your Own Location</h3>
            <p class="choice-hint">Select an existing folder or create a new one</p>
          </div>
          <div class="choice-arrow">→</div>
        </button>
      </div>

      {#if error}
        <div class="error-message">{error}</div>
      {/if}
    {:else}
      <!-- Confirmation View: Show selected path -->
      <div class="confirmation-section">
        <div class="path-display valid">
          <div class="path-icon">
            {#if validating}
              <div class="spinner"></div>
            {:else if pathValid}
              <span class="check">✓</span>
            {:else}
              <span class="error-icon">✗</span>
            {/if}
          </div>
          <div class="path-text">
            <span class="path-label">Your workspace:</span>
            <span class="path-value">{formatPath(selectedPath)}</span>
          </div>
        </div>

        {#if error}
          <div class="error-message">{error}</div>
        {/if}

        <button class="btn-change" on:click={changeLocation}>
          Choose a different location
        </button>
      </div>
    {/if}

    <!-- Info Box -->
    <div class="info-box">
      <div class="info-icon">💡</div>
      <div class="info-content">
        <p><strong>What gets stored here?</strong></p>
        <ul>
          <li>Your manuscript files and chapters</li>
          <li>Story Bible documents</li>
          <li>Voice calibration samples</li>
          <li>Project settings</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Navigation -->
  <div class="step-actions">
    <div></div>
    <button
      class="btn-primary"
      on:click={handleContinue}
      disabled={!isReady}
    >
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<style>
  .step-workspace {
    max-width: 520px;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .step-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .step-description {
    color: var(--text-secondary, #8b949e);
    margin: 0;
    font-size: 1rem;
  }

  .workspace-content {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  /* Choice Cards */
  .choice-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .choice-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.25rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--border, #2d3a47);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
  }

  .choice-card:hover:not(:disabled) {
    border-color: var(--accent-cyan, #00d9ff);
    background: rgba(0, 217, 255, 0.05);
  }

  .choice-card:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .choice-card.primary {
    border-color: var(--accent-cyan, #00d9ff);
    background: rgba(0, 217, 255, 0.08);
  }

  .choice-icon {
    font-size: 1.75rem;
    flex-shrink: 0;
  }

  .choice-content {
    flex: 1;
  }

  .choice-content h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #ffffff;
  }

  .choice-path {
    margin: 0 0 0.25rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.875rem;
    color: var(--accent-cyan, #00d9ff);
  }

  .choice-hint {
    margin: 0;
    font-size: 0.8125rem;
    color: var(--text-muted, #6e7681);
  }

  .choice-arrow {
    font-size: 1.5rem;
    color: var(--text-muted, #6e7681);
    flex-shrink: 0;
  }

  .choice-card:hover .choice-arrow {
    color: var(--accent-cyan, #00d9ff);
  }

  /* Confirmation Section */
  .confirmation-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .path-display {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.25rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--success, #3fb950);
    border-radius: 8px;
  }

  .path-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
  }

  .path-icon .check {
    color: var(--success, #3fb950);
    font-weight: bold;
  }

  .path-icon .error-icon {
    color: var(--error, #f85149);
    font-weight: bold;
  }

  .path-icon .spinner {
    width: 18px;
    height: 18px;
    border: 2px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #00d9ff);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .path-text {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .path-label {
    font-size: 0.75rem;
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .path-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9375rem;
    color: #ffffff;
    word-break: break-all;
  }

  .btn-change {
    align-self: flex-start;
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-change:hover {
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  /* Error Message */
  .error-message {
    padding: 0.75rem;
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 6px;
    color: var(--error, #f85149);
    font-size: 0.875rem;
  }

  /* Info Box */
  .info-box {
    display: flex;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(0, 217, 255, 0.05);
    border: 1px solid rgba(0, 217, 255, 0.2);
    border-radius: 8px;
  }

  .info-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
  }

  .info-content p {
    margin: 0 0 0.5rem 0;
    color: var(--accent-cyan, #00d9ff);
    font-size: 0.9375rem;
  }

  .info-content ul {
    margin: 0;
    padding-left: 1.25rem;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
  }

  .info-content li {
    margin-bottom: 0.25rem;
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .arrow {
    font-size: 1.25rem;
  }
</style>
