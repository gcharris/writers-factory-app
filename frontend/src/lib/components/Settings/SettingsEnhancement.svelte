<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Enhancement settings
  let thresholds = {
    auto: 85,
    action_prompt: 85,
    six_pass: 70,
    rewrite: 60
  };

  let aggressiveness: 'conservative' | 'medium' | 'aggressive' = 'medium';

  let saveMessage = '';
  let errorMessage = '';
  let isLoading = true;

  onMount(() => {
    loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/enhancement`);
      if (response.ok) {
        const data = await response.json();
        thresholds.auto = data.auto_threshold ?? 85;
        thresholds.action_prompt = data.action_prompt_threshold ?? 85;
        thresholds.six_pass = data.six_pass_threshold ?? 70;
        thresholds.rewrite = data.rewrite_threshold ?? 60;
        aggressiveness = data.aggressiveness ?? 'medium';
      }
    } catch (error) {
      console.error('Failed to load enhancement settings:', error);
      errorMessage = 'Failed to load settings';
    } finally {
      isLoading = false;
    }
  }

  async function saveSettings() {
    saveMessage = '';
    errorMessage = '';

    try {
      const settings = {
        auto_threshold: thresholds.auto,
        action_prompt_threshold: thresholds.action_prompt,
        six_pass_threshold: thresholds.six_pass,
        rewrite_threshold: thresholds.rewrite,
        aggressiveness: aggressiveness
      };

      const response = await fetch(`${BASE_URL}/settings/category/enhancement`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        saveMessage = 'Enhancement settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save enhancement settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefault() {
    thresholds = { auto: 85, action_prompt: 85, six_pass: 70, rewrite: 60 };
    aggressiveness = 'medium';
  }

  function getAggressivenessDescription(level: string): string {
    const descriptions = {
      conservative: 'Minimal changes - preserves original style, only fixes obvious issues',
      medium: 'Balanced polish - improves quality while respecting author intent',
      aggressive: 'Heavy rewrite - willing to significantly restructure for improvement'
    };
    return descriptions[level as keyof typeof descriptions] || '';
  }
</script>

<div class="settings-enhancement">
  <div class="header">
    <h2>Enhancement Pipeline</h2>
    <p class="subtitle">Configure when and how aggressively scenes are enhanced.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Score Thresholds -->
    <div class="section">
      <h3>Score Thresholds</h3>
      <p class="section-desc">Scenes with scores below these thresholds trigger different enhancement levels.</p>

      <div class="threshold-visual">
        <div class="threshold-bar">
          <div class="threshold-zone excellent" style="width: {100 - thresholds.auto}%">
            <span class="zone-label">Excellent ({thresholds.auto}+)</span>
          </div>
          <div class="threshold-zone surgical" style="width: {thresholds.auto - thresholds.action_prompt}%">
            <span class="zone-label">Surgical</span>
          </div>
          <div class="threshold-zone sixpass" style="width: {thresholds.action_prompt - thresholds.six_pass}%">
            <span class="zone-label">6-Pass</span>
          </div>
          <div class="threshold-zone rewrite" style="width: {thresholds.six_pass - thresholds.rewrite}%">
            <span class="zone-label">Full Rewrite</span>
          </div>
          <div class="threshold-zone critical" style="width: {thresholds.rewrite}%">
            <span class="zone-label">Critical</span>
          </div>
        </div>
        <div class="threshold-scale">
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
      </div>

      <div class="threshold-sliders">
        <div class="threshold-item">
          <div class="threshold-header">
            <label for="auto">Auto Enhancement Threshold</label>
            <span class="threshold-value">{thresholds.auto}</span>
          </div>
          <input
            type="range"
            id="auto"
            min="70"
            max="95"
            bind:value={thresholds.auto}
            class="slider"
          />
          <p class="threshold-desc">Scores below this will trigger enhancement suggestions</p>
        </div>

        <div class="threshold-item">
          <div class="threshold-header">
            <label for="action">Action Prompt Threshold</label>
            <span class="threshold-value">{thresholds.action_prompt}</span>
          </div>
          <input
            type="range"
            id="action"
            min="80"
            max="95"
            bind:value={thresholds.action_prompt}
            class="slider"
          />
          <p class="threshold-desc">Scores above this use surgical fixes only</p>
        </div>

        <div class="threshold-item">
          <div class="threshold-header">
            <label for="sixpass">6-Pass Threshold</label>
            <span class="threshold-value">{thresholds.six_pass}</span>
          </div>
          <input
            type="range"
            id="sixpass"
            min="60"
            max="80"
            bind:value={thresholds.six_pass}
            class="slider"
          />
          <p class="threshold-desc">Scores below this trigger full 6-pass enhancement</p>
        </div>

        <div class="threshold-item">
          <div class="threshold-header">
            <label for="rewrite">Rewrite Threshold</label>
            <span class="threshold-value">{thresholds.rewrite}</span>
          </div>
          <input
            type="range"
            id="rewrite"
            min="50"
            max="70"
            bind:value={thresholds.rewrite}
            class="slider"
          />
          <p class="threshold-desc">Scores below this recommend full rewrite</p>
        </div>
      </div>
    </div>

    <!-- Aggressiveness -->
    <div class="section">
      <h3>Enhancement Aggressiveness</h3>

      <div class="aggressiveness-selector">
        <button
          class="agg-btn {aggressiveness === 'conservative' ? 'active' : ''}"
          on:click={() => aggressiveness = 'conservative'}
        >
          <span class="agg-icon">&#128172;</span>
          <span class="agg-name">Conservative</span>
        </button>
        <button
          class="agg-btn {aggressiveness === 'medium' ? 'active' : ''}"
          on:click={() => aggressiveness = 'medium'}
        >
          <span class="agg-icon">&#9878;</span>
          <span class="agg-name">Medium</span>
        </button>
        <button
          class="agg-btn {aggressiveness === 'aggressive' ? 'active' : ''}"
          on:click={() => aggressiveness = 'aggressive'}
        >
          <span class="agg-icon">&#128293;</span>
          <span class="agg-name">Aggressive</span>
        </button>
      </div>

      <p class="agg-description">{getAggressivenessDescription(aggressiveness)}</p>
    </div>

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>Enhancement Levels Explained</h4>
      <ul>
        <li><strong>Excellent (85+)</strong>: No enhancement needed, scene is ready</li>
        <li><strong>Surgical</strong>: Minor tweaks - fix specific issues without rewriting</li>
        <li><strong>6-Pass</strong>: Full pipeline - voice, character, metaphor, anti-pattern, structure, polish</li>
        <li><strong>Rewrite</strong>: Start fresh - scene needs fundamental restructuring</li>
        <li><strong>Critical (&lt;60)</strong>: Consider regenerating from scaffold</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Enhancement Settings
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
  .settings-enhancement {
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
    margin: 0 0 0.5rem 0;
  }

  .section-desc {
    color: #888888;
    margin: 0 0 1.5rem 0;
    font-size: 0.875rem;
  }

  /* Threshold visual */
  .threshold-visual {
    margin-bottom: 1.5rem;
  }

  .threshold-bar {
    display: flex;
    height: 40px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .threshold-zone {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 40px;
  }

  .threshold-zone.excellent {
    background: #00ff88;
    color: #1a1a1a;
  }

  .threshold-zone.surgical {
    background: #00d9ff;
    color: #1a1a1a;
  }

  .threshold-zone.sixpass {
    background: #ffb000;
    color: #1a1a1a;
  }

  .threshold-zone.rewrite {
    background: #ff6b35;
    color: #ffffff;
  }

  .threshold-zone.critical {
    background: #ff4444;
    color: #ffffff;
  }

  .zone-label {
    font-size: 0.7rem;
    font-weight: 600;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 4px;
  }

  .threshold-scale {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #888888;
  }

  /* Threshold sliders */
  .threshold-sliders {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .threshold-item {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .threshold-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .threshold-header label {
    font-weight: 500;
    color: #ffffff;
  }

  .threshold-value {
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

  .threshold-desc {
    font-size: 0.75rem;
    color: #888888;
    margin: 0;
  }

  /* Aggressiveness */
  .aggressiveness-selector {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .agg-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.25rem;
    background: #1a1a1a;
    border: 2px solid #404040;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .agg-btn:hover {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .agg-btn.active {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .agg-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .agg-name {
    font-weight: 600;
    color: #ffffff;
  }

  .agg-description {
    color: #b0b0b0;
    font-style: italic;
    margin: 0;
    padding: 0.75rem;
    background: #1a1a1a;
    border-radius: 4px;
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
</style>
