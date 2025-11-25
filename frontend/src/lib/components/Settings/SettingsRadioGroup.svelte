<!--
  SettingsRadioGroup.svelte - Radio button group for settings

  Features:
  - Group label
  - Multiple options with labels and descriptions
  - Keyboard navigation
  - Visual selection indicator
-->
<script>
  export let label = '';
  export let value = '';
  export let options = []; // [{value, label, description}]
  export let disabled = false;
</script>

<div class="radio-group" class:disabled>
  {#if label}
    <label class="group-label">{label}</label>
  {/if}

  <div class="options">
    {#each options as option}
      <label class="radio-option" class:selected={value === option.value}>
        <input
          type="radio"
          bind:group={value}
          value={option.value}
          {disabled}
        />
        <div class="radio-indicator"></div>
        <div class="option-content">
          <span class="option-label">{option.label}</span>
          {#if option.description}
            <span class="option-desc">{option.description}</span>
          {/if}
        </div>
      </label>
    {/each}
  </div>
</div>

<style>
  .radio-group {
    margin-bottom: 1.5rem;
  }

  .radio-group.disabled {
    opacity: 0.5;
    pointer-events: none;
  }

  .group-label {
    display: block;
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
    margin-bottom: 0.75rem;
  }

  .options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .radio-option {
    display: flex;
    align-items: flex-start;
    padding: 0.75rem;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .radio-option:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-gold, #d4a574);
  }

  .radio-option.selected {
    background: rgba(212, 165, 116, 0.1);
    border-color: var(--accent-gold, #d4a574);
  }

  input[type="radio"] {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .radio-indicator {
    width: 18px;
    height: 18px;
    border: 2px solid var(--text-muted, #6e7681);
    border-radius: 50%;
    margin-right: 0.75rem;
    margin-top: 0.125rem;
    flex-shrink: 0;
    position: relative;
    transition: all 0.15s ease;
  }

  .radio-option.selected .radio-indicator {
    border-color: var(--accent-gold, #d4a574);
  }

  .radio-option.selected .radio-indicator::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    background: var(--accent-gold, #d4a574);
    border-radius: 50%;
  }

  .option-content {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }

  .option-label {
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
  }

  .option-desc {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    line-height: 1.4;
  }

  .radio-option:hover .option-label {
    color: var(--accent-gold, #d4a574);
  }
</style>
