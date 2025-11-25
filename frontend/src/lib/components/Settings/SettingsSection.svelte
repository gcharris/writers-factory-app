<!--
  SettingsSection.svelte - Collapsible section container

  Features:
  - Expandable/collapsible header
  - Animated expansion
  - Visual expand/collapse indicator
-->
<script>
  export let title = '';
  export let expanded = true;

  function toggle() {
    expanded = !expanded;
  }
</script>

<div class="settings-section" class:expanded>
  <button class="section-header" on:click={toggle} type="button">
    <span class="title">{title}</span>
    <span class="chevron">
      {#if expanded}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      {:else}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      {/if}
    </span>
  </button>

  {#if expanded}
    <div class="section-content">
      <slot></slot>
    </div>
  {/if}
</div>

<style>
  .settings-section {
    margin-bottom: 1.5rem;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--bg-tertiary, #242d38);
    border-radius: 8px;
    overflow: hidden;
  }

  .section-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: background 0.15s ease;
  }

  .section-header:hover {
    background: var(--bg-tertiary, #242d38);
  }

  .title {
    font-size: 0.9375rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 600;
    text-align: left;
  }

  .chevron {
    color: var(--text-muted, #6e7681);
    display: flex;
    align-items: center;
    transition: color 0.15s ease;
  }

  .section-header:hover .chevron {
    color: var(--accent-gold, #d4a574);
  }

  .section-content {
    padding: 0 1rem 1rem 1rem;
    animation: slideDown 0.2s ease-out;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
