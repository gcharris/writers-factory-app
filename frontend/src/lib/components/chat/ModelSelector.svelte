<!--
  ModelSelector.svelte - Dropdown to select AI model for chat messages

  Fetches available models from /api-keys/status and groups them by tier:
  - Free (MVP subsidized): DeepSeek, Qwen, Mistral, etc.
  - Premium (User keys): OpenAI, Anthropic, xAI, Google
  - Local: Ollama models

  Usage:
    <ModelSelector bind:selectedModel on:change={handleModelChange} />
-->
<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';
  import { defaultChatModel, selectedChatModel } from '$lib/stores';

  const BASE_URL = 'http://localhost:8000';
  const dispatch = createEventDispatcher();

  // Model ID to display name mapping
  const MODEL_DISPLAY_NAMES: Record<string, { name: string; provider: string }> = {
    'deepseek-chat': { name: 'DeepSeek V3', provider: 'DeepSeek' },
    'qwen-turbo': { name: 'Qwen Turbo', provider: 'Alibaba' },
    'qwen-plus': { name: 'Qwen Plus', provider: 'Alibaba' },
    'mistral-large-latest': { name: 'Mistral Large', provider: 'Mistral' },
    'moonshot-v1-8k': { name: 'Kimi', provider: 'Moonshot' },
    'glm-4': { name: 'ChatGLM-4', provider: 'Zhipu' },
    'glm-4-flash': { name: 'GLM-4 Flash', provider: 'Zhipu' },
    'gpt-4o': { name: 'GPT-4o', provider: 'OpenAI' },
    'gpt-4o-mini': { name: 'GPT-4o Mini', provider: 'OpenAI' },
    'claude-3-5-sonnet-20241022': { name: 'Claude 3.5 Sonnet', provider: 'Anthropic' },
    'claude-sonnet-4-20250514': { name: 'Claude Sonnet 4', provider: 'Anthropic' },
    'grok-2-latest': { name: 'Grok 2', provider: 'xAI' },
    'gemini-2.0-flash': { name: 'Gemini 2.0 Flash', provider: 'Google' },
    'gemini-1.5-pro': { name: 'Gemini 1.5 Pro', provider: 'Google' }
  };

  // Provider to model ID mapping (default models per provider)
  const PROVIDER_MODEL_IDS: Record<string, string> = {
    deepseek: 'deepseek-chat',
    qwen: 'qwen-plus',
    mistral: 'mistral-large-latest',
    moonshot: 'moonshot-v1-8k',
    zhipu: 'glm-4-flash',
    openai: 'gpt-4o',
    anthropic: 'claude-sonnet-4-20250514',
    xai: 'grok-2-latest',
    gemini: 'gemini-2.0-flash'
  };

  // Free tier providers (MVP subsidized)
  const FREE_PROVIDERS = ['deepseek', 'qwen', 'mistral', 'moonshot', 'zhipu'];

  // Premium tier providers (require user API keys)
  const PREMIUM_PROVIDERS = ['openai', 'anthropic', 'xai', 'gemini'];

  interface ModelOption {
    id: string;
    name: string;
    provider: string;
    tier: 'free' | 'premium' | 'local';
    available: boolean;
  }

  let isOpen = false;
  let isLoading = true;
  let dropdownRef: HTMLDivElement;

  let freeModels: ModelOption[] = [];
  let premiumModels: ModelOption[] = [];
  let localModels: ModelOption[] = [];

  // Current model (use selected or default)
  $: currentModelId = $selectedChatModel || $defaultChatModel;
  $: currentModel = getModelDisplay(currentModelId);

  onMount(async () => {
    await loadAvailableModels();
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeydown);
    return () => {
      document.removeEventListener('click', handleClickOutside);
      document.removeEventListener('keydown', handleKeydown);
    };
  });

  function handleClickOutside(e: MouseEvent) {
    if (dropdownRef && !dropdownRef.contains(e.target as Node)) {
      isOpen = false;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && isOpen) {
      isOpen = false;
    }
  }

  async function loadAvailableModels() {
    isLoading = true;

    try {
      // Fetch API key status
      const response = await fetch(`${BASE_URL}/api-keys/status`);
      if (!response.ok) throw new Error('Failed to fetch API status');

      const apiStatus = await response.json();
      // API returns { providers: { openai: { available: true }, ... } }
      const providersData = apiStatus.providers || apiStatus;
      const configuredProviders = new Set(
        Object.entries(providersData)
          .filter(([_, info]: [string, any]) =>
            info === true || info === 'configured' || info?.available === true
          )
          .map(([provider]) => provider.toLowerCase())
      );

      // Build free models list
      freeModels = FREE_PROVIDERS.map(provider => {
        const modelId = PROVIDER_MODEL_IDS[provider];
        const display = MODEL_DISPLAY_NAMES[modelId] || { name: modelId, provider };
        return {
          id: modelId,
          name: display.name,
          provider: display.provider,
          tier: 'free' as const,
          available: true // Free models always available for MVP
        };
      });

      // Build premium models list
      premiumModels = PREMIUM_PROVIDERS.map(provider => {
        const modelId = PROVIDER_MODEL_IDS[provider];
        const display = MODEL_DISPLAY_NAMES[modelId] || { name: modelId, provider };
        return {
          id: modelId,
          name: display.name,
          provider: display.provider,
          tier: 'premium' as const,
          available: configuredProviders.has(provider)
        };
      });

      // Fetch local Ollama models
      try {
        const ollamaResponse = await fetch(`${BASE_URL}/system/hardware`);
        if (ollamaResponse.ok) {
          const hardware = await ollamaResponse.json();
          if (hardware.ollama_installed && hardware.ollama_models) {
            localModels = hardware.ollama_models.map((model: string) => ({
              id: `ollama:${model}`,
              name: model,
              provider: 'Ollama',
              tier: 'local' as const,
              available: true
            }));
          }
        }
      } catch (e) {
        console.warn('Failed to fetch Ollama models:', e);
      }

    } catch (e) {
      console.error('Failed to load models:', e);
      // Fallback: at least show default model
      freeModels = [{
        id: 'deepseek-chat',
        name: 'DeepSeek V3',
        provider: 'DeepSeek',
        tier: 'free',
        available: true
      }];
    } finally {
      isLoading = false;
    }
  }

  function getModelDisplay(modelId: string): { name: string; provider: string } {
    // Check if it's an Ollama model
    if (modelId.startsWith('ollama:')) {
      return { name: modelId.replace('ollama:', ''), provider: 'Ollama' };
    }

    // Check display names map
    if (MODEL_DISPLAY_NAMES[modelId]) {
      return MODEL_DISPLAY_NAMES[modelId];
    }

    // Fallback
    return { name: modelId, provider: '' };
  }

  function selectModel(model: ModelOption) {
    if (!model.available) return;

    selectedChatModel.set(model.id);
    isOpen = false;
    dispatch('change', { modelId: model.id, modelName: model.name });
  }

  function toggle() {
    isOpen = !isOpen;
  }
