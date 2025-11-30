<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Expert mode toggle
  let expertMode = false;

  // Context settings
  let context = {
    max_conversation_history: 20,
    kb_context_limit: 1000,
    voice_bundle_injection: 'full' as 'full' | 'summary' | 'minimal',
    continuity_context_depth: 3
  };

  // Default model selection
  let defaultModel = 'deepseek-chat';
  let availableModels = [
    { id: 'deepseek-chat', name: 'DeepSeek V3', tier: 'balanced', cost: '$0.27/$1.10 per 1M' },
    { id: 'gpt-4o', name: 'GPT-4o', tier: 'premium', cost: '$2.50/$10 per 1M' },
    { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', tier: 'premium', cost: '$3/$15 per 1M' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini', tier: 'balanced', cost: '$0.15/$0.60 per 1M' },
    { id: 'qwen-plus', name: 'Qwen Plus', tier: 'balanced', cost: '$0.40/$1.20 per 1M' },
    { id: 'mistral', name: 'Mistral 7B (Local)', tier: 'budget', cost: 'Free' },
    { id: 'llama3.2', name: 'Llama 3.2 (Local)', tier: 'budget', cost: 'Free' }
  ];

  let saveMessage = '';
  let errorMessage = '';
  let isLoading = true;

  // Removed - moved to combined onMount below

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/context`);
      if (response.ok) {
        const data = await response.json();
        context.max_conversation_history = data.max_conversation_history ?? 20;
        context.kb_context_limit = data.kb_context_limit ?? 1000;
        context.voice_bundle_injection = data.voice_bundle_injection ?? 'full';
        context.continuity_context_depth = data.continuity_context_depth ?? 3;
      }

      // Load foreman settings for default model
      const foremanResponse = await fetch(`${BASE_URL}/settings/category/foreman`);
      if (foremanResponse.ok) {
        const foremanData = await foremanResponse.json();
        if (foremanData.task_models?.health_check_review) {
          defaultModel = foremanData.task_models.health_check_review;
        }
      }

      // Load expert mode preference from local storage
      expertMode = localStorage.getItem('expertMode') === 'true';
    } catch (error) {
      console.error('Failed to load advanced settings:', error);
      errorMessage = 'Failed to load settings';
    } finally {
      isLoading = false;
    }
  }

  async function saveSettings() {
    saveMessage = '';
    errorMessage = '';

    try {
      // Save context settings
      const contextResponse = await fetch(`${BASE_URL}/settings/category/context`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(context)
      });

      if (!contextResponse.ok) {
        throw new Error('Failed to save context settings');
      }

      // Save expert mode to localStorage
      localStorage.setItem('expertMode', expertMode.toString());

      saveMessage = 'Advanced settings saved successfully';
      setTimeout(() => (saveMessage = ''), 3000);
    } catch (error) {
      console.error('Failed to save advanced settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefault() {
    context = {
      max_conversation_history: 20,
      kb_context_limit: 1000,
      voice_bundle_injection: 'full',
      continuity_context_depth: 3
    };
    defaultModel = 'deepseek-chat';
    expertMode = false;
  }

  // Debug tools state
  let debugModes = [
    { id: 'architect', label: 'ARCHITECT', description: 'Story Bible creation' },
    { id: 'voice_calibration', label: 'VOICE', description: 'Voice tournament' },
    { id: 'director', label: 'DIRECTOR', description: 'Scene drafting' },
    { id: 'editor', label: 'EDITOR', description: 'Polish & revision' }
  ];
  let currentMode = 'architect';
  let forceAdvanceMessage = '';
  let forceAdvanceError = '';
  let isForcing = false;

  async function loadCurrentMode() {
    try {
      const response = await fetch(`${BASE_URL}/foreman/debug/modes`);
      if (response.ok) {
        const data = await response.json();
        currentMode = data.current_mode || 'architect';
      }
    } catch (e) {
      console.warn('Could not load current mode:', e);
    }
  }

  async function forceAdvanceMode(targetMode: string) {
    if (isForcing) return;

    isForcing = true;
    forceAdvanceMessage = '';
    forceAdvanceError = '';

    try {
      const response = await fetch(`${BASE_URL}/foreman/debug/force-mode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_mode: targetMode })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to force mode');
      }

      const result = await response.json();
      currentMode = result.new_mode;
      forceAdvanceMessage = `Mode changed: ${result.previous_mode} → ${result.new_mode}`;
      setTimeout(() => forceAdvanceMessage = '', 5000);
    } catch (e) {
      forceAdvanceError = e instanceof Error ? e.message : 'Failed to force mode';
    } finally {
      isForcing = false;
    }
  }

  // Load current mode when component mounts
  onMount(() => {
    loadSettings();
    loadCurrentMode();
  });

  function getModelDescription(injection: string): string {
    const descriptions = {
      full: 'Include complete voice bundle with all samples and style notes',
      summary: 'Include summarized voice characteristics only',
      minimal: 'Include only essential voice markers for faster responses'
    };
    return descriptions[injection as keyof typeof descriptions] || '';
  }
