<!-- VoiceCalibration.svelte -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    currentTournament,
    tournamentStatus,
    tournamentVariants,
    voiceTournamentStep,
    voiceConfig,
    voiceCalibration,
    voiceBundleGenerated,
    selectedVariants,
    foremanMode,
    foremanProjectTitle
  } from '$lib/stores';

  // Sub-components
  import VoiceTournamentLauncher from './VoiceTournamentLauncher.svelte';
  import VoiceVariantGrid from './VoiceVariantGrid.svelte';
  import VoiceComparisonView from './VoiceComparisonView.svelte';
  import VoiceBundleGenerator from './VoiceBundleGenerator.svelte';
  import VoiceVariantSelector from './VoiceVariantSelector.svelte';

  // Steps
  const STEPS = {
    SETUP: 0,
    RUNNING: 1,
    REVIEW: 2,
    SELECT_WINNER: 3,
    GENERATE_BUNDLE: 4,
    COMPLETE: 5
  };

  // Local state
  let pollInterval = null;
  let showComparison = false;
  let previewVariant = null;

  // Computed
  $: currentStep = $voiceTournamentStep;
  $: tournamentId = $currentTournament?.tournament_id;

  onMount(() => {
    // Resume polling if tournament was running
    if ($tournamentStatus === 'running' && tournamentId) {
      startPolling();
    }
  });

  onDestroy(() => {
    stopPolling();
  });

  // Polling for tournament status
  function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(checkTournamentStatus, 2000);
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  async function checkTournamentStatus() {
    if (!tournamentId) return;

    try {
      const status = await apiClient.getTournamentStatus(tournamentId);
      $tournamentStatus = status.status;

      if (status.status === 'awaiting_selection') {
        stopPolling();
        await loadVariants();
        $voiceTournamentStep = STEPS.REVIEW;
      } else if (status.status === 'failed') {
        stopPolling();
        addToast('Tournament failed. Please try again.', 'error');
        $voiceTournamentStep = STEPS.SETUP;
      }
    } catch (error) {
      console.error('Status check failed:', error);
    }
  }

  async function loadVariants() {
    try {
      const result = await apiClient.getTournamentVariants(tournamentId);
      $tournamentVariants = result.variants || [];
    } catch (error) {
      console.error('Failed to load variants:', error);
      addToast('Failed to load variants', 'error');
    }
  }

  // Event handlers from sub-components
  function handleTournamentStarted(event) {
    const { tournamentId: id } = event.detail;
    $voiceTournamentStep = STEPS.RUNNING;
    startPolling();
  }

  function handleVariantSelect(event) {
    const { variant } = event.detail;
    $selectedVariants = [variant];
    $voiceTournamentStep = STEPS.SELECT_WINNER;
  }

  function handleVariantPreview(event) {
    previewVariant = event.detail.variant;
  }

  function handleCompare(event) {
    showComparison = true;
  }

  async function handleWinnerConfirmed(event) {
    const { variant, config } = event.detail;

    try {
      const result = await apiClient.selectVoiceWinner(
        tournamentId,
        variant.agent_id,
        variant.variant_number,
        config
      );

      $voiceCalibration = result.voice_calibration;
      $voiceTournamentStep = STEPS.GENERATE_BUNDLE;
      addToast('Voice calibration saved!', 'success');
    } catch (error) {
      console.error('Failed to save winner:', error);
      addToast('Failed to save voice selection', 'error');
    }
  }

  async function handleBundleGenerated() {
    $voiceBundleGenerated = true;
    $voiceTournamentStep = STEPS.COMPLETE;
  }

  function handleTransitionToDirector() {
    // Transition Foreman to DIRECTOR mode
    $foremanMode = 'director';
    addToast('Voice calibration complete! Entering Director Mode.', 'success');
  }

  function handleBack() {
    if (currentStep === STEPS.SELECT_WINNER) {
      $voiceTournamentStep = STEPS.REVIEW;
    } else if (currentStep === STEPS.REVIEW) {
      // Can't go back from review - tournament already ran
    }
  }

  function handleReset() {
    $currentTournament = null;
    $tournamentStatus = null;
    $tournamentVariants = [];
    $selectedVariants = [];
    $voiceCalibration = null;
    $voiceBundleGenerated = false;
    $voiceTournamentStep = STEPS.SETUP;
    stopPolling();
  }
