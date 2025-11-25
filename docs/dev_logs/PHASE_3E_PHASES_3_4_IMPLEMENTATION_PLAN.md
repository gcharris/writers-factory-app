# Phase 3E: Phases 3 & 4 Implementation Plan

**Date**: November 24, 2025
**Status**: Planning
**Prerequisites**: ✅ Phases 1-2 Complete
**Integration**: Settings Panel v2 (Phase 3 of Settings Panel Implementation)

---

## Overview

Phases 3 & 4 add **writer-controlled AI intelligence** - allowing users to optimize for quality, cost, or speed through the Settings Panel.

### Why These Phases Matter for Settings Panel

**Phase 3 (Model Orchestrator)** enables:
- **Quality Tiers**: Budget/Balanced/Premium dropdown in Settings
- **Auto-optimization**: "Choose best model for my budget" checkbox
- **Cost visibility**: Real-time cost estimates per setting change

**Phase 4 (Multi-Model Tournament)** enables:
- **Critical Decision Mode**: "Use consensus for important decisions" toggle
- **Confidence thresholds**: Slider for when to trigger multi-model analysis
- **Dispute review**: UI to review model disagreements

---

## Phase 3: Model Orchestrator (4-6 hours)

### Strategic Goal

Give writers a **"quality dial"** in Settings Panel that automatically selects optimal models based on their budget and quality requirements.

### 3.1 Model Capabilities Matrix

**New File**: `backend/services/model_capabilities.py`

