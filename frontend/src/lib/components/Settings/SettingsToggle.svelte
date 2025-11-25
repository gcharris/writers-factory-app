<!--
  SettingsToggle.svelte - Toggle switch for boolean settings

  Features:
  - Label with optional description
  - Animated switch
  - Keyboard accessible
  - Visual on/off states
-->
<script>
  export let label = '';
  export let checked = false;
  export let description = '';
  export let disabled = false;
</script>

<label class="toggle" class:disabled>
  <input type="checkbox" bind:checked {disabled} />
  <span class="toggle-switch" class:checked></span>
  <div class="toggle-label">
    <span class="label-text">{label}</span>
    {#if description}
      <span class="description">{description}</span>
    {/if}
  </div>
</label>

<style>
  .toggle {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    margin-bottom: 0.75rem;
  }

  .toggle:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-gold, #d4a574);
  }

  .toggle.disabled {
    opacity: 0.5;
    pointer-events: none;
  }

  input[type="checkbox"] {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .toggle-switch {
    position: relative;
    width: 42px;
    height: 24px;
    background: var(--bg-elevated, #2d3640);
    border: 2px solid var(--text-muted, #6e7681);
    border-radius: 12px;
    transition: all 0.2s ease;
    flex-shrink: 0;
    margin-top: 0.125rem;
  }

  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    background: var(--text-muted, #6e7681);
    border-radius: 50%;
    transition: all 0.2s ease;
  }

  .toggle-switch.checked {
    background: var(--accent-gold, #d4a574);
    border-color: var(--accent-gold, #d4a574);
  }

  .toggle-switch.checked::after {
    left: 20px;
    background: var(--bg-primary, #0f1419);
  }

  .toggle:hover .toggle-switch {
    border-color: var(--accent-gold, #d4a574);
  }

  .toggle-label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }

  .label-text {
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
  }

  .description {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    line-height: 1.4;
  }

  .toggle:hover .label-text {
    color: var(--accent-gold, #d4a574);
  }
</style>
