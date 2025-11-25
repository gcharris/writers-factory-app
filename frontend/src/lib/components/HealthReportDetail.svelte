<!--
  HealthReportDetail.svelte - Detailed Health Report View

  Phase 5 Track 3 Phase 4: Graph Health UI

  Displays comprehensive health report details:
  - Overall score with tier indicator
  - Report metadata (scope, timestamp, ID)
  - Warnings grouped by severity (errors, warnings, info)
  - Each warning shows:
    - Type and category
    - Message and recommendation
    - Affected chapters/scenes/characters
    - Additional data details
  - Export options (markdown, JSON)
-->
<script>
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // Props
  export let report = null;
  export let reportId = '';

  // State
  let isLoading = false;
  let isExporting = false;
  let errorMsg = '';
  let expandedWarnings = new Set();

  // Load report if only ID provided
  $: if (reportId && !report) {
    loadReport(reportId);
  }

  // Group warnings by severity
  $: groupedWarnings = report ? groupBySeverity(report.warnings) : { errors: [], warnings: [], info: [] };

  // Load report by ID
  async function loadReport(id) {
    isLoading = true;
    errorMsg = '';

    try {
      const response = await apiClient.getHealthReport(id);
      report = response.report;
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Failed to load report';
    } finally {
      isLoading = false;
    }
  }

  // Group warnings by severity
  function groupBySeverity(warnings) {
    return {
      errors: warnings.filter(w => w.severity === 'error'),
      warnings: warnings.filter(w => w.severity === 'warning'),
      info: warnings.filter(w => w.severity === 'info')
    };
  }

  // Get score tier
  function getScoreTier(score) {
    if (score >= 90) return { label: 'Excellent', color: '#3fb950', bg: 'rgba(63, 185, 80, 0.1)' };
    if (score >= 80) return { label: 'Good', color: '#58a6ff', bg: 'rgba(88, 166, 255, 0.1)' };
    if (score >= 70) return { label: 'Fair', color: '#d29922', bg: 'rgba(210, 153, 34, 0.1)' };
    if (score >= 60) return { label: 'Needs Work', color: '#f85149', bg: 'rgba(248, 81, 73, 0.1)' };
    return { label: 'Critical', color: '#da3633', bg: 'rgba(218, 54, 51, 0.1)' };
  }

  // Get warning type display info
  function getWarningTypeInfo(type) {
    const typeMap = {
      'PACING_PLATEAU': { label: 'Pacing Plateau', category: 'Structural', icon: 'activity' },
      'BEAT_DEVIATION': { label: 'Beat Deviation', category: 'Structural', icon: 'target' },
      'BEAT_PROGRESS_BEHIND': { label: 'Beat Progress Behind', category: 'Structural', icon: 'clock' },
      'BEAT_PROGRESS_AHEAD': { label: 'Beat Progress Ahead', category: 'Structural', icon: 'fast-forward' },
      'TIMELINE_ERROR': { label: 'Timeline Error', category: 'Structural', icon: 'calendar' },
      'CHARACTER_TELEPORTATION': { label: 'Character Teleportation', category: 'Structural', icon: 'map-pin' },
      'WORLD_RULES': { label: 'World Rules Violation', category: 'Structural', icon: 'globe' },
      'DROPPED_THREAD': { label: 'Dropped Thread', category: 'Structural', icon: 'link' },
      'FLAW_CHALLENGE_GAP': { label: 'Flaw Challenge Gap', category: 'Character', icon: 'alert-triangle' },
      'UNDERUTILIZED_CHARACTER': { label: 'Underutilized Character', category: 'Character', icon: 'user-x' },
      'SYMBOL_INSUFFICIENT_RECURRENCE': { label: 'Symbol Insufficient', category: 'Thematic', icon: 'repeat' },
      'SYMBOL_STATIC_MEANING': { label: 'Static Symbol', category: 'Thematic', icon: 'pause' },
      'SYMBOL_MISSING_CRITICAL_BEATS': { label: 'Symbol Missing Beats', category: 'Thematic', icon: 'x-circle' },
      'SYMBOLIC_LAYERING_WEAK': { label: 'Weak Symbolic Layering', category: 'Thematic', icon: 'layers' },
      'WEAK_THEME': { label: 'Weak Theme', category: 'Thematic', icon: 'bookmark' },
      'CHAPTER_NOT_FOUND': { label: 'Chapter Not Found', category: 'System', icon: 'file-x' }
    };

    return typeMap[type] || { label: type.replace(/_/g, ' '), category: 'Other', icon: 'alert-circle' };
  }

  // Get severity icon
  function getSeverityIcon(severity) {
    switch (severity) {
      case 'error':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
      case 'warning':
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
      default:
        return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }
  }

  // Toggle warning expansion
  function toggleWarning(index) {
    if (expandedWarnings.has(index)) {
      expandedWarnings.delete(index);
    } else {
      expandedWarnings.add(index);
    }
    expandedWarnings = expandedWarnings;
  }

  // Export report
  async function exportReport(format) {
    if (!report) return;

    isExporting = true;
    try {
      const response = await apiClient.exportHealthReport(report.report_id, format);

      if (format === 'markdown') {
        // Download as .md file
        const blob = new Blob([response.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health-report-${report.report_id.slice(0, 8)}.md`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        // Download as .json file
        const blob = new Blob([JSON.stringify(response.content, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health-report-${report.report_id.slice(0, 8)}.json`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Export failed';
    } finally {
      isExporting = false;
    }
  }

  // Format timestamp
  function formatTimestamp(iso) {
    if (!iso) return '--';
    const date = new Date(iso);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  // Close detail view
  function close() {
    dispatch('close');
  }

  // Navigate to chapter
  function navigateToChapter(chapterId) {
    dispatch('navigateToChapter', { chapterId });
  }
</script>

<div class="report-detail">
  <!-- Header -->
  <div class="detail-header">
    <button class="back-btn" on:click={close}>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="19" y1="12" x2="5" y2="12"></line>
        <polyline points="12 19 5 12 12 5"></polyline>
      </svg>
      Back
    </button>
    <div class="header-title">
      <h2>Health Report</h2>
      {#if report}
        <span class="report-id">#{report.report_id.slice(0, 8)}</span>
      {/if}
    </div>
    <div class="header-actions">
      <button class="export-btn" on:click={() => exportReport('markdown')} disabled={isExporting || !report}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        Markdown
      </button>
      <button class="export-btn" on:click={() => exportReport('json')} disabled={isExporting || !report}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        JSON
      </button>
    </div>
  </div>

  {#if isLoading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Loading report...</p>
    </div>
  {:else if !report}
    <div class="no-report">
      <p>No report data available</p>
    </div>
  {:else}
    {@const tier = getScoreTier(report.overall_score)}

    <!-- Score Overview -->
    <div class="score-overview" style="--tier-color: {tier.color}; --tier-bg: {tier.bg}">
      <div class="score-main">
        <div class="score-circle">
          <span class="score-value">{report.overall_score}</span>
          <span class="score-max">/100</span>
        </div>
        <div class="score-details">
          <span class="score-tier">{tier.label}</span>
          <span class="score-scope">{report.scope} Analysis</span>
          {#if report.chapter_id}
            <span class="scope-detail">Chapter: {report.chapter_id}</span>
          {/if}
          {#if report.act_number}
            <span class="scope-detail">Act: {report.act_number}</span>
          {/if}
        </div>
      </div>
      <div class="score-meta">
        <div class="meta-item">
          <span class="meta-label">Report ID</span>
          <span class="meta-value">{report.report_id.slice(0, 8)}...</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Generated</span>
          <span class="meta-value">{formatTimestamp(report.timestamp)}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Project</span>
          <span class="meta-value">{report.project_id.slice(0, 12)}...</span>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="summary-stats">
      <div class="stat-card error">
        <div class="stat-icon">
          {@html getSeverityIcon('error')}
        </div>
        <div class="stat-content">
          <span class="stat-value">{groupedWarnings.errors.length}</span>
          <span class="stat-label">Critical Issues</span>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon">
          {@html getSeverityIcon('warning')}
        </div>
        <div class="stat-content">
          <span class="stat-value">{groupedWarnings.warnings.length}</span>
          <span class="stat-label">Warnings</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon">
          {@html getSeverityIcon('info')}
        </div>
        <div class="stat-content">
          <span class="stat-value">{groupedWarnings.info.length}</span>
          <span class="stat-label">Notes</span>
        </div>
      </div>
    </div>

    <!-- Warnings Sections -->
    {#if groupedWarnings.errors.length > 0}
      <div class="warnings-section error">
        <h3>
          <span class="section-icon">{@html getSeverityIcon('error')}</span>
          Critical Issues ({groupedWarnings.errors.length})
        </h3>
        <div class="warnings-list">
          {#each groupedWarnings.errors as warning, i}
            {@const typeInfo = getWarningTypeInfo(warning.type)}
            {@const isExpanded = expandedWarnings.has(`error-${i}`)}
            <div class="warning-card" class:expanded={isExpanded}>
              <button class="warning-header" on:click={() => toggleWarning(`error-${i}`)}>
                <div class="warning-type">
                  <span class="type-category">{typeInfo.category}</span>
                  <span class="type-label">{typeInfo.label}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="expand-icon" class:rotated={isExpanded}>
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
              <div class="warning-message">{warning.message}</div>
              {#if isExpanded}
                <div class="warning-details">
                  {#if warning.recommendation}
                    <div class="detail-row">
                      <span class="detail-label">Recommendation:</span>
                      <span class="detail-value">{warning.recommendation}</span>
                    </div>
                  {/if}
                  {#if warning.chapters && warning.chapters.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Chapters:</span>
                      <div class="detail-chips">
                        {#each warning.chapters as chapter}
                          <button class="chip" on:click={() => navigateToChapter(chapter)}>{chapter}</button>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.scenes && warning.scenes.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Scenes:</span>
                      <div class="detail-chips">
                        {#each warning.scenes as scene}
                          <span class="chip">{scene}</span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.characters && warning.characters.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Characters:</span>
                      <div class="detail-chips">
                        {#each warning.characters as character}
                          <span class="chip">{character}</span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.data && Object.keys(warning.data).length > 0}
                    <div class="detail-data">
                      <span class="detail-label">Details:</span>
                      <pre>{JSON.stringify(warning.data, null, 2)}</pre>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if groupedWarnings.warnings.length > 0}
      <div class="warnings-section warning">
        <h3>
          <span class="section-icon">{@html getSeverityIcon('warning')}</span>
          Warnings ({groupedWarnings.warnings.length})
        </h3>
        <div class="warnings-list">
          {#each groupedWarnings.warnings as warning, i}
            {@const typeInfo = getWarningTypeInfo(warning.type)}
            {@const isExpanded = expandedWarnings.has(`warning-${i}`)}
            <div class="warning-card" class:expanded={isExpanded}>
              <button class="warning-header" on:click={() => toggleWarning(`warning-${i}`)}>
                <div class="warning-type">
                  <span class="type-category">{typeInfo.category}</span>
                  <span class="type-label">{typeInfo.label}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="expand-icon" class:rotated={isExpanded}>
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
              <div class="warning-message">{warning.message}</div>
              {#if isExpanded}
                <div class="warning-details">
                  {#if warning.recommendation}
                    <div class="detail-row">
                      <span class="detail-label">Recommendation:</span>
                      <span class="detail-value">{warning.recommendation}</span>
                    </div>
                  {/if}
                  {#if warning.chapters && warning.chapters.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Chapters:</span>
                      <div class="detail-chips">
                        {#each warning.chapters as chapter}
                          <button class="chip" on:click={() => navigateToChapter(chapter)}>{chapter}</button>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.scenes && warning.scenes.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Scenes:</span>
                      <div class="detail-chips">
                        {#each warning.scenes as scene}
                          <span class="chip">{scene}</span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.characters && warning.characters.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Characters:</span>
                      <div class="detail-chips">
                        {#each warning.characters as character}
                          <span class="chip">{character}</span>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.data && Object.keys(warning.data).length > 0}
                    <div class="detail-data">
                      <span class="detail-label">Details:</span>
                      <pre>{JSON.stringify(warning.data, null, 2)}</pre>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if groupedWarnings.info.length > 0}
      <div class="warnings-section info">
        <h3>
          <span class="section-icon">{@html getSeverityIcon('info')}</span>
          Notes ({groupedWarnings.info.length})
        </h3>
        <div class="warnings-list">
          {#each groupedWarnings.info as warning, i}
            {@const typeInfo = getWarningTypeInfo(warning.type)}
            {@const isExpanded = expandedWarnings.has(`info-${i}`)}
            <div class="warning-card" class:expanded={isExpanded}>
              <button class="warning-header" on:click={() => toggleWarning(`info-${i}`)}>
                <div class="warning-type">
                  <span class="type-category">{typeInfo.category}</span>
                  <span class="type-label">{typeInfo.label}</span>
                </div>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="expand-icon" class:rotated={isExpanded}>
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
              <div class="warning-message">{warning.message}</div>
              {#if isExpanded}
                <div class="warning-details">
                  {#if warning.recommendation}
                    <div class="detail-row">
                      <span class="detail-label">Recommendation:</span>
                      <span class="detail-value">{warning.recommendation}</span>
                    </div>
                  {/if}
                  {#if warning.chapters && warning.chapters.length > 0}
                    <div class="detail-row">
                      <span class="detail-label">Chapters:</span>
                      <div class="detail-chips">
                        {#each warning.chapters as chapter}
                          <button class="chip" on:click={() => navigateToChapter(chapter)}>{chapter}</button>
                        {/each}
                      </div>
                    </div>
                  {/if}
                  {#if warning.data && Object.keys(warning.data).length > 0}
                    <div class="detail-data">
                      <span class="detail-label">Details:</span>
                      <pre>{JSON.stringify(warning.data, null, 2)}</pre>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      </div>
    {/if}

    {#if report.warnings.length === 0}
      <div class="all-clear">
        <div class="all-clear-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <h3>All Clear!</h3>
        <p>No structural issues detected in this analysis.</p>
      </div>
    {/if}
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
  .report-detail {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    color: #e6edf3;
    min-height: 500px;
  }

  /* Header */
  .detail-header {
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
    gap: 0.75rem;
  }

  .header-title h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .report-id {
    font-size: 0.85rem;
    color: #8b949e;
    font-family: monospace;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .export-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.875rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .export-btn:hover:not(:disabled) {
    background: #30363d;
    border-color: #58a6ff;
  }

  .export-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .export-btn svg {
    width: 14px;
    height: 14px;
  }

  /* Score Overview */
  .score-overview {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    background: var(--tier-bg, rgba(63, 185, 80, 0.1));
    border: 1px solid var(--tier-color, #3fb950);
    border-radius: 10px;
    margin-bottom: 1.5rem;
  }

  .score-main {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .score-circle {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    border: 4px solid var(--tier-color, #3fb950);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.2);
  }

  .score-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--tier-color, #3fb950);
    line-height: 1;
  }

  .score-max {
    font-size: 0.85rem;
    color: #8b949e;
  }

  .score-details {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .score-tier {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--tier-color, #3fb950);
  }

  .score-scope {
    font-size: 1rem;
    color: #e6edf3;
    text-transform: capitalize;
  }

  .scope-detail {
    font-size: 0.85rem;
    color: #8b949e;
  }

  .score-meta {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    text-align: right;
  }

  .meta-item {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }

  .meta-label {
    font-size: 0.7rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .meta-value {
    font-size: 0.85rem;
    color: #e6edf3;
    font-family: monospace;
  }

  /* Summary Stats */
  .summary-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
  }

  .stat-card.error {
    border-color: rgba(248, 81, 73, 0.3);
    background: rgba(248, 81, 73, 0.05);
  }

  .stat-card.warning {
    border-color: rgba(210, 153, 34, 0.3);
    background: rgba(210, 153, 34, 0.05);
  }

  .stat-card.info {
    border-color: rgba(88, 166, 255, 0.3);
    background: rgba(88, 166, 255, 0.05);
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .stat-card.error .stat-icon :global(svg) {
    stroke: #f85149;
    width: 28px;
    height: 28px;
  }

  .stat-card.warning .stat-icon :global(svg) {
    stroke: #d29922;
    width: 28px;
    height: 28px;
  }

  .stat-card.info .stat-icon :global(svg) {
    stroke: #58a6ff;
    width: 28px;
    height: 28px;
  }

  .stat-content {
    display: flex;
    flex-direction: column;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1;
  }

  .stat-card.error .stat-value { color: #f85149; }
  .stat-card.warning .stat-value { color: #d29922; }
  .stat-card.info .stat-value { color: #58a6ff; }

  .stat-label {
    font-size: 0.8rem;
    color: #8b949e;
    margin-top: 0.25rem;
  }

  /* Warnings Sections */
  .warnings-section {
    margin-bottom: 1.5rem;
  }

  .warnings-section h3 {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 0 0 1rem;
    font-size: 1rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .section-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .warnings-section.error .section-icon :global(svg) { stroke: #f85149; }
  .warnings-section.warning .section-icon :global(svg) { stroke: #d29922; }
  .warnings-section.info .section-icon :global(svg) { stroke: #58a6ff; }

  .warnings-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .warning-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    overflow: hidden;
  }

  .warnings-section.error .warning-card {
    border-left: 3px solid #f85149;
  }

  .warnings-section.warning .warning-card {
    border-left: 3px solid #d29922;
  }

  .warnings-section.info .warning-card {
    border-left: 3px solid #58a6ff;
  }

  .warning-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 1rem;
    background: none;
    border: none;
    color: inherit;
    font: inherit;
    cursor: pointer;
    text-align: left;
  }

  .warning-header:hover {
    background: rgba(255, 255, 255, 0.02);
  }

  .warning-type {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .type-category {
    font-size: 0.7rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .type-label {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .expand-icon {
    width: 20px;
    height: 20px;
    stroke: #8b949e;
    transition: transform 0.2s ease;
  }

  .expand-icon.rotated {
    transform: rotate(180deg);
  }

  .warning-message {
    padding: 0 1rem 1rem;
    font-size: 0.9rem;
    color: #c9d1d9;
    line-height: 1.5;
  }

  .warning-details {
    padding: 1rem;
    background: rgba(0, 0, 0, 0.15);
    border-top: 1px solid #21262d;
  }

  .detail-row {
    margin-bottom: 0.75rem;
  }

  .detail-row:last-child {
    margin-bottom: 0;
  }

  .detail-label {
    display: block;
    font-size: 0.75rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
  }

  .detail-value {
    font-size: 0.9rem;
    color: #e6edf3;
    line-height: 1.5;
  }

  .detail-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chip {
    padding: 0.35rem 0.75rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    font-size: 0.8rem;
    color: #e6edf3;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  button.chip:hover {
    border-color: #58a6ff;
    background: rgba(88, 166, 255, 0.1);
  }

  .detail-data {
    margin-top: 0.75rem;
  }

  .detail-data pre {
    margin: 0.35rem 0 0;
    padding: 0.75rem;
    background: #0d1117;
    border-radius: 6px;
    font-size: 0.75rem;
    color: #8b949e;
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
  }

  /* All Clear */
  .all-clear {
    text-align: center;
    padding: 3rem;
    background: rgba(63, 185, 80, 0.05);
    border: 1px solid rgba(63, 185, 80, 0.2);
    border-radius: 10px;
  }

  .all-clear-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 1.5rem;
    background: rgba(63, 185, 80, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .all-clear-icon svg {
    width: 40px;
    height: 40px;
    stroke: #3fb950;
  }

  .all-clear h3 {
    margin: 0 0 0.5rem;
    font-size: 1.5rem;
    color: #3fb950;
  }

  .all-clear p {
    margin: 0;
    color: #8b949e;
  }

  /* Loading */
  .loading, .no-report {
    text-align: center;
    padding: 3rem;
    color: #8b949e;
  }

  .spinner {
    width: 40px;
    height: 40px;
    margin: 0 auto 1rem;
    border: 3px solid #30363d;
    border-top-color: #58a6ff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Error */
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
    .detail-header {
      flex-wrap: wrap;
    }

    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }

    .score-overview {
      flex-direction: column;
      gap: 1.5rem;
      text-align: center;
    }

    .score-meta {
      text-align: center;
      flex-direction: row;
      flex-wrap: wrap;
      justify-content: center;
      gap: 1.5rem;
    }

    .summary-stats {
      grid-template-columns: 1fr;
    }
  }
</style>
