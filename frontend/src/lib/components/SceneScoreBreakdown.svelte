<!--
  SceneScoreBreakdown.svelte - Detailed Score Analysis

  Displays the full 100-point scoring breakdown:
  - Voice Authenticity (30 pts)
  - Character Consistency (20 pts)
  - Metaphor Discipline (20 pts)
  - Anti-Pattern Compliance (15 pts)
  - Phase Appropriateness (15 pts)

  Each category shows detailed feedback and specific issues.
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { currentSceneAnalysis } from '$lib/stores';

  const dispatch = createEventDispatcher();

  // Props
  export let analysis = null;

  // Use props or store
  $: displayAnalysis = analysis || $currentSceneAnalysis;

  // Score categories with full configuration
  const categories = [
    {
      key: 'voice_authenticity',
      label: 'Voice Authenticity',
      weight: 30,
      color: '#d4a574',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path></svg>`,
      description: 'Consistency with established voice profile and Gold Standard'
    },
    {
      key: 'character_consistency',
      label: 'Character Consistency',
      weight: 20,
      color: '#a371f7',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
      description: 'Alignment with character psychology and arc progression'
    },
    {
      key: 'metaphor_discipline',
      label: 'Metaphor Discipline',
      weight: 20,
      color: '#58a6ff',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z"></path></svg>`,
      description: 'Appropriate domain usage without saturation'
    },
    {
      key: 'anti_pattern_compliance',
      label: 'Anti-Pattern Compliance',
      weight: 15,
      color: '#3fb950',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      description: 'Avoidance of zero-tolerance violations'
    },
    {
      key: 'phase_appropriateness',
      label: 'Phase Appropriateness',
      weight: 15,
      color: '#d29922',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
      description: 'Voice evolution matching story phase'
    }
  ];

  // Get score tier
  function getScoreTier(score, max) {
    const percentage = (score / max) * 100;
    if (percentage >= 95) return { label: 'Gold', color: '#d4a574' };
    if (percentage >= 90) return { label: 'Excellent', color: '#3fb950' };
    if (percentage >= 85) return { label: 'Strong', color: '#58a6ff' };
    if (percentage >= 80) return { label: 'Good', color: '#d29922' };
    if (percentage >= 75) return { label: 'Acceptable', color: '#8b949e' };
    return { label: 'Needs Work', color: '#f85149' };
  }

  // Get total tier
  function getTotalTier(score) {
    if (score >= 95) return { label: 'Gold Standard', color: '#d4a574' };
    if (score >= 90) return { label: 'Excellent', color: '#3fb950' };
    if (score >= 85) return { label: 'Strong', color: '#58a6ff' };
    if (score >= 80) return { label: 'Good', color: '#d29922' };
    if (score >= 75) return { label: 'Acceptable', color: '#8b949e' };
    if (score >= 70) return { label: 'Needs Work', color: '#f85149' };
    return { label: 'Regenerate', color: '#484f58' };
  }

  // Get enhancement recommendation
  function getRecommendation(score) {
    if (score >= 85) return 'action_prompt';
    if (score >= 70) return 'six_pass';
    return 'rewrite';
  }

  // Close handler
  function close() {
    dispatch('close');
  }

  // Enhance action
  function enhance() {
    dispatch('enhance', {
      mode: getRecommendation(displayAnalysis?.total_score || 0),
      analysis: displayAnalysis
    });
  }
</script>

