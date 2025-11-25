<!--
  VoiceBundleGenerator.svelte - Generate Voice Reference Bundle

  After voice calibration is complete, this component:
  1. Shows preview of what will be generated
  2. Generates Voice Bundle files:
     - Voice-Gold-Standard.md
     - Voice-Anti-Pattern-Sheet.md
     - Phase-Evolution-Guide.md
     - voice_settings.yaml
  3. Shows generation progress
  4. Confirms completion and enables Director Mode
-->
<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    voiceCalibration,
    voiceBundleGenerated,
    foremanProjectTitle,
    foremanMode,
    voiceTournamentStep
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let calibration = null;

  // State
  let isGenerating = false;
  let generatedFiles = null;
  let generationProgress = 0;

  // Use prop or store
  $: activeCalibration = calibration || $voiceCalibration;

  // Format voice type for display
  function formatVoiceType(type) {
    return type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'N/A';
  }

  // Format POV for display
  function formatPov(pov) {
    const povMap = {
      'first_person': 'First Person',
      'third_limited': 'Third Person Limited',
      'third_omniscient': 'Third Person Omniscient'
    };
    return povMap[pov] || pov;
  }

  async function generateBundle() {
    if (!activeCalibration) {
      addToast('No voice calibration available', 'error');
      return;
    }

    isGenerating = true;
    generationProgress = 0;

    try {
      const projectId = activeCalibration.project_id || $foremanProjectTitle || 'default_project';

      // Simulate progress steps
      generationProgress = 20;
      await new Promise(r => setTimeout(r, 300));

      generationProgress = 40;
      const result = await apiClient.generateVoiceBundle(projectId);

      generationProgress = 80;
      await new Promise(r => setTimeout(r, 200));

      generatedFiles = result.files;
      $voiceBundleGenerated = true;
      generationProgress = 100;

      addToast('Voice Bundle generated successfully!', 'success');
      dispatch('generated', { files: generatedFiles });

    } catch (error) {
      console.error('Failed to generate voice bundle:', error);
      addToast(`Failed to generate bundle: ${error.message}`, 'error');
      generationProgress = 0;
    } finally {
      isGenerating = false;
    }
  }

  async function proceedToDirector() {
    // Transition Foreman to Director mode
    try {
      // The Foreman mode change would happen via chat or API
      $foremanMode = 'DIRECTOR';
      addToast('Ready for Director Mode!', 'success');
      dispatch('complete');
    } catch (error) {
      console.error('Failed to proceed:', error);
    }
  }

  function handleBack() {
    $voiceTournamentStep = 3; // Back to winner selection
    dispatch('back');
  }
</script>

