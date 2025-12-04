<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import CloudModelsList from '../Shared/CloudModelsList.svelte';

  const dispatch = createEventDispatcher();

  function handleConfigure() {
    // Dispatch event to parent (Settings.svelte) to switch tab
    dispatch('navigate', { tab: 'api-keys' });
  }
</script>

<div class="settings-models">
  <div class="header">
    <h2>AI Models</h2>
    <p class="description">
      View and test all available AI models.
    </p>
  </div>

  <CloudModelsList on:configure={handleConfigure} />
</div>

<style>
  .settings-models {
    max-width: 100%;
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
</style>