</script>

<div class="model-selector" bind:this={dropdownRef}>
  <button class="selector-trigger" on:click={toggle} title="Select AI model">
    <span class="trigger-icon">🤖</span>
    <span class="trigger-text">{currentModel.name}</span>
    <span class="trigger-arrow" class:open={isOpen}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </span>
  </button>

  {#if isOpen}
    <div class="selector-dropdown">
      {#if isLoading}
        <div class="dropdown-loading">Loading models...</div>
      {:else}
        <!-- Free Models -->
        {#if freeModels.length > 0}
          <div class="model-group">
            <div class="group-header">
              <span class="group-icon">✨</span>
              <span class="group-label">Free for MVP</span>
            </div>
            {#each freeModels as model}
              <button
                class="model-option"
                class:selected={currentModelId === model.id}
                class:unavailable={!model.available}
                on:click={() => selectModel(model)}
                disabled={!model.available}
              >
                <span class="option-indicator">
                  {#if currentModelId === model.id}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {:else}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {/if}
                </span>
                <span class="option-content">
                  <span class="option-name">{model.name}</span>
                  <span class="option-provider">{model.provider}</span>
                </span>
              </button>
            {/each}
          </div>
        {/if}

        <!-- Premium Models -->
        {#if premiumModels.length > 0}
          <div class="model-group">
            <div class="group-header">
              <span class="group-icon">⭐</span>
              <span class="group-label">Premium</span>
            </div>
            {#each premiumModels as model}
              <button
                class="model-option"
                class:selected={currentModelId === model.id}
                class:unavailable={!model.available}
                on:click={() => selectModel(model)}
                disabled={!model.available}
              >
                <span class="option-indicator">
                  {#if currentModelId === model.id}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {:else}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {/if}
                </span>
                <span class="option-content">
                  <span class="option-name">{model.name}</span>
                  <span class="option-provider">{model.provider}</span>
                </span>
                {#if !model.available}
                  <span class="option-badge unavailable">No key</span>
                {/if}
              </button>
            {/each}
          </div>
        {/if}

        <!-- Local Models -->
        {#if localModels.length > 0}
          <div class="model-group">
            <div class="group-header">
              <span class="group-icon">💻</span>
              <span class="group-label">Local</span>
            </div>
            {#each localModels as model}
              <button
                class="model-option"
                class:selected={currentModelId === model.id}
                on:click={() => selectModel(model)}
              >
                <span class="option-indicator">
                  {#if currentModelId === model.id}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {:else}
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <circle cx="12" cy="12" r="6"></circle>
                    </svg>
                  {/if}
                </span>
                <span class="option-content">
                  <span class="option-name">{model.name}</span>
                  <span class="option-provider">{model.provider}</span>
                </span>
              </button>
            {/each}
          </div>
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  .model-selector {
    position: relative;
  }

  .selector-trigger {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: var(--bg-tertiary, #252d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-xs, 11px);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .selector-trigger:hover {
    background: var(--bg-elevated, #2d3748);
    border-color: var(--border-strong, #444c56);
    color: var(--text-primary, #e6edf3);
  }

  .trigger-icon {
    font-size: 12px;
  }

  .trigger-text {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-weight: 500;
  }

  .trigger-arrow {
    display: flex;
    align-items: center;
    transition: transform 0.15s ease;
  }

  .trigger-arrow.open {
    transform: rotate(180deg);
  }

  .selector-dropdown {
    position: absolute;
    bottom: calc(100% + 4px);
    left: 0;
    min-width: 220px;
    max-width: 280px;
    max-height: 400px;
    overflow-y: auto;
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    z-index: 100;
  }

  .dropdown-loading {
    padding: 12px 16px;
    color: var(--text-muted, #8b949e);
    font-size: var(--text-xs, 11px);
  }

  .model-group {
    padding: 4px 0;
  }

  .model-group:not(:last-child) {
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .group-header {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted, #8b949e);
  }

  .group-icon {
    font-size: 10px;
  }

  .model-option {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 8px 12px;
    background: transparent;
    border: none;
    color: var(--text-secondary, #c9d1d9);
    font-size: var(--text-sm, 12px);
    text-align: left;
    cursor: pointer;
    transition: background 0.1s ease;
  }

  .model-option:hover:not(:disabled) {
    background: var(--bg-tertiary, #252d38);
  }

  .model-option.selected {
    color: var(--accent-cyan, #58a6ff);
  }

  .model-option.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .option-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  .model-option.selected .option-indicator {
    color: var(--accent-cyan, #58a6ff);
  }

  .option-content {
    display: flex;
    flex-direction: column;
    gap: 1px;
    min-width: 0;
    flex: 1;
  }

  .option-name {
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .option-provider {
    font-size: 10px;
    color: var(--text-muted, #8b949e);
  }

  .option-badge {
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 600;
    text-transform: uppercase;
  }

  .option-badge.unavailable {
    background: var(--warning-bg, #d2992215);
    color: var(--warning, #d29922);
  }

  /* Scrollbar */
  .selector-dropdown::-webkit-scrollbar {
    width: 6px;
  }

  .selector-dropdown::-webkit-scrollbar-track {
    background: transparent;
  }

  .selector-dropdown::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 3px;
  }

  .selector-dropdown::-webkit-scrollbar-thumb:hover {
    background: var(--border-strong, #444c56);
  }
</style>
