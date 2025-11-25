<!--
  VoiceVariantSelector.svelte - Winner Selection & Voice Configuration

  After reviewing variants, the writer:
  1. Confirms their winning variant selection
  2. Configures voice parameters (POV, Tense, Voice Type)
  3. Defines metaphor domains
  4. Sets anti-patterns to avoid
  5. Optionally creates a hybrid from multiple variants

  This produces the VoiceCalibrationDocument stored in KB.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';
  import { addToast } from '$lib/toastStore';
  import {
    currentTournament,
    voiceConfig,
    voiceTournamentStep,
    voiceCalibration
  } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let selectedVariant = null;
  export let allVariants = [];

  // Form state bound to store
  let pov = $voiceConfig.pov;
  let tense = $voiceConfig.tense;
  let voiceType = $voiceConfig.voice_type;
  let metaphorDomains = $voiceConfig.metaphor_domains.join(', ');
  let antiPatterns = $voiceConfig.anti_patterns.join('\n');

  // UI state
  let isSubmitting = false;
  let showAdvanced = false;

  // Options
  const povOptions = [
    { value: 'first_person', label: 'First Person', desc: '"I walked into the room..."' },
    { value: 'third_limited', label: 'Third Limited', desc: 'He saw the truth in her eyes...' },
    { value: 'third_omniscient', label: 'Third Omniscient', desc: 'Unknown to them all, the clock was ticking...' }
  ];

  const tenseOptions = [
    { value: 'past', label: 'Past Tense', desc: '"She walked away."' },
    { value: 'present', label: 'Present Tense', desc: '"She walks away."' }
  ];

  const voiceTypeOptions = [
    { value: 'character_voice', label: 'Character Voice', desc: 'Narrator sees through character\'s lens' },
    { value: 'author_voice', label: 'Author Voice', desc: 'Distinct authorial presence' }
  ];

  // Example metaphor domains for suggestions
  const suggestedDomains = [
    'Boxing/Fighting', 'Weather/Climate', 'Architecture/Buildings',
    'Music/Sound', 'Food/Cooking', 'Nature/Animals', 'Technology',
    'Medical/Body', 'Military/War', 'Ocean/Water'
  ];

  // Common anti-patterns to suggest
  const suggestedAntiPatterns = [
    'Similes (like/as comparisons)',
    '-ly adverbs',
    '"despite the" constructions',
    'First-person italics in third-person narration',
    'Computer metaphors for psychology',
    'Academic commentary on emotions'
  ];

  function addDomain(domain) {
    const current = metaphorDomains.split(',').map(d => d.trim()).filter(d => d);
    if (!current.includes(domain)) {
      current.push(domain);
      metaphorDomains = current.join(', ');
    }
  }

  function addAntiPattern(pattern) {
    const current = antiPatterns.split('\n').filter(p => p.trim());
    if (!current.includes(pattern)) {
      current.push(pattern);
      antiPatterns = current.join('\n');
    }
  }

  async function confirmSelection() {
    if (!selectedVariant || !$currentTournament) return;

    isSubmitting = true;

    // Parse inputs
    const domains = metaphorDomains.split(',').map(d => d.trim()).filter(d => d);
    const patterns = antiPatterns.split('\n').map(p => p.trim()).filter(p => p);

    // Update store
    $voiceConfig = {
      pov,
      tense,
      voice_type: voiceType,
      metaphor_domains: domains,
      anti_patterns: patterns,
      phase_evolution: $voiceConfig.phase_evolution
    };

    try {
      // Find variant index within agent's variants
      const agentVariants = allVariants.filter(v => v.agent_id === selectedVariant.agent_id);
      const variantIndex = agentVariants.findIndex(
        v => v.strategy === selectedVariant.strategy
      );

      const result = await apiClient.selectVoiceWinner(
        $currentTournament.tournament_id,
        selectedVariant.agent_id,
        variantIndex,
        $voiceConfig
      );

      $voiceCalibration = result.voice_calibration;
      $voiceTournamentStep = 4; // Move to bundle generation

      addToast('Voice calibration saved successfully', 'success');
      dispatch('complete', { calibration: result.voice_calibration });

    } catch (error) {
      console.error('Failed to save voice calibration:', error);
      addToast(`Failed to save: ${error.message}`, 'error');
    } finally {
      isSubmitting = false;
    }
  }

  function handleBack() {
    dispatch('back');
  }

  function getParagraphs(content) {
    if (!content) return [];
    return content.split('\n\n').filter(p => p.trim()).slice(0, 3);
  }