```python
"""
Model Capabilities Matrix - defines strengths, costs, and speed for all models.

Used by Model Orchestrator to select optimal model for each task.
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum

class TaskStrength(Enum):
    """Task categories where models excel."""
    NARRATIVE = "narrative"           # Timeline, character psychology
    THEMATIC = "thematic"             # Theme analysis, symbolism
    STRUCTURAL = "structural"         # Beat structure, pacing
    REASONING = "reasoning"           # Strategic planning, conflicts
    COST_OPTIMIZED = "cost_optimized" # Good enough, cheap
    VERSATILE = "versatile"           # General purpose, reliable

@dataclass
class ModelCapabilities:
    """Capabilities profile for a single model."""
    model_id: str                     # e.g., "claude-3-5-sonnet"
    provider: str                     # e.g., "anthropic"

    # Strengths (TaskStrength enum values)
    strengths: List[TaskStrength]

    # Performance metrics
    quality_score: int                # 0-10 (subjective quality rating)
    speed: str                        # "very_fast" | "fast" | "medium" | "slow"
    context_window: int               # tokens

    # Cost (USD per 1M tokens)
    cost_per_1m_input: float
    cost_per_1m_output: float

    # Availability
    requires_api_key: bool
    local_only: bool

# The definitive capabilities matrix
MODEL_CAPABILITIES: Dict[str, ModelCapabilities] = {
    # === Cloud Premium Models ===

    "claude-3-5-sonnet": ModelCapabilities(
        model_id="claude-3-5-sonnet",
        provider="anthropic",
        strengths=[TaskStrength.NARRATIVE, TaskStrength.REASONING, TaskStrength.VERSATILE],
        quality_score=10,
        speed="medium",
        context_window=200_000,
        cost_per_1m_input=3.00,
        cost_per_1m_output=15.00,
        requires_api_key=True,
        local_only=False
    ),

    "claude-3-opus": ModelCapabilities(
        model_id="claude-3-opus",
        provider="anthropic",
        strengths=[TaskStrength.NARRATIVE, TaskStrength.THEMATIC, TaskStrength.REASONING],
        quality_score=10,
        speed="slow",
        context_window=200_000,
        cost_per_1m_input=15.00,
        cost_per_1m_output=75.00,
        requires_api_key=True,
        local_only=False
    ),

    "gpt-4o": ModelCapabilities(
        model_id="gpt-4o",
        provider="openai",
        strengths=[TaskStrength.THEMATIC, TaskStrength.VERSATILE, TaskStrength.REASONING],
        quality_score=9,
        speed="fast",
        context_window=128_000,
        cost_per_1m_input=2.50,
        cost_per_1m_output=10.00,
        requires_api_key=True,
        local_only=False
    ),

    "gpt-4o-mini": ModelCapabilities(
        model_id="gpt-4o-mini",
        provider="openai",
        strengths=[TaskStrength.VERSATILE, TaskStrength.COST_OPTIMIZED],
        quality_score=8,
        speed="very_fast",
        context_window=128_000,
        cost_per_1m_input=0.15,
        cost_per_1m_output=0.60,
        requires_api_key=True,
        local_only=False
    ),

    # === Cloud Budget Models ===

    "deepseek-chat": ModelCapabilities(
        model_id="deepseek-chat",
        provider="deepseek",
        strengths=[TaskStrength.REASONING, TaskStrength.STRUCTURAL, TaskStrength.COST_OPTIMIZED],
        quality_score=9,
        speed="fast",
        context_window=64_000,
        cost_per_1m_input=0.27,
        cost_per_1m_output=1.10,
        requires_api_key=True,
        local_only=False
    ),

    "qwen-plus": ModelCapabilities(
        model_id="qwen-plus",
        provider="qwen",
        strengths=[TaskStrength.VERSATILE, TaskStrength.COST_OPTIMIZED],
        quality_score=8,
        speed="very_fast",
        context_window=32_000,
        cost_per_1m_input=0.40,
        cost_per_1m_output=1.20,
        requires_api_key=True,
        local_only=False
    ),

    "qwen-turbo": ModelCapabilities(
        model_id="qwen-turbo",
        provider="qwen",
        strengths=[TaskStrength.COST_OPTIMIZED],
        quality_score=7,
        speed="very_fast",
        context_window=8_000,
        cost_per_1m_input=0.12,
        cost_per_1m_output=0.12,
        requires_api_key=True,
        local_only=False
    ),

    # === Local Models (Free) ===

    "mistral": ModelCapabilities(
        model_id="mistral",
        provider="ollama",
        strengths=[TaskStrength.STRUCTURAL, TaskStrength.COST_OPTIMIZED, TaskStrength.VERSATILE],
        quality_score=7,
        speed="very_fast",
        context_window=8_000,
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
        requires_api_key=False,
        local_only=True
    ),

    "llama3.2": ModelCapabilities(
        model_id="llama3.2",
        provider="ollama",
        strengths=[TaskStrength.COST_OPTIMIZED],
        quality_score=6,
        speed="very_fast",
        context_window=8_000,
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
        requires_api_key=False,
        local_only=True
    ),

    "llama3.1:70b": ModelCapabilities(
        model_id="llama3.1:70b",
        provider="ollama",
        strengths=[TaskStrength.REASONING, TaskStrength.VERSATILE],
        quality_score=8,
        speed="medium",
        context_window=128_000,
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
        requires_api_key=False,
        local_only=True
    ),
}

# Task type to strength mapping
TASK_STRENGTH_MAP = {
    # Foreman tasks
    "coordinator": TaskStrength.COST_OPTIMIZED,
    "health_check_review": TaskStrength.REASONING,
    "voice_calibration_guidance": TaskStrength.REASONING,
    "beat_structure_advice": TaskStrength.STRUCTURAL,
    "conflict_resolution": TaskStrength.NARRATIVE,
    "scaffold_enrichment_decisions": TaskStrength.REASONING,
    "theme_analysis": TaskStrength.THEMATIC,
    "structural_planning": TaskStrength.STRUCTURAL,

    # Health check tasks
    "timeline_consistency": TaskStrength.NARRATIVE,
    "theme_resonance": TaskStrength.THEMATIC,
    "flaw_challenges": TaskStrength.NARRATIVE,
    "cast_function": TaskStrength.STRUCTURAL,
    "pacing_analysis": TaskStrength.STRUCTURAL,
    "beat_progress": TaskStrength.STRUCTURAL,
    "symbolic_layering": TaskStrength.THEMATIC,
}
```

---

### 3.2 Model Orchestrator Service

**New File**: `backend/services/model_orchestrator.py`

