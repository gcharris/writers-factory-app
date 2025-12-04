<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import CloudModelsList from '../Shared/CloudModelsList.svelte';
  import PremiumKeyForm from '../Shared/PremiumKeyForm.svelte';

  const dispatch = createEventDispatcher();

  let cloudModelsList: CloudModelsList;
  let showConfigureModal = false;
  let keyStatus: any = null;

  // We need to get keyStatus to pass to the modal
  // We can get it from the list component or fetch it ourselves
  // Let's fetch it ourselves or expose it from the list
  // Simpler to just let the list handle its data and we fetch for the modal when opening
  
  const BASE_URL = 'http://localhost:8000';

  async function loadKeyStatus() {
    try {
      const response = await fetch(`${BASE_URL}/api-keys/status?t=${Date.now()}`);
      if (response.ok) {
        keyStatus = await response.json();
      }
    } catch (e) {
      console.error('Failed to load key status', e);
    }
  }

  function handleBack() {
    dispatch('back');
  }

  function handleContinue() {
    dispatch('next');
  }

  async function openConfigureModal() {
    await loadKeyStatus();
    showConfigureModal = true;
  }

  function closeConfigureModal() {
    showConfigureModal = false;
  }

  function handleSaved() {
    // Refresh the list
    if (cloudModelsList) {
      cloudModelsList.loadKeyStatus();
    }
    // Close modal after a short delay (handled by form component? no, form just emits saved)
    // The form component handles the "Saved!" message. We should wait a bit or just close.
    // Let's let the user close it or close it automatically.
    // The user might want to enter multiple keys.
    // But for better UX, let's refresh status in background.
    loadKeyStatus();
  }
</script>

<div class="step-cloud-models">
  <div class="step-header">
    <h2>Cloud AI Models</h2>
    <p class="step-description">
      Configure your AI models. Some are included free, others require your own API keys.
    </p>
  </div>

  <CloudModelsList 
    bind:this={cloudModelsList} 
    on:configure={openConfigureModal} 
  />

  <!-- Info Note -->
  <div class="info-note">
    <p class="skip-text">You can configure keys later in Settings.</p>
  </div>

  <!-- Navigation -->
  <div class="step-actions">
    <button class="btn-secondary" on:click={handleBack}>
      <span class="arrow">←</span>
      Back
    </button>
    <button class="btn-primary" on:click={handleContinue}>
      Continue
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<!-- Configure Keys Modal -->
{#if showConfigureModal}
  <div class="modal-overlay" on:click={closeConfigureModal} on:keydown={(e) => e.key === 'Escape' && closeConfigureModal()} role="button" tabindex="0">
    <div class="modal-content" on:click|stopPropagation on:keydown|stopPropagation role="dialog" aria-modal="true" tabindex="-1">
      <!-- PremiumKeyForm handles its own header/body/footer structure, 
           but we need to ensure it fits in our modal wrapper or if it brings its own.
           The shared component has header/body/footer. 
           So we just wrap it in the overlay/content box.
      -->
      <PremiumKeyForm 
        {keyStatus} 
        on:saved={handleSaved}
        on:cancel={closeConfigureModal}
      />
    </div>
  </div>
{/if}

<style>
  .step-cloud-models {
    max-width: 900px;
    margin: 0 auto;
  }

  .step-header {
    text-align: center;
    margin-bottom: 1.5rem;
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

  .info-note {
    text-align: center;
    margin-top: 1rem;
    margin-bottom: 2rem;
  }

  .skip-text {
    font-style: italic;
    font-size: 0.9rem;
    color: var(--text-secondary, #8b949e);
    opacity: 0.8;
  }

  .step-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .btn-primary {
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-primary:hover {
    background: #00b8d9;
  }

  .btn-secondary {
    background: transparent;
    border: 1px solid var(--border, #30363d);
    color: #ffffff;
    padding: 0.75rem 2rem;
    border-radius: 6px;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: background 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-secondary:hover {
    background: var(--bg-tertiary, #21262d);
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .modal-content {
    background: var(--bg-secondary, #161b22);
    border: 1px solid var(--border, #30363d);
    border-radius: 12px;
    width: 100%;
    max-width: 600px;
    height: 80vh; /* Fixed height for the form to scroll */
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    overflow: hidden;
  }
</style>
