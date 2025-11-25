<script lang="ts">
  import { onMount } from 'svelte';

  const BASE_URL = 'http://localhost:8000';

  // Health check settings
  let enabled = true;
  let pacing = {
    enabled: true,
    plateau_window: 3,
    plateau_tolerance: 1.0
  };
  let structure = {
    enabled: true,
    beat_deviation_warning: 5,
    beat_deviation_error: 10
  };
  let character = {
    enabled: true,
    flaw_challenge_frequency: 10,
    min_cast_appearances: 3
  };
  let theme = {
    enabled: true,
    min_symbol_occurrences: 3,
    min_resonance_score: 6,
    auto_score: true,
    allow_manual_override: true
  };
  let timeline = {
    enabled: true,
    confidence_threshold: 0.7
  };
  let reporting = {
    auto_trigger: true,
    notification_mode: 'foreman_proactive' as 'foreman_proactive' | 'silent' | 'always'
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
      const response = await fetch(`${BASE_URL}/settings/category/health_checks`);
      if (response.ok) {
        const data = await response.json();
        enabled = data.enabled ?? true;

        if (data.pacing) {
          pacing.enabled = data.pacing.enabled ?? true;
          pacing.plateau_window = data.pacing.plateau_window ?? 3;
          pacing.plateau_tolerance = data.pacing.plateau_tolerance ?? 1.0;
        }
        if (data.structure) {
          structure.enabled = data.structure.enabled ?? true;
          structure.beat_deviation_warning = data.structure.beat_deviation_warning ?? 5;
          structure.beat_deviation_error = data.structure.beat_deviation_error ?? 10;
        }
        if (data.character) {
          character.enabled = data.character.enabled ?? true;
          character.flaw_challenge_frequency = data.character.flaw_challenge_frequency ?? 10;
          character.min_cast_appearances = data.character.min_cast_appearances ?? 3;
        }
        if (data.theme) {
          theme.enabled = data.theme.enabled ?? true;
          theme.min_symbol_occurrences = data.theme.min_symbol_occurrences ?? 3;
          theme.min_resonance_score = data.theme.min_resonance_score ?? 6;
          theme.auto_score = data.theme.auto_score ?? true;
          theme.allow_manual_override = data.theme.allow_manual_override ?? true;
        }
        if (data.timeline) {
          timeline.enabled = data.timeline.enabled ?? true;
          timeline.confidence_threshold = data.timeline.confidence_threshold ?? 0.7;
        }
        if (data.reporting) {
          reporting.auto_trigger = data.reporting.auto_trigger ?? true;
          reporting.notification_mode = data.reporting.notification_mode ?? 'foreman_proactive';
        }
      }
    } catch (error) {
      console.error('Failed to load health check settings:', error);
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
        enabled,
        pacing,
        structure,
        character,
        theme,
        timeline,
        reporting
      };

      const response = await fetch(`${BASE_URL}/settings/category/health_checks`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        saveMessage = 'Health check settings saved successfully';
        setTimeout(() => (saveMessage = ''), 3000);
      } else {
        const error = await response.json();
        errorMessage = `Failed to save: ${error.detail || 'Unknown error'}`;
      }
    } catch (error) {
      console.error('Failed to save health check settings:', error);
      errorMessage = 'Failed to save settings';
    }
  }

  function resetToDefault() {
    enabled = true;
    pacing = { enabled: true, plateau_window: 3, plateau_tolerance: 1.0 };
    structure = { enabled: true, beat_deviation_warning: 5, beat_deviation_error: 10 };
    character = { enabled: true, flaw_challenge_frequency: 10, min_cast_appearances: 3 };
    theme = { enabled: true, min_symbol_occurrences: 3, min_resonance_score: 6, auto_score: true, allow_manual_override: true };
    timeline = { enabled: true, confidence_threshold: 0.7 };
    reporting = { auto_trigger: true, notification_mode: 'foreman_proactive' };
  }
</script>