```python
"""
Model Orchestrator - Intelligent model selection based on writer preferences.

Selects optimal model for each task based on:
- Quality tier (budget/balanced/premium)
- Task requirements (narrative, thematic, structural, etc.)
- Cost constraints
- Available API keys
"""

import os
from typing import List, Optional
from dataclasses import dataclass

from backend.services.model_capabilities import (
    MODEL_CAPABILITIES,
    TASK_STRENGTH_MAP,
    TaskStrength,
    ModelCapabilities
)
from backend.services.settings_service import settings_service

@dataclass
class SelectionCriteria:
    """Criteria for model selection."""
    task_type: str                    # e.g., "theme_analysis"
    quality_tier: str                 # "budget" | "balanced" | "premium"
    max_cost_per_query: float         # Max acceptable cost (USD)
    prefer_local: bool = False        # Prefer local models when possible
    require_cloud: bool = False       # Must use cloud model

class ModelOrchestrator:
    """Selects optimal models based on writer preferences and task requirements."""

    def __init__(self):
        self.capabilities = MODEL_CAPABILITIES
        self.task_strengths = TASK_STRENGTH_MAP

    def select_model(self, criteria: SelectionCriteria) -> str:
        """
        Select optimal model for given criteria.

        Returns:
            model_id: String identifier (e.g., "claude-3-5-sonnet")
        """
        # Get task strength requirement
        required_strength = self.task_strengths.get(
            criteria.task_type,
            TaskStrength.VERSATILE
        )

        # Filter candidates by task strength
        candidates = [
            model for model_id, model in self.capabilities.items()
            if required_strength in model.strengths or TaskStrength.VERSATILE in model.strengths
        ]

        # Filter by API key availability
        candidates = [
            model for model in candidates
            if not model.requires_api_key or self._has_api_key(model.provider)
        ]

        # Filter by local/cloud preference
        if criteria.prefer_local:
            local_candidates = [m for m in candidates if m.local_only]
            if local_candidates:
                candidates = local_candidates

        if criteria.require_cloud:
            candidates = [m for m in candidates if not m.local_only]

        # Filter by cost constraint
        candidates = [
            model for model in candidates
            if self._estimate_query_cost(model) <= criteria.max_cost_per_query
        ]

        # No candidates? Fall back to local default
        if not candidates:
            return "mistral"

        # Apply quality tier
        return self._select_by_tier(candidates, criteria.quality_tier)

    def _select_by_tier(
        self,
        candidates: List[ModelCapabilities],
        tier: str
    ) -> str:
        """Select best model from candidates based on quality tier."""

        if tier == "budget":
            # Minimize cost, accept quality >= 7
            viable = [m for m in candidates if m.quality_score >= 7]
            if not viable:
                viable = candidates
            return min(viable, key=lambda m: m.cost_per_1m_input).model_id

        elif tier == "balanced":
            # Optimize value (quality / cost ratio)
            def value_score(model: ModelCapabilities) -> float:
                cost = model.cost_per_1m_input or 0.01  # Avoid division by zero
                return model.quality_score / cost

            return max(candidates, key=value_score).model_id

        elif tier == "premium":
            # Maximize quality, cost is secondary
            return max(candidates, key=lambda m: m.quality_score).model_id

        else:
            # Default to balanced
            return self._select_by_tier(candidates, "balanced")

    def _has_api_key(self, provider: str) -> bool:
        """Check if API key is available for provider."""
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "qwen": "QWEN_API_KEY",
        }
        return bool(os.getenv(key_map.get(provider, "")))

    def _estimate_query_cost(self, model: ModelCapabilities) -> float:
        """
        Estimate cost for typical query (2K input, 500 output tokens).

        Returns:
            Estimated cost in USD
        """
        input_tokens = 2000
        output_tokens = 500

        cost = (
            (input_tokens / 1_000_000) * model.cost_per_1m_input +
            (output_tokens / 1_000_000) * model.cost_per_1m_output
        )
        return cost

    def get_cost_estimate(
        self,
        task_type: str,
        quality_tier: str,
        queries_per_month: int = 100
    ) -> Dict[str, float]:
        """
        Estimate monthly cost for a task type at given tier.

        Returns:
            {
                "cost_per_query": 0.002,
                "monthly_cost": 0.20,
                "model_selected": "deepseek-chat"
            }
        """
        criteria = SelectionCriteria(
            task_type=task_type,
            quality_tier=quality_tier,
            max_cost_per_query=999.0  # No limit for estimation
        )

        model_id = self.select_model(criteria)
        model = self.capabilities[model_id]

        cost_per_query = self._estimate_query_cost(model)

        return {
            "cost_per_query": round(cost_per_query, 4),
            "monthly_cost": round(cost_per_query * queries_per_month, 2),
            "model_selected": model_id,
            "quality_score": model.quality_score
        }

# Singleton instance
_orchestrator = None

def get_orchestrator() -> ModelOrchestrator:
    """Get or create ModelOrchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ModelOrchestrator()
    return _orchestrator
```

---

### 3.3 Settings Integration

**File Modified**: `backend/services/settings_service.py`

Add new settings section:

```python
orchestrator: Dict[str, Any] = field(default_factory=lambda: {
    "enabled": True,  # Use orchestrator for model selection

    # Quality tier (used when orchestrator enabled)
    "quality_tier": "balanced",  # "budget" | "balanced" | "premium"

    # Cost constraints
    "max_cost_per_query": 0.01,      # Max cost per query (USD)
    "monthly_budget": 5.0,            # Monthly budget (USD)
    "warn_at_percentage": 80,         # Warn when 80% of budget used

    # Preferences
    "prefer_local": False,            # Prefer local models when quality is close
    "allow_premium_for_critical": True,  # Use premium for critical decisions even if budget tier

    # Override specific tasks (when orchestrator can't find good match)
    "task_overrides": {},  # {"theme_analysis": "gpt-4o"} - force specific model
})
```

---

### 3.4 Foreman Integration

**File Modified**: `backend/agents/foreman.py`