<div class="bundle-container">
  <div class="bundle-header">
    <div class="header-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="12" y1="18" x2="12" y2="12"/>
        <line x1="9" y1="15" x2="15" y2="15"/>
      </svg>
    </div>
    <div class="header-text">
      <h2>Generate Voice Bundle</h2>
      <p>Create reference files for Director Mode</p>
    </div>
  </div>

  <div class="bundle-content">
    <!-- Calibration Summary -->
    {#if activeCalibration}
      <section class="summary-section">
        <h3 class="section-title">Voice Calibration Summary</h3>

        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">Winning Agent</span>
            <span class="summary-value highlight">{activeCalibration.winning_agent}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Point of View</span>
            <span class="summary-value">{formatPov(activeCalibration.pov)}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Tense</span>
            <span class="summary-value">{activeCalibration.tense === 'past' ? 'Past Tense' : 'Present Tense'}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Voice Type</span>
            <span class="summary-value">{formatVoiceType(activeCalibration.voice_type)}</span>
          </div>
        </div>

        {#if activeCalibration.metaphor_domains?.length > 0}
          <div class="domains-section">
            <span class="summary-label">Metaphor Domains</span>
            <div class="domain-chips">
              {#each activeCalibration.metaphor_domains as domain}
                <span class="domain-chip">{domain}</span>
              {/each}
            </div>
          </div>
        {/if}
      </section>
    {/if}

    <!-- Files to Generate -->
    <section class="files-section">
      <h3 class="section-title">Files to Generate</h3>

      <div class="file-list">
        <div class="file-item" class:generated={generatedFiles?.gold_standard}>
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">Voice-Gold-Standard.md</span>
            <span class="file-desc">Reference sample, authentication tests, voice characteristics</span>
          </div>
          <div class="file-status">
            {#if generatedFiles?.gold_standard}
              <svg viewBox="0 0 24 24" fill="currentColor" class="check-icon">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            {:else if isGenerating && generationProgress >= 40}
              <div class="spinner small"></div>
            {:else}
              <span class="pending-dot"></span>
            {/if}
          </div>
        </div>

        <div class="file-item" class:generated={generatedFiles?.anti_patterns}>
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">Voice-Anti-Pattern-Sheet.md</span>
            <span class="file-desc">Patterns to avoid, zero-tolerance violations, AI vocabulary</span>
          </div>
          <div class="file-status">
            {#if generatedFiles?.anti_patterns}
              <svg viewBox="0 0 24 24" fill="currentColor" class="check-icon">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            {:else if isGenerating && generationProgress >= 60}
              <div class="spinner small"></div>
            {:else}
              <span class="pending-dot"></span>
            {/if}
          </div>
        </div>

        <div class="file-item" class:generated={generatedFiles?.phase_evolution}>
          <div class="file-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">Phase-Evolution-Guide.md</span>
            <span class="file-desc">How voice evolves through story phases (Act 1-3)</span>
          </div>
          <div class="file-status">
            {#if generatedFiles?.phase_evolution}
              <svg viewBox="0 0 24 24" fill="currentColor" class="check-icon">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            {:else if isGenerating && generationProgress >= 80}
              <div class="spinner small"></div>
            {:else}
              <span class="pending-dot"></span>
            {/if}
          </div>
        </div>

        <div class="file-item" class:generated={generatedFiles?.settings}>
          <div class="file-icon yaml">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/>
            </svg>
          </div>
          <div class="file-info">
            <span class="file-name">voice_settings.yaml</span>
            <span class="file-desc">Scoring weights, thresholds, and enhancement parameters</span>
          </div>
          <div class="file-status">
            {#if generatedFiles?.settings}
              <svg viewBox="0 0 24 24" fill="currentColor" class="check-icon">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
            {:else if isGenerating && generationProgress >= 90}
              <div class="spinner small"></div>
            {:else}
              <span class="pending-dot"></span>
            {/if}
          </div>
        </div>
      </div>
    </section>

    <!-- Progress Bar -->
    {#if isGenerating}
      <div class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" style="width: {generationProgress}%"></div>
        </div>
        <span class="progress-text">Generating... {generationProgress}%</span>
      </div>
    {/if}

    <!-- Success Message -->
    {#if generatedFiles && !isGenerating}
      <div class="success-message">
        <svg viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
        <div class="success-text">
          <span class="success-title">Voice Bundle Generated!</span>
          <span class="success-desc">Your voice reference files are ready for Director Mode</span>
        </div>
      </div>
    {/if}

    <!-- What's Next -->
    <section class="next-section">
      <h3 class="section-title">What's Next?</h3>
      <div class="next-info">
        <p>With your Voice Bundle ready, the Foreman will transition to <strong>Director Mode</strong> where you can:</p>
        <ul>
          <li>Generate scene scaffolds with KB context</li>
          <li>Run writing tournaments with voice consistency</li>
          <li>Apply 6-pass enhancement pipeline</li>
          <li>Track health metrics across chapters</li>
        </ul>
      </div>
    </section>
  </div>

  <!-- Footer Actions -->
  <div class="bundle-footer">
    <button class="btn secondary" on:click={handleBack}>
      Back
    </button>

    {#if !generatedFiles}
      <button
        class="btn primary"
        on:click={generateBundle}
        disabled={isGenerating || !activeCalibration}
      >
        {#if isGenerating}
          <span class="spinner"></span>
          Generating...
        {:else}
          Generate Voice Bundle
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        {/if}
      </button>
    {:else}
      <button class="btn primary gold" on:click={proceedToDirector}>
        Proceed to Director Mode
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    {/if}
  </div>
</div>

<style>
  .bundle-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
  }

  .bundle-header {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: linear-gradient(135deg, rgba(212, 165, 116, 0.1), rgba(88, 166, 255, 0.05));
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    background: var(--accent-gold, #d4a574);
    border-radius: var(--radius-lg, 8px);
    color: var(--bg-primary, #0f1419);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header-text h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .header-text p {
    margin: 2px 0 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .bundle-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .section-title {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-md, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  /* Summary Section */
  .summary-section {
    margin-bottom: var(--space-4, 16px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .summary-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3, 12px);
  }

  .summary-item {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .summary-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .summary-value {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .summary-value.highlight {
    color: var(--accent-gold, #d4a574);
  }

  .domains-section {
    margin-top: var(--space-3, 12px);
    padding-top: var(--space-3, 12px);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .domain-chips {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
    margin-top: var(--space-2, 8px);
  }

  .domain-chip {
    padding: 2px 8px;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    color: var(--text-secondary, #8b949e);
  }

  /* Files Section */
  .files-section {
    margin-bottom: var(--space-4, 16px);
  }

  .file-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .file-item {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    transition: all 0.2s ease;
  }

  .file-item.generated {
    border-color: var(--success, #3fb950);
    background: rgba(63, 185, 80, 0.05);
  }

  .file-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-elevated, #2d3640);
    border-radius: var(--radius-sm, 4px);
    color: var(--accent-cyan, #58a6ff);
  }

  .file-icon.yaml {
    color: var(--accent-gold, #d4a574);
  }

  .file-icon svg {
    width: 18px;
    height: 18px;
  }

  .file-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .file-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
    font-family: var(--font-mono, monospace);
  }

  .file-desc {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .file-status {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .check-icon {
    width: 18px;
    height: 18px;
    color: var(--success, #3fb950);
  }

  .pending-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--text-muted, #6e7681);
  }

  /* Progress Section */
  .progress-section {
    margin-bottom: var(--space-4, 16px);
  }

  .progress-bar {
    height: 4px;
    background: var(--bg-tertiary, #242d38);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: var(--space-2, 8px);
  }

  .progress-fill {
    height: 100%;
    background: var(--accent-cyan, #58a6ff);
    transition: width 0.3s ease;
  }

  .progress-text {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  /* Success Message */
  .success-message {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
    padding: var(--space-3, 12px);
    background: rgba(63, 185, 80, 0.1);
    border: 1px solid var(--success, #3fb950);
    border-radius: var(--radius-md, 6px);
    margin-bottom: var(--space-4, 16px);
  }

  .success-message svg {
    width: 32px;
    height: 32px;
    color: var(--success, #3fb950);
    flex-shrink: 0;
  }

  .success-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .success-title {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--success, #3fb950);
  }

  .success-desc {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  /* Next Section */
  .next-section {
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .next-info {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .next-info p {
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .next-info strong {
    color: var(--accent-gold, #d4a574);
  }

  .next-info ul {
    margin: 0;
    padding-left: var(--space-4, 16px);
  }

  .next-info li {
    margin-bottom: var(--space-1, 4px);
  }

  /* Footer */
  .bundle-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-2, 8px);
    padding: var(--space-4, 16px);
    border-top: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #242d38);
  }

  .btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border: none;
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn.secondary {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-secondary, #8b949e);
  }

  .btn.secondary:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .btn.primary {
    background: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .btn.primary.gold {
    background: var(--accent-gold, #d4a574);
  }

  .btn.primary:hover:not(:disabled) {
    filter: brightness(1.1);
  }

  .btn.primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn svg {
    width: 16px;
    height: 16px;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner.small {
    width: 12px;
    height: 12px;
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
