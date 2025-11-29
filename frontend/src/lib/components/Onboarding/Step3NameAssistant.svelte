<!--
  Step3NameAssistant.svelte - Name Your Assistant & Choose Default Model

  Purpose: Personalization - give the assistant a name and select default AI model.
  Final step before entering the main app.

  Model Selection Logic:
  - Scenario A (no premium keys): DeepSeek V3 auto-selected, info text shown
  - Scenario B (premium keys exist): Radio selection with DeepSeek (free) + available premiums
-->
<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { assistantName, defaultChatModel } from '$lib/stores';

  const dispatch = createEventDispatcher();
  const BASE_URL = 'http://localhost:8000';

  // Preset name options
  const presetNames = ['Muse', 'Scribe', 'Quill', 'Ghost', 'Companion'];

  // Name selection state
  let selectedPreset = 'Muse';
  let customName = '';
  let useCustomName = false;

  // Model selection state
  let loadingKeyStatus = true;
  let keyStatusError = '';
  let hasPremiumKeys = false;
  let availablePremiumModels: Array<{
    id: string;
    provider: string;
    modelName: string;
    description: string;
  }> = [];
  let selectedModel = 'deepseek-chat'; // Default to DeepSeek

  // Premium model definitions (provider ID -> model info)
  const premiumModelMap: Record<string, { id: string; provider: string; modelName: string; description: string }> = {
    anthropic: {
      id: 'claude-3-5-sonnet-20241022',
      provider: 'Anthropic',
      modelName: 'Claude 3.5 Sonnet',
      description: 'Best for nuanced writing and creative tasks'
    },
    openai: {
      id: 'gpt-4o',
      provider: 'OpenAI',
      modelName: 'GPT-4o',
      description: 'Versatile all-purpose model'
    },
    xai: {
      id: 'grok-2-latest',
      provider: 'xAI',
      modelName: 'Grok 2',
      description: 'Fast and capable reasoning'
    },
    gemini: {
      id: 'gemini-2.0-flash',
      provider: 'Google',
      modelName: 'Gemini 2.0 Flash',
      description: 'Fast multimodal model'
    }
  };

  // Premium providers to check (order determines display order)
  const premiumProviders = ['anthropic', 'openai', 'xai', 'gemini'];

  // Reactive display name
  $: displayName = useCustomName && customName.trim() ? customName.trim() : selectedPreset;

  onMount(async () => {
    await loadKeyStatus();
  });

  async function loadKeyStatus() {
    loadingKeyStatus = true;
    keyStatusError = '';

    try {
      const response = await fetch(`${BASE_URL}/api-keys/status`);
      if (!response.ok) {
        throw new Error('Failed to load API key status');
      }

      const data = await response.json();
      const keyStatus = data.providers || data.keys || {};

      // Check which premium providers have keys configured
      availablePremiumModels = [];
      for (const provider of premiumProviders) {
        const status = keyStatus[provider];
        if (status && status.available) {
          const modelInfo = premiumModelMap[provider];
          if (modelInfo) {
            availablePremiumModels.push(modelInfo);
          }
        }
      }

      hasPremiumKeys = availablePremiumModels.length > 0;

      // If premium keys available, default to first premium model
      // Otherwise stick with DeepSeek
      if (hasPremiumKeys && availablePremiumModels.length > 0) {
        // Still default to DeepSeek but user can change
        selectedModel = 'deepseek-chat';
      }

    } catch (e) {
      keyStatusError = e instanceof Error ? e.message : 'Failed to check API keys';
      // On error, default to DeepSeek (safe fallback)
      hasPremiumKeys = false;
    } finally {
      loadingKeyStatus = false;
    }
  }

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

  async function handleComplete() {
    const nameToSave = useCustomName && customName.trim() ? customName.trim() : selectedPreset || 'Muse';

    // Save assistant name to store
    assistantName.set(nameToSave);

    // Save default model to store
    defaultChatModel.set(selectedModel);

    // Also save to backend settings
    try {
      await fetch(`${BASE_URL}/settings/category/agents`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          default_chat_model: selectedModel
        })
      });
    } catch (e) {
      // Non-blocking - local store is primary
      console.warn('Failed to save model preference to backend:', e);
    }

    dispatch('complete', { name: nameToSave, model: selectedModel });
  }

  function getModelDisplayName(modelId: string): string {
    if (modelId === 'deepseek-chat') return 'DeepSeek V3';
    const found = availablePremiumModels.find(m => m.id === modelId);
    return found ? found.modelName : modelId;
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

  <!-- Model Selection -->
  <div class="model-info-box">
    <h4>Your Default Model</h4>

    {#if loadingKeyStatus}
      <div class="loading-state">
        <span class="loading-dots">Checking available models...</span>
      </div>
    {:else if !hasPremiumKeys}
      <!-- Scenario A: No premium keys - DeepSeek auto-selected -->
      <div class="scenario-a">
        <p>
          <strong>DeepSeek V3</strong> will be your default model for most tasks.
        </p>
        <p class="help-text">
          This is a powerful open-source model included free with Writers Factory.
          You can add premium API keys anytime in Settings to unlock additional models.
        </p>
      </div>
    {:else}
      <!-- Scenario B: Premium keys available - show selection -->
      <div class="scenario-b">
        <p class="intro-text">
          You have premium AI models available! Choose your preferred default:
        </p>

        <div class="model-options">
          <!-- DeepSeek (always available, free) -->
          <label class="model-option {selectedModel === 'deepseek-chat' ? 'selected' : ''}">
            <input
              type="radio"
              name="default-model"
              value="deepseek-chat"
              bind:group={selectedModel}
            />
            <div class="model-info">
              <span class="model-name">DeepSeek V3</span>
              <span class="model-badge free">Free</span>
            </div>
            <span class="model-desc">Open-source, included with Writers Factory</span>
          </label>

          <!-- Premium models (based on available keys) -->
          {#each availablePremiumModels as model}
            <label class="model-option {selectedModel === model.id ? 'selected' : ''}">
              <input
                type="radio"
                name="default-model"
                value={model.id}
                bind:group={selectedModel}
              />
              <div class="model-info">
                <span class="model-name">{model.modelName}</span>
                <span class="model-badge premium">{model.provider}</span>
              </div>
              <span class="model-desc">{model.description}</span>
            </label>
          {/each}
        </div>

        <p class="help-text">
          You can change models at each prompt using the dropdown in the chat input.
        </p>
      </div>
    {/if}

    {#if keyStatusError}
      <p class="error-text">{keyStatusError}</p>
    {/if}
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
    margin: 0 0 0.75rem 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .loading-state {
    padding: 1rem 0;
    text-align: center;
  }

  .loading-dots {
    color: var(--text-secondary, #8b949e);
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* Scenario A: No premium keys */
  .scenario-a p {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 0.5rem 0;
    line-height: 1.5;
  }

  .scenario-a p:last-child {
    margin-bottom: 0;
  }

  .scenario-a strong {
    color: #ffffff;
  }

  /* Scenario B: Premium keys available */
  .scenario-b .intro-text {
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
    margin: 0 0 1rem 0;
  }

  .model-options {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .model-option {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    padding: 0.75rem 1rem;
    background: var(--bg-primary, #0f1419);
    border: 2px solid var(--border, #2d3a47);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .model-option:hover {
    border-color: var(--accent-cyan, #00d9ff);
  }

  .model-option.selected {
    border-color: var(--accent-cyan, #00d9ff);
    background: rgba(0, 217, 255, 0.08);
  }

  .model-option input[type="radio"] {
    display: none;
  }

  .model-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .model-name {
    font-weight: 600;
    color: #ffffff;
    font-size: 0.9rem;
  }

  .model-badge {
    font-size: 0.65rem;
    font-weight: 600;
    padding: 0.125rem 0.375rem;
    border-radius: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .model-badge.free {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
  }

  .model-badge.premium {
    background: rgba(255, 184, 0, 0.2);
    color: #ffb800;
  }

  .model-desc {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
  }

  .help-text {
    font-size: 0.8rem !important;
    opacity: 0.8;
    color: var(--text-secondary, #8b949e);
    margin: 0;
  }

  .error-text {
    color: #ff6b6b;
    font-size: 0.8rem;
    margin: 0.5rem 0 0 0;
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