</script>

<div class="selector-container">
  <div class="selector-header">
    <h3 class="selector-title">Configure Your Voice</h3>
    <p class="selector-desc">Fine-tune the voice parameters based on your winning selection</p>
  </div>

  <div class="selector-content">
    <!-- Selected Variant Preview -->
    {#if selectedVariant}
      <section class="selected-preview">
        <div class="preview-header">
          <span class="preview-label">Selected Variant</span>
          <div class="preview-badges">
            <span class="agent-badge">{selectedVariant.agent_name}</span>
            <span class="strategy-badge">{selectedVariant.strategy.replace('_', ' ')}</span>
          </div>
        </div>
        <div class="preview-content">
          {#each getParagraphs(selectedVariant.content) as paragraph}
            <p>{paragraph}</p>
          {/each}
          {#if selectedVariant.content.split('\n\n').length > 3}
            <p class="more-indicator">...</p>
          {/if}
        </div>
      </section>
    {/if}

    <!-- Voice Configuration -->
    <section class="config-section">
      <h4 class="section-title">Narrative Structure</h4>

      <!-- POV Selection -->
      <div class="option-group">
        <label class="option-label">Point of View</label>
        <div class="option-cards">
          {#each povOptions as option}
            <button
              class="option-card"
              class:selected={pov === option.value}
              on:click={() => pov = option.value}
            >
              <span class="option-name">{option.label}</span>
              <span class="option-example">{option.desc}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Tense Selection -->
      <div class="option-group">
        <label class="option-label">Tense</label>
        <div class="option-cards horizontal">
          {#each tenseOptions as option}
            <button
              class="option-card"
              class:selected={tense === option.value}
              on:click={() => tense = option.value}
            >
              <span class="option-name">{option.label}</span>
              <span class="option-example">{option.desc}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Voice Type Selection -->
      <div class="option-group">
        <label class="option-label">Voice Type</label>
        <div class="option-cards horizontal">
          {#each voiceTypeOptions as option}
            <button
              class="option-card"
              class:selected={voiceType === option.value}
              on:click={() => voiceType = option.value}
            >
              <span class="option-name">{option.label}</span>
              <span class="option-example">{option.desc}</span>
            </button>
          {/each}
        </div>
      </div>
    </section>

    <!-- Advanced Configuration -->
    <button class="toggle-advanced" on:click={() => showAdvanced = !showAdvanced}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class:rotated={showAdvanced}>
        <path d="M9 18l6-6-6-6"/>
      </svg>
      Advanced Voice Configuration
    </button>

    {#if showAdvanced}
      <section class="config-section advanced">
        <!-- Metaphor Domains -->
        <div class="option-group">
          <label class="option-label">Metaphor Domains</label>
          <p class="option-hint">Which imagery domains should anchor your prose?</p>
          <textarea
            class="text-input"
            placeholder="e.g., Boxing, Weather, Architecture"
            bind:value={metaphorDomains}
            rows="2"
          ></textarea>
          <div class="suggestions">
            <span class="suggestion-label">Suggestions:</span>
            {#each suggestedDomains as domain}
              <button class="suggestion-chip" on:click={() => addDomain(domain)}>
                {domain}
              </button>
            {/each}
          </div>
        </div>

        <!-- Anti-Patterns -->
        <div class="option-group">
          <label class="option-label">Anti-Patterns</label>
          <p class="option-hint">Patterns to avoid in your prose (one per line)</p>
          <textarea
            class="text-input"
            placeholder="e.g., Similes&#10;-ly adverbs&#10;'despite the' constructions"
            bind:value={antiPatterns}
            rows="4"
          ></textarea>
          <div class="suggestions">
            <span class="suggestion-label">Common:</span>
            {#each suggestedAntiPatterns.slice(0, 4) as pattern}
              <button class="suggestion-chip" on:click={() => addAntiPattern(pattern)}>
                + {pattern.slice(0, 20)}...
              </button>
            {/each}
          </div>
        </div>
      </section>
    {/if}
  </div>

  <!-- Footer Actions -->
  <div class="selector-footer">
    <button class="btn secondary" on:click={handleBack}>
      Back to Grid
    </button>
    <button
      class="btn primary"
      on:click={confirmSelection}
      disabled={!selectedVariant || isSubmitting}
    >
      {#if isSubmitting}
        <span class="spinner"></span>
        Saving...
      {:else}
        Confirm Voice Selection
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      {/if}
    </button>
  </div>
</div>

<style>
  .selector-container {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-secondary, #1a2027);
  }

  .selector-header {
    padding: var(--space-4, 16px);
    border-bottom: 1px solid var(--border, #2d3a47);
    background: var(--bg-tertiary, #242d38);
  }

  .selector-title {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .selector-desc {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .selector-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  /* Selected Preview */
  .selected-preview {
    margin-bottom: var(--space-4, 16px);
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--accent-gold, #d4a574);
    border-radius: var(--radius-md, 6px);
  }

  .preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-2, 8px);
  }

  .preview-label {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--accent-gold, #d4a574);
  }

  .preview-badges {
    display: flex;
    gap: var(--space-2, 8px);
  }

  .agent-badge,
  .strategy-badge {
    padding: 2px 8px;
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    font-weight: var(--font-medium, 500);
  }

  .agent-badge {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .strategy-badge {
    background: rgba(88, 166, 255, 0.2);
    color: var(--accent-cyan, #58a6ff);
  }

  .preview-content {
    font-family: 'Merriweather', Georgia, serif;
    font-size: var(--text-sm, 12px);
    line-height: 1.6;
    color: var(--text-secondary, #8b949e);
  }

  .preview-content p {
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .more-indicator {
    color: var(--text-muted, #6e7681);
    text-align: center;
  }

  /* Config Section */
  .config-section {
    margin-bottom: var(--space-4, 16px);
  }

  .config-section.advanced {
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .section-title {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-md, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .option-group {
    margin-bottom: var(--space-4, 16px);
  }

  .option-label {
    display: block;
    margin-bottom: var(--space-2, 8px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .option-hint {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Option Cards */
  .option-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-2, 8px);
  }

  .option-cards.horizontal {
    grid-template-columns: repeat(2, 1fr);
  }

  .option-card {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    text-align: left;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .option-card:hover {
    background: var(--bg-elevated, #2d3640);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .option-card.selected {
    background: rgba(88, 166, 255, 0.1);
    border-color: var(--accent-cyan, #58a6ff);
  }

  .option-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .option-example {
    font-size: 10px;
    font-style: italic;
    color: var(--text-muted, #6e7681);
  }

  /* Text Inputs */
  .text-input {
    width: 100%;
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    font-family: inherit;
    resize: vertical;
  }

  .text-input:focus {
    outline: none;
    border-color: var(--accent-cyan, #58a6ff);
  }

  /* Suggestions */
  .suggestions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: var(--space-1, 4px);
    margin-top: var(--space-2, 8px);
  }

  .suggestion-label {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .suggestion-chip {
    padding: 2px 8px;
    background: var(--bg-elevated, #2d3640);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-full, 9999px);
    font-size: 10px;
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .suggestion-chip:hover {
    background: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  /* Toggle Advanced */
  .toggle-advanced {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    width: 100%;
    padding: var(--space-2, 8px);
    background: transparent;
    border: 1px dashed var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
    margin-bottom: var(--space-3, 12px);
  }

  .toggle-advanced:hover {
    background: var(--bg-tertiary, #242d38);
    color: var(--text-primary, #e6edf3);
  }

  .toggle-advanced svg {
    width: 14px;
    height: 14px;
    transition: transform 0.2s ease;
  }

  .toggle-advanced svg.rotated {
    transform: rotate(90deg);
  }

  /* Footer */
  .selector-footer {
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
    background: var(--accent-gold, #d4a574);
    color: var(--bg-primary, #0f1419);
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

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
