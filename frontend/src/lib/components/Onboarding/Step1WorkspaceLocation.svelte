<!--
  Step1WorkspaceLocation.svelte - Workspace Location Setup Step

  Purpose: Let users choose where their writing projects will be stored.
  This is the first step before Local AI setup.

  Flow:
  1. Show default location (~/Documents/Writers Factory)
  2. Let user browse for custom location
  3. Validate the path is writable
  4. Continue when a valid path is selected
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { open } from '@tauri-apps/plugin-dialog';
  import { workspacePath } from '$lib/stores';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // State
  let selectedPath: string = '';
  let validating = false;
  let pathValid = false;
  let error = '';
  let defaultPath = '';

  // Check if path is valid
  $: isReady = selectedPath && pathValid && !validating;

  onMount(async () => {
    // Get the default workspace path from backend
    await getDefaultPath();

    // Check if we already have a saved workspace path
    if ($workspacePath) {
      selectedPath = $workspacePath;
      await validatePath(selectedPath);
    } else if (defaultPath) {
      selectedPath = defaultPath;
      await validatePath(defaultPath);
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
      // Fallback - will be set by backend
      defaultPath = '';
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

  async function browseFolder() {
    try {
      const selected = await open({
        directory: true,
        multiple: false,
        title: 'Choose Workspace Location'
      });

      if (selected && typeof selected === 'string') {
        selectedPath = selected;
        await validatePath(selected);
      }
    } catch (e) {
      console.error('Failed to open folder dialog:', e);
      error = 'Could not open folder picker';
    }
  }

  async function useDefaultPath() {
    if (defaultPath) {
      selectedPath = defaultPath;
      await validatePath(defaultPath);
    }
  }

  function handleContinue() {
    if (isReady) {
      // Save the workspace path to the store
      workspacePath.set(selectedPath);
      dispatch('complete', { path: selectedPath });
      dispatch('next');
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
    <!-- Current Selection -->
    <div class="path-display {pathValid ? 'valid' : error ? 'invalid' : ''}">
      <div class="path-icon">
        {#if validating}
          <div class="spinner"></div>
        {:else if pathValid}
          <span class="check">✓</span>
        {:else if error}
          <span class="error-icon">✗</span>
        {:else}
          <span class="folder-icon">📁</span>
        {/if}
      </div>
      <div class="path-text">
        {#if selectedPath}
          <span class="path-value">{formatPath(selectedPath)}</span>
        {:else}
          <span class="path-placeholder">No location selected</span>
        {/if}
      </div>
    </div>

    {#if error}
      <div class="error-message">{error}</div>
    {/if}

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button class="btn-primary" on:click={browseFolder}>
        <span class="btn-icon">📂</span>
        Browse...
      </button>
      {#if defaultPath && selectedPath !== defaultPath}
        <button class="btn-secondary" on:click={useDefaultPath}>
          Use Default Location
        </button>
      {/if}
    </div>

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
    <div></div> <!-- Spacer for alignment -->
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
    max-width: 500px;
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

  /* Workspace Content */
  .workspace-content {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  /* Path Display */
  .path-display {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--border, #2d3a47);
    border-radius: 8px;
    transition: border-color 0.2s;
  }

  .path-display.valid {
    border-color: var(--success, #3fb950);
  }

  .path-display.invalid {
    border-color: var(--error, #f85149);
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
    overflow: hidden;
  }

  .path-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9375rem;
    color: #ffffff;
    word-break: break-all;
  }

  .path-placeholder {
    color: var(--text-secondary, #8b949e);
    font-style: italic;
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

  /* Action Buttons */
  .action-buttons {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .btn-icon {
    margin-right: 0.5rem;
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

  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #242d38);
    border-color: var(--accent-cyan, #00d9ff);
    color: var(--accent-cyan, #00d9ff);
  }

  .arrow {
    font-size: 1.25rem;
  }
</style>
