<!--
  ThemeOverridePanel.svelte - Manual Theme Score Override Interface

  Phase 5 Track 3 Phase 4: Graph Health UI

  Implements Strategic Decision 2: Hybrid LLM + Manual Override

  Allows writers to:
  - View all theme resonance scores (LLM and manual)
  - Override LLM scores with manual assessments
  - Provide explanation for each override
  - See comparison between LLM and manual scores

  This supports the writer's authority over their creative work
  while still providing LLM guidance.
-->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // Props
  export let projectId = '';

  // State
  let isLoading = false;
  let isSaving = false;
  let errorMsg = '';
  let successMsg = '';
  let overrides = [];

  // Edit state
  let editingOverride = null;
  let editScore = 5;
  let editReason = '';

  // New override form
  let showNewForm = false;
  let newBeatId = '';
  let newThemeId = 'default';
  let newScore = 5;
  let newReason = '';

  // Load initial data
  onMount(() => {
    if (projectId) {
      loadOverrides();
    }
  });

  // Load all overrides
  async function loadOverrides() {
    isLoading = true;
    errorMsg = '';

    try {
      const response = await apiClient.getThemeOverrides(projectId);
      overrides = response.overrides || [];
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Failed to load overrides';
      overrides = [];
    } finally {
      isLoading = false;
    }
  }

  // Save override
  async function saveOverride(beatId, themeId, score, reason) {
    isSaving = true;
    errorMsg = '';
    successMsg = '';

    try {
      await apiClient.setThemeOverride(
        projectId,
        beatId,
        themeId,
        score,
        reason
      );

      successMsg = 'Override saved successfully';
      editingOverride = null;
      showNewForm = false;

      // Reload overrides
      await loadOverrides();

      // Clear success message after 3 seconds
      setTimeout(() => { successMsg = ''; }, 3000);

      // Dispatch event
      dispatch('overrideSet', { beatId, themeId, score, reason });

    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Failed to save override';
    } finally {
      isSaving = false;
    }
  }

  // Start editing override
  function startEdit(override) {
    editingOverride = override;
    editScore = override.manual_score ?? override.llm_score ?? 5;
    editReason = override.reason || '';
  }

  // Cancel editing
  function cancelEdit() {
    editingOverride = null;
    editScore = 5;
    editReason = '';
  }

  // Submit edit
  function submitEdit() {
    if (!editingOverride) return;
    saveOverride(
      editingOverride.beat_id,
      editingOverride.theme_id,
      editScore,
      editReason
    );
  }

  // Toggle new form
  function toggleNewForm() {
    showNewForm = !showNewForm;
    if (!showNewForm) {
      newBeatId = '';
      newThemeId = 'default';
      newScore = 5;
      newReason = '';
    }
  }

  // Submit new override
  function submitNew() {
    if (!newBeatId.trim() || !newReason.trim()) {
      errorMsg = 'Beat ID and reason are required';
      return;
    }
    saveOverride(newBeatId, newThemeId, newScore, newReason);
  }

  // Get score color
  function getScoreColor(score) {
    if (score === null || score === undefined) return '#8b949e';
    if (score >= 8) return '#3fb950';
    if (score >= 6) return '#58a6ff';
    if (score >= 4) return '#d29922';
    return '#f85149';
  }

  // Get score label
  function getScoreLabel(score) {
    if (score === null || score === undefined) return 'Not Set';
    if (score >= 8) return 'Strong';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'Weak';
  }

  // Format timestamp
  function formatTimestamp(iso) {
    if (!iso) return '--';
    const date = new Date(iso);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Close panel
  function close() {
    dispatch('close');
  }
</script>

<div class="override-panel">
  <!-- Header -->
  <div class="panel-header">
    <button class="back-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back
    </button>
    <div class="header-title">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
      </div>
      <div>
        <h2>Theme Overrides</h2>
        <p class="subtitle">Manual theme resonance score adjustments</p>
      </div>
    </div>
    <button class="add-btn" on:click={toggleNewForm}>
      {#if showNewForm}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        Cancel
      {:else}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        Add Override
      {/if}
    </button>
  </div>

  <!-- Explanation -->
  <div class="explanation-box">
    <div class="explanation-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
    </div>
    <div class="explanation-text">
      <p><strong>Hybrid LLM + Manual Override</strong></p>
      <p>The system uses AI to score theme presence at each beat, but you have final authority. Use overrides when you intentionally deviate from typical structure or when the AI misses subtle thematic elements.</p>
    </div>
  </div>

  <!-- New Override Form -->
  {#if showNewForm}
    <div class="new-form">
      <h3>Add New Override</h3>
      <div class="form-grid">
        <div class="form-field">
          <label for="newBeatId">Beat ID</label>
          <input
            type="text"
            id="newBeatId"
            bind:value={newBeatId}
            placeholder="e.g., beat_catalyst, beat_midpoint"
          />
          <span class="field-hint">The beat identifier from your beat sheet</span>
        </div>
        <div class="form-field">
          <label for="newThemeId">Theme</label>
          <input
            type="text"
            id="newThemeId"
            bind:value={newThemeId}
            placeholder="default"
          />
          <span class="field-hint">Theme identifier (use "default" for main theme)</span>
        </div>
        <div class="form-field">
          <label for="newScore">Manual Score (0-10)</label>
          <div class="score-input-group">
            <input
              type="range"
              id="newScore"
              bind:value={newScore}
              min="0"
              max="10"
              step="0.5"
            />
            <span class="score-value" style="color: {getScoreColor(newScore)}">
              {newScore}/10
            </span>
          </div>
          <span class="field-hint">{getScoreLabel(newScore)} theme presence</span>
        </div>
        <div class="form-field full-width">
          <label for="newReason">Reason for Override</label>
          <textarea
            id="newReason"
            bind:value={newReason}
            rows="3"
            placeholder="Explain why you're overriding the AI score..."
          ></textarea>
          <span class="field-hint">Required - helps you remember your creative intent</span>
        </div>
      </div>
      <div class="form-actions">
        <button class="cancel-btn" on:click={toggleNewForm}>Cancel</button>
        <button
          class="save-btn"
          on:click={submitNew}
          disabled={isSaving || !newBeatId.trim() || !newReason.trim()}
        >
          {#if isSaving}
            <span class="spinner"></span>
            Saving...
          {:else}
            Save Override
          {/if}
        </button>
      </div>
    </div>
  {/if}

  <!-- Overrides List -->
  <div class="overrides-section">
    <h3>Current Overrides ({overrides.length})</h3>

    {#if isLoading}
      <div class="loading">
        <div class="spinner"></div>
        <p>Loading overrides...</p>
      </div>
    {:else if overrides.length === 0}
      <div class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <p>No theme overrides set</p>
        <p class="hint">AI scores will be used for all beats</p>
      </div>
    {:else}
      <div class="overrides-list">
        {#each overrides as override (override.beat_id + override.theme_id)}
          <div class="override-card" class:editing={editingOverride === override}>
            {#if editingOverride === override}
              <!-- Edit Mode -->
              <div class="edit-form">
                <div class="edit-header">
                  <span class="beat-id">{override.beat_id}</span>
                  <span class="theme-id">Theme: {override.theme_id}</span>
                </div>
                <div class="edit-fields">
                  <div class="edit-field">
                    <label>Manual Score (0-10)</label>
                    <div class="score-input-group">
                      <input
                        type="range"
                        bind:value={editScore}
                        min="0"
                        max="10"
                        step="0.5"
                      />
                      <span class="score-value" style="color: {getScoreColor(editScore)}">
                        {editScore}/10
                      </span>
                    </div>
                  </div>
                  <div class="edit-field">
                    <label>Reason</label>
                    <textarea
                      bind:value={editReason}
                      rows="2"
                      placeholder="Explain your override..."
                    ></textarea>
                  </div>
                </div>
                <div class="edit-actions">
                  <button class="cancel-btn" on:click={cancelEdit}>Cancel</button>
                  <button
                    class="save-btn"
                    on:click={submitEdit}
                    disabled={isSaving || !editReason.trim()}
                  >
                    {isSaving ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
            {:else}
              <!-- Display Mode -->
              <div class="override-header">
                <div class="override-beat">
                  <span class="beat-label">Beat</span>
                  <span class="beat-id">{override.beat_id}</span>
                </div>
                <div class="override-theme">
                  <span class="theme-label">Theme</span>
                  <span class="theme-id">{override.theme_id}</span>
                </div>
                <button class="edit-btn" on:click={() => startEdit(override)}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                  </svg>
                  Edit
                </button>
              </div>

              <div class="scores-comparison">
                <div class="score-box llm">
                  <span class="score-label">AI Score</span>
                  <span class="score-value" style="color: {getScoreColor(override.llm_score)}">
                    {override.llm_score !== null ? `${override.llm_score}/10` : '--'}
                  </span>
                  <span class="score-tier">{getScoreLabel(override.llm_score)}</span>
                </div>
                <div class="score-arrow">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </div>
                <div class="score-box manual" class:active={override.manual_score !== null}>
                  <span class="score-label">Your Score</span>
                  <span class="score-value" style="color: {getScoreColor(override.manual_score)}">
                    {override.manual_score !== null ? `${override.manual_score}/10` : '--'}
                  </span>
                  <span class="score-tier">{getScoreLabel(override.manual_score)}</span>
                </div>
              </div>

              {#if override.reason}
                <div class="override-reason">
                  <span class="reason-label">Your Reasoning:</span>
                  <p class="reason-text">{override.reason}</p>
                </div>
              {/if}

              <div class="override-footer">
                <span class="timestamp">
                  Updated: {formatTimestamp(override.timestamp)}
                </span>
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  </div>

  <!-- Success/Error Messages -->
  {#if successMsg}
    <div class="success-box">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      {successMsg}
    </div>
  {/if}

  {#if errorMsg}
    <div class="error-box">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="15" y1="9" x2="9" y2="15"></line>
        <line x1="9" y1="9" x2="15" y2="15"></line>
      </svg>
      {errorMsg}
    </div>
  {/if}
</div>

<style>
  .override-panel {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    color: #e6edf3;
  }

  /* Header */
  .panel-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #30363d;
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .back-btn:hover {
    background: #30363d;
    border-color: #58a6ff;
  }

  .back-btn svg {
    width: 16px;
    height: 16px;
  }

  .header-title {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .header-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #a371f7 0%, #8957e5 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
    stroke: white;
  }

  h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .subtitle {
    margin: 0.25rem 0 0;
    font-size: 0.85rem;
    color: #8b949e;
  }

  .add-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .add-btn:hover {
    background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
  }

  .add-btn svg {
    width: 16px;
    height: 16px;
  }

  /* Explanation Box */
  .explanation-box {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: rgba(88, 166, 255, 0.05);
    border: 1px solid rgba(88, 166, 255, 0.2);
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }

  .explanation-icon {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .explanation-icon svg {
    width: 24px;
    height: 24px;
    stroke: #58a6ff;
  }

  .explanation-text p {
    margin: 0;
    font-size: 0.85rem;
    color: #c9d1d9;
    line-height: 1.5;
  }

  .explanation-text p:first-child {
    color: #e6edf3;
    margin-bottom: 0.35rem;
  }

  /* New Form */
  .new-form {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .new-form h3 {
    margin: 0 0 1rem;
    font-size: 1rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-field {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .form-field.full-width {
    grid-column: span 2;
  }

  .form-field label {
    font-size: 0.8rem;
    font-weight: 500;
    color: #e6edf3;
  }

  .form-field input,
  .form-field textarea {
    padding: 0.6rem 0.875rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-field input:focus,
  .form-field textarea:focus {
    outline: none;
    border-color: #58a6ff;
  }

  .field-hint {
    font-size: 0.75rem;
    color: #6e7681;
  }

  .score-input-group {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .score-input-group input[type="range"] {
    flex: 1;
    height: 6px;
    -webkit-appearance: none;
    background: #30363d;
    border-radius: 3px;
    padding: 0;
  }

  .score-input-group input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    background: #58a6ff;
    border-radius: 50%;
    cursor: pointer;
  }

  .score-input-group .score-value {
    font-size: 1.25rem;
    font-weight: 700;
    min-width: 60px;
    text-align: right;
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #30363d;
  }

  .cancel-btn {
    padding: 0.5rem 1rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.85rem;
    cursor: pointer;
  }

  .cancel-btn:hover {
    background: #30363d;
  }

  .save-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 0.85rem;
    cursor: pointer;
  }

  .save-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
  }

  .save-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Overrides Section */
  .overrides-section h3 {
    margin: 0 0 1rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .overrides-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .override-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    overflow: hidden;
  }

  .override-card.editing {
    border-color: #58a6ff;
  }

  .override-header {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid #21262d;
  }

  .override-beat,
  .override-theme {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .beat-label,
  .theme-label {
    font-size: 0.7rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .beat-id {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
    font-family: monospace;
  }

  .theme-id {
    font-size: 0.85rem;
    color: #8b949e;
  }

  .edit-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
    padding: 0.4rem 0.75rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #8b949e;
    font-size: 0.8rem;
    cursor: pointer;
  }

  .edit-btn:hover {
    background: #30363d;
    color: #e6edf3;
    border-color: #58a6ff;
  }

  .edit-btn svg {
    width: 14px;
    height: 14px;
  }

  /* Scores Comparison */
  .scores-comparison {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1.5rem;
    padding: 1.25rem;
  }

  .score-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    padding: 1rem 1.5rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    min-width: 120px;
  }

  .score-box.manual.active {
    border-color: #a371f7;
    background: rgba(163, 113, 247, 0.1);
  }

  .score-box .score-label {
    font-size: 0.7rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .score-box .score-value {
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1;
  }

  .score-box .score-tier {
    font-size: 0.8rem;
    color: #8b949e;
  }

  .score-arrow {
    color: #6e7681;
  }

  .score-arrow svg {
    width: 24px;
    height: 24px;
  }

  /* Override Reason */
  .override-reason {
    padding: 1rem;
    background: rgba(163, 113, 247, 0.05);
    border-top: 1px solid #21262d;
  }

  .reason-label {
    display: block;
    font-size: 0.75rem;
    color: #a371f7;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
  }

  .reason-text {
    margin: 0;
    font-size: 0.9rem;
    color: #c9d1d9;
    line-height: 1.5;
    font-style: italic;
  }

  /* Override Footer */
  .override-footer {
    padding: 0.75rem 1rem;
    background: rgba(0, 0, 0, 0.1);
    border-top: 1px solid #21262d;
  }

  .timestamp {
    font-size: 0.75rem;
    color: #6e7681;
  }

  /* Edit Form within Card */
  .edit-form {
    padding: 1rem;
  }

  .edit-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #30363d;
  }

  .edit-fields {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .edit-field label {
    display: block;
    font-size: 0.8rem;
    color: #8b949e;
    margin-bottom: 0.35rem;
  }

  .edit-field textarea {
    width: 100%;
    padding: 0.6rem 0.875rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.9rem;
    font-family: inherit;
    resize: vertical;
  }

  .edit-field textarea:focus {
    outline: none;
    border-color: #58a6ff;
  }

  .edit-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.75rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #30363d;
  }

  /* Loading & Empty */
  .loading,
  .empty-state {
    text-align: center;
    padding: 3rem;
    color: #8b949e;
  }

  .empty-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    background: #21262d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .empty-icon svg {
    width: 32px;
    height: 32px;
    stroke: #6e7681;
  }

  .empty-state .hint {
    font-size: 0.8rem;
    color: #6e7681;
    margin-top: 0.5rem;
  }

  /* Spinner */
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #30363d;
    border-top-color: #58a6ff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Success/Error Messages */
  .success-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid rgba(63, 185, 80, 0.3);
    border-radius: 8px;
    color: #3fb950;
    font-size: 0.9rem;
    margin-top: 1rem;
  }

  .success-box svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  .error-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(248, 81, 73, 0.1);
    border: 1px solid rgba(248, 81, 73, 0.3);
    border-radius: 8px;
    color: #f85149;
    font-size: 0.9rem;
    margin-top: 1rem;
  }

  .error-box svg {
    width: 20px;
    height: 20px;
    flex-shrink: 0;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .panel-header {
      flex-wrap: wrap;
    }

    .add-btn {
      width: 100%;
      justify-content: center;
    }

    .form-grid {
      grid-template-columns: 1fr;
    }

    .form-field.full-width {
      grid-column: span 1;
    }

    .scores-comparison {
      flex-direction: column;
      gap: 1rem;
    }

    .score-arrow {
      transform: rotate(90deg);
    }

    .override-header {
      flex-wrap: wrap;
    }

    .edit-btn {
      width: 100%;
      justify-content: center;
      margin-left: 0;
    }
  }
</style>
