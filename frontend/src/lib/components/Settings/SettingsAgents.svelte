<script lang="ts">
  import { onMount } from 'svelte';
  import PremiumKeyForm from '../Shared/PremiumKeyForm.svelte';

  const BASE_URL = 'http://localhost:8000';

  let keyStatus: any = null;
  let loading = true;
  let error = '';

  onMount(async () => {
    await loadKeyStatus();
  });

  async function loadKeyStatus() {
    loading = true;
    error = '';
    try {
      const response = await fetch(`${BASE_URL}/api-keys/status?t=${Date.now()}`);
      if (response.ok) {
        keyStatus = await response.json();
      } else {
        throw new Error('Failed to load key status');
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to check API keys';
    } finally {
      loading = false;
    }
  }

  function handleSaved() {
    loadKeyStatus();
  }

  function handleCancel() {
    // In settings, cancel might just clear the form or do nothing
    // For now, we'll just reload status to reset any unsaved changes
    loadKeyStatus();
  }
</script>

<div class="settings-agents">
  <div class="header">
    <h2>Key Management</h2>
    <p class="description">
      Configure your API keys.
    </p>
  </div>

  {#if loading}
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Loading key status...</p>
    </div>
  {:else if error}
    <div class="error-state">
      <p>{error}</p>
      <button class="btn-secondary" on:click={loadKeyStatus}>Retry</button>
    </div>
  {:else}
    <!-- We wrap the form in a container that removes the modal styling context if needed, 
         but PremiumKeyForm is designed as a modal content. 
         For the Settings page, we might want it embedded. 
         Let's adjust the styling in PremiumKeyForm to be flexible, 
         or just render it here. 
         
         Actually, the user requested "Premium Keys" page to be the place to enter keys.
         The form component has a "Cancel" button and "Modal Header".
         We can hide those via CSS or props if we want it to look like a normal page.
         For now, let's just render it. It will look like a card.
    -->
    <div class="form-container">
      <PremiumKeyForm 
        {keyStatus} 
        on:saved={handleSaved}
        on:cancel={handleCancel}
      />
    </div>
  {/if}
</div>

<style>
  .settings-agents {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
  }

  .header {
    margin-bottom: 1.5rem;
  }

  .header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
  }

  .description {
    color: var(--text-secondary, #8b949e);
    margin: 0;
    font-size: 1rem;
  }

  .form-container {
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border, #30363d);
    border-radius: 12px;
    overflow: hidden;
  }

  /* Loading/Error States */
  .loading-state, .error-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 3rem;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--border, #2d3a47);
    border-top-color: var(--accent-cyan, #00d9ff);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-state p, .error-state p {
    margin-top: 1rem;
    color: var(--text-secondary, #8b949e);
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border, #30363d);
    color: #ffffff;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #21262d);
  }
</style>
