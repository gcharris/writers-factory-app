# Phase 3E: Intelligent Foreman - Cloud-Native Multi-Model Architecture

**Date**: November 24, 2025
**Status**: 🚧 In Progress
**Priority**: P0 - Critical (Enables enterprise-grade AI infrastructure)
**Estimated Effort**: 8-10 hours
**Depends On**: ✅ Phase 3D (Graph Health Service - Complete)

---

## 🎯 Strategic Vision

**Context**: With no resource or time constraints and access to world-class cloud AI models, we're building an **Intelligent Foreman** that automatically selects the optimal model for each task, maximizing quality while minimizing cost.

### The Problem

Current Foreman limitations:
- Uses single model (llama3.2) for all tasks
- Limited reasoning capability for strategic decisions
- Cannot leverage cloud models for complex analysis
- No automatic task complexity detection

### The Solution

**Multi-Model Orchestra**: Automatically route tasks to optimal models based on complexity, cost, and quality requirements.

```
Simple Coordination → Mistral 7B (local, fast, free)
Strategic Reasoning → DeepSeek V3 (cloud, powerful, $0.27/1M)
Critical Decisions → Multi-model tournament (consensus)
Premium Quality → Claude Sonnet / GPT-4o (when needed)
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INTELLIGENT FOREMAN                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Task Complexity Classifier                  │    │
│  │  - Simple coordination → Mistral 7B (local)       │    │
│  │  - Strategic reasoning → Cloud advisor             │    │
│  │  - Critical decisions → Multi-model tournament     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Local Models │   │ Cloud Budget │   │ Cloud Premium│
│              │   │              │   │              │
│ Mistral 7B   │   │ DeepSeek V3  │   │ Claude Sonnet│
│ (fast, free) │   │ Qwen Plus    │   │ GPT-4o       │
│              │   │ ($0.27-0.40) │   │ ($2.50-3.00) │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 🚀 Implementation Phases

### Phase 1: Dual-Model Foreman (2-3 hours) ⭐ PRIORITY

**Goal**: Enable Foreman to use both local and cloud models with automatic routing.

**Components**:

1. **Update Settings Configuration**
   ```python
   foreman: Dict[str, Any] = field(default_factory=lambda: {
       "coordinator_model": "mistral",         # Local 7B - Smart coordination
       "advisor_model": "deepseek-chat",       # Cloud - Strategic reasoning

       "coordinator_options": {
           "fast": "llama3.2",      # 3B - Fastest
           "balanced": "mistral",   # 7B - RECOMMENDED
       },

       "advisor_options": {
           "budget": "deepseek-chat",      # ~$0.27/1M tokens
           "balanced": "qwen-plus",         # ~$0.40/1M tokens
           "premium": "claude-3-5-sonnet",  # ~$3/1M tokens
       },

       "use_advisor_for": [
           "health_check_review",
           "voice_calibration_guidance",
           "beat_structure_advice",
           "conflict_resolution",
           "scaffold_enrichment_decisions",
       ],
   })
   ```

2. **Add Cloud Provider Support to Foreman**
   - Reuse agent registry for API key detection
   - Add methods: `_query_openai()`, `_query_anthropic()`, `_query_deepseek()`, etc.
   - Implement automatic provider detection based on model name

3. **Implement Task Complexity Classifier**
   - Simple keyword matching for MVP
   - Route to advisor for complex tasks
   - Route to coordinator for simple tasks

**Files Modified**:
- `backend/services/settings_service.py` - Add foreman.coordinator_model and foreman.advisor_model
- `backend/agents/foreman.py` - Add cloud provider methods and routing logic

**Success Criteria**:
- ✅ Foreman can query cloud models (OpenAI, Anthropic, DeepSeek, etc.)
- ✅ Automatic routing based on task complexity
- ✅ Falls back gracefully if cloud keys missing

---

### Phase 2: Cloud-Native Health Checks (2-3 hours)

**Goal**: Upgrade placeholder health checks to use optimal cloud models for maximum accuracy.

**Strategic Model Selection**:

| Health Check | Model | Reasoning |
|--------------|-------|-----------|
| **Timeline Consistency** | Claude Sonnet | Best at narrative reasoning, character psychology |
| **Theme Resonance** | GPT-4o | Excellent thematic analysis, fast |
| **Flaw Challenges** | DeepSeek V3 | Deep character psychology, cheap |
| **Cast Function** | Qwen Plus | Fast, cheap, good enough |

**Implementation**:

```python
class CloudPoweredHealthService:
    """Use best-in-class cloud models for each health check type."""

    async def _check_timeline_consistency(self, scenes):
        """Use Claude Sonnet for nuanced timeline analysis."""
        model = self._get_optimal_model("timeline")  # Returns claude-3-5-sonnet

        # Build rich context
        context = self._build_timeline_context(scenes)

        # Query with sophisticated prompt
        conflicts = await self._query_llm_semantic(
            model=model,
            prompt=TIMELINE_ANALYSIS_PROMPT,
            context=context
        )

        return self._parse_timeline_conflicts(conflicts)
