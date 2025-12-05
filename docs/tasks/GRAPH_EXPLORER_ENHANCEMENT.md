# Graph Explorer Enhancement: Narrative Intelligence Visualization

**Status**: Ready for Implementation
**Priority**: Critical - "Wow Factor" for Course Demo
**Depends On**: GraphRAG Phase 5 (complete on `nifty-antonelli`)
**Estimated Effort**: 4-6 hours

---

## Goal

Transform the existing `GraphExplorer.svelte` into a **narrative intelligence visualization** that makes the GraphRAG analysis visible and impressive. This is the centerpiece demo component for the course.

**Demo Impact**: When students see communities color-coded, tension edges pulsing, and bridge characters highlighted - they immediately understand what GraphRAG does and why it matters.

---

## Existing Infrastructure

The foundation is already built:

| Component | Location | Status |
|-----------|----------|--------|
| `GraphExplorer.svelte` | Full-featured explorer | Working |
| `GraphCanvas.svelte` | Canvas-based physics | Working |
| `LiveGraph.svelte` | Simple SVG viewer | Working |
| `GraphControls.svelte` | Search/filter UI | Working |
| `GraphNodeDetails.svelte` | Node detail panel | Working |

**Backend endpoints available:**
- `GET /graph/analysis/communities` - Louvain community detection
- `GET /graph/analysis/bridges?top_k=5` - Betweenness centrality
- `GET /graph/analysis/tension` - Narrative tension score
- `GET /graph/analysis/pacing` - Action/setup/resolution ratios
- `GET /graph/analysis/summary` - Comprehensive narrative analysis

---

## Deliverables

### 1. Community Coloring in GraphCanvas

**Goal**: Color nodes by their detected community, making character clusters visible.

**Implementation**:
```javascript
// In GraphCanvas.svelte
let communities = {};  // { community_name: [node_ids] }
let communityColors = {};  // { community_name: color }

async function loadCommunities() {
  const res = await fetch('http://localhost:8000/graph/analysis/communities');
  const data = await res.json();
  communities = data.communities || {};

  // Generate distinct colors for each community
  const palette = [
    '#58a6ff', '#a371f7', '#3fb950', '#f85149',
    '#d4a574', '#d29922', '#8b949e', '#ff7b72'
  ];
  Object.keys(communities).forEach((name, i) => {
    communityColors[name] = palette[i % palette.length];
  });
}

function getNodeCommunity(nodeId) {
  for (const [name, members] of Object.entries(communities)) {
    if (members.includes(nodeId)) return name;
  }
  return null;
}
```

**Visual Effect**:
```
┌────────────────────────────────────────────┐
│                                            │
│     [Primary Cast - Blue]                  │
│         ●Mickey    ●Sarah                  │
│              \    /                        │
│               \  /                         │
│                \/                          │
│     [Secondary Cast - Purple]              │
│         ●Guard    ●Dealer                  │
│                                            │
│     [Antagonists - Red]                    │
│         ●The Woman                         │
│                                            │
└────────────────────────────────────────────┘
```

**Legend**: Add a floating legend showing community colors.

---

### 2. Bridge Character Highlighting

**Goal**: Make bridge characters (protagonists, connectors) visually prominent.

**Implementation**:
```javascript
let bridgeCharacters = [];  // [{ name, centrality, role }]

async function loadBridges() {
  const res = await fetch('http://localhost:8000/graph/analysis/bridges?top_k=5');
  bridgeCharacters = await res.json();
}

function getNodeRadius(node) {
  const base = 18;
  const bridge = bridgeCharacters.find(b => b.name === node.name);
  if (bridge) {
    // Larger nodes for higher centrality
    return base + (bridge.centrality * 20);
  }
  return base;
}

function renderNode(node) {
  const bridge = bridgeCharacters.find(b => b.name === node.name);

  if (bridge) {
    // Draw star/crown indicator above node
    ctx.fillStyle = '#ffd700';
    ctx.font = '14px';
    ctx.fillText('★', node.x, node.y - node.radius - 10);

    // Role badge (protagonist/major/supporting)
    ctx.fillStyle = '#d4a574';
    ctx.font = '9px';
    ctx.fillText(bridge.role.toUpperCase(), node.x, node.y + node.radius + 22);
  }
}
```