</script>

<div class="voice-calibration">
  <!-- Progress indicator -->
  <div class="progress-steps">
    {#each ['Setup', 'Running', 'Review', 'Select', 'Bundle', 'Done'] as stepName, i}
      <div
        class="step"
        class:active={currentStep === i}
        class:complete={currentStep > i}
      >
        <div class="step-number">{i + 1}</div>
        <span class="step-name">{stepName}</span>
      </div>
      {#if i < 5}
        <div class="step-connector" class:complete={currentStep > i}></div>
      {/if}
    {/each}
  </div>

  <!-- Content area -->
  <div class="content-area">
    {#if currentStep === STEPS.SETUP}
      <VoiceTournamentLauncher
        on:started={handleTournamentStarted}
        on:close={() => {}}
      />

    {:else if currentStep === STEPS.RUNNING}
      <div class="running-state">
        <div class="spinner-large"></div>
        <h3>Tournament in Progress</h3>
        <p>Generating {$currentTournament?.selected_agents?.length * 5 || '~15'} voice variants...</p>
        <p class="hint">This typically takes 2-5 minutes</p>

        <div class="progress-info">
          <span>Status: {$tournamentStatus}</span>
        </div>
      </div>

    {:else if currentStep === STEPS.REVIEW}
      <div class="review-header">
        <h3>Review Voice Variants</h3>
        <p>Click a variant to select it, or select multiple for comparison.</p>
      </div>

      <VoiceVariantGrid
        variants={$tournamentVariants}
        selectionMode="multi"
        on:select={handleVariantSelect}
        on:preview={handleVariantPreview}
        on:compare={handleCompare}
      />

    {:else if currentStep === STEPS.SELECT_WINNER}
      <VoiceVariantSelector
        variant={$selectedVariants[0]}
        on:confirm={handleWinnerConfirmed}
        on:back={handleBack}
      />

    {:else if currentStep === STEPS.GENERATE_BUNDLE}
      <VoiceBundleGenerator
        projectId={$foremanProjectTitle || 'default_project'}
        voiceCalibration={$voiceCalibration}
        on:generated={handleBundleGenerated}
      />

    {:else if currentStep === STEPS.COMPLETE}
      <div class="complete-state">
        <div class="success-icon">✓</div>
        <h3>Voice Calibration Complete!</h3>
        <p>Your voice profile has been created and bundled.</p>

        <div class="bundle-summary">
          <h4>Generated Files:</h4>
          <ul>
            <li>Voice-Gold-Standard.md</li>
            <li>Voice-Anti-Pattern-Sheet.md</li>
            <li>Phase-Evolution-Guide.md</li>
            <li>voice_settings.yaml</li>
          </ul>
        </div>

        <button class="btn primary" on:click={handleTransitionToDirector}>
          Enter Director Mode
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    {/if}
  </div>

  <!-- Comparison modal -->
  {#if showComparison && $selectedVariants.length >= 2}
    <div class="modal-overlay" on:click={() => showComparison = false}>
      <div class="modal-content" on:click|stopPropagation>
        <VoiceComparisonView
          variants={$selectedVariants}
          on:select={handleVariantSelect}
          on:close={() => showComparison = false}
        />
      </div>
    </div>
  {/if}

  <!-- Preview modal -->
  {#if previewVariant}
    <div class="modal-overlay" on:click={() => previewVariant = null}>
      <div class="modal-content preview" on:click|stopPropagation>
        <div class="preview-header">
          <span class="agent-name">{previewVariant.agent_name}</span>
          <span class="strategy">{previewVariant.strategy}</span>
          <button class="close-btn" on:click={() => previewVariant = null}>×</button>
        </div>
        <div class="preview-content">
          {previewVariant.content}
        </div>
        <div class="preview-footer">
          <span>{previewVariant.word_count} words</span>
          <button class="btn primary" on:click={() => {
            $selectedVariants = [previewVariant];
            previewVariant = null;
            $voiceTournamentStep = STEPS.SELECT_WINNER;
          }}>
            Select This Variant
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Reset button (dev/debug) -->
  {#if currentStep > STEPS.SETUP}
    <button class="reset-btn" on:click={handleReset} title="Reset Tournament">
      ↺ Start Over
    </button>
  {/if}
</div>

<style>
  .voice-calibration {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary);
  }

  /* Progress steps */
  .progress-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-4) var(--space-6);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
  }

  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-1);
  }

  .step-number {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary);
    border: 2px solid var(--border);
    border-radius: 50%;
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--text-muted);
    transition: all 0.2s ease;
  }

  .step.active .step-number {
    background: var(--accent-cyan);
    border-color: var(--accent-cyan);
    color: var(--bg-primary);
  }

  .step.complete .step-number {
    background: var(--success);
    border-color: var(--success);
    color: white;
  }

  .step-name {
    font-size: 10px;
    color: var(--text-muted);
  }

  .step.active .step-name {
    color: var(--accent-cyan);
    font-weight: var(--font-medium);
  }

  .step-connector {
    width: 40px;
    height: 2px;
    background: var(--border);
    margin: 0 var(--space-2);
    margin-bottom: 18px;
  }

  .step-connector.complete {
    background: var(--success);
  }

  /* Content area */
  .content-area {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4);
  }

  /* Running state */
  .running-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
    color: var(--text-secondary);
  }

  .spinner-large {
    width: 48px;
    height: 48px;
    border: 3px solid var(--border);
    border-top-color: var(--accent-cyan);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: var(--space-4);
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .running-state h3 {
    margin: 0 0 var(--space-2);
    color: var(--text-primary);
  }

  .hint {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-2);
  }

  .progress-info {
    margin-top: var(--space-4);
    padding: var(--space-2) var(--space-4);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
  }

  /* Complete state */
  .complete-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
  }

  .success-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--success);
    border-radius: 50%;
    font-size: 32px;
    color: white;
    margin-bottom: var(--space-4);
  }

  .bundle-summary {
    margin: var(--space-4) 0;
    padding: var(--space-4);
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    text-align: left;
  }

  .bundle-summary h4 {
    margin: 0 0 var(--space-2);
    font-size: var(--text-sm);
    color: var(--text-secondary);
  }

  .bundle-summary ul {
    margin: 0;
    padding-left: var(--space-4);
    font-size: var(--text-sm);
    color: var(--text-muted);
  }

  /* Review header */
  .review-header {
    margin-bottom: var(--space-4);
  }

  .review-header h3 {
    margin: 0 0 var(--space-1);
    color: var(--text-primary);
  }

  .review-header p {
    margin: 0;
    font-size: var(--text-sm);
    color: var(--text-secondary);
  }

  /* Buttons */
  .btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-5);
    border: none;
    border-radius: var(--radius-md);
    font-size: var(--text-md);
    font-weight: var(--font-medium);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .btn.primary {
    background: var(--accent-cyan);
    color: var(--bg-primary);
  }

  .btn.primary:hover {
    filter: brightness(1.1);
  }

  .btn svg {
    width: 18px;
    height: 18px;
  }

  /* Reset button */
  .reset-btn {
    position: absolute;
    bottom: var(--space-4);
    right: var(--space-4);
    padding: var(--space-2) var(--space-3);
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    font-size: var(--text-xs);
    color: var(--text-muted);
    cursor: pointer;
  }

  .reset-btn:hover {
    color: var(--text-primary);
    border-color: var(--text-muted);
  }

  /* Modals */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }

  .modal-content {
    max-width: 90vw;
    max-height: 90vh;
    background: var(--bg-secondary);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }

  .modal-content.preview {
    width: 600px;
  }

  .preview-header {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border);
  }

  .preview-header .agent-name {
    font-weight: var(--font-semibold);
    color: var(--text-primary);
  }

  .preview-header .strategy {
    padding: 2px 8px;
    background: var(--bg-elevated);
    border-radius: var(--radius-full);
    font-size: var(--text-xs);
    color: var(--text-secondary);
  }

  .preview-header .close-btn {
    margin-left: auto;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    font-size: 18px;
    color: var(--text-muted);
    cursor: pointer;
  }

  .preview-content {
    padding: var(--space-4);
    max-height: 400px;
    overflow-y: auto;
    font-size: var(--text-sm);
    line-height: 1.6;
    color: var(--text-secondary);
    white-space: pre-wrap;
  }

  .preview-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border);
  }

  .preview-footer span {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }
</style>