```

**Files Modified**:
- `backend/services/graph_health_service.py` - Implement 4 placeholder checks with cloud models

**Success Criteria**:
- ✅ Timeline consistency uses Claude Sonnet semantic analysis
- ✅ Theme resonance uses GPT-4o for scoring
- ✅ All 7 health checks fully functional
- ✅ Confidence scores > 0.95 on test cases

---

### Phase 3: Model Orchestrator (1-2 hours)

**Goal**: Build intelligent model selection system that optimizes for quality, cost, and latency.

**Capabilities Matrix**:

```python
MODEL_CAPABILITIES = {
    "claude-3-5-sonnet": {
        "strengths": ["narrative", "subtext", "character", "theme"],
        "cost_per_1m": 3.0,
        "speed": "medium",
        "quality": 10,
    },
    "deepseek-chat": {
        "strengths": ["reasoning", "structure", "logic", "cost"],
        "cost_per_1m": 0.27,
        "speed": "fast",
        "quality": 9,
    },
    "gpt-4o": {
        "strengths": ["versatile", "reliable", "fast", "balanced"],
        "cost_per_1m": 2.5,
        "speed": "fast",
        "quality": 9,
    },
    "qwen-plus": {
        "strengths": ["multilingual", "cheap", "fast"],
        "cost_per_1m": 0.4,
        "speed": "very_fast",
        "quality": 8,
    },
    "mistral": {
        "strengths": ["local", "fast", "free"],
        "cost_per_1m": 0.0,
        "speed": "very_fast",
        "quality": 7,
    },
}
```

**Selection Algorithm**:

```python
def select_optimal_model(
    task_type: str,      # "timeline", "theme", "coordination"
    quality_tier: str,   # "budget", "balanced", "premium"
    latency_req: str,    # "instant", "fast", "acceptable"
) -> str:
    """Choose optimal model based on requirements."""

    # Filter by task strengths
    candidates = [
        m for m, caps in MODEL_CAPABILITIES.items()
        if task_type in caps["strengths"]
    ]

    # Apply quality constraint
    if quality_tier == "premium":
        candidates = [m for m in candidates if MODEL_CAPABILITIES[m]["quality"] >= 9]

    # Sort by value (quality / cost)
    return sorted(candidates, key=lambda m: value_score(m))[0]