Update `_query_llm()` to use orchestrator when enabled:

```python
async def _query_llm(
    self,
    prompt: str,
    system_prompt: str,
    model: str = None,
    task_type: str = "coordinator"
) -> str:
    """
    Query LLM with intelligent model selection.

    Phase 3E:
    - Phase 1-2: Configurable task models
    - Phase 3: Orchestrator-based selection (NEW)
    """
    from backend.services.settings_service import settings_service
    from backend.services.model_orchestrator import get_orchestrator, SelectionCriteria

    foreman_settings = settings_service.get_category("foreman")
    orchestrator_settings = settings_service.get_category("orchestrator")

    # Determine which model to use
    if model is None:
        # Phase 3: Check if orchestrator is enabled
        if orchestrator_settings.get("enabled", False):
            # Use orchestrator for intelligent selection
            orchestrator = get_orchestrator()

            criteria = SelectionCriteria(
                task_type=task_type,
                quality_tier=orchestrator_settings.get("quality_tier", "balanced"),
                max_cost_per_query=orchestrator_settings.get("max_cost_per_query", 0.01),
                prefer_local=orchestrator_settings.get("prefer_local", False)
            )

            model = orchestrator.select_model(criteria)
            logger.info(f"🎯 Orchestrator selected {model} for {task_type} (tier: {criteria.quality_tier})")
        else:
            # Phase 1-2: Use configured task models
            task_models = foreman_settings.get("task_models", {})
            model = task_models.get(task_type, foreman_settings.get("coordinator_model", "mistral"))

            if task_type == "coordinator":
                logger.debug(f"📋 Using {model} for {task_type}")
            else:
                logger.info(f"🧠 Using {model} for {task_type}")

    # Route to provider (existing logic)
    if model.startswith("gpt-"):
        return await self._query_openai(prompt, system_prompt, model)
    # ... rest of routing logic
```

---

### 3.5 API Endpoints

**File Modified**: `backend/api.py`

Add orchestrator endpoints:

```python
@app.get("/orchestrator/estimate")
async def get_cost_estimate(
    task_type: str,
    quality_tier: str = "balanced",
    queries_per_month: int = 100
):
    """
    Estimate monthly cost for a task type at given quality tier.

    Used by Settings Panel to show real-time cost estimates.

    Example: GET /orchestrator/estimate?task_type=theme_analysis&quality_tier=premium
    """
    from backend.services.model_orchestrator import get_orchestrator

    orchestrator = get_orchestrator()
    return orchestrator.get_cost_estimate(task_type, quality_tier, queries_per_month)

@app.get("/orchestrator/capabilities")
async def get_model_capabilities():
    """
    Get full capabilities matrix for all models.

    Used by Settings Panel to show model comparison table.
    """
    from backend.services.model_capabilities import MODEL_CAPABILITIES

    return {
        model_id: {
            "provider": caps.provider,
            "quality_score": caps.quality_score,
            "speed": caps.speed,
            "cost_per_query": round(
                (2000 / 1_000_000) * caps.cost_per_1m_input +
                (500 / 1_000_000) * caps.cost_per_1m_output,
                4
            ),
            "local_only": caps.local_only,
            "strengths": [s.value for s in caps.strengths]
        }
        for model_id, caps in MODEL_CAPABILITIES.items()
    }

@app.post("/orchestrator/test")
async def test_selection(criteria: dict):
    """
    Test model selection with given criteria.

    Used by Settings Panel "Preview Selection" button.

    Body: {
        "task_type": "theme_analysis",
        "quality_tier": "premium",
        "max_cost_per_query": 0.01
    }
    """
    from backend.services.model_orchestrator import get_orchestrator, SelectionCriteria

    orchestrator = get_orchestrator()
    selection_criteria = SelectionCriteria(**criteria)
    selected_model = orchestrator.select_model(selection_criteria)

    model_caps = MODEL_CAPABILITIES[selected_model]

    return {
        "selected_model": selected_model,
        "quality_score": model_caps.quality_score,
        "estimated_cost": orchestrator._estimate_query_cost(model_caps),
        "reasoning": f"Selected for {criteria['quality_tier']} tier based on {criteria['task_type']} requirements"
    }
```

---

### 3.6 Settings Panel UI Components

**New Components for Phase 3**:

#### `SettingsOrchestrator.svelte`