</script>

<div class="settings-advanced">
  <div class="header">
    <h2>Advanced Settings</h2>
    <p class="subtitle">Expert configuration for power users. Most writers can use defaults.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Expert Mode Toggle -->
    <div class="section highlight">
      <div class="expert-toggle">
        <div class="toggle-group">
          <label class="toggle-label">
            <input type="checkbox" bind:checked={expertMode} class="toggle-input" />
            <span class="toggle-switch"></span>
            <span class="toggle-text">Expert Mode</span>
          </label>
          <p class="toggle-desc">
            {expertMode
              ? 'Showing all advanced options across settings panels'
              : 'Enable to unlock advanced configuration options throughout the app'}
          </p>
        </div>
        <div class="mode-indicator {expertMode ? 'expert' : 'simple'}">
          {expertMode ? 'EXPERT' : 'SIMPLE'}
        </div>
      </div>
    </div>

    <!-- Default System Model -->
    <div class="section">
      <h3>Default AI Model</h3>
      <p class="section-desc">
        Primary model used for strategic tasks when online. DeepSeek V3 offers excellent quality at low cost.
      </p>

      <div class="model-selector">
        {#each availableModels as model}
          <button
            class="model-option {defaultModel === model.id ? 'selected' : ''}"
            on:click={() => defaultModel = model.id}
          >
            <div class="model-info">
              <span class="model-name">{model.name}</span>
              <span class="model-tier tier-{model.tier}">{model.tier}</span>
            </div>
            <span class="model-cost">{model.cost}</span>
          </button>
        {/each}
      </div>

      <div class="model-note">
        <strong>Note:</strong> When offline, the system automatically falls back to local models (Mistral/Llama).
      </div>
    </div>

    <!-- Context Window Settings -->
    <div class="section">
      <h3>Context Window</h3>
      <p class="section-desc">Control how much context is sent to AI models.</p>

      <div class="context-settings">
        <div class="setting-item">
          <div class="setting-header">
            <label for="history">Conversation History</label>
            <span class="setting-value">{context.max_conversation_history} messages</span>
          </div>
          <input
            type="range"
            id="history"
            min="10"
            max="50"
            bind:value={context.max_conversation_history}
            class="slider"
          />
          <p class="setting-desc">Number of previous messages to include in context</p>
        </div>

        <div class="setting-item">
          <div class="setting-header">
            <label for="kb_limit">Knowledge Base Limit</label>
            <span class="setting-value">{context.kb_context_limit} tokens</span>
          </div>
          <input
            type="range"
            id="kb_limit"
            min="500"
            max="2000"
            step="100"
            bind:value={context.kb_context_limit}
            class="slider"
          />
          <p class="setting-desc">Maximum KB context injected per request</p>
        </div>

        <div class="setting-item">
          <div class="setting-header">
            <label for="continuity">Continuity Depth</label>
            <span class="setting-value">{context.continuity_context_depth} chapters</span>
          </div>
          <input
            type="range"
            id="continuity"
            min="1"
            max="5"
            bind:value={context.continuity_context_depth}
            class="slider"
          />
          <p class="setting-desc">How many previous chapters to consider for continuity</p>
        </div>
      </div>
    </div>

    <!-- Voice Bundle Injection -->
    <div class="section">
      <h3>Voice Bundle Injection</h3>
      <p class="section-desc">How much voice calibration data to include in prompts.</p>

      <div class="injection-selector">
        <button
          class="injection-option {context.voice_bundle_injection === 'full' ? 'selected' : ''}"
          on:click={() => context.voice_bundle_injection = 'full'}
        >
          <span class="option-icon">&#128214;</span>
          <span class="option-name">Full</span>
          <span class="option-hint">Best quality</span>
        </button>
        <button
          class="injection-option {context.voice_bundle_injection === 'summary' ? 'selected' : ''}"
          on:click={() => context.voice_bundle_injection = 'summary'}
        >
          <span class="option-icon">&#128196;</span>
          <span class="option-name">Summary</span>
          <span class="option-hint">Balanced</span>
        </button>
        <button
          class="injection-option {context.voice_bundle_injection === 'minimal' ? 'selected' : ''}"
          on:click={() => context.voice_bundle_injection = 'minimal'}
        >
          <span class="option-icon">&#9889;</span>
          <span class="option-name">Minimal</span>
          <span class="option-hint">Fastest</span>
        </button>
      </div>
      <p class="injection-description">{getModelDescription(context.voice_bundle_injection)}</p>
    </div>

    <!-- Debug Tools (Expert Mode Only) -->
    {#if expertMode}
      <div class="section debug-section">
        <h3>Debug Tools</h3>
        <p class="section-desc">
          Development tools for testing. Force mode changes bypass normal requirements.
        </p>

        <div class="debug-warning">
          <span class="warning-icon">⚠️</span>
          <span>Debug mode - requirements are bypassed. Use only for testing.</span>
        </div>

        <div class="mode-selector">
          <div class="current-mode">
            <span class="mode-label">Current Mode:</span>
            <span class="mode-value">{currentMode.toUpperCase().replace('_', ' ')}</span>
          </div>

          <div class="mode-buttons">
            {#each debugModes as mode}
              <button
                class="mode-btn {currentMode === mode.id ? 'current' : ''}"
                on:click={() => forceAdvanceMode(mode.id)}
                disabled={isForcing || currentMode === mode.id}
              >
                <span class="mode-btn-label">{mode.label}</span>
                <span class="mode-btn-desc">{mode.description}</span>
              </button>
            {/each}
          </div>
        </div>

        {#if forceAdvanceMessage}
          <div class="debug-message success">{forceAdvanceMessage}</div>
        {/if}
        {#if forceAdvanceError}
          <div class="debug-message error">{forceAdvanceError}</div>
        {/if}
      </div>
    {/if}

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>When to Adjust These Settings</h4>
      <ul>
        <li><strong>Slow responses?</strong> Reduce context limits and use minimal voice injection</li>
        <li><strong>Quality issues?</strong> Increase context and use full voice injection</li>
        <li><strong>Budget concerns?</strong> Use local models (Mistral/Llama) as default</li>
        <li><strong>Complex manuscripts?</strong> Increase continuity depth for better coherence</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Advanced Settings
      </button>
    </div>

    {#if saveMessage}
      <div class="message success">{saveMessage}</div>
    {/if}
    {#if errorMessage}
      <div class="message error">{errorMessage}</div>
    {/if}
  {/if}
</div>

<style>
  .settings-advanced {
    padding: 2rem;
    max-width: 900px;
    color: #ffffff;
  }

  .header {
    margin-bottom: 2rem;
  }

  .header h2 {
    font-size: 1.75rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
  }

  .subtitle {
    color: #b0b0b0;
    margin: 0;
  }

  .loading {
    text-align: center;
    padding: 3rem;
    color: #b0b0b0;
  }

  .section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 8px;
  }

  .section.highlight {
    border-color: #00d9ff;
    background: linear-gradient(135deg, #2d2d2d 0%, #1a3a4a 100%);
  }

  .section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.5rem 0;
  }

  .section-desc {
    color: #888888;
    margin: 0 0 1.5rem 0;
    font-size: 0.875rem;
  }

  /* Expert mode toggle */
  .expert-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .toggle-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    user-select: none;
  }

  .toggle-input {
    display: none;
  }

  .toggle-switch {
    position: relative;
    width: 48px;
    height: 24px;
    background: #404040;
    border-radius: 12px;
    transition: background 0.2s;
    flex-shrink: 0;
  }

  .toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background: #ffffff;
    border-radius: 50%;
    transition: transform 0.2s;
  }

  .toggle-input:checked + .toggle-switch {
    background: #00d9ff;
  }

  .toggle-input:checked + .toggle-switch::after {
    transform: translateX(24px);
  }

  .toggle-text {
    font-size: 1.25rem;
    font-weight: 600;
  }

  .toggle-desc {
    margin: 0;
    padding-left: 3.25rem;
    font-size: 0.875rem;
    color: #888888;
  }

  .mode-indicator {
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1px;
  }

  .mode-indicator.simple {
    background: #404040;
    color: #888888;
  }

  .mode-indicator.expert {
    background: #00d9ff;
    color: #1a1a1a;
  }

  /* Model selector */
  .model-selector {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .model-option {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .model-option:hover {
    border-color: #00d9ff;
  }

  .model-option.selected {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .model-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .model-name {
    font-weight: 500;
    color: #ffffff;
  }

  .model-tier {
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .tier-budget {
    background: #00ff8820;
    color: #00ff88;
  }

  .tier-balanced {
    background: #00d9ff20;
    color: #00d9ff;
  }

  .tier-premium {
    background: #ffb00020;
    color: #ffb000;
  }

  .model-cost {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #888888;
  }

  .model-note {
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 0.875rem;
    color: #b0b0b0;
  }

  .model-note strong {
    color: #00d9ff;
  }

  /* Context settings */
  .context-settings {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .setting-item {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .setting-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .setting-header label {
    font-weight: 500;
    color: #ffffff;
  }

  .setting-value {
    font-family: 'JetBrains Mono', monospace;
    color: #00d9ff;
    font-weight: 600;
  }

  .slider {
    width: 100%;
    height: 6px;
    -webkit-appearance: none;
    appearance: none;
    background: #404040;
    border-radius: 3px;
    outline: none;
    margin-bottom: 0.5rem;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    background: #00d9ff;
    border-radius: 50%;
    cursor: pointer;
  }

  .slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #00d9ff;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }

  .setting-desc {
    font-size: 0.75rem;
    color: #888888;
    margin: 0;
  }

  /* Injection selector */
  .injection-selector {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .injection-option {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .injection-option:hover {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .injection-option.selected {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .option-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .option-name {
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .option-hint {
    font-size: 0.75rem;
    color: #888888;
  }

  .injection-description {
    color: #b0b0b0;
    font-style: italic;
    margin: 0;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  /* Info panel */
  .info-panel {
    padding: 1.5rem;
    background: #1a3a4a20;
    border: 1px solid #00d9ff40;
    border-radius: 8px;
    margin-bottom: 2rem;
  }

  .info-panel h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.75rem 0;
  }

  .info-panel ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .info-panel li {
    color: #b0b0b0;
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }

  .info-panel li strong {
    color: #ffffff;
  }

  /* Actions */
  .actions {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
  }

  .btn-secondary {
    padding: 0.75rem 1.5rem;
    background: transparent;
    color: #b0b0b0;
    border: 1px solid #404040;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover {
    border-color: #00d9ff;
    color: #00d9ff;
  }

  .btn-save {
    padding: 0.75rem 2rem;
    background: #00d9ff;
    color: #1a1a1a;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }

  .btn-save:hover {
    background: #00b8d9;
  }

  .message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    font-weight: 500;
  }

  .message.success {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  .message.error {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff4444;
  }

  /* Debug Tools */
  .debug-section {
    border-color: #ff8c00;
    background: linear-gradient(135deg, #2d2d2d 0%, #3a2a1a 100%);
  }

  .debug-section h3 {
    color: #ff8c00;
  }

  .debug-warning {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    background: #ff8c0020;
    border: 1px solid #ff8c0040;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    font-size: 0.875rem;
    color: #ffb347;
  }

  .warning-icon {
    font-size: 1.25rem;
  }

  .mode-selector {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .current-mode {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
  }

  .mode-label {
    color: #888888;
    font-size: 0.875rem;
  }

  .mode-value {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: #ff8c00;
  }

  .mode-buttons {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
  }

  .mode-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 0.5rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .mode-btn:hover:not(:disabled) {
    border-color: #ff8c00;
    transform: translateY(-2px);
  }

  .mode-btn.current {
    border-color: #ff8c00;
    background: #3a2a1a;
  }

  .mode-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }

  .mode-btn-label {
    font-weight: 600;
    font-size: 0.75rem;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .mode-btn-desc {
    font-size: 0.65rem;
    color: #888888;
    text-align: center;
  }

  .debug-message {
    margin-top: 1rem;
    padding: 0.75rem;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .debug-message.success {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  .debug-message.error {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff4444;
  }
</style>
