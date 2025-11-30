<!--
  ScoreDisplay.svelte - Scene Analysis Score Visualization

  Displays the 100-point scoring rubric breakdown for a scene:
  - Total score with letter grade
  - 5-category breakdown with visual bars
  - Violations list with penalty amounts
  - Enhancement recommendation

  Part of Track A: Minimal Testing Path
-->
<script>
  /**
   * @typedef {Object} SubcategoryScore
   * @property {number} score
   * @property {number} max_score
   * @property {string} notes
   * @property {string[]} violations
   */

  /**
   * @typedef {Object} CategoryScore
   * @property {number} score
   * @property {number} max
   * @property {Object.<string, SubcategoryScore>} subcategories
   */

  /**
   * @typedef {Object} PatternViolation
   * @property {string} pattern_name
   * @property {string} pattern_type - "zero_tolerance" or "formulaic"
   * @property {string} description
   * @property {string} matched_text
   * @property {number} line_number
   * @property {number} penalty
   */

  /**
   * @typedef {Object} SceneAnalysisResult
   * @property {string} scene_id
   * @property {number} total_score
   * @property {string} grade
   * @property {Object.<string, CategoryScore>} categories
   * @property {PatternViolation[]} violations
   * @property {boolean} enhancement_needed
   * @property {string} recommended_mode
   * @property {string|null} action_prompt
   */

  /** @type {SceneAnalysisResult|null} */
  export let analysis = null;

  /** @type {boolean} Show compact view (just score and grade) */
  export let compact = false;

  /** @type {boolean} Show violations section */
  export let showViolations = true;

  // Category display names
  const CATEGORY_LABELS = {
    voice_authenticity: 'Voice Authenticity',
    character_consistency: 'Character Consistency',
    metaphor_discipline: 'Metaphor Discipline',
    anti_pattern_compliance: 'Anti-Pattern Compliance',
    phase_appropriateness: 'Phase Appropriateness'
  };

  // Category colors (matching the cyber-noir theme)
  const CATEGORY_COLORS = {
    voice_authenticity: '#58a6ff',      // Cyan
    character_consistency: '#a371f7',   // Purple
    metaphor_discipline: '#d4a574',     // Gold
    anti_pattern_compliance: '#f85149', // Red (for penalties)
    phase_appropriateness: '#3fb950'    // Green
  };

  // Get color based on score percentage
  function getScoreColor(score) {
    if (score >= 85) return 'var(--success, #3fb950)';
    if (score >= 70) return 'var(--warning, #d29922)';
    return 'var(--error, #f85149)';
  }

  // Get grade color
  function getGradeColor(grade) {
    if (grade.startsWith('A')) return 'var(--success, #3fb950)';
    if (grade.startsWith('B')) return 'var(--warning, #d29922)';
    if (grade.startsWith('C')) return 'var(--accent-gold, #d4a574)';
    return 'var(--error, #f85149)';
  }

  // Format recommended mode for display
  function formatMode(mode) {
    const modes = {
      'none': 'No Enhancement Needed',
      'action_prompt': 'Action Prompt (Surgical Fixes)',
      'six_pass': '6-Pass Enhancement',
      'rewrite': 'Needs Rewrite'
    };
    return modes[mode] || mode;
  }

  // Calculate category percentage
  function getCategoryPercent(category) {
    if (!category || !category.max) return 0;
    return Math.round((category.score / category.max) * 100);
  }
</script>