```svelte
<script>
  import { settings } from '$lib/stores/settingsStore';
  import SettingDropdown from './SettingDropdown.svelte';
  import SettingSlider from './SettingSlider.svelte';
  import SettingToggle from './SettingToggle.svelte';
  import CostEstimator from './CostEstimator.svelte';

  let enabled = $settings.orchestrator.enabled;
  let qualityTier = $settings.orchestrator.quality_tier;
  let monthlyBudget = $settings.orchestrator.monthly_budget;
</script>

<div class="settings-section">
  <h2>Model Orchestrator</h2>
  <p class="description">
    Automatically select optimal AI models based on your quality and budget preferences.
  </p>

  <SettingToggle
    label="Enable Orchestrator"
    bind:value={enabled}
    tooltip="Let the system automatically choose the best model for each task"
  />

  {#if enabled}
    <SettingDropdown
      label="Quality Tier"
      bind:value={qualityTier}
      options={[
        { value: 'budget', label: 'Budget ($0-1/month)' },
        { value: 'balanced', label: 'Balanced ($1-3/month)' },
        { value: 'premium', label: 'Premium ($3-10/month)' }
      ]}
      tooltip="Choose your quality vs. cost trade-off"
    />

    <SettingSlider
      label="Monthly Budget"
      bind:value={monthlyBudget}
      min={0}
      max={20}
      step={1}
      suffix=" USD"
      tooltip="Maximum monthly spend on cloud AI models"
    />

    <!-- Real-time cost estimator -->
    <CostEstimator
      tier={qualityTier}
      budget={monthlyBudget}
    />
  {/if}
</div>
```

#### `CostEstimator.svelte`

```svelte
<script>
  import { onMount } from 'svelte';

  export let tier;
  export let budget;

  let estimates = {};
  let loading = true;

  async function fetchEstimates() {
    loading = true;

    const taskTypes = [
      'theme_analysis',
      'health_check_review',
      'beat_structure_advice',
      'timeline_consistency'
    ];

    const promises = taskTypes.map(async (taskType) => {
      const response = await fetch(
        `/orchestrator/estimate?task_type=${taskType}&quality_tier=${tier}&queries_per_month=100`
      );
      return { taskType, data: await response.json() };
    });

    const results = await Promise.all(promises);
    estimates = Object.fromEntries(
      results.map(r => [r.taskType, r.data])
    );

    loading = false;
  }

  $: if (tier || budget) {
    fetchEstimates();
  }

  onMount(fetchEstimates);
</script>

<div class="cost-estimator">
  <h3>Estimated Costs</h3>

  {#if loading}
    <p class="loading">Calculating...</p>
  {:else}
    <table>
      <thead>
        <tr>
          <th>Task</th>
          <th>Model</th>
          <th>Cost/Query</th>
          <th>Monthly (100x)</th>
        </tr>
      </thead>
      <tbody>
        {#each Object.entries(estimates) as [task, estimate]}
          <tr>
            <td>{task}</td>
            <td class="model">{estimate.model_selected}</td>
            <td>${estimate.cost_per_query.toFixed(4)}</td>
            <td class="monthly">${estimate.monthly_cost}</td>
          </tr>
        {/each}
      </tbody>
    </table>

    <div class="total">
      <strong>Estimated Total:</strong>
      ${Object.values(estimates).reduce((sum, e) => sum + e.monthly_cost, 0).toFixed(2)}/month
    </div>

    {#if Object.values(estimates).reduce((sum, e) => sum + e.monthly_cost, 0) > budget}
      <div class="warning">
        ⚠️ Estimated cost exceeds monthly budget. Consider lowering quality tier or increasing budget.
      </div>
    {/if}
  {/if}
</div>

<style>
  .cost-estimator {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--bg-secondary);
    border-radius: 8px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
  }

  th, td {
    text-align: left;
    padding: 0.5rem;
  }

  .model {
    font-family: monospace;
    font-size: 0.9em;
  }

  .monthly {
    font-weight: bold;
  }

  .total {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 2px solid var(--border-color);
    font-size: 1.1em;
  }

  .warning {
    margin-top: 1rem;
    padding: 0.75rem;
    background: var(--warning-bg);
    color: var(--warning-text);
    border-radius: 4px;
  }
</style>
```

---

## Phase 4: Multi-Model Tournament (6-8 hours)

### Strategic Goal

For **critical decisions**, query multiple models and synthesize consensus - giving writers confidence in important structural advice.

### 4.1 Tournament Service

**New File**: `backend/services/tournament_service.py`

