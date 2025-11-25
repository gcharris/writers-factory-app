<!--
  SettingsAntiPatterns.svelte - Anti-Pattern Detection Configuration

  Features:
  - Toggle built-in patterns (zero-tolerance, formulaic)
  - Custom pattern builder with regex validation
  - Pattern list with edit/remove
  - Severity selection
-->
<script>
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import SettingsToggle from './settings/SettingsToggle.svelte';
  import SettingsSection from './settings/SettingsSection.svelte';

  // Built-in patterns
  let zeroTolerancePatterns = {};
  let formulaicPatterns = {};

  // Custom patterns
  let customPatterns = [];

  // Modal state
  let showAddModal = false;
  let newPattern = {
    pattern: '',
    severity: 'formulaic',
    reason: ''
  };
  let editingIndex = -1;

  // State
  let isLoading = true;
  let isSaving = false;
  let hasChanges = false;
  let originalState = {};

  onMount(async () => {
    await loadSettings();
  });

  async function loadSettings() {
    isLoading = true;
    try {
      const settings = await apiClient.getSettingsCategory('anti_patterns');

      zeroTolerancePatterns = settings.zero_tolerance || {};
      formulaicPatterns = settings.formulaic || {};
      customPatterns = settings.custom || [];

      originalState = {
        zeroTolerance: JSON.stringify(zeroTolerancePatterns),
        formulaic: JSON.stringify(formulaicPatterns),
        custom: JSON.stringify(customPatterns)
      };
    } catch (e) {
      console.error('Failed to load anti-pattern settings:', e);
      addToast({ type: 'error', message: 'Failed to load settings' });
    } finally {
      isLoading = false;
    }
  }

  // Track changes
  $: {
    hasChanges =
      JSON.stringify(zeroTolerancePatterns) !== originalState.zeroTolerance ||
      JSON.stringify(formulaicPatterns) !== originalState.formulaic ||
      JSON.stringify(customPatterns) !== originalState.custom;
  }

  function openAddModal() {
    newPattern = { pattern: '', severity: 'formulaic', reason: '' };
    editingIndex = -1;
    showAddModal = true;
  }

  function openEditModal(index) {
    newPattern = { ...customPatterns[index] };
    editingIndex = index;
    showAddModal = true;
  }

  function closeModal() {
    showAddModal = false;
    newPattern = { pattern: '', severity: 'formulaic', reason: '' };
    editingIndex = -1;
  }

  function validatePattern(pattern) {
    if (!pattern || pattern.trim() === '') {
      return { valid: false, error: 'Pattern cannot be empty' };
    }

    try {
      new RegExp(pattern);
      return { valid: true };
    } catch (e) {
      return { valid: false, error: `Invalid regex: ${e.message}` };
    }
  }

  function addOrUpdatePattern() {
    const validation = validatePattern(newPattern.pattern);
    if (!validation.valid) {
      addToast({ type: 'error', message: validation.error });
      return;
    }

    // Check for duplicates
    const isDuplicate = customPatterns.some((p, i) =>
      i !== editingIndex && p.pattern === newPattern.pattern
    );

    if (isDuplicate) {
      addToast({ type: 'error', message: 'Pattern already exists' });
      return;
    }

    if (editingIndex >= 0) {
      // Update existing
      customPatterns[editingIndex] = { ...newPattern };
    } else {
      // Add new
      customPatterns = [...customPatterns, { ...newPattern }];
    }

    closeModal();
  }

  function removePattern(index) {
    if (!confirm('Remove this custom pattern?')) return;
    customPatterns = customPatterns.filter((_, i) => i !== index);
  }

  async function saveSettings() {
    isSaving = true;
    try {
      // Save zero-tolerance patterns
      for (const [key, value] of Object.entries(zeroTolerancePatterns)) {
        await apiClient.setSetting(`anti_patterns.zero_tolerance.${key}.enabled`, value.enabled);
      }

      // Save formulaic patterns
      for (const [key, value] of Object.entries(formulaicPatterns)) {
        await apiClient.setSetting(`anti_patterns.formulaic.${key}.enabled`, value.enabled);
      }

      // Save custom patterns
      await apiClient.setSetting('anti_patterns.custom', customPatterns);

      originalState = {
        zeroTolerance: JSON.stringify(zeroTolerancePatterns),
        formulaic: JSON.stringify(formulaicPatterns),
        custom: JSON.stringify(customPatterns)
      };

      hasChanges = false;
      addToast({ type: 'success', message: 'Anti-pattern settings saved' });
    } catch (e) {
      console.error('Failed to save anti-pattern settings:', e);
      addToast({ type: 'error', message: 'Failed to save settings' });
    } finally {
      isSaving = false;
    }
  }

  async function resetToDefaults() {
    if (!confirm('Reset anti-patterns to defaults? This will re-enable all built-in patterns and remove custom patterns.')) return;

    // Re-enable all built-in patterns
    Object.keys(zeroTolerancePatterns).forEach(key => {
      zeroTolerancePatterns[key].enabled = true;
    });
    Object.keys(formulaicPatterns).forEach(key => {
      formulaicPatterns[key].enabled = true;
    });

    // Clear custom patterns
    customPatterns = [];

    await saveSettings();
  }

  // Pattern display names
  const patternLabels = {
    first_person_italics: 'First-person italics without dialogue tag',
    with_precision: '"with X precision" phrasing',
    explaining_to_camera: 'Explaining character to camera',
    ai_explaining_character: 'AI explaining character psychology',
    despite_the: '"despite the" construction',
    eyes_widened: '"eyes widened" reaction',
    breath_caught: '"breath caught" physiological tell',
    pulse_quickened: '"pulse quickened" reaction'
  };
