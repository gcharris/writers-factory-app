<!--
  HealthTrends.svelte - Historical Health Trend Charts

  Phase 5 Track 3 Phase 4: Graph Health UI

  Displays historical trends for health metrics:
  - Overall health score over time
  - Pacing plateau frequency
  - Beat deviation count
  - Flaw challenge gaps
  - Theme resonance issues

  Features:
  - Metric selector
  - Date range picker
  - SVG line chart visualization
  - Data point hover details
-->
<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // Props
  export let projectId = '';

  // State
  let isLoading = false;
  let errorMsg = '';
  let selectedMetric = 'overall_health';
  let trendData = [];
  let startDate = '';
  let endDate = '';
  let hoveredPoint = null;

  // Metric configurations
  const metrics = [
    {
      id: 'overall_health',
      label: 'Overall Health Score',
      description: 'Combined health score (0-100)',
      color: '#3fb950',
      valueKey: 'score',
      unit: '/100',
      yMin: 0,
      yMax: 100
    },
    {
      id: 'pacing_plateaus',
      label: 'Pacing Plateaus',
      description: 'Flat tension arc warnings',
      color: '#f85149',
      valueKey: 'pacing_plateaus_detected',
      unit: ' issues',
      yMin: 0,
      yMax: null // Auto-scale
    },
    {
      id: 'beat_deviations',
      label: 'Beat Deviations',
      description: '15-beat structure compliance issues',
      color: '#d29922',
      valueKey: 'beat_deviations_detected',
      unit: ' issues',
      yMin: 0,
      yMax: null
    },
    {
      id: 'flaw_challenges',
      label: 'Flaw Challenge Gaps',
      description: 'Fatal flaw testing frequency issues',
      color: '#a371f7',
      valueKey: 'flaw_challenges_detected',
      unit: ' issues',
      yMin: 0,
      yMax: null
    },
    {
      id: 'theme_resonance',
      label: 'Theme Resonance Issues',
      description: 'Weak theme presence at beats',
      color: '#58a6ff',
      valueKey: 'theme_resonance_detected',
      unit: ' issues',
      yMin: 0,
      yMax: null
    }
  ];

  // Current metric config
  $: currentMetric = metrics.find(m => m.id === selectedMetric) || metrics[0];

  // Chart dimensions
  const chartWidth = 600;
  const chartHeight = 300;
  const padding = { top: 20, right: 30, bottom: 40, left: 50 };
  const plotWidth = chartWidth - padding.left - padding.right;
  const plotHeight = chartHeight - padding.top - padding.bottom;

  // Computed chart data
  $: chartPoints = computeChartPoints(trendData, currentMetric);
  $: yAxisTicks = computeYAxisTicks(chartPoints, currentMetric);
  $: xAxisTicks = computeXAxisTicks(trendData);

  // Load initial data
  onMount(() => {
    if (projectId) {
      loadTrendData();
    }
  });

  // Load trend data
  async function loadTrendData() {
    isLoading = true;
    errorMsg = '';

    try {
      const response = await apiClient.getHealthTrends(
        selectedMetric,
        projectId,
        startDate || undefined,
        endDate || undefined
      );
      trendData = response.data || [];
    } catch (err) {
      errorMsg = err instanceof Error ? err.message : 'Failed to load trends';
      trendData = [];
    } finally {
      isLoading = false;
    }
  }

  // Compute chart points
  function computeChartPoints(data, metric) {
    if (!data || data.length === 0) return [];

    const valueKey = metric.valueKey;
    const values = data.map(d => d[valueKey] ?? d.score ?? 0);

    // Determine Y scale
    let yMin = metric.yMin ?? 0;
    let yMax = metric.yMax;

    if (yMax === null) {
      yMax = Math.max(...values, 1) * 1.2; // 20% headroom
    }

    const yRange = yMax - yMin;

    return data.map((d, i) => {
      const value = d[valueKey] ?? d.score ?? 0;
      const x = padding.left + (i / Math.max(data.length - 1, 1)) * plotWidth;
      const y = padding.top + plotHeight - ((value - yMin) / yRange) * plotHeight;

      return {
        x,
        y,
        value,
        data: d,
        index: i
      };
    });
  }

  // Compute Y axis ticks
  function computeYAxisTicks(points, metric) {
    const values = points.map(p => p.value);
    let yMin = metric.yMin ?? 0;
    let yMax = metric.yMax;

    if (yMax === null) {
      yMax = Math.max(...values, 1) * 1.2;
    }

    const yRange = yMax - yMin;
    const tickCount = 5;
    const ticks = [];

    for (let i = 0; i <= tickCount; i++) {
      const value = yMin + (i / tickCount) * yRange;
      const y = padding.top + plotHeight - (i / tickCount) * plotHeight;
      ticks.push({ value: Math.round(value), y });
    }

    return ticks;
  }

  // Compute X axis ticks
  function computeXAxisTicks(data) {
    if (!data || data.length === 0) return [];

    // Show max 6 labels
    const maxLabels = 6;
    const step = Math.max(1, Math.floor(data.length / maxLabels));
    const ticks = [];

    for (let i = 0; i < data.length; i += step) {
      const x = padding.left + (i / Math.max(data.length - 1, 1)) * plotWidth;
      const d = data[i];
      const label = d.chapter_id || (d.act_number ? `Act ${d.act_number}` : formatShortDate(d.timestamp));
      ticks.push({ x, label });
    }

    return ticks;
  }

  // Format short date
  function formatShortDate(iso) {
    if (!iso) return '';
    const date = new Date(iso);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  }

  // Format full date
  function formatFullDate(iso) {
    if (!iso) return '';
    const date = new Date(iso);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  // Generate path
  function generatePath(points) {
    if (points.length === 0) return '';
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  }

  // Generate area path
  function generateAreaPath(points) {
    if (points.length === 0) return '';
    const linePath = generatePath(points);
    const bottomY = padding.top + plotHeight;
    return `${linePath} L ${points[points.length - 1].x} ${bottomY} L ${points[0].x} ${bottomY} Z`;
  }

  // Handle metric change
  function handleMetricChange(metricId) {
    selectedMetric = metricId;
    loadTrendData();
  }

  // Handle date change
  function handleDateChange() {
    loadTrendData();
  }

  // Handle point hover
  function handlePointHover(point) {
    hoveredPoint = point;
  }

  // Handle point leave
  function handlePointLeave() {
    hoveredPoint = null;
  }

  // Close
  function close() {
    dispatch('close');
  }
</script>

<div class="trends-panel">
  <!-- Header -->
  <div class="trends-header">
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
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
      </div>
      <div>
        <h2>Health Trends</h2>
        <p class="subtitle">Historical manuscript health analysis</p>
      </div>
    </div>
  </div>

  <!-- Controls -->
  <div class="controls-section">
    <!-- Metric Selector -->
    <div class="metric-selector">
      {#each metrics as metric}
        <button
          class="metric-btn"
          class:selected={selectedMetric === metric.id}
          style="--metric-color: {metric.color}"
          on:click={() => handleMetricChange(metric.id)}
        >
          <span class="metric-dot"></span>
          <span class="metric-label">{metric.label}</span>
        </button>
      {/each}
    </div>

    <!-- Date Range -->
    <div class="date-range">
      <div class="date-input">
        <label for="startDate">From:</label>
        <input
          type="date"
          id="startDate"
          bind:value={startDate}
          on:change={handleDateChange}
        />
      </div>
      <div class="date-input">
        <label for="endDate">To:</label>
        <input
          type="date"
          id="endDate"
          bind:value={endDate}
          on:change={handleDateChange}
        />
      </div>
      <button class="refresh-btn" on:click={loadTrendData} disabled={isLoading}>
        {#if isLoading}
          <span class="spinner"></span>
        {:else}
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
        {/if}
      </button>
    </div>
  </div>

  <!-- Chart Section -->
  <div class="chart-section">
    <div class="chart-header">
      <h3 style="--metric-color: {currentMetric.color}">{currentMetric.label}</h3>
      <p class="chart-description">{currentMetric.description}</p>
    </div>

    {#if isLoading}
      <div class="chart-loading">
        <div class="spinner"></div>
        <p>Loading trend data...</p>
      </div>
    {:else if trendData.length === 0}
      <div class="chart-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10"></line>
          <line x1="12" y1="20" x2="12" y2="4"></line>
          <line x1="6" y1="20" x2="6" y2="14"></line>
        </svg>
        <p>No trend data available</p>
        <p class="hint">Run health checks to generate historical data</p>
      </div>
    {:else}
      <div class="chart-container">
        <svg
          viewBox="0 0 {chartWidth} {chartHeight}"
          class="trend-chart"
        >
          <!-- Grid lines -->
          <g class="grid-lines">
            {#each yAxisTicks as tick}
              <line
                x1={padding.left}
                y1={tick.y}
                x2={chartWidth - padding.right}
                y2={tick.y}
              />
            {/each}
          </g>

          <!-- Area fill -->
          <path
            class="area-fill"
            d={generateAreaPath(chartPoints)}
            fill="url(#areaGradient)"
          />

          <!-- Gradient definition -->
          <defs>
            <linearGradient id="areaGradient" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stop-color={currentMetric.color} stop-opacity="0.3" />
              <stop offset="100%" stop-color={currentMetric.color} stop-opacity="0.05" />
            </linearGradient>
          </defs>

          <!-- Line -->
          <path
            class="trend-line"
            d={generatePath(chartPoints)}
            stroke={currentMetric.color}
            fill="none"
            stroke-width="2"
          />

          <!-- Data points -->
          {#each chartPoints as point, i}
            <circle
              cx={point.x}
              cy={point.y}
              r={hoveredPoint?.index === i ? 6 : 4}
              fill={currentMetric.color}
              class="data-point"
              on:mouseenter={() => handlePointHover(point)}
              on:mouseleave={handlePointLeave}
              role="graphics-symbol"
            />
          {/each}

          <!-- Y axis -->
          <g class="y-axis">
            <line
              x1={padding.left}
              y1={padding.top}
              x2={padding.left}
              y2={chartHeight - padding.bottom}
            />
            {#each yAxisTicks as tick}
              <text x={padding.left - 10} y={tick.y + 4} text-anchor="end">
                {tick.value}
              </text>
            {/each}
          </g>

          <!-- X axis -->
          <g class="x-axis">
            <line
              x1={padding.left}
              y1={chartHeight - padding.bottom}
              x2={chartWidth - padding.right}
              y2={chartHeight - padding.bottom}
            />
            {#each xAxisTicks as tick}
              <text
                x={tick.x}
                y={chartHeight - padding.bottom + 20}
                text-anchor="middle"
              >
                {tick.label}
              </text>
            {/each}
          </g>
        </svg>

        <!-- Tooltip -->
        {#if hoveredPoint}
          <div
            class="tooltip"
            style="left: {hoveredPoint.x}px; top: {hoveredPoint.y - 60}px;"
          >
            <div class="tooltip-value" style="color: {currentMetric.color}">
              {hoveredPoint.value}{currentMetric.unit}
            </div>
            <div class="tooltip-label">
              {#if hoveredPoint.data.chapter_id}
                {hoveredPoint.data.chapter_id}
              {:else if hoveredPoint.data.act_number}
                Act {hoveredPoint.data.act_number}
              {/if}
            </div>
            <div class="tooltip-time">{formatFullDate(hoveredPoint.data.timestamp)}</div>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- Summary Stats -->
  {#if trendData.length > 0}
    {@const values = chartPoints.map(p => p.value)}
    {@const latest = values[values.length - 1]}
    {@const first = values[0]}
    {@const avg = values.reduce((a, b) => a + b, 0) / values.length}
    {@const trend = latest - first}
    <div class="stats-section">
      <div class="stat-card">
        <span class="stat-label">Current</span>
        <span class="stat-value" style="color: {currentMetric.color}">
          {latest.toFixed(1)}{currentMetric.unit}
        </span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Average</span>
        <span class="stat-value">{avg.toFixed(1)}{currentMetric.unit}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Min</span>
        <span class="stat-value">{Math.min(...values).toFixed(1)}{currentMetric.unit}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Max</span>
        <span class="stat-value">{Math.max(...values).toFixed(1)}{currentMetric.unit}</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Trend</span>
        <span
          class="stat-value trend"
          class:positive={selectedMetric === 'overall_health' ? trend > 0 : trend < 0}
          class:negative={selectedMetric === 'overall_health' ? trend < 0 : trend > 0}
        >
          {trend > 0 ? '+' : ''}{trend.toFixed(1)}
        </span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Data Points</span>
        <span class="stat-value">{trendData.length}</span>
      </div>
    </div>
  {/if}

  <!-- Error -->
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
  .trends-panel {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.5rem;
    color: #e6edf3;
  }

  /* Header */
  .trends-header {
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
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .header-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #58a6ff 0%, #388bfd 100%);
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

  /* Controls */
  .controls-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .metric-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .metric-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 20px;
    color: #8b949e;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .metric-btn:hover {
    border-color: var(--metric-color, #58a6ff);
    color: #e6edf3;
  }

  .metric-btn.selected {
    background: rgba(88, 166, 255, 0.1);
    border-color: var(--metric-color, #58a6ff);
    color: var(--metric-color, #58a6ff);
  }

  .metric-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--metric-color, #58a6ff);
  }

  .date-range {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .date-input {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .date-input label {
    font-size: 0.8rem;
    color: #8b949e;
  }

  .date-input input {
    padding: 0.5rem 0.75rem;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    font-size: 0.85rem;
  }

  .date-input input:focus {
    outline: none;
    border-color: #58a6ff;
  }

  .refresh-btn {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .refresh-btn:hover:not(:disabled) {
    background: #30363d;
    border-color: #58a6ff;
  }

  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .refresh-btn svg {
    width: 18px;
    height: 18px;
  }

  /* Chart Section */
  .chart-section {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  .chart-header {
    margin-bottom: 1rem;
  }

  .chart-header h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--metric-color, #58a6ff);
  }

  .chart-description {
    margin: 0.25rem 0 0;
    font-size: 0.8rem;
    color: #6e7681;
  }

  .chart-container {
    position: relative;
  }

  .trend-chart {
    width: 100%;
    height: auto;
    max-height: 350px;
  }

  .grid-lines line {
    stroke: #21262d;
    stroke-dasharray: 4 4;
  }

  .y-axis line,
  .x-axis line {
    stroke: #30363d;
  }

  .y-axis text,
  .x-axis text {
    fill: #8b949e;
    font-size: 11px;
  }

  .data-point {
    cursor: pointer;
    transition: r 0.15s ease;
  }

  .trend-line {
    stroke-linecap: round;
    stroke-linejoin: round;
  }

  .chart-loading,
  .chart-empty {
    text-align: center;
    padding: 3rem;
    color: #8b949e;
  }

  .chart-loading .spinner,
  .chart-empty svg {
    width: 48px;
    height: 48px;
    margin: 0 auto 1rem;
  }

  .chart-empty svg {
    stroke: #30363d;
  }

  .chart-empty .hint {
    font-size: 0.8rem;
    color: #6e7681;
    margin-top: 0.5rem;
  }

  /* Tooltip */
  .tooltip {
    position: absolute;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.75rem;
    pointer-events: none;
    transform: translateX(-50%);
    z-index: 10;
    min-width: 120px;
    text-align: center;
  }

  .tooltip-value {
    font-size: 1.25rem;
    font-weight: 700;
    line-height: 1;
  }

  .tooltip-label {
    font-size: 0.85rem;
    color: #e6edf3;
    margin-top: 0.35rem;
  }

  .tooltip-time {
    font-size: 0.75rem;
    color: #6e7681;
    margin-top: 0.25rem;
  }

  /* Stats Section */
  .stats-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.75rem;
  }

  .stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }

  .stat-label {
    display: block;
    font-size: 0.7rem;
    color: #6e7681;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
  }

  .stat-value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #e6edf3;
  }

  .stat-value.trend.positive {
    color: #3fb950;
  }

  .stat-value.trend.negative {
    color: #f85149;
  }

  /* Spinner */
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #30363d;
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
    .controls-section {
      flex-direction: column;
    }

    .metric-selector {
      flex-wrap: wrap;
    }

    .date-range {
      flex-wrap: wrap;
    }

    .stats-section {
      grid-template-columns: repeat(2, 1fr);
    }
  }
</style>