```python
"""
Multi-Model Tournament - Consensus detection for critical decisions.

Queries 2-4 models in parallel, compares responses, detects:
- Agreement (high confidence issues)
- Disputes (models disagree - flag for human review)
- Confidence scores per issue
"""

import asyncio
import json
from dataclasses import dataclass
from typing import List, Dict, Any
from collections import Counter

@dataclass
class TournamentResult:
    """Result from multi-model tournament."""
    agreed_issues: List[Dict]         # High confidence (2+ models agree)
    disputed_issues: List[Dict]        # Low confidence (models disagree)
    confidence_by_issue: Dict[str, float]  # Issue -> confidence score
    models_used: List[str]
    execution_time_ms: int

class TournamentService:
    """Runs multi-model tournaments for critical decisions."""

    def __init__(self):
        from backend.services.settings_service import settings_service
        tournament_settings = settings_service.get_category("tournament")

        self.enabled = tournament_settings.get("enabled", False)
        self.min_models = tournament_settings.get("min_models", 3)
        self.agreement_threshold = tournament_settings.get("agreement_threshold", 2)
        self.model_pool = tournament_settings.get("model_pool", [
            "claude-3-5-sonnet",
            "gpt-4o",
            "deepseek-chat"
        ])

    async def run_tournament(
        self,
        prompt: str,
        system_prompt: str,
        models: List[str] = None
    ) -> TournamentResult:
        """
        Query multiple models in parallel and synthesize consensus.

        Args:
            prompt: User query
            system_prompt: System context
            models: Optional model list (defaults to configured pool)

        Returns:
            TournamentResult with agreed/disputed issues
        """
        import time
        start_time = time.time()

        models = models or self.model_pool[:self.min_models]

        # Query all models in parallel
        tasks = [
            self._query_single_model(model, prompt, system_prompt)
            for model in models
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse responses
        parsed = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Tournament model {models[i]} failed: {response}")
                continue

            try:
                parsed.append({
                    "model": models[i],
                    "data": json.loads(response)
                })
            except json.JSONDecodeError:
                logger.warning(f"Model {models[i]} returned non-JSON: {response[:100]}")

        # Find consensus
        agreed, disputed, confidence = self._detect_consensus(parsed)

        execution_time = int((time.time() - start_time) * 1000)

        return TournamentResult(
            agreed_issues=agreed,
            disputed_issues=disputed,
            confidence_by_issue=confidence,
            models_used=models,
            execution_time_ms=execution_time
        )

    async def _query_single_model(
        self,
        model: str,
        prompt: str,
        system_prompt: str
    ) -> str:
        """Query a single model (reuses Foreman's _query_llm routing)."""
        from backend.agents.foreman import get_foreman

        foreman = get_foreman()
        return await foreman._query_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model,
            task_type="tournament"  # Bypass orchestrator
        )

    def _detect_consensus(
        self,
        responses: List[Dict]
    ) -> tuple[List[Dict], List[Dict], Dict[str, float]]:
        """
        Detect agreement and disputes across model responses.

        Returns:
            (agreed_issues, disputed_issues, confidence_scores)
        """
        agreed = []
        disputed = []
        confidence = {}

        # Extract issues from each model
        all_issues = []
        for response in responses:
            model_name = response["model"]
            data = response["data"]

            # Assumes responses have "issues" or "warnings" array
            issues = data.get("issues", data.get("warnings", data.get("conflicts", [])))

            for issue in issues:
                all_issues.append({
                    "model": model_name,
                    "type": issue.get("type", "UNKNOWN"),
                    "severity": issue.get("severity", "info"),
                    "description": issue.get("description", ""),
                    "confidence": issue.get("confidence", 0.5)
                })

        # Group issues by type
        issues_by_type = {}
        for issue in all_issues:
            issue_type = issue["type"]
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        # Detect consensus per issue type
        for issue_type, issue_list in issues_by_type.items():
            models_reporting = len(set(i["model"] for i in issue_list))
            total_models = len(responses)

            consensus_ratio = models_reporting / total_models

            # Calculate aggregate confidence
            avg_confidence = sum(i["confidence"] for i in issue_list) / len(issue_list)

            # Combine descriptions (most common)
            descriptions = [i["description"] for i in issue_list]
            most_common_desc = Counter(descriptions).most_common(1)[0][0]

            issue_summary = {
                "type": issue_type,
                "description": most_common_desc,
                "models_agreeing": models_reporting,
                "total_models": total_models,
                "confidence": round(avg_confidence, 2),
                "consensus_ratio": round(consensus_ratio, 2)
            }

            confidence[issue_type] = consensus_ratio

            # Agreement threshold (default: 2+ models)
            if models_reporting >= self.agreement_threshold:
                agreed.append(issue_summary)
            else:
                disputed.append(issue_summary)

        return agreed, disputed, confidence

# Singleton
_tournament_service = None

def get_tournament_service() -> TournamentService:
    """Get or create TournamentService singleton."""
    global _tournament_service
    if _tournament_service is None:
        _tournament_service = TournamentService()
    return _tournament_service
```

---

### 4.2 Settings Integration

**File Modified**: `backend/services/settings_service.py`

Add tournament settings:

