<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Scoring weights (must sum to 100)
  let weights = {
    voice_authenticity: 30,
    character_consistency: 20,
    metaphor_discipline: 20,
    anti_pattern_compliance: 15,
    phase_appropriateness: 15
  };

  // Presets
  const presets = {
    balanced: { voice_authenticity: 30, character_consistency: 20, metaphor_discipline: 20, anti_pattern_compliance: 15, phase_appropriateness: 15 },
    literary: { voice_authenticity: 40, character_consistency: 25, metaphor_discipline: 15, anti_pattern_compliance: 10, phase_appropriateness: 10 },
    thriller: { voice_authenticity: 25, character_consistency: 20, metaphor_discipline: 15, anti_pattern_compliance: 25, phase_appropriateness: 15 },
    romance: { voice_authenticity: 20, character_consistency: 30, metaphor_discipline: 20, anti_pattern_compliance: 15, phase_appropriateness: 15 }
  };

  let selectedPreset = 'balanced';
  let saveMessage = '';
  let errorMessage = '';
  let isLoading = true;

  // Calculate total and validate
  $: total = weights.voice_authenticity + weights.character_consistency + weights.metaphor_discipline + weights.anti_pattern_compliance + weights.phase_appropriateness;
  $: isValid = total === 100;

  onMount(() => {
    loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const response = await fetch(`${BASE_URL}/settings/category/scoring`);
      if (response.ok) {
        const data = await response.json();
        weights.voice_authenticity = data.voice_authenticity_weight ?? 30;
        weights.character_consistency = data.character_consistency_weight ?? 20;
        weights.metaphor_discipline = data.metaphor_discipline_weight ?? 20;
        weights.anti_pattern_compliance = data.anti_pattern_compliance_weight ?? 15;
        weights.phase_appropriateness = data.phase_appropriateness_weight ?? 15;
        detectPreset();
      }
    } catch (error) {
      console.error('Failed to load scoring settings:', error);
      errorMessage = 'Failed to load settings';
    } finally {
      isLoading = false;
    }
  }

  function detectPreset() {
    for (const [name, preset] of Object.entries(presets)) {
      if (
        preset.voice_authenticity === weights.voice_authenticity &&
        preset.character_consistency === weights.character_consistency &&
        preset.metaphor_discipline === weights.metaphor_discipline &&
        preset.anti_pattern_compliance === weights.anti_pattern_compliance &&
        preset.phase_appropriateness === weights.phase_appropriateness
      ) {
        selectedPreset = name;
        return;
      }
    }
    selectedPreset = 'custom';
  }

  function applyPreset(presetName: string) {
    if (presetName === 'custom') return;
    const preset = presets[presetName as keyof typeof presets];
    if (preset) {
      weights = { ...preset };
      selectedPreset = presetName;
    }
  }

  function handleWeightChange() {
    detectPreset();
  }

  async function saveSettings() {
    if (!isValid) {
      errorMessage = 'Weights must sum to 100';
      return;
    }

    saveMessage = '';
    errorMessage = '';

    try {
      const settings = {
        voice_authenticity_weight: weights.voice_authenticity,
        character_consistency_weight: weights.character_consistency,
        metaphor_discipline_weight: weights.metaphor_discipline,
        anti_pattern_compliance_weight: weights.anti_pattern_compliance,
        phase_appropriateness_weight: weights.phase_appropriateness
      };

      const response = await fetch(`${BASE_URL}/settings/category/scoring`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        saveMessage = 'Scoring settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save scoring settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefault() {
    applyPreset('balanced');
  }
</script>

<div class="settings-scoring">
  <div class="header">
    <h2>Scoring Rubric</h2>
    <p class="subtitle">Configure how scenes are evaluated. Weights must sum to 100.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Preset Selector -->
    <div class="section">
      <h3>Quick Presets</h3>
      <div class="preset-buttons">
        <button
          class="preset-btn {selectedPreset === 'balanced' ? 'active' : ''}"
          on:click={() => applyPreset('balanced')}
        >
          <span class="preset-icon">&#9878;</span>
          <span class="preset-name">Balanced</span>
          <span class="preset-desc">Default weights</span>
        </button>
        <button
          class="preset-btn {selectedPreset === 'literary' ? 'active' : ''}"
          on:click={() => applyPreset('literary')}
        >
          <span class="preset-icon">&#128214;</span>
          <span class="preset-name">Literary Fiction</span>
          <span class="preset-desc">Voice-focused</span>
        </button>
        <button
          class="preset-btn {selectedPreset === 'thriller' ? 'active' : ''}"
          on:click={() => applyPreset('thriller')}
        >
          <span class="preset-icon">&#128270;</span>
          <span class="preset-name">Thriller</span>
          <span class="preset-desc">Clean & tight</span>
        </button>
        <button
          class="preset-btn {selectedPreset === 'romance' ? 'active' : ''}"
          on:click={() => applyPreset('romance')}
        >
          <span class="preset-icon">&#10084;</span>
          <span class="preset-name">Romance</span>
          <span class="preset-desc">Character-focused</span>
        </button>
      </div>
    </div>

    <!-- Weight Sliders -->
    <div class="section">
      <h3>Category Weights</h3>

      <div class="weight-total {isValid ? 'valid' : 'invalid'}">
        Total: {total}/100 {isValid ? '' : '(must equal 100)'}
      </div>

      <div class="weight-sliders">
        <div class="weight-item">
          <div class="weight-header">
            <label for="voice">Voice Authenticity</label>
            <span class="weight-value">{weights.voice_authenticity}%</span>
          </div>
          <input
            type="range"
            id="voice"
            min="10"
            max="50"
            bind:value={weights.voice_authenticity}
            on:input={handleWeightChange}
            class="slider"
          />
          <p class="weight-desc">How well the scene sounds like this specific author</p>
        </div>

        <div class="weight-item">
          <div class="weight-header">
            <label for="character">Character Consistency</label>
            <span class="weight-value">{weights.character_consistency}%</span>
          </div>
          <input
            type="range"
            id="character"
            min="10"
            max="30"
            bind:value={weights.character_consistency}
            on:input={handleWeightChange}
            class="slider"
          />
          <p class="weight-desc">Characters behave consistently with their established traits</p>
        </div>

        <div class="weight-item">
          <div class="weight-header">
            <label for="metaphor">Metaphor Discipline</label>
            <span class="weight-value">{weights.metaphor_discipline}%</span>
          </div>
          <input
            type="range"
            id="metaphor"
            min="10"
            max="30"
            bind:value={weights.metaphor_discipline}
            on:input={handleWeightChange}
            class="slider"
          />
          <p class="weight-desc">Metaphors stay within the author's domain vocabulary</p>
        </div>

        <div class="weight-item">
          <div class="weight-header">
            <label for="antipattern">Anti-Pattern Compliance</label>
            <span class="weight-value">{weights.anti_pattern_compliance}%</span>
          </div>
          <input
            type="range"
            id="antipattern"
            min="5"
            max="25"
            bind:value={weights.anti_pattern_compliance}
            on:input={handleWeightChange}
            class="slider"
          />
          <p class="weight-desc">Avoidance of AI tells and formulaic writing</p>
        </div>

        <div class="weight-item">
          <div class="weight-header">
            <label for="phase">Phase Appropriateness</label>
            <span class="weight-value">{weights.phase_appropriateness}%</span>
          </div>
          <input
            type="range"
            id="phase"
            min="5"
            max="25"
            bind:value={weights.phase_appropriateness}
            on:input={handleWeightChange}
            class="slider"
          />
          <p class="weight-desc">Scene fits its position in the story structure</p>
        </div>
      </div>
    </div>

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>How Scoring Works</h4>
      <ul>
        <li><strong>Voice Authenticity</strong>: Compares scene against calibrated voice samples</li>
        <li><strong>Character Consistency</strong>: Checks behavior against character profiles</li>
        <li><strong>Metaphor Discipline</strong>: Validates metaphor domains match author's style</li>
        <li><strong>Anti-Pattern Compliance</strong>: Detects and penalizes AI-sounding phrases</li>
        <li><strong>Phase Appropriateness</strong>: Validates scene fits story beat expectations</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings} disabled={!isValid}>
        Save Scoring Settings
      </button>
    </div>

    <!-- Messages -->
    {#if saveMessage}
      <div class="message success">{saveMessage}</div>
    {/if}
    {#if errorMessage}
      <div class="message error">{errorMessage}</div>
    {/if}
  {/if}
</div>

<style>
  .settings-scoring {
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
    margin: 0 0 1rem 0;
  }

  /* Preset buttons */
  .preset-buttons {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
  }

  .preset-btn {
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

  .preset-btn:hover {
    border-color: #00d9ff;
    transform: translateY(-2px);
  }

  .preset-btn.active {
    border-color: #00d9ff;
    background: #1a3a4a;
  }

  .preset-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .preset-name {
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.25rem;
  }

  .preset-desc {
    font-size: 0.75rem;
    color: #888888;
  }

  /* Weight total indicator */
  .weight-total {
    padding: 0.75rem;
    border-radius: 4px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .weight-total.valid {
    background: #00ff8820;
    color: #00ff88;
    border: 1px solid #00ff88;
  }

  .weight-total.invalid {
    background: #ff444420;
    color: #ff4444;
    border: 1px solid #ff4444;
  }

  /* Weight sliders */
  .weight-sliders {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .weight-item {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
  }

  .weight-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .weight-header label {
    font-weight: 500;
    color: #ffffff;
  }

  .weight-value {
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
    transition: background 0.2s;
  }

  .slider::-webkit-slider-thumb:hover {
    background: #00b8d9;
  }

  .slider::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #00d9ff;
    border-radius: 50%;
    cursor: pointer;
    border: none;
  }

  .weight-desc {
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

  .btn-save:hover:not(:disabled) {
    background: #00b8d9;
  }

  .btn-save:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Messages */
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