**Visual Effect**:
```
        ★ PROTAGONIST
           ●●●
          Mickey ← Larger, gold-starred
         /   |   \
        /    |    \
       ●    ●●     ●
     Sarah  Guard  Woman
     MAJOR         SUPPORTING
```

---

### 3. Tension Edge Visualization

**Goal**: Make narrative tension edges (HINDERS, CHALLENGES, FORESHADOWS) visually distinct and animated.

**Implementation**:
```javascript
// Edge type visual properties
const edgeStyles = {
  HINDERS: { color: '#f85149', width: 3, dash: [], glow: true },
  CHALLENGES: { color: '#d29922', width: 2, dash: [], glow: true },
  FORESHADOWS: { color: '#a371f7', width: 2, dash: [5, 5], glow: false },
  CALLBACKS: { color: '#3fb950', width: 2, dash: [3, 3], glow: false },
  CONTRADICTS: { color: '#ff4444', width: 4, dash: [], glow: true },
  // Default for other types
  DEFAULT: { color: '#3d4a57', width: 1, dash: [], glow: false }
};

function renderEdge(edge, time) {
  const style = edgeStyles[edge.type] || edgeStyles.DEFAULT;

  ctx.strokeStyle = style.color;
  ctx.lineWidth = style.width;
  ctx.setLineDash(style.dash);

  // Pulsing animation for tension edges
  if (style.glow) {
    const pulse = Math.sin(time / 300) * 0.3 + 0.7;
    ctx.globalAlpha = pulse;
    ctx.lineWidth = style.width + 2;
    ctx.stroke();
    ctx.globalAlpha = 1;
    ctx.lineWidth = style.width;
  }

  ctx.stroke();
}
```

**Visual Effect**: HINDERS edges pulse red, FORESHADOWS are dashed purple, CHALLENGES glow gold.

---

### 4. Tension Meter Overlay

**Goal**: Show the overall narrative tension as a real-time overlay on the graph.

**Implementation**: Create a `TensionOverlay.svelte` component.

```svelte
<!-- TensionOverlay.svelte -->
<script>
  export let score = 0;  // 0-1
  export let level = 'medium';

  $: fillWidth = score * 100;
  $: fillColor = level === 'high' ? '#f85149' :
                 level === 'medium' ? '#d29922' : '#3fb950';
</script>

<div class="tension-overlay">
  <div class="tension-label">NARRATIVE TENSION</div>
  <div class="tension-bar">
    <div class="tension-fill" style="width: {fillWidth}%; background: {fillColor}"></div>
  </div>
  <div class="tension-score">{Math.round(score * 100)}%</div>
</div>
```

**Placement**: Top-left corner of the graph canvas, semi-transparent.

---

### 5. Analysis Mode Toggle

**Goal**: Add a toggle to switch between "Structure View" (node types) and "Analysis View" (communities + tension).

**Implementation**:
```svelte
<div class="view-toggle">
  <button class:active={viewMode === 'structure'} on:click={() => viewMode = 'structure'}>
    📊 Structure
  </button>
  <button class:active={viewMode === 'analysis'} on:click={() => viewMode = 'analysis'}>
    🧠 Analysis
  </button>
</div>
```

| View Mode | Node Coloring | Edge Styling | Overlays |
|-----------|---------------|--------------|----------|
| Structure | By type (CHARACTER=blue, LOCATION=purple) | Uniform gray | None |
| Analysis | By community | By narrative type | Tension meter, bridge badges |

---

### 6. Narrative Summary Panel

**Goal**: Show the comprehensive narrative analysis when requested.

**Integration**: Add to `GraphExplorer.svelte` as a collapsible bottom panel.

