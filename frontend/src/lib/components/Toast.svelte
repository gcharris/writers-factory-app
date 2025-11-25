<!--
  Toast.svelte - Toast notification system

  Usage:
  import { toasts, addToast, dismissToast } from '$lib/stores';
  addToast({ type: 'success', message: 'Settings saved!' });
-->
<script>
  import { onMount } from 'svelte';
  import { toasts, dismissToast } from '$lib/toastStore';

  // Icons for each type
  const icons = {
    success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>`,
    error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="8" x2="12" y2="12"></line>
      <line x1="12" y1="16" x2="12.01" y2="16"></line>
    </svg>`,
    warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
      <line x1="12" y1="9" x2="12" y2="13"></line>
      <line x1="12" y1="17" x2="12.01" y2="17"></line>
    </svg>`,
    info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="10"></circle>
      <line x1="12" y1="16" x2="12" y2="12"></line>
      <line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>`
  };
</script>

<div class="toast-container" role="region" aria-label="Notifications">
  {#each $toasts as toast (toast.id)}
    <div class="toast toast-{toast.type}" role="alert">
      <span class="toast-icon">{@html icons[toast.type] || icons.info}</span>
      <span class="toast-message">{toast.message}</span>
      {#if toast.action}
        <button class="toast-action" on:click={toast.action.handler}>
          {toast.action.label}
        </button>
      {/if}
      <button class="toast-dismiss" on:click={() => dismissToast(toast.id)} aria-label="Dismiss">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  {/each}
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: var(--space-6, 24px);
    right: var(--space-6, 24px);
    z-index: var(--z-toast, 600);
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px) var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: var(--shadow-lg, 0 8px 24px rgba(0, 0, 0, 0.5));
    animation: slideIn 300ms cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: auto;
    max-width: 400px;
  }

  @keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }

  .toast-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .toast-success .toast-icon { color: var(--success, #3fb950); }
  .toast-error .toast-icon { color: var(--error, #f85149); }
  .toast-warning .toast-icon { color: var(--warning, #d29922); }
  .toast-info .toast-icon { color: var(--info, #58a6ff); }

  .toast-message {
    flex: 1;
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    line-height: var(--leading-normal, 1.5);
  }

  .toast-action {
    padding: var(--space-1, 4px) var(--space-2, 8px);
    background: transparent;
    border: 1px solid var(--accent-cyan, #58a6ff);
    border-radius: var(--radius-sm, 4px);
    color: var(--accent-cyan, #58a6ff);
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .toast-action:hover {
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
  }

  .toast-dismiss {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .toast-dismiss:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }
</style>