</script>

<div class="settings-anti-patterns">
  {#if isLoading}
    <div class="loading">Loading settings...</div>
  {:else}
    <!-- Zero-Tolerance Patterns -->
    <SettingsSection title="Zero-Tolerance Patterns (-2 points each)">
      <div class="pattern-list">
        {#each Object.entries(zeroTolerancePatterns) as [key, value]}
          <SettingsToggle
            label={patternLabels[key] || key}
            bind:checked={value.enabled}
          />
        {/each}
      </div>
    </SettingsSection>

    <!-- Formulaic Patterns -->
    <SettingsSection title="Formulaic Patterns (-1 point each)">
      <div class="pattern-list">
        {#each Object.entries(formulaicPatterns) as [key, value]}
          <SettingsToggle
            label={patternLabels[key] || key}
            bind:checked={value.enabled}
          />
        {/each}
      </div>
    </SettingsSection>

    <!-- Custom Patterns -->
    <SettingsSection title="Custom Patterns" expanded={true}>
      {#if customPatterns.length > 0}
        <div class="custom-patterns">
          {#each customPatterns as pattern, i}
            <div class="custom-pattern-card">
              <div class="pattern-info">
                <span class="pattern-text">{pattern.pattern}</span>
                <span class="pattern-severity severity-{pattern.severity}">
                  {pattern.severity === 'formulaic' ? '-1' : '-2'}
                </span>
              </div>
              {#if pattern.reason}
                <div class="pattern-reason">{pattern.reason}</div>
              {/if}
              <div class="pattern-actions">
                <button class="btn-edit" on:click={() => openEditModal(i)}>Edit</button>
                <button class="btn-remove" on:click={() => removePattern(i)}>Remove</button>
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="empty-state">
          No custom patterns defined. Add patterns to avoid specific phrases in your writing.
        </div>
      {/if}

      <button class="btn-add" on:click={openAddModal}>
        + Add Custom Pattern
      </button>
    </SettingsSection>

    <!-- Actions -->
    <div class="actions">
      <button class="btn-secondary" on:click={resetToDefaults} disabled={isSaving}>
        Reset to Defaults
      </button>
      <button class="btn-primary" on:click={saveSettings} disabled={!hasChanges || isSaving}>
        {isSaving ? 'Saving...' : 'Save Changes'}
      </button>
    </div>
  {/if}
</div>

<!-- Add/Edit Pattern Modal -->
{#if showAddModal}
  <div class="modal-backdrop" on:click={closeModal}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h3>{editingIndex >= 0 ? 'Edit' : 'Add'} Custom Pattern</h3>
        <button class="btn-close" on:click={closeModal}>×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label for="pattern-input">Pattern:</label>
          <input
            id="pattern-input"
            type="text"
            bind:value={newPattern.pattern}
            placeholder="e.g., suddenly"
          />
          <span class="hint">Supports regex patterns (e.g., "very\s+\w+")</span>
        </div>

        <div class="form-group">
          <label>Severity:</label>
          <div class="radio-group">
            <label>
              <input type="radio" bind:group={newPattern.severity} value="formulaic" />
              Formulaic (-1 point)
            </label>
            <label>
              <input type="radio" bind:group={newPattern.severity} value="zero" />
              Zero-Tolerance (-2 points)
            </label>
          </div>
        </div>

        <div class="form-group">
          <label for="reason-input">Reason (optional):</label>
          <textarea
            id="reason-input"
            bind:value={newPattern.reason}
            placeholder="e.g., Overused surprise word"
            rows="2"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={closeModal}>Cancel</button>
        <button class="btn-primary" on:click={addOrUpdatePattern}>
          {editingIndex >= 0 ? 'Update' : 'Add'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .settings-anti-patterns {
    padding: 1rem 0;
  }

  .loading {
    text-align: center;
    color: var(--text-secondary, #8b949e);
    padding: 2rem;
  }

  .pattern-list {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .custom-patterns {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .custom-pattern-card {
    padding: 0.75rem;
    background: var(--bg-elevated, #2d3640);
    border: 1px solid var(--text-muted, #6e7681);
    border-radius: 6px;
  }

  .pattern-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .pattern-text {
    font-family: 'Courier New', monospace;
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    flex: 1;
  }

  .pattern-severity {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .severity-formulaic {
    background: rgba(255, 159, 67, 0.2);
    color: #ff9f43;
  }

  .severity-zero {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
  }

  .pattern-reason {
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    margin-bottom: 0.5rem;
  }

  .pattern-actions {
    display: flex;
    gap: 0.5rem;
  }

  .btn-edit,
  .btn-remove {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-edit {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .btn-edit:hover {
    background: #68b6ff;
  }

  .btn-remove {
    background: rgba(248, 81, 73, 0.2);
    color: #f85149;
  }

  .btn-remove:hover {
    background: rgba(248, 81, 73, 0.3);
  }

  .empty-state {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary, #8b949e);
    font-size: 0.875rem;
  }

  .btn-add {
    width: 100%;
    padding: 0.75rem;
    background: var(--bg-elevated, #2d3640);
    border: 2px dashed var(--accent-gold, #d4a574);
    border-radius: 6px;
    color: var(--accent-gold, #d4a574);
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn-add:hover {
    background: rgba(212, 165, 116, 0.1);
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 1.5rem;
  }

  .btn-primary,
  .btn-secondary {
    padding: 0.625rem 1.25rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
    border: none;
  }

  .btn-primary {
    background: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
  }

  .btn-primary:hover:not(:disabled) {
    background: #e0b584;
    transform: translateY(-1px);
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn-secondary {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
    border: 1px solid var(--text-muted, #6e7681);
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-gold, #d4a574);
  }

  /* Modal Styles */
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal {
    background: var(--bg-secondary, #1a2027);
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid var(--bg-tertiary, #242d38);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--text-primary, #e6edf3);
  }

  .btn-close {
    background: none;
    border: none;
    color: var(--text-muted, #6e7681);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
  }

  .btn-close:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .modal-body {
    padding: 1rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    font-size: 0.875rem;
    color: var(--text-primary, #e6edf3);
    font-weight: 500;
    margin-bottom: 0.5rem;
  }

  .form-group input[type="text"],
  .form-group textarea {
    width: 100%;
    padding: 0.5rem;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--text-muted, #6e7681);
    border-radius: 4px;
    color: var(--text-primary, #e6edf3);
    font-size: 0.875rem;
    font-family: 'Courier New', monospace;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-gold, #d4a574);
  }

  .hint {
    display: block;
    font-size: 0.75rem;
    color: var(--text-secondary, #8b949e);
    margin-top: 0.25rem;
  }

  .radio-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .radio-group label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--bg-tertiary, #242d38);
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: normal;
  }

  .radio-group input[type="radio"] {
    cursor: pointer;
  }

  .modal-footer {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    padding: 1rem;
    border-top: 1px solid var(--bg-tertiary, #242d38);
  }
</style>
