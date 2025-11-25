<!--
  VoiceEvolutionChart.svelte - Voice Phase Evolution Visualization

  Visualizes how the narrative voice should evolve through story phases:
  - Act 1: Setup (Opening Image to Break into Two)
  - Act 2A: Fun & Games to Midpoint
  - Act 2B: Bad Guys Close In to All Is Lost
  - Act 3: Resolution

  Features:
  - Visual timeline with phase markers
  - Editable descriptions for each phase
  - Example sentences showing voice characteristics per phase
  - Save phase evolution to voice config
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { voiceConfig, voiceCalibration } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let editable = true;
  export let phaseEvolution = null;

  // Phase definitions based on Save the Cat! structure
  const phases = [
    {
      id: 'Act 1',
      name: 'Act 1: The Setup',
      beats: '1-15%',
      description: 'Opening Image → Catalyst → Break into Two',
      color: '#58a6ff',
      defaultVoice: 'Grounded, establishing narrator reliability. Shorter sentences, concrete details. The world as the protagonist knows it.'
    },
    {
      id: 'Act 2A',
      name: 'Act 2A: Promise of Premise',
      beats: '15-50%',
      description: 'Fun & Games → B Story → Midpoint',
      color: '#3fb950',
      defaultVoice: 'Expanded vocabulary, longer rhythms as stakes build. Metaphors emerge from character expertise. Confidence or growing unease.'
    },
    {
      id: 'Act 2B',
      name: 'Act 2B: The Descent',
      beats: '50-75%',
      description: 'Bad Guys Close In → All Is Lost → Dark Night',
      color: '#d29922',
      defaultVoice: 'Fragmented when under pressure. Internal contradictions surface. Metaphors darken, sentences shorten in crisis moments.'
    },
    {
      id: 'Act 3',
      name: 'Act 3: The Resolution',
      beats: '75-100%',
      description: 'Break into Three → Finale → Final Image',
      color: '#a371f7',
      defaultVoice: 'Integration of learned truths. Voice reflects transformation—old patterns broken, new clarity. Rhythms resolve toward closing image.'
    }
  ];

  // Initialize phase evolution from props, store, or defaults
  let evolution = {};
  $: {
    const source = phaseEvolution || $voiceConfig.phase_evolution || {};
    phases.forEach(phase => {
      evolution[phase.id] = source[phase.id] || phase.defaultVoice;
    });
  }

  // Example sentences for each phase (based on common patterns)
  const exampleSentences = {
    'Act 1': [
      'The office smelled like coffee and desperation.',
      'She counted the ceiling tiles again. Thirty-two.',
      'This was the job. This was always the job.'
    ],
    'Act 2A': [
      'The puzzle pieces fell into place with satisfying clicks.',
      'For the first time in months, the weight on her shoulders felt manageable.',
      'She was good at this. Better than good.'
    ],
    'Act 2B': [
      'Nothing. Nothing made sense.',
      'The walls were closing in. Every exit blocked.',
      'Trust. She had trusted—'
    ],
    'Act 3': [
      'The truth had always been there. She just hadn\'t been ready to see it.',
      'Different now. Everything different.',
      'She walked out into the morning. Behind her, the door clicked shut for the last time.'
    ]
  };

  function handlePhaseChange(phaseId, value) {
    evolution[phaseId] = value;
    evolution = evolution; // Trigger reactivity
  }

  function saveEvolution() {
    $voiceConfig = {
      ...$voiceConfig,
      phase_evolution: { ...evolution }
    };
    dispatch('save', { evolution });
  }

  function resetToDefaults() {
    phases.forEach(phase => {
      evolution[phase.id] = phase.defaultVoice;
    });
    evolution = evolution;
  }
</script>

