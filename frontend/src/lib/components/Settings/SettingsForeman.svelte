<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Foreman behavior settings
  let foreman = {
    proactiveness: 'medium' as 'low' | 'medium' | 'high',
    challenge_intensity: 'medium' as 'low' | 'medium' | 'high',
    explanation_verbosity: 'medium' as 'low' | 'medium' | 'high',
    auto_kb_writes: true
  };

  let saveMessage = '';
  let errorMessage = '';
  let isLoading = true;

  onMount(() => {
    loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/foreman`);
      if (response.ok) {
        const data = await response.json();
        foreman.proactiveness = data.proactiveness ?? 'medium';
        foreman.challenge_intensity = data.challenge_intensity ?? 'medium';
        foreman.explanation_verbosity = data.explanation_verbosity ?? 'medium';
        foreman.auto_kb_writes = data.auto_kb_writes ?? true;
      }
    } catch (error) {
      console.error('Failed to load foreman settings:', error);
      errorMessage = 'Failed to load settings';
    } finally {
      isLoading = false;
    }
  }

  async function saveSettings() {
    saveMessage = '';
    errorMessage = '';

    try {
      const response = await fetch(`${BASE_URL}/settings/category/foreman`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(foreman)
      });

      if (response.ok) {
        saveMessage = 'Foreman settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save foreman settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefault() {
    foreman = {
      proactiveness: 'medium',
      challenge_intensity: 'medium',
      explanation_verbosity: 'medium',
      auto_kb_writes: true
    };
  }

  function getDescription(setting: string, level: string): string {
    const descriptions: Record<string, Record<string, string>> = {
      proactiveness: {
        low: 'Foreman waits for you to ask - minimal suggestions',
        medium: 'Foreman offers helpful suggestions at key moments',
        high: 'Foreman actively guides you - frequent recommendations'
      },
      challenge_intensity: {
        low: 'Gentle guidance - Foreman accepts most decisions',
        medium: 'Balanced feedback - pushes back on weak choices',
        high: 'Rigorous - Foreman challenges assumptions strongly'
      },
      explanation_verbosity: {
        low: 'Brief - just the essentials',
        medium: 'Clear explanations with reasoning',
        high: 'Detailed - comprehensive background and context'
      }
    };
    return descriptions[setting]?.[level] || '';
  }
</script>

<div class="settings-foreman">
  <div class="header">
    <h2>Foreman Behavior</h2>
    <p class="subtitle">Configure how your AI writing assistant interacts with you.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Proactiveness -->
    <div class="section">
      <h3>Proactiveness</h3>
      <p class="section-desc">How often should the Foreman offer unsolicited suggestions?</p>

      <div class="level-selector">
        <button
          class="level-btn {foreman.proactiveness === 'low' ? 'active' : ''}"
          on:click={() => foreman.proactiveness = 'low'}
        >
          <span class="level-icon">&#128172;</span>
          <span class="level-name">Low</span>
          <span class="level-hint">Wait for me</span>
        </button>
        <button
          class="level-btn {foreman.proactiveness === 'medium' ? 'active' : ''}"
          on:click={() => foreman.proactiveness = 'medium'}
        >
          <span class="level-icon">&#9878;</span>
          <span class="level-name">Medium</span>
          <span class="level-hint">Helpful hints</span>
        </button>
        <button
          class="level-btn {foreman.proactiveness === 'high' ? 'active' : ''}"
          on:click={() => foreman.proactiveness = 'high'}
        >
          <span class="level-icon">&#128161;</span>
          <span class="level-name">High</span>
          <span class="level-hint">Guide me</span>
        </button>
      </div>
      <p class="level-description">{getDescription('proactiveness', foreman.proactiveness)}</p>
    </div>

    <!-- Challenge Intensity -->
    <div class="section">
      <h3>Challenge Intensity</h3>
      <p class="section-desc">How strongly should the Foreman push back on weak creative choices?</p>

      <div class="level-selector">
        <button
          class="level-btn {foreman.challenge_intensity === 'low' ? 'active' : ''}"
          on:click={() => foreman.challenge_intensity = 'low'}
        >
          <span class="level-icon">&#128522;</span>
          <span class="level-name">Low</span>
          <span class="level-hint">Gentle</span>
        </button>
        <button
          class="level-btn {foreman.challenge_intensity === 'medium' ? 'active' : ''}"
          on:click={() => foreman.challenge_intensity = 'medium'}
        >
          <span class="level-icon">&#129300;</span>
          <span class="level-name">Medium</span>
          <span class="level-hint">Balanced</span>
        </button>
        <button
          class="level-btn {foreman.challenge_intensity === 'high' ? 'active' : ''}"
          on:click={() => foreman.challenge_intensity = 'high'}
        >
          <span class="level-icon">&#128170;</span>
          <span class="level-name">High</span>
          <span class="level-hint">Rigorous</span>
        </button>
      </div>
      <p class="level-description">{getDescription('challenge_intensity', foreman.challenge_intensity)}</p>
    </div>

    <!-- Explanation Verbosity -->
    <div class="section">
      <h3>Explanation Verbosity</h3>
      <p class="section-desc">How much detail should the Foreman include in explanations?</p>

      <div class="level-selector">
        <button
          class="level-btn {foreman.explanation_verbosity === 'low' ? 'active' : ''}"
          on:click={() => foreman.explanation_verbosity = 'low'}
        >
          <span class="level-icon">&#8226;</span>
          <span class="level-name">Low</span>
          <span class="level-hint">Brief</span>
        </button>
        <button
          class="level-btn {foreman.explanation_verbosity === 'medium' ? 'active' : ''}"
          on:click={() => foreman.explanation_verbosity = 'medium'}
        >
          <span class="level-icon">&#9776;</span>
          <span class="level-name">Medium</span>
          <span class="level-hint">Clear</span>
        </button>
        <button
          class="level-btn {foreman.explanation_verbosity === 'high' ? 'active' : ''}"
          on:click={() => foreman.explanation_verbosity = 'high'}
        >
          <span class="level-icon">&#128214;</span>
          <span class="level-name">High</span>
          <span class="level-hint">Detailed</span>
        </button>
      </div>
      <p class="level-description">{getDescription('explanation_verbosity', foreman.explanation_verbosity)}</p>
    </div>

    <!-- Auto KB Writes Toggle -->
    <div class="section">
      <div class="toggle-group">
        <label class="toggle-label">
          <input
            type="checkbox"
            bind:checked={foreman.auto_kb_writes}
            class="toggle-input"
          />
          <span class="toggle-switch"></span>
          <span class="toggle-text">Auto-Save to Knowledge Base</span>
        </label>
        <p class="toggle-desc">
          When enabled, the Foreman automatically saves important decisions, character details, and plot points to the Knowledge Base for future reference.
        </p>
      </div>
    </div>

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>About the Foreman</h4>
      <p>
        The Foreman is your AI writing assistant that helps maintain story consistency, suggests improvements, and tracks important details throughout your manuscript.
      </p>
      <ul>
        <li><strong>Proactiveness</strong>: Controls how often Foreman initiates suggestions</li>
        <li><strong>Challenge Intensity</strong>: How strongly Foreman questions weak choices</li>
        <li><strong>Verbosity</strong>: Level of detail in Foreman's explanations</li>
        <li><strong>Auto KB</strong>: Automatically captures important story elements</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Foreman Settings
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
  .settings-foreman {
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

  .section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 0.25rem 0;
  }

  .section-desc {
    color: #888888;
    margin: 0 0 1rem 0;
    font-size: 0.875rem;
  }

  /* Level selector */
  .level-selector {
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }

  .level-btn {
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

  .level-btn:hover {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .level-btn.active {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .level-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .level-name {
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .level-hint {
    font-size: 0.75rem;
    color: #888888;
  }

  .level-description {
    color: #b0b0b0;
    font-style: italic;
    margin: 0;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  /* Toggle styles */
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
    font-size: 1rem;
    font-weight: 500;
  }

  .toggle-desc {
    margin: 0;
    padding-left: 3.25rem;
    font-size: 0.875rem;
    color: #888888;
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
    margin: 0 0 0.5rem 0;
  }

  .info-panel p {
    color: #b0b0b0;
    margin: 0 0 0.75rem 0;
  }

  .info-panel ul {
    margin: 0;
    padding-left: 1.5rem;
  }

  .info-panel li {
    color: #b0b0b0;
    line-height: 1.6;
    margin-bottom: 0.25rem;
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
</style>