```python
tournament: Dict[str, Any] = field(default_factory=lambda: {
    "enabled": False,  # Enable multi-model tournament for critical decisions

    # Tournament configuration
    "min_models": 3,               # Minimum models to query
    "agreement_threshold": 2,       # Min models that must agree for consensus

    # Model pool for tournament
    "model_pool": [
        "claude-3-5-sonnet",
        "gpt-4o",
        "deepseek-chat"
    ],

    # When to trigger tournament
    "critical_tasks": [
        "beat_structure_advice",
        "conflict_resolution",
        "theme_analysis"
    ],

    # Automatic vs manual
    "auto_trigger": True,          # Trigger automatically for critical tasks
    "confidence_threshold": 0.7,   # Only use tournament if single-model confidence < 0.7

    # Cost control
    "max_tournaments_per_day": 10,  # Limit to control costs
})
```

---

### 4.3 Foreman Integration

**File Modified**: `backend/agents/foreman.py`

Add tournament detection to `chat()`:

```python
async def chat(self, user_message: str) -> Dict:
    """
    Process a chat message and return response.

    Phase 3E:
    - Phase 1-2: Configurable models
    - Phase 3: Orchestrator selection
    - Phase 4: Tournament for critical decisions (NEW)
    """
    if not self.work_order:
        return {"error": "No active project. Call start_project first."}

    # Add user message
    self.conversation.append(ConversationMessage(role="user", content=user_message))

    # Classify task
    task_type = self._classify_task_complexity(user_message, self.get_context())

    # Phase 4: Check if tournament should be triggered
    from backend.services.settings_service import settings_service
    from backend.services.tournament_service import get_tournament_service

    tournament_settings = settings_service.get_category("tournament")
    should_use_tournament = (
        tournament_settings.get("enabled", False) and
        tournament_settings.get("auto_trigger", True) and
        task_type in tournament_settings.get("critical_tasks", [])
    )

    if should_use_tournament:
        # Use tournament for critical decision
        system_prompt = self._get_system_prompt()
        # ... add work order, KB context as before

        tournament_service = get_tournament_service()
        tournament_result = await tournament_service.run_tournament(
            prompt=user_message,
            system_prompt=system_prompt
        )

        # Format tournament result as response
        response_text = self._format_tournament_response(tournament_result)

        return {
            "response": response_text,
            "tournament_result": {
                "agreed_issues": tournament_result.agreed_issues,
                "disputed_issues": tournament_result.disputed_issues,
                "models_used": tournament_result.models_used,
                "execution_time_ms": tournament_result.execution_time_ms
            },
            "work_order": self.work_order.to_dict(),
            "kb_entries_pending": len(self.kb_entries)
        }

    # Otherwise, use single-model query (existing logic)
    # ... rest of existing chat() implementation
```

---

### 4.4 Settings Panel UI Components

**New Components for Phase 4**:

#### `SettingsTournament.svelte`

```svelte
<script>
  import { settings } from '$lib/stores/settingsStore';
  import SettingToggle from './SettingToggle.svelte';
  import SettingMultiSelect from './SettingMultiSelect.svelte';
  import SettingSlider from './SettingSlider.svelte';

  let enabled = $settings.tournament.enabled;
  let autoTrigger = $settings.tournament.auto_trigger;
  let criticalTasks = $settings.tournament.critical_tasks;
</script>

<div class="settings-section">
  <h2>Multi-Model Tournament</h2>
  <p class="description">
    For critical decisions, query multiple AI models and get consensus.
    Improves accuracy but increases cost (3x per query).
  </p>

  <SettingToggle
    label="Enable Tournament"
    bind:value={enabled}
    tooltip="Query multiple models for critical decisions to improve accuracy"
  />

  {#if enabled}
    <SettingToggle
      label="Auto-Trigger"
      bind:value={autoTrigger}
      tooltip="Automatically use tournament for critical tasks"
    />

    <SettingMultiSelect
      label="Critical Tasks"
      bind:value={criticalTasks}
      options={[
        { value: 'beat_structure_advice', label: 'Beat Structure Advice' },
        { value: 'conflict_resolution', label: 'Conflict Resolution' },
        { value: 'theme_analysis', label: 'Theme Analysis' },
        { value: 'timeline_consistency', label: 'Timeline Consistency' },
        { value: 'voice_calibration_guidance', label: 'Voice Calibration' }
      ]}
      tooltip="Tasks that should use multi-model consensus"
    />

    <div class="info-box">
      <h4>Tournament Costs</h4>
      <p>
        Tournament queries 3 models in parallel:
      </p>
      <ul>
        <li>Claude Sonnet ($0.006/query)</li>
        <li>GPT-4o ($0.005/query)</li>
        <li>DeepSeek ($0.0005/query)</li>
      </ul>
      <p><strong>Total: ~$0.0115/tournament query</strong></p>
      <p class="cost-comparison">
        vs. $0.0005 for single DeepSeek query (23x cost)
      </p>
    </div>
  {/if}
</div>

<style>
  .info-box {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--info-bg);
    border-left: 4px solid var(--info-border);
    border-radius: 4px;
  }

  .info-box h4 {
    margin-top: 0;
  }

  .info-box ul {
    margin: 0.5rem 0;
  }

  .cost-comparison {
    font-size: 0.9em;
    color: var(--text-secondary);
    margin-top: 0.5rem;
  }
</style>
```