<div class="evolution-container">
  <div class="evolution-header">
    <div class="header-content">
      <h3 class="evolution-title">Voice Phase Evolution</h3>
      <p class="evolution-desc">Define how your voice transforms through the story arc</p>
    </div>
    {#if editable}
      <div class="header-actions">
        <button class="action-btn" on:click={resetToDefaults} title="Reset to defaults">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 12a9 9 0 109-9 9.75 9.75 0 00-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
          </svg>
        </button>
        <button class="action-btn primary" on:click={saveEvolution} title="Save changes">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
        </button>
      </div>
    {/if}
  </div>

  <!-- Visual Timeline -->
  <div class="timeline">
    <div class="timeline-track">
      {#each phases as phase, i}
        <div
          class="timeline-segment"
          style="--phase-color: {phase.color}; flex: {i === 0 || i === 3 ? 1 : 1.5}"
        >
          <div class="segment-marker"></div>
          <span class="segment-label">{phase.beats}</span>
        </div>
      {/each}
      <div class="timeline-end"></div>
    </div>
    <div class="timeline-labels">
      <span>Opening Image</span>
      <span>Midpoint</span>
      <span>All Is Lost</span>
      <span>Final Image</span>
    </div>
  </div>

  <!-- Phase Cards -->
  <div class="phase-cards">
    {#each phases as phase}
      <div class="phase-card" style="--phase-color: {phase.color}">
        <div class="phase-header">
          <div class="phase-indicator"></div>
          <div class="phase-info">
            <span class="phase-name">{phase.name}</span>
            <span class="phase-beats">{phase.description}</span>
          </div>
        </div>

        <div class="phase-content">
          {#if editable}
            <textarea
              class="phase-input"
              placeholder="Describe how the voice should sound in this phase..."
              value={evolution[phase.id]}
              on:input={(e) => handlePhaseChange(phase.id, e.target.value)}
              rows="3"
            ></textarea>
          {:else}
            <p class="phase-text">{evolution[phase.id]}</p>
          {/if}
        </div>

        <!-- Example Sentences -->
        <details class="phase-examples">
          <summary>Example sentences</summary>
          <div class="examples-content">
            {#each exampleSentences[phase.id] as example}
              <p class="example-sentence">"{example}"</p>
            {/each}
          </div>
        </details>
      </div>
    {/each}
  </div>

  <!-- Voice Characteristics Legend -->
  <div class="characteristics-legend">
    <h4 class="legend-title">Voice Characteristics by Phase</h4>
    <div class="characteristics-grid">
      <div class="characteristic">
        <span class="char-label">Sentence Length</span>
        <div class="char-bar">
          <span class="bar-segment" style="width: 20%; background: #58a6ff">Short</span>
          <span class="bar-segment" style="width: 35%; background: #3fb950">Expanding</span>
          <span class="bar-segment" style="width: 25%; background: #d29922">Variable</span>
          <span class="bar-segment" style="width: 20%; background: #a371f7">Resolved</span>
        </div>
      </div>
      <div class="characteristic">
        <span class="char-label">Emotional Register</span>
        <div class="char-bar">
          <span class="bar-segment" style="width: 20%; background: #58a6ff">Grounded</span>
          <span class="bar-segment" style="width: 35%; background: #3fb950">Building</span>
          <span class="bar-segment" style="width: 25%; background: #d29922">Crisis</span>
          <span class="bar-segment" style="width: 20%; background: #a371f7">Clarity</span>
        </div>
      </div>
      <div class="characteristic">
        <span class="char-label">Metaphor Density</span>
        <div class="char-bar">
          <span class="bar-segment" style="width: 20%; background: #58a6ff">Sparse</span>
          <span class="bar-segment" style="width: 35%; background: #3fb950">Rich</span>
          <span class="bar-segment" style="width: 25%; background: #d29922">Dark</span>
          <span class="bar-segment" style="width: 20%; background: #a371f7">Integrated</span>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .evolution-container {
    display: flex;
    flex-direction: column;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
  }

  .evolution-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
  }

  .evolution-title {
    margin: 0 0 var(--space-1, 4px) 0;
    font-size: var(--text-md, 14px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .evolution-desc {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .header-actions {
    display: flex;
    gap: var(--space-1, 4px);
  }

  .action-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    color: var(--text-secondary, #8b949e);
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .action-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .action-btn.primary {
    background: var(--accent-cyan, #58a6ff);
    border-color: var(--accent-cyan, #58a6ff);
    color: var(--bg-primary, #0f1419);
  }

  .action-btn.primary:hover {
    filter: brightness(1.1);
  }

  .action-btn svg {
    width: 16px;
    height: 16px;
  }

  /* Timeline */
  .timeline {
    padding: var(--space-3, 12px) 0;
  }

  .timeline-track {
    display: flex;
    align-items: center;
    height: 8px;
    background: var(--bg-tertiary, #242d38);
    border-radius: 4px;
    overflow: hidden;
  }

  .timeline-segment {
    position: relative;
    height: 100%;
    background: var(--phase-color);
    opacity: 0.7;
    transition: opacity 0.2s ease;
  }

  .timeline-segment:hover {
    opacity: 1;
  }

  .segment-marker {
    position: absolute;
    left: 0;
    top: -4px;
    width: 2px;
    height: 16px;
    background: var(--phase-color);
  }

  .segment-label {
    position: absolute;
    left: 4px;
    top: 12px;
    font-size: 9px;
    color: var(--text-muted, #6e7681);
    white-space: nowrap;
  }

  .timeline-end {
    width: 2px;
    height: 16px;
    background: var(--text-muted, #6e7681);
    margin-top: -4px;
  }

  .timeline-labels {
    display: flex;
    justify-content: space-between;
    margin-top: var(--space-4, 16px);
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  /* Phase Cards */
  .phase-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3, 12px);
  }

  .phase-card {
    display: flex;
    flex-direction: column;
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    overflow: hidden;
  }

  .phase-header {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-3, 12px);
    background: var(--bg-elevated, #2d3640);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .phase-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: var(--phase-color);
    flex-shrink: 0;
  }

  .phase-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .phase-name {
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .phase-beats {
    font-size: 10px;
    color: var(--text-muted, #6e7681);
  }

  .phase-content {
    padding: var(--space-3, 12px);
    flex: 1;
  }

  .phase-input {
    width: 100%;
    padding: var(--space-2, 8px);
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-sm, 4px);
    font-size: var(--text-sm, 12px);
    color: var(--text-primary, #e6edf3);
    font-family: inherit;
    resize: vertical;
    line-height: 1.5;
  }

  .phase-input:focus {
    outline: none;
    border-color: var(--phase-color);
  }

  .phase-text {
    margin: 0;
    font-size: var(--text-sm, 12px);
    line-height: 1.5;
    color: var(--text-secondary, #8b949e);
  }

  /* Examples */
  .phase-examples {
    border-top: 1px solid var(--border, #2d3a47);
  }

  .phase-examples summary {
    padding: var(--space-2, 8px) var(--space-3, 12px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .phase-examples summary:hover {
    color: var(--text-secondary, #8b949e);
  }

  .examples-content {
    padding: 0 var(--space-3, 12px) var(--space-2, 8px);
  }

  .example-sentence {
    margin: 0 0 var(--space-1, 4px) 0;
    font-family: 'Merriweather', Georgia, serif;
    font-size: 11px;
    font-style: italic;
    color: var(--text-secondary, #8b949e);
    line-height: 1.5;
  }

  /* Characteristics Legend */
  .characteristics-legend {
    padding: var(--space-3, 12px);
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-md, 6px);
  }

  .legend-title {
    margin: 0 0 var(--space-3, 12px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .characteristics-grid {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .characteristic {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .char-label {
    width: 120px;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
    flex-shrink: 0;
  }

  .char-bar {
    flex: 1;
    display: flex;
    height: 20px;
    border-radius: 4px;
    overflow: hidden;
    background: var(--bg-secondary, #1a2027);
  }

  .bar-segment {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    color: var(--bg-primary, #0f1419);
    font-weight: var(--font-medium, 500);
    white-space: nowrap;
    overflow: hidden;
  }

  /* Responsive */
  @media (max-width: 800px) {
    .phase-cards {
      grid-template-columns: 1fr;
    }
  }
</style>
