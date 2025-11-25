<!--
  Modal.svelte - Reusable modal dialog component

  Usage:
  <Modal bind:open={showModal} title="Settings">
    <SettingsPanel />
  </Modal>
-->
<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';

  export let open = false;
  export let title = '';
  export let size = 'medium'; // small, medium, large, full
  export let closable = true;

  const dispatch = createEventDispatcher();

  function handleClose() {
    if (closable) {
      open = false;
      dispatch('close');
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape' && closable) {
      handleClose();
    }
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget && closable) {
      handleClose();
    }
  }

  onMount(() => {
    document.addEventListener('keydown', handleKeydown);
  });

  onDestroy(() => {
    document.removeEventListener('keydown', handleKeydown);
  });

  $: sizeClass = {
    small: 'modal-small',
    medium: 'modal-medium',
    large: 'modal-large',
    full: 'modal-full'
  }[size] || 'modal-medium';
</script>

{#if open}
  <div class="modal-backdrop" on:click={handleBackdropClick} role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-container {sizeClass}">
      <div class="modal-header">
        {#if title}
          <h2 id="modal-title" class="modal-title">{title}</h2>
        {/if}
        {#if closable}
          <button class="modal-close" on:click={handleClose} aria-label="Close modal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        {/if}
      </div>
      <div class="modal-content">
        <slot />
      </div>
      {#if $$slots.footer}
        <div class="modal-footer">
          <slot name="footer" />
        </div>
      {/if}
    </div>
  </div>
{/if}

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
    z-index: var(--z-modal, 400);
    animation: fadeIn 150ms ease-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal-container {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.5));
    display: flex;
    flex-direction: column;
    max-height: 90vh;
    animation: slideIn 200ms ease-out;
  }

  @keyframes slideIn {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  .modal-small { width: 400px; }
  .modal-medium { width: 600px; }
  .modal-large { width: 900px; }
  .modal-full { width: calc(100vw - 64px); height: calc(100vh - 64px); }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .modal-title {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .modal-close {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .modal-close:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .modal-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--space-2, 8px);
    padding: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
  }
</style>