---

## Implementation Schedule

### Phase 3: Model Orchestrator (4-6 hours)

**Week 1**:
1. Create `model_capabilities.py` (1 hour)
2. Create `model_orchestrator.py` (2 hours)
3. Update settings service (30 min)
4. Add API endpoints (1 hour)
5. Create UI components (`SettingsOrchestrator.svelte`, `CostEstimator.svelte`) (1.5 hours)

**Testing**: 30 min
- Test tier selection (budget/balanced/premium)
- Verify cost estimates
- Test orchestrator with different API key configurations

---

### Phase 4: Multi-Model Tournament (6-8 hours)

**Week 2**:
1. Create `tournament_service.py` (3 hours)
2. Update settings service (30 min)
3. Update Foreman integration (2 hours)
4. Create UI components (`SettingsTournament.svelte`) (1.5 hours)
5. Add tournament result display in chat UI (1 hour)

**Testing**: 1 hour
- Test consensus detection
- Test dispute flagging
- Verify cost controls (max tournaments/day)

---

## Settings Panel Integration

These phases integrate directly into the Settings Panel as **Category 8: AI Intelligence**:

```
Settings Panel
├── Agents & Models (Category 1)
├── Scoring & Rubrics (Category 2)
├── Voice & Metaphor (Categories 3 & 4)
├── Anti-Patterns (Category 5)
├── Enhancement (Category 6)
├── Foreman (Category 7)
├── AI Intelligence (Categories 8 - NEW) ← Phase 3 & 4
│   ├── Model Orchestrator
│   │   ├── Quality Tier dropdown
│   │   ├── Monthly Budget slider
│   │   └── Cost Estimator widget
│   └── Multi-Model Tournament
│       ├── Enable Tournament toggle
│       ├── Critical Tasks multi-select
│       └── Cost Warning widget
└── Graph Health (Category 9)
```

---

## Value Proposition

### Phase 3 Value

**For Budget-Conscious Writers**:
- Set budget to $1/month → automatically uses DeepSeek for strategic, Mistral for coordination
- Real-time cost visibility in Settings Panel
- Warning when approaching budget limit

**For Quality-Focused Writers**:
- Set tier to Premium → automatically uses Claude/GPT-4o for all tasks
- No manual model selection needed
- Optimal model per task type

**For Balanced Writers**:
- Set tier to Balanced → uses DeepSeek for most, Claude for narrative-critical
- Best value (quality/cost ratio)
- Recommended for most users

---

### Phase 4 Value

**For High-Stakes Decisions**:
- Major structural changes (moving Midpoint)
- Timeline conflict resolution
- Theme analysis before manuscript submission

**Confidence Through Consensus**:
- 3 models agree → High confidence, proceed
- Models disagree → Flag for human review, show different perspectives

**Cost Control**:
- Limit to 10 tournaments/day (< $0.12/day = $3.60/month)
- Manual trigger option for writers who want full control

---

## Success Metrics

### Phase 3

- [ ] Orchestrator correctly selects models based on tier
- [ ] Cost estimates match actual usage (within 10%)
- [ ] Budget warnings trigger at 80% threshold
- [ ] Settings Panel shows real-time cost calculator
- [ ] Writers can change tier and see instant cost impact

### Phase 4

- [ ] Tournament detects consensus (2+ models agree) > 85% of time
- [ ] Disputed issues flagged for review
- [ ] Execution time < 10 seconds for 3-model tournament
- [ ] Cost controls enforce daily limit
- [ ] Settings Panel shows tournament costs clearly

---

## Documentation Updates

- [ ] Update CONFIGURABLE_MODEL_ASSIGNMENTS.md with orchestrator info
- [ ] Create ORCHESTRATOR_GUIDE.md with tier recommendations
- [ ] Create TOURNAMENT_GUIDE.md with use cases
- [ ] Update SETTINGS_PANEL_IMPLEMENTATION_PLAN.md with Phase 3 & 4 UI

---

**Phase 3 & 4 together deliver the "AI Intelligence dial" - giving writers full control over the quality/cost trade-off through an intuitive Settings Panel interface.**

*Next: Implement Phase 3 first (6 hours), validate with users, then decide if Phase 4 tournament is needed based on feedback.*
