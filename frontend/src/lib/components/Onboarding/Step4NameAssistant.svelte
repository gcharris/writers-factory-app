<!--
  Step4NameAssistant.svelte - Name Your Assistant

  Purpose: Personalization - give the assistant a name.
  Final step before entering the main app.
-->
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { assistantName } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Preset name options
  const presetNames = ['Muse', 'Scribe', 'Quill', 'Ghost', 'Companion'];

  let selectedPreset = 'Muse';
  let customName = '';
  let useCustomName = false;

  // Reactive display name
  $: displayName = useCustomName && customName.trim() ? customName.trim() : selectedPreset;

  function selectPreset(name: string) {
    selectedPreset = name;
    useCustomName = false;
    customName = '';
  }

  function enableCustomName() {
    useCustomName = true;
    selectedPreset = '';
  }

  function handleBack() {
    dispatch('back');
  }

  function handleComplete() {
    const nameToSave = useCustomName && customName.trim() ? customName.trim() : selectedPreset || 'Muse';
    assistantName.set(nameToSave);
    dispatch('complete', { name: nameToSave });
  }
</script>

<div class="step-name-assistant">
  <div class="step-header">
    <h2>Name Your Assistant</h2>
    <p class="step-description">
      What would you like to call your writing assistant?
    </p>
  </div>

  <!-- Name Selection -->
  <div class="name-section">
    <div class="preset-selector">
      {#each presetNames as name}
        <button
          class="preset-btn {selectedPreset === name && !useCustomName ? 'active' : ''}"
          on:click={() => selectPreset(name)}
        >
          {name}
        </button>
      {/each}
      <button
        class="preset-btn custom {useCustomName ? 'active' : ''}"
        on:click={enableCustomName}
      >
        Custom...
      </button>
    </div>

    {#if useCustomName}
      <div class="custom-name-input">
        <input
          type="text"
          bind:value={customName}
          placeholder="Enter a custom name..."
          maxlength="20"
          autofocus
        />
        <span class="char-count">{customName.length}/20</span>
      </div>
    {/if}

    <!-- Preview -->
    <div class="preview-section">
      <div class="preview-label">Preview:</div>
      <div class="preview-message">
        <span class="assistant-avatar">✨</span>
        <div class="message-bubble">
          "Hi! I'm <strong>{displayName}</strong>. What would you like to work on today?"
        </div>
      </div>
    </div>
  </div>

  <!-- Model Info -->
  <div class="model-info-box">
    <h4>Your Default Model</h4>
    <p>
      <strong>DeepSeek V3</strong> will be your default model for most tasks.
    </p>
    <p class="help-text">
      You can choose any available model at each prompt using the dropdown in the chat input.
    </p>
  </div>

  <!-- Navigation -->
  <div class="step-actions">
    <button class="btn-secondary" on:click={handleBack}>
      <span class="arrow">←</span>
      Back
    </button>
    <button class="btn-primary" on:click={handleComplete}>
      Get Started
      <span class="arrow">→</span>
    </button>
  </div>
</div>

<style>
  .step-name-assistant {
    max-width: 600px;
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

  /* Name Section */
  .name-section {
    margin-bottom: 2rem;
  }

  /* Preset Selector */
  .preset-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    justify-content: center;
  }

  .preset-btn {
    padding: 0.875rem 1.5rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--border, #2d3a47);
    border-radius: 8px;
    color: #ffffff;
    font-weight: 500;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .preset-btn:hover {
    border-color: var(--accent-cyan, #00d9ff);
  }

  .preset-btn.active {
    border-color: var(--accent-cyan, #00d9ff);
    background: rgba(0, 217, 255, 0.1);
    color: var(--accent-cyan, #00d9ff);
  }

  .preset-btn.custom {
    font-style: italic;
    color: var(--text-secondary, #8b949e);
  }

  .preset-btn.custom.active {
    color: var(--accent-cyan, #00d9ff);
  }

  /* Custom Name Input */
  .custom-name-input {
    position: relative;
    max-width: 400px;
    margin: 0 auto 1.5rem;
  }

  .custom-name-input input {
    width: 100%;
    padding: 0.875rem 1rem;
    padding-right: 4rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--border, #2d3a47);
    border-radius: 8px;
    color: #ffffff;
    font-size: 1.125rem;
    text-align: center;
    transition: border-color 0.2s;
  }

  .custom-name-input input:focus {
    outline: none;
    border-color: var(--accent-cyan, #00d9ff);
  }

  .custom-name-input input::placeholder {
    color: var(--text-secondary, #8b949e);
  }

  .char-count {
    position: absolute;
    right: 1rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  /* Preview Section */
  .preview-section {
    background: var(--bg-primary, #0f1419);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 12px;
    padding: 1.5rem;
  }

  .preview-label {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
    text-align: center;
  }

  .preview-message {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .assistant-avatar {
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .message-bubble {
    flex: 1;
    padding: 1rem;
    background: var(--bg-secondary, #1a2027);
    border-radius: 12px;
    border-top-left-radius: 4px;
    color: var(--text-primary, #e6edf3);
    font-size: 1rem;
    line-height: 1.5;
  }

  .message-bubble strong {
    color: var(--accent-cyan, #00d9ff);
  }

  /* Model Info Box */
  .model-info-box {
    padding: 1.25rem;
    background: rgba(0, 217, 255, 0.05);
    border: 1px solid rgba(0, 217, 255, 0.3);
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .model-info-box h4 {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--accent-cyan, #00d9ff);
    margin: 0 0 0.5rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .model-info-box p {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 0.5rem 0;
    line-height: 1.5;
  }

  .model-info-box p:last-child {
    margin-bottom: 0;
  }

  .model-info-box strong {
    color: #ffffff;
  }

  .help-text {
    font-size: 0.8rem !important;
    opacity: 0.8;
  }

  /* Navigation */
  .step-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border, #2d3a47);
  }

  .btn-primary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.875rem 2rem;
    background: var(--accent-cyan, #00d9ff);
    color: var(--bg-primary, #0f1419);
    border: none;
    border-radius: 6px;
    font-weight: 600;
    font-size: 1.125rem;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-primary:hover {
    background: #00b8d9;
  }

  .btn-secondary {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: var(--text-secondary, #8b949e);
    border: 1px solid var(--border, #2d3a47);
    border-radius: 6px;
    font-weight: 500;
    font-size: 1rem;
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

  /* Responsive */
  @media (max-width: 500px) {
    .preset-selector {
      flex-direction: column;
    }

    .preset-btn {
      width: 100%;
    }

    .step-actions {
      flex-direction: column;
      gap: 1rem;
    }

    .btn-primary, .btn-secondary {
      width: 100%;
      justify-content: center;
    }
  }
</style>
