<!--
  GraphHealthDashboard.svelte - Graph Health Overview Dashboard

  Phase 5 Track 3 Phase 4: Graph Health UI

  Displays comprehensive manuscript health status:
  - Overall health score (0-100)
  - 7 health check categories with status
  - Run health checks (chapter, act, manuscript)
  - Recent reports list
  - Warning counts by severity
  - Links to detailed views and trends

  7 Health Check Categories:
  A. Structural Integrity:
     1. Pacing Plateau Detection
     2. Beat Progress Validation
     3. Timeline Consistency
  B. Character Arc Health:
     4. Fatal Flaw Challenge Monitoring
     5. Cast Function Verification
  C. Thematic Health:
     6. Symbolic Layering
     7. Theme Resonance
-->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // Props
  export let projectId = '';

  // State
  let isLoading = false;
  let isRunningCheck = false;
  let errorMsg = '';
  let latestReport = null;
  let recentReports = [];
  let selectedScope = 'manuscript';
  let chapterId = '';
  let actNumber = 1;

  // Health check categories configuration
  const healthCategories = [
    {
      id: 'structural',
      name: 'Structural Integrity',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21h18"></path><path d="M5 21V7l7-4 7 4v14"></path><path d="M9 21v-6h6v6"></path></svg>`,
      checks: [
        {
          type: 'PACING_PLATEAU',
          name: 'Pacing Flow',
          description: 'Detects flat tension across chapters',
          model: 'pacing_analysis_model'
        },
        {
          type: 'BEAT_DEVIATION',
          name: 'Beat Progress',
          description: '15-beat Save the Cat! compliance',
          model: 'beat_progress_model'
        },
        {
          type: 'TIMELINE_ERROR',
          name: 'Timeline Consistency',
          description: 'Character locations & world rules',
          model: 'timeline_consistency_model'
        }
      ]
    },
    {
      id: 'character',
      name: 'Character Arc Health',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
      checks: [
        {
          type: 'FLAW_CHALLENGE_GAP',
          name: 'Fatal Flaw Testing',
          description: 'Protagonist flaw challenge frequency',
          model: 'flaw_challenges_model'
        },
        {
          type: 'UNDERUTILIZED_CHARACTER',
          name: 'Cast Function',
          description: 'Supporting character narrative roles',
          model: 'cast_function_model'
        }
      ]
    },
    {
      id: 'thematic',
      name: 'Thematic Health',
      icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path></svg>`,
      checks: [
        {
          type: 'SYMBOL_INSUFFICIENT_RECURRENCE',
          name: 'Symbolic Layering',
          description: 'Symbol recurrence & evolution',
          model: 'symbolic_layering_model'
        },
        {
          type: 'WEAK_THEME',
          name: 'Theme Resonance',
          description: 'Theme presence at critical beats',
          model: 'theme_resonance_model'
        }
      ]
    }
  ];

  // Computed: Get warning counts by category
  $: warningsByCategory = latestReport ? categorizeWarnings(latestReport.warnings) : {};

  // Computed: Get severity counts
  $: severityCounts = latestReport ? countBySeverity(latestReport.warnings) : { error: 0, warning: 0, info: 0 };

  // Load initial data
  onMount(async () => {
    if (projectId) {
      await loadRecentReports();
    }
  });

  // Load recent reports
  async function loadRecentReports() {
    isLoading = true;
    errorMsg = '';

    try {
      const response = await apiClient.listHealthReports(projectId, 10, 0);
      recentReports = response.reports || [];

      // Set latest report if available
      if (recentReports.length > 0) {
        const latestId = recentReports[0].report_id;
        const detailResponse = await apiClient.getHealthReport(latestId);
        latestReport = detailResponse.report;
      }
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Failed to load reports';
    } finally {
      isLoading = false;
    }
  }

  // Run health check
  async function runHealthCheck() {
    if (!projectId) {
      errorMsg = 'No project selected';
      return;
    }

    isRunningCheck = true;
    errorMsg = '';

    try {
      const response = await apiClient.runHealthCheck(
        projectId,
        selectedScope,
        selectedScope === 'chapter' ? chapterId : undefined,
        selectedScope === 'act' ? actNumber : undefined
      );

      latestReport = response.report;

      // Refresh recent reports
      await loadRecentReports();

      // Dispatch event for parent components
      dispatch('reportGenerated', { report: latestReport, markdown: response.markdown });

    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Health check failed';
    } finally {
      isRunningCheck = false;
    }
  }

  // Categorize warnings by type
  function categorizeWarnings(warnings) {
    const byType = {};
    for (const w of warnings) {
      if (!byType[w.type]) {
        byType[w.type] = [];
      }
      byType[w.type].push(w);
    }
    return byType;
  }

  // Count warnings by severity
  function countBySeverity(warnings) {
    return warnings.reduce((acc, w) => {
      acc[w.severity] = (acc[w.severity] || 0) + 1;
      return acc;
    }, { error: 0, warning: 0, info: 0 });
  }

  // Get check status from warnings
  function getCheckStatus(checkType) {
    if (!latestReport) return 'unknown';
    const warnings = warningsByCategory[checkType] || [];
    if (warnings.some(w => w.severity === 'error')) return 'error';
    if (warnings.some(w => w.severity === 'warning')) return 'warning';
    if (warnings.length > 0) return 'info';
    return 'pass';
  }

  // Get status color
  function getStatusColor(status) {
    switch (status) {
      case 'pass': return '#3fb950';
      case 'info': return '#58a6ff';
      case 'warning': return '#d29922';
      case 'error': return '#f85149';
      default: return '#8b949e';
    }
  }

  // Get status icon
  function getStatusIcon(status) {
    switch (status) {
      case 'pass': return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
      case 'info': return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
      case 'warning': return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
      case 'error': return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
      default: return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;
    }
  }

  // Get score tier
  function getScoreTier(score) {
    if (score >= 90) return { label: 'Excellent', color: '#3fb950' };
    if (score >= 80) return { label: 'Good', color: '#58a6ff' };
    if (score >= 70) return { label: 'Fair', color: '#d29922' };
    if (score >= 60) return { label: 'Needs Work', color: '#f85149' };
    return { label: 'Critical', color: '#da3633' };
  }

  // Format timestamp
  function formatTimestamp(iso) {
    if (!iso) return '--';
    const date = new Date(iso);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // View report detail
  function viewReport(reportId) {
    dispatch('viewReport', { reportId });
  }

  // View trends
  function viewTrends() {
    dispatch('viewTrends', { projectId });
  }

  // Open theme override panel
  function openThemeOverride() {
    dispatch('openThemeOverride', { projectId });
  }
</script>

<div class="health-dashboard">
  <!-- Header -->
  <div class="dashboard-header">
    <div class="header-content">
      <div class="header-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
        </svg>
      </div>
      <div>
        <h2>Graph Health</h2>
        <p class="subtitle">Manuscript structural analysis</p>
      </div>
    </div>
    <div class="header-actions">
      <button class="action-btn secondary" on:click={viewTrends} title="View Trends">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        Trends
      </button>
      <button class="action-btn secondary" on:click={openThemeOverride} title="Theme Overrides">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
        Overrides
      </button>
    </div>
  </div>

  <!-- Overall Score Section -->
  {#if latestReport}
    {@const tier = getScoreTier(latestReport.overall_score)}
    <div class="score-section" style="--tier-color: {tier.color}">
      <div class="score-circle">
        <span class="score-value">{latestReport.overall_score}</span>
        <span class="score-max">/100</span>
      </div>
      <div class="score-info">
        <span class="score-tier">{tier.label}</span>
        <span class="score-scope">{latestReport.scope} check</span>
        <span class="score-time">{formatTimestamp(latestReport.timestamp)}</span>
      </div>
      <div class="severity-badges">
        {#if severityCounts.error > 0}
          <span class="severity-badge error">{severityCounts.error} Error{severityCounts.error > 1 ? 's' : ''}</span>
        {/if}
        {#if severityCounts.warning > 0}
          <span class="severity-badge warning">{severityCounts.warning} Warning{severityCounts.warning > 1 ? 's' : ''}</span>
        {/if}
        {#if severityCounts.info > 0}
          <span class="severity-badge info">{severityCounts.info} Note{severityCounts.info > 1 ? 's' : ''}</span>
        {/if}
        {#if severityCounts.error === 0 && severityCounts.warning === 0 && severityCounts.info === 0}
          <span class="severity-badge pass">All Clear</span>
        {/if}
      </div>
    </div>
  {:else}
    <div class="no-report">
      <div class="no-report-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <p>No health report available</p>
      <p class="hint">Run a health check to analyze your manuscript</p>
    </div>
  {/if}

  <!-- Run Health Check Section -->
  <div class="run-check-section">
    <h3>Run Health Check</h3>
    <div class="scope-selector">
      <label class="scope-option" class:selected={selectedScope === 'manuscript'}>
        <input type="radio" bind:group={selectedScope} value="manuscript" />
        <span class="scope-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
        </span>
        <span class="scope-label">Full Manuscript</span>
      </label>
      <label class="scope-option" class:selected={selectedScope === 'act'}>
        <input type="radio" bind:group={selectedScope} value="act" />
        <span class="scope-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
          </svg>
        </span>
        <span class="scope-label">Act</span>
      </label>
      <label class="scope-option" class:selected={selectedScope === 'chapter'}>
        <input type="radio" bind:group={selectedScope} value="chapter" />
        <span class="scope-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
        </span>
        <span class="scope-label">Chapter</span>
      </label>
    </div>

    {#if selectedScope === 'act'}
      <div class="scope-input">
        <label for="actNumber">Act Number:</label>
        <select id="actNumber" bind:value={actNumber}>
          <option value={1}>Act 1</option>
          <option value={2}>Act 2</option>
          <option value={3}>Act 3</option>
        </select>
      </div>
    {/if}

    {#if selectedScope === 'chapter'}
      <div class="scope-input">
        <label for="chapterId">Chapter ID:</label>
        <input
          type="text"
          id="chapterId"
          bind:value={chapterId}
          placeholder="e.g., chapter_2.5"
        />
      </div>
    {/if}

    <button
      class="run-btn"
      on:click={runHealthCheck}
      disabled={isRunningCheck || !projectId || (selectedScope === 'chapter' && !chapterId)}
    >
      {#if isRunningCheck}
        <span class="spinner"></span>
        Running Analysis...
      {:else}
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        Run Health Check
      {/if}
    </button>
  </div>

  <!-- Health Categories Grid -->
  <div class="categories-section">
    <h3>Health Categories</h3>
    <div class="categories-grid">
      {#each healthCategories as category}
        <div class="category-card">
          <div class="category-header">
            <div class="category-icon" style="--category-color: {category.id === 'structural' ? '#58a6ff' : category.id === 'character' ? '#a371f7' : '#3fb950'}">
              {@html category.icon}
            </div>
            <h4>{category.name}</h4>
          </div>
          <div class="checks-list">
            {#each category.checks as check}
              {@const status = getCheckStatus(check.type)}
              <div class="check-item" style="--status-color: {getStatusColor(status)}">
                <div class="check-status">
                  {@html getStatusIcon(status)}
                </div>
                <div class="check-info">
                  <span class="check-name">{check.name}</span>
                  <span class="check-desc">{check.description}</span>
                </div>
                {#if warningsByCategory[check.type]?.length > 0}
                  <span class="check-count">{warningsByCategory[check.type].length}</span>
                {/if}
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Recent Reports -->
  {#if recentReports.length > 0}
    <div class="recent-section">
      <h3>Recent Reports</h3>
      <div class="reports-list">
        {#each recentReports.slice(0, 5) as report}
          {@const tier = getScoreTier(report.overall_score)}
          <button class="report-item" on:click={() => viewReport(report.report_id)}>
            <div class="report-score" style="--tier-color: {tier.color}">
              {report.overall_score}
            </div>
            <div class="report-info">
              <span class="report-scope">{report.scope}</span>
              <span class="report-time">{formatTimestamp(report.timestamp)}</span>
            </div>
            <div class="report-counts">
              {#if report.error_count > 0}
                <span class="count error">{report.error_count}</span>
              {/if}
              {#if report.warning_count > 0}
                <span class="count warning">{report.warning_count}</span>
              {/if}
            </div>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="arrow">
              <polyline points="9 18 15 12 9 6"></polyline>
            </svg>
          </button>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Error Display -->
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

  <!-- Loading Overlay -->
  {#if isLoading}
    <div class="loading-overlay">
      <div class="spinner large"></div>
      <p>Loading health data...</p>
    </div>
  {/if}
</div>

<style>
  .health-dashboard {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    color: #e6edf3;
    position: relative;
    min-height: 400px;
  }

  /* Header */
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #30363d;
  }

  .header-content {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .header-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #3fb950 0%, #238636 100%);
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
    color: #e6edf3;
  }

  .subtitle {
    margin: 0.25rem 0 0;
    font-size: 0.85rem;
    color: #8b949e;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid #30363d;
    border-radius: 6px;
    background: #21262d;
    color: #e6edf3;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .action-btn:hover {
    background: #30363d;
    border-color: #58a6ff;
  }

  .action-btn svg {
    width: 16px;
    height: 16px;
  }

  /* Score Section */
  .score-section {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-bottom: 1.5rem;
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
    background: rgba(255, 255, 255, 0.02);
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

  .score-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .score-tier {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--tier-color, #3fb950);
  }

  .score-scope {
    font-size: 0.9rem;
    color: #8b949e;
    text-transform: capitalize;
  }

  .score-time {
    font-size: 0.8rem;
    color: #6e7681;
  }

  .severity-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-left: auto;
  }

  .severity-badge {
    padding: 0.35rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .severity-badge.error {
    background: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border: 1px solid rgba(248, 81, 73, 0.3);
  }

  .severity-badge.warning {
    background: rgba(210, 153, 34, 0.15);
    color: #d29922;
    border: 1px solid rgba(210, 153, 34, 0.3);
  }

  .severity-badge.info {
    background: rgba(88, 166, 255, 0.15);
    color: #58a6ff;
    border: 1px solid rgba(88, 166, 255, 0.3);
  }

  .severity-badge.pass {
    background: rgba(63, 185, 80, 0.15);
    color: #3fb950;
    border: 1px solid rgba(63, 185, 80, 0.3);
  }

  /* No Report */
  .no-report {
    text-align: center;
    padding: 2rem;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-bottom: 1.5rem;
  }

  .no-report-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 1rem;
    background: #21262d;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .no-report-icon svg {
    width: 32px;
    height: 32px;
    stroke: #8b949e;
  }

  .no-report p {
    margin: 0;
    color: #8b949e;
  }

  .no-report .hint {
    font-size: 0.85rem;
    margin-top: 0.5rem;
    color: #6e7681;
  }

  /* Run Check Section */
  .run-check-section {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .run-check-section h3 {
    margin: 0 0 1rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .scope-selector {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .scope-option {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .scope-option input {
    display: none;
  }

  .scope-option:hover {
    border-color: #58a6ff;
  }

  .scope-option.selected {
    border-color: #58a6ff;
    background: rgba(88, 166, 255, 0.1);
  }

  .scope-icon {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .scope-icon svg {
    width: 24px;
    height: 24px;
    stroke: #8b949e;
  }

  .scope-option.selected .scope-icon svg {
    stroke: #58a6ff;
  }

  .scope-label {
    font-size: 0.85rem;
    color: #8b949e;
  }

  .scope-option.selected .scope-label {
    color: #58a6ff;
  }

  .scope-input {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .scope-input label {
    font-size: 0.85rem;
    color: #8b949e;
    min-width: 100px;
  }

  .scope-input input,
  .scope-input select {
    flex: 1;
    padding: 0.6rem 1rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.9rem;
  }

  .scope-input input:focus,
  .scope-input select:focus {
    outline: none;
    border-color: #58a6ff;
  }

  .run-btn {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 0.875rem 1.5rem;
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
    border: none;
    border-radius: 8px;
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .run-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
  }

  .run-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .run-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Categories Section */
  .categories-section h3 {
    margin: 0 0 1rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .categories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .category-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    overflow: hidden;
  }

  .category-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.02);
    border-bottom: 1px solid #30363d;
  }

  .category-icon {
    width: 36px;
    height: 36px;
    background: rgba(88, 166, 255, 0.1);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .category-icon svg {
    width: 18px;
    height: 18px;
    stroke: var(--category-color, #58a6ff);
  }

  .category-header h4 {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .checks-list {
    padding: 0.5rem;
  }

  .check-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-radius: 6px;
    transition: background 0.2s ease;
  }

  .check-item:hover {
    background: rgba(255, 255, 255, 0.02);
  }

  .check-status {
    width: 24px;
    height: 24px;
    flex-shrink: 0;
  }

  .check-status svg {
    width: 24px;
    height: 24px;
    stroke: var(--status-color, #8b949e);
  }

  .check-info {
    flex: 1;
    min-width: 0;
  }

  .check-name {
    display: block;
    font-size: 0.85rem;
    font-weight: 500;
    color: #e6edf3;
  }

  .check-desc {
    display: block;
    font-size: 0.75rem;
    color: #6e7681;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .check-count {
    width: 24px;
    height: 24px;
    background: rgba(248, 81, 73, 0.15);
    color: #f85149;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
  }

  /* Recent Reports */
  .recent-section h3 {
    margin: 0 0 1rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e6edf3;
  }

  .reports-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .report-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    text-align: left;
    color: inherit;
    font: inherit;
  }

  .report-item:hover {
    border-color: #58a6ff;
    background: rgba(88, 166, 255, 0.05);
  }

  .report-score {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 2px solid var(--tier-color, #3fb950);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 700;
    color: var(--tier-color, #3fb950);
  }

  .report-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .report-scope {
    font-size: 0.9rem;
    font-weight: 500;
    color: #e6edf3;
    text-transform: capitalize;
  }

  .report-time {
    font-size: 0.8rem;
    color: #6e7681;
  }

  .report-counts {
    display: flex;
    gap: 0.5rem;
  }

  .count {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .count.error {
    background: rgba(248, 81, 73, 0.15);
    color: #f85149;
  }

  .count.warning {
    background: rgba(210, 153, 34, 0.15);
    color: #d29922;
  }

  .arrow {
    width: 20px;
    height: 20px;
    stroke: #8b949e;
  }

  /* Error Box */
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

  /* Loading */
  .loading-overlay {
    position: absolute;
    inset: 0;
    background: rgba(13, 17, 23, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    border-radius: 12px;
    z-index: 10;
  }

  .loading-overlay p {
    color: #8b949e;
    font-size: 0.9rem;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #30363d;
    border-top-color: #58a6ff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .spinner.large {
    width: 40px;
    height: 40px;
    border-width: 3px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Responsive */
  @media (max-width: 768px) {
    .dashboard-header {
      flex-direction: column;
      gap: 1rem;
    }

    .header-actions {
      width: 100%;
    }

    .action-btn {
      flex: 1;
      justify-content: center;
    }

    .score-section {
      flex-direction: column;
      text-align: center;
    }

    .severity-badges {
      margin-left: 0;
      justify-content: center;
    }

    .scope-selector {
      flex-direction: column;
    }

    .categories-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
