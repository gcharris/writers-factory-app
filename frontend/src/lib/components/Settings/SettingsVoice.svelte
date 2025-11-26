<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Voice strictness settings
  let strictness = {
    authenticity: 'medium' as 'low' | 'medium' | 'high',
    purpose: 'medium' as 'low' | 'medium' | 'high',
    fusion: 'medium' as 'low' | 'medium' | 'high'
  };

  // Metaphor discipline settings
  let metaphor = {
    saturation_threshold: 30,
    primary_allowance: 35,
    simile_tolerance: 2,
    min_domains: 3
  };

  let saveMessage = '';
  let errorMessage = '';
  let isLoading = true;
  let showAdvanced = false;

  onMount(() => {
    loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/scoring`);
      if (response.ok) {
        const data = await response.json();
        strictness.authenticity = data.authenticity_strictness ?? 'medium';
        strictness.purpose = data.purpose_strictness ?? 'medium';
        strictness.fusion = data.fusion_strictness ?? 'medium';
        metaphor.saturation_threshold = data.saturation_threshold ?? 30;
        metaphor.primary_allowance = data.primary_allowance ?? 35;
        metaphor.simile_tolerance = data.simile_tolerance ?? 2;
        metaphor.min_domains = data.min_domains ?? 3;
      }
    } catch (error) {
      console.error('Failed to load voice settings:', error);
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
        authenticity_strictness: strictness.authenticity,
        purpose_strictness: strictness.purpose,
        fusion_strictness: strictness.fusion,
        saturation_threshold: metaphor.saturation_threshold,
        primary_allowance: metaphor.primary_allowance,
        simile_tolerance: metaphor.simile_tolerance,
        min_domains: metaphor.min_domains
      };

      const response = await fetch(`${BASE_URL}/settings/category/scoring`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        saveMessage = 'Voice settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save voice settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function getStrictnessDescription(level: string, type: string): string {
    const descriptions = {
      authenticity: {
        low: 'Forgiving - suitable for early drafts',
        medium: 'Balanced - production-ready quality',
        high: 'Demanding - publication-quality standards'
      },
      purpose: {
        low: 'Loose - scenes can wander from theme',
        medium: 'Moderate - scenes should serve theme',
        high: 'Tight - every scene must advance theme'
      },
      fusion: {
        low: 'Flexible - expertise can be obvious',
        medium: 'Natural - expertise blends with personality',
        high: 'Seamless - expertise invisible to reader'
      }
    };
    return descriptions[type as keyof typeof descriptions]?.[level as keyof typeof descriptions.authenticity] || '';
  }

  function resetToDefault() {
    strictness = { authenticity: 'medium', purpose: 'medium', fusion: 'medium' };
    metaphor = { saturation_threshold: 30, primary_allowance: 35, simile_tolerance: 2, min_domains: 3 };
  }
</script>

<div class="settings-voice">
  <div class="header">
    <h2>Voice Authentication</h2>
    <p class="subtitle">Configure how strictly scenes must match the author's calibrated voice.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Strictness Settings -->
    <div class="section">
      <h3>Strictness Levels</h3>

      <!-- Authenticity -->
      <div class="strictness-item">
        <div class="strictness-header">
          <label>Authenticity Test</label>
          <span class="strictness-value">{strictness.authenticity}</span>
        </div>
        <p class="strictness-desc">{getStrictnessDescription(strictness.authenticity, 'authenticity')}</p>
        <div class="level-selector">
          <button
            class="level-btn {strictness.authenticity === 'low' ? 'active' : ''}"
            on:click={() => strictness.authenticity = 'low'}
          >Low</button>
          <button
            class="level-btn {strictness.authenticity === 'medium' ? 'active' : ''}"
            on:click={() => strictness.authenticity = 'medium'}
          >Medium</button>
          <button
            class="level-btn {strictness.authenticity === 'high' ? 'active' : ''}"
            on:click={() => strictness.authenticity = 'high'}
          >High</button>
        </div>
      </div>

      <!-- Purpose -->
      <div class="strictness-item">
        <div class="strictness-header">
          <label>Purpose Test</label>
          <span class="strictness-value">{strictness.purpose}</span>
        </div>
        <p class="strictness-desc">{getStrictnessDescription(strictness.purpose, 'purpose')}</p>
        <div class="level-selector">
          <button
            class="level-btn {strictness.purpose === 'low' ? 'active' : ''}"
            on:click={() => strictness.purpose = 'low'}
          >Low</button>
          <button
            class="level-btn {strictness.purpose === 'medium' ? 'active' : ''}"
            on:click={() => strictness.purpose = 'medium'}
          >Medium</button>
          <button
            class="level-btn {strictness.purpose === 'high' ? 'active' : ''}"
            on:click={() => strictness.purpose = 'high'}
          >High</button>
        </div>
      </div>

      <!-- Fusion -->
      <div class="strictness-item">
        <div class="strictness-header">
          <label>Fusion Test</label>
          <span class="strictness-value">{strictness.fusion}</span>
        </div>
        <p class="strictness-desc">{getStrictnessDescription(strictness.fusion, 'fusion')}</p>
        <div class="level-selector">
          <button
            class="level-btn {strictness.fusion === 'low' ? 'active' : ''}"
            on:click={() => strictness.fusion = 'low'}
          >Low</button>
          <button
            class="level-btn {strictness.fusion === 'medium' ? 'active' : ''}"
            on:click={() => strictness.fusion = 'medium'}
          >Medium</button>
          <button
            class="level-btn {strictness.fusion === 'high' ? 'active' : ''}"
            on:click={() => strictness.fusion = 'high'}
          >High</button>
        </div>
      </div>
    </div>

    <!-- Advanced: Metaphor Settings -->
    <div class="section">
      <button class="toggle-advanced" on:click={() => showAdvanced = !showAdvanced}>
        <span>{showAdvanced ? '&#9660;' : '&#9654;'} Advanced: Metaphor Discipline</span>
      </button>

      {#if showAdvanced}
        <div class="advanced-settings">
          <div class="setting-item">
            <div class="setting-header">
              <label for="saturation">Domain Saturation Threshold</label>
              <span class="setting-value">{metaphor.saturation_threshold}%</span>
            </div>
            <input
              type="range"
              id="saturation"
              min="20"
              max="50"
              bind:value={metaphor.saturation_threshold}
              class="slider"
            />
            <p class="setting-desc">Maximum percentage any single metaphor domain can occupy</p>
          </div>

          <div class="setting-item">
            <div class="setting-header">
              <label for="primary">Primary Domain Allowance</label>
              <span class="setting-value">{metaphor.primary_allowance}%</span>
            </div>
            <input
              type="range"
              id="primary"
              min="25"
              max="45"
              bind:value={metaphor.primary_allowance}
              class="slider"
            />
            <p class="setting-desc">Higher limit for the designated primary metaphor domain</p>
          </div>

          <div class="setting-item">
            <div class="setting-header">
              <label for="simile">Simile Tolerance</label>
              <span class="setting-value">{metaphor.simile_tolerance}</span>
            </div>
            <input
              type="range"
              id="simile"
              min="0"
              max="5"
              bind:value={metaphor.simile_tolerance}
              class="slider"
            />
            <p class="setting-desc">How many explicit similes allowed per scene before penalty</p>
          </div>

          <div class="setting-item">
            <div class="setting-header">
              <label for="domains">Minimum Domains</label>
              <span class="setting-value">{metaphor.min_domains}</span>
            </div>
            <input
              type="range"
              id="domains"
              min="2"
              max="6"
              bind:value={metaphor.min_domains}
              class="slider"
            />
            <p class="setting-desc">Minimum different metaphor domains required per scene</p>
          </div>
        </div>
      {/if}
    </div>

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>Understanding Voice Tests</h4>
      <ul>
        <li><strong>Authenticity</strong>: Does this sound like the calibrated author?</li>
        <li><strong>Purpose</strong>: Does every scene element serve the theme?</li>
        <li><strong>Fusion</strong>: Is research/expertise seamlessly integrated?</li>
        <li><strong>Metaphor Discipline</strong>: Are metaphors consistent with author's style?</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Voice Settings
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
  .settings-voice {
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
    margin: 0 0 1.5rem 0;
  }

  /* Strictness items */
  .strictness-item {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
    margin-bottom: 1rem;
  }

  .strictness-item:last-child {
    margin-bottom: 0;
  }

  .strictness-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }

  .strictness-header label {
    font-weight: 600;
    color: #ffffff;
  }

  .strictness-value {
    text-transform: capitalize;
    color: #00d9ff;
    font-weight: 500;
  }

  .strictness-desc {
    font-size: 0.875rem;
    color: #888888;
    margin: 0 0 0.75rem 0;
  }

  .level-selector {
    display: flex;
    gap: 0.5rem;
  }

  .level-btn {
    flex: 1;
    padding: 0.5rem 1rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #b0b0b0;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .level-btn:hover {
    border-color: #00d9ff;
    color: #ffffff;
  }

  .level-btn.active {
    background: #00d9ff;
    border-color: #00d9ff;
    color: #1a1a1a;
  }

  /* Advanced toggle */
  .toggle-advanced {
    width: 100%;
    padding: 0.75rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #00d9ff;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }

  .toggle-advanced:hover {
    background: #252525;
  }

  .advanced-settings {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
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