```

**Files Created**:
- `backend/services/model_orchestrator.py` - Intelligent model selection

**Success Criteria**:
- ✅ Automatic model selection based on task
- ✅ Writer can choose quality tier (budget/balanced/premium)
- ✅ Cost optimization for budget-conscious writers

---

### Phase 4: Multi-Model Tournament (2-3 hours)

**Goal**: For critical decisions, query multiple models and synthesize consensus.

**Use Cases**:
- Major structural warnings (beat deviation > 10%)
- Timeline conflicts with high impact
- Theme resonance failures at critical beats
- Before suggesting chapter rewrites

**Implementation**:

```python
async def critical_decision_tournament(
    task: str,
    context: Dict,
    models: List[str] = ["claude-3-5-sonnet", "gpt-4o", "deepseek-chat"]
) -> TournamentResult:
    """
    Query multiple models, synthesize consensus.

    Returns:
        - Agreed issues (high confidence)
        - Disputed issues (flag for human review)
        - Confidence scores per issue
    """

    # Query all models in parallel
    results = await asyncio.gather(*[
        self._query_model(model, task, context)
        for model in models
    ])

    # Find agreement (2+ models agree)
    consensus = self._find_agreement(results, threshold=2)

    # Find conflicts (models disagree)
    disputes = self._find_conflicts(results)

    return TournamentResult(
        agreed_issues=consensus,      # High confidence
        disputed_issues=disputes,     # Needs human judgment
        confidence_by_issue={...},
    )
```

**Files Modified**:
- `backend/services/graph_health_service.py` - Add tournament mode for critical checks

**Success Criteria**:
- ✅ Critical decisions use multi-model consensus
- ✅ Disagreements flagged for human review
- ✅ False positive rate < 1%

---

## 💰 Cost Analysis

**Heavy User Profile** (1000 interactions/month):
- 900 coordinator calls: Mistral 7B (free)
- 100 advisor calls: DeepSeek V3 (~2000 tokens each) = 200K tokens
- 50 health checks: Claude Sonnet (~3000 tokens each) = 150K tokens
- 20 tournaments: 3 models × 2000 tokens = 120K tokens

**Total Monthly Cost**: ~$2-5

**Compare to**:
- Running 32B model locally: $1000+ GPU + $20-50/month electricity
- Manual structural analysis: Impossible

**Verdict**: Cloud-first is 200x cheaper and infinitely better.

---

## 📈 Success Metrics

### Performance
- [ ] Mistral 7B coordination: < 500ms response time
- [ ] Cloud advisor calls: < 2s response time
- [ ] Health check accuracy: > 95%
- [ ] Tournament consensus rate: > 85%

### Cost
- [ ] Average cost per session: < $0.01
- [ ] Monthly cost for heavy user: < $10
- [ ] Cost savings vs local 32B: > 200x

### Quality
- [ ] Strategic guidance quality: 9/10 (user rating)
- [ ] False positive rate: < 5%
- [ ] Writer satisfaction: > 90%

---

## 🔧 Implementation Order

1. **Phase 1** (NOW - 2-3 hours): Dual-model Foreman
   - Update settings for coordinator + advisor
   - Add cloud provider methods to Foreman
   - Implement basic task routing

2. **Phase 2** (NEXT - 2-3 hours): Cloud health checks
   - Timeline Consistency with Claude Sonnet
   - Theme Resonance with GPT-4o
   - Flaw Challenges with DeepSeek V3
   - Cast Function with Qwen Plus

3. **Phase 3** (THEN - 1-2 hours): Model orchestrator
   - Build capabilities matrix
   - Implement selection algorithm
   - Add quality tier support

4. **Phase 4** (FINALLY - 2-3 hours): Multi-model tournament
   - Implement parallel querying
   - Add consensus detection
   - Flag disputes for human review

---

## 🎯 Future Enhancements

### Phase 3F: Adaptive Learning (Future)
- Track model performance per task type
- Automatic model selection tuning
- Cost optimization based on usage patterns

### Phase 3G: Hybrid Reasoning (Future)
- Chain-of-thought prompting
- Multi-step reasoning with verification
- Automatic fact-checking against Story Bible

### Phase 3H: Writer Preferences (Future)
- Per-writer model preferences
- Custom quality/cost trade-offs
- Feedback-driven model selection

---

## 📝 Documentation Updates Needed

- [ ] Update `README.md` with cloud model support
- [ ] Add `CLOUD_MODELS_GUIDE.md` for writers
- [ ] Update `SETTINGS_CONFIGURATION.md` with foreman models
- [ ] Add cost calculator to settings UI (Phase 5)

---

*This document specifies the Intelligent Foreman architecture for Phase 3E.*
*All multi-model features should reference this design.*