```svelte
{#if showNarrativeSummary}
  <div class="narrative-summary">
    <h3>Narrative Intelligence</h3>

    <div class="summary-grid">
      <!-- Tension -->
      <div class="summary-card">
        <span class="card-icon">⚡</span>
        <span class="card-value">{tension.level}</span>
        <span class="card-label">Tension</span>
      </div>

      <!-- Pacing -->
      <div class="summary-card">
        <span class="card-icon">📈</span>
        <span class="card-value">{pacing.type}</span>
        <span class="card-label">Pacing</span>
      </div>

      <!-- Communities -->
      <div class="summary-card">
        <span class="card-icon">👥</span>
        <span class="card-value">{Object.keys(communities).length}</span>
        <span class="card-label">Story Clusters</span>
      </div>

      <!-- Bridge Characters -->
      <div class="summary-card">
        <span class="card-icon">⭐</span>
        <span class="card-value">{bridges[0]?.name || 'None'}</span>
        <span class="card-label">Protagonist</span>
      </div>
    </div>

    <!-- Recommendations -->
    <div class="recommendations">
      <p>{tension.recommendation}</p>
      <p>{pacing.recommendation}</p>
    </div>
  </div>
{/if}
```

---

## API Client Extensions

Add to `frontend/src/lib/api_client.ts`:

```typescript
// Graph Analysis Types
interface CommunityResult {
  communities: Record<string, string[]>;
  algorithm: string;
  modularity?: number;
}

interface BridgeCharacter {
  name: string;
  centrality: number;
  role: 'protagonist' | 'major' | 'supporting' | 'minor';
  connections: number;
}

interface TensionResult {
  tension_score: number;
  level: 'low' | 'medium' | 'high';
  indicators: {
    active_obstacles: number;
    unresolved_foreshadowing: number;
    contradictions: number;
    flaw_challenges: number;
    active_conflicts: number;
  };
  recommendation: string;
}

interface PacingResult {
  pacing: 'fast' | 'slow' | 'balanced' | 'concluding';
  edge_counts: Record<string, number>;
  ratios: {
    action_ratio: number;
    setup_ratio: number;
    resolution_ratio: number;
  };
  recommendation: string;
}

interface NarrativeSummary {
  communities: CommunityResult;
  bridges: BridgeCharacter[];
  tension: TensionResult;
  pacing: PacingResult;
}

// API Functions
export async function getCommunities(): Promise<CommunityResult> {
  const res = await fetch(`${API_BASE}/graph/analysis/communities`);
  if (!res.ok) throw new Error('Failed to fetch communities');
  return res.json();
}

export async function getBridges(topK = 5): Promise<BridgeCharacter[]> {
  const res = await fetch(`${API_BASE}/graph/analysis/bridges?top_k=${topK}`);
  if (!res.ok) throw new Error('Failed to fetch bridges');
  return res.json();
}

export async function getTension(): Promise<TensionResult> {
  const res = await fetch(`${API_BASE}/graph/analysis/tension`);
  if (!res.ok) throw new Error('Failed to fetch tension');
  return res.json();
}

export async function getPacing(): Promise<PacingResult> {
  const res = await fetch(`${API_BASE}/graph/analysis/pacing`);
  if (!res.ok) throw new Error('Failed to fetch pacing');
  return res.json();
}

export async function getNarrativeSummary(): Promise<NarrativeSummary> {
  const res = await fetch(`${API_BASE}/graph/analysis/summary`);
  if (!res.ok) throw new Error('Failed to fetch narrative summary');
  return res.json();
}
```

---

## Visual Mockup: Analysis View