<div class="settings-health">
  <div class="header">
    <h2>Health Check Settings</h2>
    <p class="subtitle">Configure manuscript validation thresholds and automation.</p>
  </div>

  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Master Toggle -->
    <div class="section">
      <div class="toggle-group">
        <label class="toggle-label">
          <input type="checkbox" bind:checked={enabled} class="toggle-input" />
          <span class="toggle-switch"></span>
          <span class="toggle-text">Enable Health Checks</span>
        </label>
        <p class="toggle-desc">
          Run automated validation checks on your manuscript structure, pacing, and themes.
        </p>
      </div>
    </div>

    <!-- Health Check Categories -->
    <div class="section" class:disabled={!enabled}>
      <h3>Check Categories</h3>

      <!-- Pacing -->
      <div class="check-category">
        <div class="check-header">
          <label class="check-toggle">
            <input type="checkbox" bind:checked={pacing.enabled} disabled={!enabled} />
            <span>Pacing Analysis</span>
          </label>
          <span class="check-status" class:enabled={pacing.enabled}>
            {pacing.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <p class="check-desc">Detects tension plateaus across consecutive chapters</p>
        {#if pacing.enabled && showAdvanced}
          <div class="check-settings">
            <div class="setting-row">
              <label>Plateau Window</label>
              <input type="number" min="2" max="5" bind:value={pacing.plateau_window} disabled={!enabled} />
              <span class="setting-hint">chapters</span>
            </div>
            <div class="setting-row">
              <label>Tolerance</label>
              <input type="number" min="0.5" max="2" step="0.1" bind:value={pacing.plateau_tolerance} disabled={!enabled} />
              <span class="setting-hint">tension variance</span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Structure -->
      <div class="check-category">
        <div class="check-header">
          <label class="check-toggle">
            <input type="checkbox" bind:checked={structure.enabled} disabled={!enabled} />
            <span>Beat Structure</span>
          </label>
          <span class="check-status" class:enabled={structure.enabled}>
            {structure.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <p class="check-desc">Validates 15-beat Save the Cat! structure compliance</p>
        {#if structure.enabled && showAdvanced}
          <div class="check-settings">
            <div class="setting-row">
              <label>Warning at</label>
              <input type="number" min="3" max="10" bind:value={structure.beat_deviation_warning} disabled={!enabled} />
              <span class="setting-hint">% deviation</span>
            </div>
            <div class="setting-row">
              <label>Error at</label>
              <input type="number" min="8" max="15" bind:value={structure.beat_deviation_error} disabled={!enabled} />
              <span class="setting-hint">% deviation</span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Character -->
      <div class="check-category">
        <div class="check-header">
          <label class="check-toggle">
            <input type="checkbox" bind:checked={character.enabled} disabled={!enabled} />
            <span>Character Arcs</span>
          </label>
          <span class="check-status" class:enabled={character.enabled}>
            {character.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <p class="check-desc">Monitors fatal flaw challenges and cast utilization</p>
        {#if character.enabled && showAdvanced}
          <div class="check-settings">
            <div class="setting-row">
              <label>Flaw challenge every</label>
              <input type="number" min="5" max="20" bind:value={character.flaw_challenge_frequency} disabled={!enabled} />
              <span class="setting-hint">scenes max</span>
            </div>
            <div class="setting-row">
              <label>Min cast appearances</label>
              <input type="number" min="1" max="5" bind:value={character.min_cast_appearances} disabled={!enabled} />
              <span class="setting-hint">per character</span>
            </div>
          </div>
        {/if}
      </div>

      <!-- Theme -->
      <div class="check-category">
        <div class="check-header">
          <label class="check-toggle">
            <input type="checkbox" bind:checked={theme.enabled} disabled={!enabled} />
            <span>Theme & Symbols</span>
          </label>
          <span class="check-status" class:enabled={theme.enabled}>
            {theme.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <p class="check-desc">Tracks symbol recurrence and theme resonance</p>
        {#if theme.enabled && showAdvanced}
          <div class="check-settings">
            <div class="setting-row">
              <label>Min symbol occurrences</label>
              <input type="number" min="2" max="6" bind:value={theme.min_symbol_occurrences} disabled={!enabled} />
            </div>
            <div class="setting-row">
              <label>Min resonance score</label>
              <input type="number" min="4" max="8" bind:value={theme.min_resonance_score} disabled={!enabled} />
              <span class="setting-hint">/10</span>
            </div>
            <div class="setting-row checkbox-row">
              <label>
                <input type="checkbox" bind:checked={theme.auto_score} disabled={!enabled} />
                Auto-score with AI
              </label>
            </div>
            <div class="setting-row checkbox-row">
              <label>
                <input type="checkbox" bind:checked={theme.allow_manual_override} disabled={!enabled} />
                Allow manual score override
              </label>
            </div>
          </div>
        {/if}
      </div>

      <!-- Timeline -->
      <div class="check-category">
        <div class="check-header">
          <label class="check-toggle">
            <input type="checkbox" bind:checked={timeline.enabled} disabled={!enabled} />
            <span>Timeline Consistency</span>
          </label>
          <span class="check-status" class:enabled={timeline.enabled}>
            {timeline.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </div>
        <p class="check-desc">Detects character teleportation and world rule violations</p>
        {#if timeline.enabled && showAdvanced}
          <div class="check-settings">
            <div class="setting-row">
              <label>Confidence threshold</label>
              <input type="number" min="0.5" max="0.95" step="0.05" bind:value={timeline.confidence_threshold} disabled={!enabled} />
              <span class="setting-hint">for flagging</span>
            </div>
          </div>
        {/if}
      </div>

      <button class="toggle-advanced" on:click={() => showAdvanced = !showAdvanced}>
        {showAdvanced ? '&#9660; Hide' : '&#9654; Show'} Advanced Thresholds
      </button>
    </div>

    <!-- Automation -->
    <div class="section" class:disabled={!enabled}>
      <h3>Automation</h3>

      <div class="automation-options">
        <div class="toggle-group">
          <label class="toggle-label">
            <input type="checkbox" bind:checked={reporting.auto_trigger} class="toggle-input" disabled={!enabled} />
            <span class="toggle-switch"></span>
            <span class="toggle-text">Auto-run after chapter completion</span>
          </label>
        </div>

        <div class="notification-selector">
          <label>Notification Mode:</label>
          <select bind:value={reporting.notification_mode} disabled={!enabled}>
            <option value="foreman_proactive">Follow Foreman setting</option>
            <option value="always">Always notify</option>
            <option value="silent">Silent (check dashboard)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Info Panel -->
    <div class="info-panel">
      <h4>7 Health Checks</h4>
      <ul>
        <li><strong>Pacing</strong>: Detect tension plateaus across chapters</li>
        <li><strong>Beat Progress</strong>: Validate Save the Cat! structure</li>
        <li><strong>Timeline</strong>: Catch continuity errors and teleportation</li>
        <li><strong>Flaw Challenges</strong>: Ensure protagonist's flaw is tested</li>
        <li><strong>Cast Function</strong>: Verify supporting character utilization</li>
        <li><strong>Symbolic Layering</strong>: Track symbol recurrence</li>
        <li><strong>Theme Resonance</strong>: Score thematic depth per beat</li>
      </ul>
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefault}>
        Reset to Default
      </button>
      <button class="btn-save" on:click={saveSettings}>
        Save Health Settings
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
  .settings-health {
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
    transition: opacity 0.2s;
  }

  .section.disabled {
    opacity: 0.5;
    pointer-events: none;
  }

  .section h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #00d9ff;
    margin: 0 0 1rem 0;
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

  /* Check categories */
  .check-category {
    padding: 1rem;
    background: #1a1a1a;
    border-radius: 6px;
    margin-bottom: 0.75rem;
  }

  .check-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.25rem;
  }

  .check-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-weight: 500;
  }

  .check-toggle input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  .check-status {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    background: #404040;
    color: #888888;
  }

  .check-status.enabled {
    background: #00ff8820;
    color: #00ff88;
  }

  .check-desc {
    font-size: 0.875rem;
    color: #888888;
    margin: 0;
  }

  .check-settings {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid #2d2d2d;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .setting-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  .setting-row label {
    color: #b0b0b0;
    min-width: 150px;
  }

  .setting-row input[type="number"] {
    width: 70px;
    padding: 0.25rem 0.5rem;
    background: #2d2d2d;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
    font-family: 'JetBrains Mono', monospace;
  }

  .setting-row input[type="number"]:focus {
    outline: none;
    border-color: #00d9ff;
  }

  .setting-hint {
    color: #666666;
    font-size: 0.75rem;
  }

  .checkbox-row label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
  }

  .checkbox-row input {
    width: 16px;
    height: 16px;
  }

  .toggle-advanced {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background: transparent;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #00d9ff;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .toggle-advanced:hover {
    border-color: #00d9ff;
    background: #00d9ff10;
  }

  /* Automation */
  .automation-options {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .notification-selector {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .notification-selector label {
    color: #b0b0b0;
  }

  .notification-selector select {
    flex: 1;
    max-width: 250px;
    padding: 0.5rem;
    background: #1a1a1a;
    border: 1px solid #404040;
    border-radius: 4px;
    color: #ffffff;
  }

  .notification-selector select:focus {
    outline: none;
    border-color: #00d9ff;
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
    columns: 2;
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