{#if analysis}
  <div class="score-display" class:compact>
    <!-- Main Score Circle -->
    <div class="score-header">
      <div class="score-circle" style="--score-color: {getScoreColor(analysis.total_score)}">
        <span class="grade" style="color: {getGradeColor(analysis.grade)}">{analysis.grade}</span>
        <span class="points">{analysis.total_score}<span class="max">/100</span></span>
      </div>

      {#if !compact}
        <div class="score-summary">
          <div class="recommendation" class:needs-work={analysis.enhancement_needed}>
            <span class="rec-label">Recommendation:</span>
            <span class="rec-value">{formatMode(analysis.recommended_mode)}</span>
          </div>
          {#if analysis.violations.length > 0}
            <div class="violation-summary">
              <span class="violation-count">{analysis.violations.length}</span>
              <span class="violation-label">issues found</span>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <!-- Category Breakdown -->
    {#if !compact}
      <div class="categories">
        {#each Object.entries(analysis.categories) as [key, category]}
          <div class="category">
            <div class="category-header">
              <span class="category-name">{CATEGORY_LABELS[key] || key}</span>
              <span class="category-score">{category.score}/{category.max}</span>
            </div>
            <div class="category-bar">
              <div
                class="bar-fill"
                style="
                  width: {getCategoryPercent(category)}%;
                  background: {CATEGORY_COLORS[key] || 'var(--accent-cyan)'};
                "
              ></div>
            </div>
            {#if category.subcategories}
              <div class="subcategories">
                {#each Object.entries(category.subcategories) as [subKey, sub]}
                  <div class="subcategory">
                    <span class="sub-name">{subKey.replace(/_/g, ' ')}</span>
                    <span class="sub-score">{sub.score}/{sub.max_score}</span>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>

      <!-- Violations Section -->
      {#if showViolations && analysis.violations.length > 0}
        <div class="violations">
          <h4 class="violations-header">
            Issues Found ({analysis.violations.length})
          </h4>
          <div class="violation-list">
            {#each analysis.violations as violation}
              <div class="violation {violation.pattern_type}">
                <div class="violation-top">
                  <span class="violation-name">{violation.pattern_name}</span>
                  <span class="violation-penalty">-{violation.penalty}</span>
                </div>
                <div class="violation-text">"{violation.matched_text}"</div>
                <div class="violation-location">Line {violation.line_number}</div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- Action Prompt Preview (if any) -->
      {#if analysis.action_prompt}
        <div class="action-prompt-preview">
          <h4 class="action-header">Suggested Fixes</h4>
          <div class="action-content">
            {analysis.action_prompt.slice(0, 200)}{analysis.action_prompt.length > 200 ? '...' : ''}
          </div>
        </div>
      {/if}
    {/if}
  </div>
{:else}
  <div class="score-display empty">
    <div class="empty-state">
      <span class="empty-icon">📊</span>
      <span class="empty-text">No analysis available</span>
    </div>
  </div>
{/if}

<style>
  .score-display {
    background: var(--bg-secondary, #1a2027);
    border: 1px solid var(--border, #2d3a47);
    border-radius: var(--radius-lg, 8px);
    padding: var(--space-4, 16px);
  }

  .score-display.compact {
    padding: var(--space-2, 8px) var(--space-3, 12px);
  }

  /* Score Header */
  .score-header {
    display: flex;
    align-items: center;
    gap: var(--space-4, 16px);
    margin-bottom: var(--space-4, 16px);
  }

  .compact .score-header {
    margin-bottom: 0;
  }

  .score-circle {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: var(--bg-tertiary, #252d38);
    border: 3px solid var(--score-color, var(--accent-cyan));
    flex-shrink: 0;
  }

  .compact .score-circle {
    width: 48px;
    height: 48px;
    border-width: 2px;
  }

  .grade {
    font-size: var(--text-xl, 20px);
    font-weight: var(--font-bold, 700);
    line-height: 1;
  }

  .compact .grade {
    font-size: var(--text-base, 14px);
  }

  .points {
    font-size: var(--text-sm, 12px);
    color: var(--text-secondary, #c9d1d9);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  .compact .points {
    font-size: var(--text-xs, 10px);
  }

  .max {
    color: var(--text-muted, #8b949e);
    font-size: 0.8em;
  }

  .score-summary {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
  }

  .recommendation {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .rec-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .rec-value {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .recommendation.needs-work .rec-value {
    color: var(--warning, #d29922);
  }

  .violation-summary {
    display: flex;
    align-items: center;
    gap: var(--space-2, 8px);
  }

  .violation-count {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 20px;
    height: 20px;
    padding: 0 6px;
    background: var(--error-bg, rgba(248, 81, 73, 0.15));
    border-radius: 10px;
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--error, #f85149);
  }

  .violation-label {
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  /* Categories */
  .categories {
    display: flex;
    flex-direction: column;
    gap: var(--space-3, 12px);
    margin-bottom: var(--space-4, 16px);
  }

  .category {
    display: flex;
    flex-direction: column;
    gap: var(--space-1, 4px);
  }

  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .category-name {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-medium, 500);
    color: var(--text-primary, #e6edf3);
  }

  .category-score {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--text-secondary, #c9d1d9);
  }

  .category-bar {
    height: 6px;
    background: var(--bg-tertiary, #252d38);
    border-radius: 3px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }

  .subcategories {
    display: flex;
    flex-wrap: wrap;
    gap: var(--space-2, 8px);
    margin-top: var(--space-1, 4px);
    padding-left: var(--space-2, 8px);
  }

  .subcategory {
    display: flex;
    align-items: center;
    gap: var(--space-1, 4px);
    font-size: var(--text-xs, 11px);
    color: var(--text-muted, #8b949e);
  }

  .sub-name {
    text-transform: capitalize;
  }

  .sub-score {
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--text-secondary, #c9d1d9);
  }

  /* Violations */
  .violations {
    border-top: 1px solid var(--border, #2d3a47);
    padding-top: var(--space-3, 12px);
    margin-bottom: var(--space-4, 16px);
  }

  .violations-header {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-semibold, 600);
    color: var(--error, #f85149);
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .violation-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2, 8px);
    max-height: 200px;
    overflow-y: auto;
  }

  .violation {
    background: var(--bg-tertiary, #252d38);
    border-radius: var(--radius-md, 6px);
    padding: var(--space-2, 8px);
    border-left: 3px solid var(--error, #f85149);
  }

  .violation.formulaic {
    border-left-color: var(--warning, #d29922);
  }

  .violation-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-1, 4px);
  }

  .violation-name {
    font-size: var(--text-xs, 11px);
    font-weight: var(--font-semibold, 600);
    color: var(--text-primary, #e6edf3);
    text-transform: capitalize;
  }

  .violation-penalty {
    font-size: var(--text-xs, 11px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    color: var(--error, #f85149);
    font-weight: var(--font-semibold, 600);
  }

  .formulaic .violation-penalty {
    color: var(--warning, #d29922);
  }

  .violation-text {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #c9d1d9);
    font-style: italic;
    margin-bottom: var(--space-1, 4px);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .violation-location {
    font-size: 10px;
    color: var(--text-muted, #8b949e);
    font-family: var(--font-mono, 'SF Mono', monospace);
  }

  /* Action Prompt Preview */
  .action-prompt-preview {
    border-top: 1px solid var(--border, #2d3a47);
    padding-top: var(--space-3, 12px);
  }

  .action-header {
    font-size: var(--text-sm, 13px);
    font-weight: var(--font-semibold, 600);
    color: var(--accent-cyan, #58a6ff);
    margin: 0 0 var(--space-2, 8px) 0;
  }

  .action-content {
    font-size: var(--text-xs, 11px);
    color: var(--text-secondary, #c9d1d9);
    background: var(--bg-tertiary, #252d38);
    padding: var(--space-2, 8px);
    border-radius: var(--radius-md, 6px);
    font-family: var(--font-mono, 'SF Mono', monospace);
    white-space: pre-wrap;
  }

  /* Empty State */
  .score-display.empty {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2, 8px);
    color: var(--text-muted, #8b949e);
  }

  .empty-icon {
    font-size: 24px;
    opacity: 0.5;
  }

  .empty-text {
    font-size: var(--text-sm, 13px);
  }

  /* Scrollbar */
  .violation-list::-webkit-scrollbar {
    width: 4px;
  }

  .violation-list::-webkit-scrollbar-track {
    background: transparent;
  }

  .violation-list::-webkit-scrollbar-thumb {
    background: var(--border, #2d3a47);
    border-radius: 2px;
  }
</style>