```
┌──────────────────────────────────────────────────────────────────────┐
│ [📊 Structure] [🧠 Analysis]                              [⚙ Settings]│
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                                                 │
│  │ TENSION: 65%    │   ★ PROTAGONIST                                 │
│  │ ████████░░ HIGH │      ●●●●                                       │
│  └─────────────────┘     Mickey ←─── Gold star, large node           │
│                         /   |   \                                    │
│  ┌─ PRIMARY CAST ──┐   /    |    \   ←─── Red pulsing (HINDERS)      │
│  │ ●Mickey ●Sarah  │  /     |     \                                  │
│  └─────────────────┘ ●     ●●      ● ←─── Purple dashed (FORESHADOWS)│
│                    Sarah   Guard   Woman                             │
│  ┌─ ANTAGONISTS ───┐  │            │                                 │
│  │ ●Woman          │  │            │                                 │
│  └─────────────────┘  └────────────┘                                 │
│                                                                      │
│  Legend: ━━ HINDERS  ┄┄ FORESHADOWS  ── KNOWS                       │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│ Narrative Intelligence                                          [▼] │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐                  │
│ │ ⚡ HIGH  │ │ 📈 FAST │ │ 👥 3    │ │ ⭐ Mickey   │                  │
│ │ Tension │ │ Pacing  │ │ Clusters│ │ Protagonist │                  │
│ └─────────┘ └─────────┘ └─────────┘ └─────────────┘                  │
│ 💡 Consider adding a resolution scene to balance the high tension.   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Checklist

**Create:**
- [ ] `TensionOverlay.svelte` - Tension meter component
- [ ] `CommunityLegend.svelte` - Community color legend
- [ ] `NarrativeSummaryPanel.svelte` - Bottom summary panel

**Modify:**
- [ ] `GraphCanvas.svelte` - Community coloring, bridge highlighting, edge animations
- [ ] `GraphExplorer.svelte` - Analysis mode toggle, load analysis data
- [ ] `GraphControls.svelte` - View mode toggle buttons
- [ ] `api_client.ts` - Analysis endpoint functions + types

---

## Demo Script

For the course demo, walk through:

1. **Start with Structure View**: "Here's the knowledge graph showing characters, locations, and events."

2. **Toggle to Analysis View**: "Now watch what happens when we switch to narrative analysis..."
   - Communities highlight in distinct colors
   - Bridge characters get stars
   - Tension edges start pulsing

3. **Explain communities**: "The system automatically detected these character clusters - primary cast, antagonists, supporting characters."

4. **Show bridge character**: "Mickey is identified as the protagonist because he has the highest betweenness centrality - he connects the most story threads."

5. **Point to tension edges**: "The red pulsing lines are HINDERS relationships - active obstacles creating conflict. Purple dashed lines are FORESHADOWS - setups waiting for payoffs."

6. **Reveal summary panel**: "The system calculates overall narrative health: 65% tension (slightly high), fast pacing, 3 story clusters."

7. **The hook**: "This is what GraphRAG gives us - not just storage, but computable narrative intelligence."

---

## Success Criteria

- [ ] Communities are visually distinct (color-coded)
- [ ] Bridge characters have visual prominence (size + badge)
- [ ] Tension edges animate (pulsing/dashed)
- [ ] View toggle works smoothly
- [ ] Tension overlay updates from API
- [ ] Summary panel shows all metrics
- [ ] Demo script can be executed without bugs
- [ ] `npm run check` passes

---

## Technical Notes

### Performance Considerations
- Cache analysis results (don't re-fetch on every render)
- Use `requestAnimationFrame` for edge animations
- Debounce view toggle transitions

### Fallback Behavior
- If analysis endpoints fail, fall back to Structure View
- Show loading skeleton while fetching analysis
- Handle empty graphs gracefully

### Color Accessibility
- Ensure community colors have sufficient contrast
- Don't rely solely on color for tension edges (also use dash pattern)

---

## Handoff

When complete, provide:
1. Screenshots showing Structure vs Analysis view
2. Screen recording of the demo flow (optional but impressive)
3. Branch name and commit hash
4. `npm run check` output

---

*Task created: December 5, 2025*
*For: Course demo "wow factor"*
*Builds on: GraphRAG Phase 5 (nifty-antonelli)*