<div class="score-breakdown">
  <!-- Header -->
  <div class="header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      </div>
      <div>
        <h2>Score Analysis</h2>
        <p class="subtitle">100-point rubric breakdown</p>
      </div>
    </div>
    <button class="close-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>

  {#if displayAnalysis}
    {@const totalTier = getTotalTier(displayAnalysis.total_score)}

    <!-- Total Score -->
    <div class="total-score-section" style="--tier-color: {totalTier.color}">
      <div class="total-score-circle">
        <span class="total-value">{displayAnalysis.total_score}</span>
        <span class="total-max">/100</span>
      </div>
      <div class="total-info">
        <span class="total-tier">{totalTier.label}</span>
        <span class="total-recommendation">
          {#if displayAnalysis.enhancement_mode === 'action_prompt'}
            Ready for Action Prompt (surgical fixes)
          {:else if displayAnalysis.enhancement_mode === 'six_pass'}
            Needs 6-Pass Enhancement
          {:else}
            Consider regenerating
          {/if}
        </span>
      </div>
    </div>

    <!-- Categories -->
    <div class="content">
      <div class="categories-list">
        {#each categories as category}
          {@const score = displayAnalysis.scores?.[category.key] || 0}
          {@const tier = getScoreTier(score, category.weight)}
          {@const percentage = (score / category.weight) * 100}
          {@const details = displayAnalysis.details?.[category.key.split('_')[0]] || {}}

          <div class="category-card" style="--category-color: {category.color}">
            <div class="category-header">
              <div class="category-icon">
                {@html category.icon}
              </div>
              <div class="category-info">
                <h4>{category.label}</h4>
                <span class="category-description">{category.description}</span>
              </div>
              <div class="category-score">
                <span class="score-value" style="color: {tier.color}">{score}</span>
                <span class="score-max">/{category.weight}</span>
              </div>
            </div>

            <div class="score-bar">
              <div class="score-fill" style="width: {percentage}%; background: {category.color}"></div>
            </div>

            <!-- Category Details -->
            {#if category.key === 'voice_authenticity' && details.tests}
              <div class="category-details">
                <span class="details-label">Voice Tests:</span>
                <div class="tests-list">
                  {#each details.tests as test}
                    <div class="test-item" class:passed={test.score >= 80}>
                      <span class="test-name">{test.name}</span>
                      <span class="test-score">{test.score}%</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            {#if category.key === 'character_consistency' && (details.issues?.length || details.strengths?.length)}
              <div class="category-details">
                {#if details.strengths?.length}
                  <div class="feedback-section">
                    <span class="feedback-label success">Strengths</span>
                    <ul>
                      {#each details.strengths as strength}
                        <li class="success">{strength}</li>
                      {/each}
                    </ul>
                  </div>
                {/if}
                {#if details.issues?.length}
                  <div class="feedback-section">
                    <span class="feedback-label warning">Issues</span>
                    <ul>
                      {#each details.issues as issue}
                        <li class="warning">{issue}</li>
                      {/each}
                    </ul>
                  </div>
                {/if}
              </div>
            {/if}

            {#if category.key === 'metaphor_discipline' && details.domains}
              <div class="category-details">
                <span class="details-label">Domain Usage:</span>
                <div class="domains-grid">
                  {#each Object.entries(details.domains || {}) as [domain, count]}
                    <div class="domain-item">
                      <span class="domain-name">{domain}</span>
                      <span class="domain-count">{count}</span>
                    </div>
                  {/each}
                </div>
                {#if details.violations?.length}
                  <div class="violations-list">
                    <span class="details-label error">Violations:</span>
                    {#each details.violations as violation}
                      <span class="violation">{violation}</span>
                    {/each}
                  </div>
                {/if}
              </div>
            {/if}

            {#if category.key === 'anti_pattern_compliance' && details.found?.length}
              <div class="category-details">
                <span class="details-label error">Violations Found:</span>
                <div class="violations-list">
                  {#each details.found as violation}
                    <div class="violation-item">
                      <span class="violation-pattern">{violation.pattern}</span>
                      <span class="violation-line">Line {violation.line}</span>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            {#if category.key === 'phase_appropriateness' && details.current}
              <div class="category-details">
                <div class="phase-info">
                  <span class="phase-label">Current Phase:</span>
                  <span class="phase-value">{details.current}</span>
                </div>
                <div class="phase-info">
                  <span class="phase-label">Appropriateness:</span>
                  <span class="phase-value">{details.appropriateness}</span>
                </div>
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Recommendation -->
      {#if displayAnalysis.recommendation}
        <div class="recommendation-section">
          <h4>Recommendation</h4>
          <p>{displayAnalysis.recommendation}</p>
        </div>
      {/if}
    </div>

    <!-- Actions -->
    <div class="actions">
      <button class="secondary-btn" on:click={close}>Close</button>
      <button class="primary-btn" on:click={enhance}>
        {#if displayAnalysis.enhancement_mode === 'action_prompt'}
          Generate Action Prompt
        {:else if displayAnalysis.enhancement_mode === 'six_pass'}
          Start 6-Pass Enhancement
        {:else}
          Return to Generation
        {/if}
      </button>
    </div>

  {:else}
    <div class="empty-state">
      <p>No analysis data available</p>
      <p class="hint">Run scene analysis to see detailed score breakdown</p>
    </div>
  {/if}
</div>

<style>
  .score-breakdown {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-height: 85vh;
    background: var(--bg-secondary, #1a2027);
    border-radius: var(--radius-lg, 8px);
    overflow: hidden;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: var(--space-3, 12px);
  }

  .header-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--accent-cyan-muted, rgba(88, 166, 255, 0.2));
    border-radius: var(--radius-md, 6px);
    color: var(--accent-cyan, #58a6ff);
  }

  .header-icon svg {
    width: 24px;
    height: 24px;
  }

  .header h2 {
    margin: 0;
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .subtitle {
    margin: 0;
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #8b949e);
  }

  .close-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: none;
    border-radius: var(--radius-sm, 4px);
    color: var(--text-muted, #6e7681);
    cursor: pointer;
  }

  .close-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .close-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Total Score Section */
  .total-score-section {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-bottom: 1px solid var(--border, #2d3a47);
  }

  .total-score-circle {
    display: flex;
    align-items: baseline;
    justify-content: center;
    width: 100px;
    height: 100px;
    background: color-mix(in srgb, var(--tier-color) 20%, transparent);
    border: 3px solid var(--tier-color);
    border-radius: 50%;
  }

  .total-value {
    font-size: var(--text-2xl, 24px);
    font-weight: var(--font-bold, 700);
    color: var(--tier-color);
  }

  .total-max {
    font-size: var(--text-sm, 12px);
    color: var(--text-muted, #6e7681);
  }

  .total-info {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .total-tier {
    font-size: var(--text-xl, 18px);
    font-weight: var(--font-bold, 700);
    color: var(--tier-color);
  }

  .total-recommendation {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  /* Content */
  .content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-4, 16px);
  }

  .categories-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
  }

  .category-card {
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-3, 12px);
  }

  .category-header {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3, 12px);
    margin-bottom: var(--space-3, 12px);
  }

  .category-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--category-color) 20%, transparent);
    border-radius: var(--radius-md, 6px);
    color: var(--category-color);
    flex-shrink: 0;
  }

  .category-icon :global(svg) {
    width: 18px;
    height: 18px;
  }

  .category-info {
    flex: 1;
  }

  .category-info h4 {
    margin: 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .category-description {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .category-score {
    display: flex;
    align-items: baseline;
    gap: 2px;
  }

  .score-value {
    font-size: var(--text-lg, 16px);
    font-weight: var(--font-bold, 700);
  }

  .score-max {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  .score-bar {
    height: 6px;
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-full, 9999px);
    overflow: hidden;
    margin-bottom: var(--space-3, 12px);
  }

  .score-fill {
    height: 100%;
    border-radius: var(--radius-full, 9999px);
    transition: width var(--transition-normal, 200ms ease);
  }

  /* Category Details */
  .category-details {
    background: var(--bg-input, #161b22);
    border-radius: var(--radius-sm, 4px);
    padding: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
  }

  .details-label {
    display: block;
    margin-bottom: var(--space-1, 4px);
    font-weight: var(--font-medium, 500);
    color: var(--text-muted, #6e7681);
  }

  .details-label.error {
    color: var(--error, #f85149);
  }

  .tests-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .test-item {
    display: flex;
    justify-content: space-between;
    padding: 2px 4px;
    border-radius: var(--radius-sm, 4px);
  }

  .test-item.passed {
    background: var(--success-muted, rgba(63, 185, 80, 0.1));
  }

  .test-name {
    color: var(--text-secondary, #8b949e);
  }

  .test-score {
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .feedback-section {
    margin-bottom: var(--space-2, 8px);
  }

  .feedback-label {
    font-size: 10px;
    font-weight: var(--font-semibold, 600);
    text-transform: uppercase;
  }

  .feedback-label.success {
    color: var(--success, #3fb950);
  }

  .feedback-label.warning {
    color: var(--warning, #d29922);
  }

  .feedback-section ul {
    margin: var(--space-1, 4px) 0 0 0;
    padding-left: var(--space-4, 16px);
  }

  .feedback-section li {
    color: var(--text-secondary, #8b949e);
    margin-bottom: 2px;
  }

  .feedback-section li.success::marker {
    color: var(--success, #3fb950);
  }

  .feedback-section li.warning::marker {
    color: var(--warning, #d29922);
  }

  .domains-grid {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-1, 4px);
    margin-bottom: var(--space-2, 8px);
  }

  .domain-item {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    padding: 2px 6px;
    background: var(--bg-tertiary, #242d38);
    border-radius: var(--radius-full, 9999px);
  }

  .domain-name {
    color: var(--text-secondary, #8b949e);
  }

  .domain-count {
    font-weight: var(--font-semibold, 600);
    color: var(--category-color);
  }

  .violations-list {
    margin-top: var(--space-2, 8px);
  }

  .violation-item {
    display: flex;
    justify-content: space-between;
    padding: 2px 4px;
    background: var(--error-muted, rgba(248, 81, 73, 0.1));
    border-radius: var(--radius-sm, 4px);
    margin-bottom: var(--space-1, 4px);
  }

  .violation-pattern {
    color: var(--error, #f85149);
  }

  .violation-line {
    color: var(--text-muted, #6e7681);
  }

  .violation {
    display: block;
    color: var(--error, #f85149);
    margin-bottom: 2px;
  }

  .phase-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: var(--space-1, 4px);
  }

  .phase-label {
    color: var(--text-muted, #6e7681);
  }

  .phase-value {
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  /* Recommendation Section */
  .recommendation-section {
    margin-top: var(--space-4, 16px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-md, 6px);
  }

  .recommendation-section h4 {
    margin: 0 0 var(--space-2, 8px) 0;
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
  }

  .recommendation-section p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
    line-height: var(--leading-relaxed, 1.7);
  }

  /* Empty State */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: var(--space-8, 32px);
    text-align: center;
  }

  .empty-state p {
    margin: 0;
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #8b949e);
  }

  .empty-state .hint {
    margin-top: var(--space-2, 8px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #6e7681);
  }

  /* Actions */
  .actions {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3, 12px);
    padding: var(--space-4, 16px);
    background: var(--bg-tertiary, #242d38);
    border-top: 1px solid var(--border, #2d3a47);
  }

  .secondary-btn,
  .primary-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
    padding: var(--space-2, 8px) var(--space-4, 16px);
    border-radius: var(--radius-md, 6px);
    font-size: var(--text-sm, 12px);
    font-weight: var(--font-medium, 500);
    cursor: pointer;
    transition: all var(--transition-fast, 100ms ease);
  }

  .secondary-btn {
    background: transparent;
    border: 1px solid var(--border, #2d3a47);
    color: var(--text-secondary, #8b949e);
  }

  .secondary-btn:hover {
    background: var(--bg-elevated, #2d3640);
    color: var(--text-primary, #e6edf3);
  }

  .primary-btn {
    background: var(--accent-gold, #d4a574);
    border: none;
    color: var(--bg-primary, #0f1419);
  }

  .primary-btn:hover {
    background: var(--accent-gold-hover, #e0b585);
  }
</style>
