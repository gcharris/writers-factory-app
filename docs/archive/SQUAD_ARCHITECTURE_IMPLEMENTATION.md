# Squad Architecture Implementation Plan

> Technical specification for implementing the 3-Squad model selection system
> Version: 1.0 | Created: November 25, 2025 | Status: Ready for Implementation

## Executive Summary

Transform the current complex 10-model configuration into a simple 3-Squad system:
- **Local Squad** - Free, offline, hardware-dependent
- **Hybrid Squad** - Best value, course default (~$0.50/week)
- **Pro Squad** - Premium quality, BYOK (~$3-5/week)

Plus a **Course Mode toggle** for instructor-subsidized deployments.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Data Structures](#2-data-structures)
3. [Backend Implementation](#3-backend-implementation)
4. [Frontend Implementation](#4-frontend-implementation)
5. [API Endpoints](#5-api-endpoints)
6. [Migration Strategy](#6-migration-strategy)
7. [Testing Plan](#7-testing-plan)
8. [File Checklist](#8-file-checklist)

---

## 1. Architecture Overview

### 1.1 Squad Definitions

```
┌─────────────────────────────────────────────────────────────────┐
│  LOCAL SQUAD ($0/week)                                          │
├─────────────────────────────────────────────────────────────────┤
│  Requirements: Ollama installed, 8GB+ RAM                       │
│  Foreman: User-selected local model (default: mistral:7b)       │
│  Tournament Models: User-selected local models                  │
│  Health Checks: Local models only                               │
│  Use Case: Privacy-conscious, offline work, zero budget         │
│  Limitations: Quality ceiling, no premium model access          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  HYBRID SQUAD (~$0.50/week) - COURSE DEFAULT                    │
├─────────────────────────────────────────────────────────────────┤
│  Requirements: Internet + Course API keys OR personal keys      │
│  Foreman: DeepSeek V3 (strategic), local (coordination)         │
│  Tournament Models: DeepSeek, Qwen, Zhipu, Gemini (all budget)  │
│  Health Checks: DeepSeek (complex), local (simple)              │
│  Use Case: Best quality-per-dollar, course students             │
│  Fallback: Local models when offline                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PRO SQUAD (~$3-5/week) - BYOK                                  │
├─────────────────────────────────────────────────────────────────┤
│  Requirements: Personal API keys for premium providers          │
│  Foreman: Claude Sonnet (strategic), DeepSeek (coordination)    │
│  Tournament Models: Claude, GPT-4o, Grok, Mistral Large + all   │
│  Health Checks: Claude (timeline), GPT-4o (theme), DeepSeek     │
│  Use Case: Professional writers, publishers, maximum quality    │
│  Note: Students provide own keys (BYOK)                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Course Mode vs Individual Mode

```
┌────────────────────────────────────────────────────────────────┐
│  COURSE MODE (Toggle ON)                                       │
├────────────────────────────────────────────────────────────────┤
│  - Instructor provides budget API keys (DeepSeek, Qwen, etc.)  │
│  - Hybrid Squad available to all students at no cost           │
│  - Pro Squad requires student BYOK                             │
│  - Usage tracking enabled for instructor visibility            │
│  - Default: Hybrid Squad                                       │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  INDIVIDUAL MODE (Toggle OFF)                                  │
├────────────────────────────────────────────────────────────────┤
│  - User manages all API keys                                   │
│  - All squads available based on configured keys               │
│  - No usage restrictions                                       │
│  - Default: Based on available keys                            │
└────────────────────────────────────────────────────────────────┘
```

### 1.3 Tournament Model Selection Philosophy

Users can select ANY combination of available models for tournaments:
- Multi-checkbox UI showing all 10+ models
- Models grouped by tier (Free/Budget/Premium)
- Cost estimation shown before running
- Goal: Find the model(s) that best capture the author's voice

---

## 2. Data Structures

### 2.1 Squad Presets Configuration

**File**: `backend/config/squad_presets.json`

```json
{
  "version": "1.0",
  "presets": {
    "local": {
      "id": "local",
      "name": "Local Squad",
      "description": "100% offline, zero cost, privacy-focused",
      "icon": "🏠",
      "tier": "free",
      "requirements": {
        "ollama_required": true,
        "min_ram_gb": 8,
        "api_keys": []
      },
      "default_models": {
        "foreman_strategic": "mistral:7b",
        "foreman_coordinator": "mistral:7b",
        "tournament": ["mistral:7b", "llama3.2:3b"],
        "health_checks": {
          "default": "mistral:7b",
          "timeline_consistency": "mistral:7b",
          "theme_resonance": "mistral:7b",
          "flaw_challenges": "mistral:7b",
          "cast_function": "mistral:7b",
          "pacing_analysis": "mistral:7b",
          "beat_progress": "mistral:7b",
          "symbolic_layering": "mistral:7b"
        }
      },
      "cost_estimate": {
        "weekly_usd": 0,
        "monthly_usd": 0
      }
    },
    "hybrid": {
      "id": "hybrid",
      "name": "Hybrid Squad",
      "description": "Best value - cloud intelligence + local speed",
      "icon": "💎",
      "tier": "budget",
      "recommended": true,
      "requirements": {
        "ollama_required": true,
        "min_ram_gb": 8,
        "api_keys": ["DEEPSEEK_API_KEY"]
      },
      "optional_api_keys": ["QWEN_API_KEY", "ZHIPU_API_KEY", "GEMINI_API_KEY"],
      "default_models": {
        "foreman_strategic": "deepseek-chat",
        "foreman_coordinator": "mistral:7b",
        "tournament": ["deepseek-chat", "qwen-plus", "zhipu-glm4", "gemini-2.0-flash"],
        "health_checks": {
          "default": "mistral:7b",
          "timeline_consistency": "deepseek-chat",
          "theme_resonance": "deepseek-chat",
          "flaw_challenges": "deepseek-chat",
          "cast_function": "qwen-plus",
          "pacing_analysis": "mistral:7b",
          "beat_progress": "mistral:7b",
          "symbolic_layering": "deepseek-chat"
        }
      },
      "fallback": {
        "offline_model": "mistral:7b",
        "api_failure_model": "mistral:7b"
      },
      "cost_estimate": {
        "weekly_usd": 0.50,
        "monthly_usd": 2.00
      }
    },
    "pro": {
      "id": "pro",
      "name": "Pro Squad",
      "description": "Maximum quality for professional writers",
      "icon": "🚀",
      "tier": "premium",
      "requirements": {
        "ollama_required": false,
        "min_ram_gb": 4,
        "api_keys": ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
      },
      "optional_api_keys": ["XAI_API_KEY", "MISTRAL_API_KEY", "DEEPSEEK_API_KEY"],
      "default_models": {
        "foreman_strategic": "claude-3-7-sonnet-20250219",
        "foreman_coordinator": "deepseek-chat",
        "tournament": [
          "claude-3-7-sonnet-20250219",
          "gpt-4o",
          "grok-2",
          "mistral-large-latest",
          "deepseek-chat",
          "qwen-plus"
        ],
        "health_checks": {
          "default": "deepseek-chat",
          "timeline_consistency": "claude-3-7-sonnet-20250219",
          "theme_resonance": "gpt-4o",
          "flaw_challenges": "deepseek-chat",
          "cast_function": "qwen-plus",
          "pacing_analysis": "deepseek-chat",
          "beat_progress": "deepseek-chat",
          "symbolic_layering": "gpt-4o"
        }
      },
      "cost_estimate": {
        "weekly_usd": 3.50,
        "monthly_usd": 15.00
      }
    }
  },
  "model_tiers": {
    "free": ["mistral:7b", "llama3.2:3b"],
    "budget": ["deepseek-chat", "qwen-plus", "zhipu-glm4", "gemini-2.0-flash-exp"],
    "premium": ["claude-3-7-sonnet-20250219", "gpt-4o", "grok-2", "mistral-large-latest"]
  }
}
```

### 2.2 User Squad Settings

**File**: Added to `settings_service.py` defaults

```python
squad: Dict[str, Any] = {
    "active_squad": "hybrid",           # "local" | "hybrid" | "pro"
    "course_mode": False,               # Toggle for instructor-provided keys
    "setup_complete": False,            # Has user completed Squad Builder?

    # Custom overrides (when user wants to deviate from squad defaults)
    "custom_tournament_models": None,   # List[str] or None (use squad default)
    "custom_foreman_strategic": None,   # str or None
    "custom_foreman_coordinator": None, # str or None

    # Local model preferences (discovered via hardware detection)
    "local_models": {
        "available": [],                # Models Ollama reports as installed
        "preferred_strategic": None,    # User's choice for heavy local work
        "preferred_quick": None,        # User's choice for fast local work
    },

    # Smart recommendation results
    "voice_recommendation": {
        "recommended_squad": None,      # Based on voice tournament
        "top_model": None,              # Best voice match
        "top_model_score": None,        # Voice match percentage
        "recommendation_reason": None,  # Explanation text
    }
}
```

### 2.3 Hardware Detection Response

```python
@dataclass
class HardwareInfo:
    ram_gb: int                         # Total RAM
    available_ram_gb: int               # Available RAM
    cpu_cores: int                      # CPU core count
    gpu_available: bool                 # Has GPU acceleration
    gpu_name: Optional[str]             # GPU model name
    gpu_vram_gb: Optional[int]          # GPU VRAM if available
    ollama_installed: bool              # Is Ollama present
    ollama_version: Optional[str]       # Ollama version
    ollama_models: List[str]            # Installed Ollama models
    recommended_max_params: str         # "3b" | "7b" | "12b" | "30b" | "70b"
    platform: str                       # "darwin" | "linux" | "windows"
```

---

## 3. Backend Implementation

### 3.1 New Service: SquadService

**File**: `backend/services/squad_service.py`

```python
"""
Squad Service - Manages squad presets and model selection.

Responsibilities:
1. Load and validate squad presets
2. Detect available squads based on hardware + API keys
3. Apply squad configuration to project settings
4. Provide tournament model recommendations
5. Generate smart recommendations from voice results
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import os

from .settings_service import SettingsService
from .hardware_service import HardwareService


@dataclass
class SquadRequirements:
    ollama_required: bool
    min_ram_gb: int
    api_keys: List[str]
    optional_api_keys: List[str] = None


@dataclass
class SquadPreset:
    id: str
    name: str
    description: str
    icon: str
    tier: str  # "free" | "budget" | "premium"
    recommended: bool
    requirements: SquadRequirements
    default_models: Dict[str, Any]
    fallback: Optional[Dict[str, str]]
    cost_estimate: Dict[str, float]


class SquadService:
    """Manages squad presets and intelligent model selection."""

    def __init__(
        self,
        settings_service: SettingsService,
        hardware_service: 'HardwareService',
        presets_path: str = "backend/config/squad_presets.json"
    ):
        self.settings = settings_service
        self.hardware = hardware_service
        self.presets = self._load_presets(presets_path)
        self.model_tiers = self.presets.get("model_tiers", {})

    def _load_presets(self, path: str) -> Dict:
        """Load squad presets from JSON configuration."""
        with open(path, 'r') as f:
            return json.load(f)

    def get_available_squads(
        self,
        hardware_info: Dict = None,
        check_api_keys: bool = True
    ) -> List[Dict]:
        """
        Returns squads the user can run based on hardware and API keys.

        Args:
            hardware_info: Pre-fetched hardware info (or fetches if None)
            check_api_keys: Whether to validate API key availability

        Returns:
            List of available squad presets with availability status
        """
        if hardware_info is None:
            hardware_info = self.hardware.detect()

        available = []
        for squad_id, preset in self.presets["presets"].items():
            availability = self._check_squad_availability(
                preset, hardware_info, check_api_keys
            )
            available.append({
                **preset,
                "available": availability["available"],
                "missing_requirements": availability["missing"],
                "warnings": availability["warnings"]
            })

        return available

    def _check_squad_availability(
        self,
        preset: Dict,
        hardware: Dict,
        check_keys: bool
    ) -> Dict:
        """Check if a squad can be used."""
        missing = []
        warnings = []

        reqs = preset["requirements"]

        # Check Ollama
        if reqs.get("ollama_required") and not hardware.get("ollama_installed"):
            missing.append("Ollama not installed")

        # Check RAM
        min_ram = reqs.get("min_ram_gb", 0)
        if hardware.get("ram_gb", 0) < min_ram:
            missing.append(f"Requires {min_ram}GB RAM")

        # Check required API keys
        if check_keys:
            for key_name in reqs.get("api_keys", []):
                if not os.environ.get(key_name):
                    missing.append(f"Missing {key_name}")

        # Check optional API keys (warnings only)
        for key_name in preset.get("optional_api_keys", []):
            if not os.environ.get(key_name):
                warnings.append(f"Optional: {key_name} not configured")

        return {
            "available": len(missing) == 0,
            "missing": missing,
            "warnings": warnings
        }

    def apply_squad(
        self,
        squad_id: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Apply a squad's configuration to settings.

        Args:
            squad_id: "local" | "hybrid" | "pro"
            project_id: Optional project-specific override

        Returns:
            Applied configuration summary
        """
        preset = self.presets["presets"].get(squad_id)
        if not preset:
            raise ValueError(f"Unknown squad: {squad_id}")

        # Update squad settings
        self.settings.set("squad.active_squad", squad_id, project_id)
        self.settings.set("squad.setup_complete", True, project_id)

        # Apply Foreman models
        models = preset["default_models"]
        self.settings.set(
            "foreman.task_models.coordinator",
            models["foreman_coordinator"],
            project_id
        )

        # Apply strategic task models
        strategic_model = models["foreman_strategic"]
        strategic_tasks = [
            "health_check_review",
            "voice_calibration_guidance",
            "beat_structure_advice",
            "conflict_resolution",
            "theme_analysis",
            "structural_planning"
        ]
        for task in strategic_tasks:
            self.settings.set(
                f"foreman.task_models.{task}",
                strategic_model,
                project_id
            )

        # Apply health check models
        for check_type, model in models["health_checks"].items():
            self.settings.set(
                f"health_checks.models.{check_type}",
                model,
                project_id
            )

        return {
            "squad": squad_id,
            "applied_models": models,
            "status": "success"
        }

    def get_tournament_models(
        self,
        project_id: Optional[str] = None,
        include_unavailable: bool = False
    ) -> List[Dict]:
        """
        Get models available for tournament selection.

        Returns list of models with tier, availability, and cost info.
        """
        # Get active squad
        squad_id = self.settings.get("squad.active_squad", project_id) or "hybrid"
        preset = self.presets["presets"].get(squad_id, {})

        # Get custom selection if any
        custom = self.settings.get("squad.custom_tournament_models", project_id)
        if custom:
            default_selected = set(custom)
        else:
            default_selected = set(preset.get("default_models", {}).get("tournament", []))

        # Build model list with metadata
        all_models = []
        for tier, models in self.model_tiers.items():
            for model_id in models:
                model_info = self._get_model_info(model_id)
                all_models.append({
                    "id": model_id,
                    "name": model_info.get("name", model_id),
                    "tier": tier,
                    "provider": model_info.get("provider"),
                    "available": self._is_model_available(model_id),
                    "selected": model_id in default_selected,
                    "cost_per_1k_tokens": model_info.get("cost", 0),
                    "description": model_info.get("description", "")
                })

        if not include_unavailable:
            all_models = [m for m in all_models if m["available"]]

        return all_models

    def _get_model_info(self, model_id: str) -> Dict:
        """Get model metadata from agents.yaml or capabilities."""
        # Implementation would look up from agents.yaml
        # Placeholder for now
        return {"name": model_id, "provider": "unknown", "cost": 0}

    def _is_model_available(self, model_id: str) -> bool:
        """Check if model is available (API key present or local)."""
        # Local models always available if Ollama running
        if model_id.startswith(("mistral:", "llama", "ollama-")):
            return self.hardware.is_ollama_running()

        # Map model to API key
        key_map = {
            "deepseek-chat": "DEEPSEEK_API_KEY",
            "qwen-plus": "QWEN_API_KEY",
            "zhipu-glm4": "ZHIPU_API_KEY",
            "gemini-2.0-flash": "GEMINI_API_KEY",
            "claude-": "ANTHROPIC_API_KEY",
            "gpt-4": "OPENAI_API_KEY",
            "grok-": "XAI_API_KEY",
            "mistral-large": "MISTRAL_API_KEY"
        }

        for prefix, key_name in key_map.items():
            if model_id.startswith(prefix) or prefix in model_id:
                return bool(os.environ.get(key_name))

        return False

    def generate_voice_recommendation(
        self,
        tournament_results: List[Dict],
        current_squad: str,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Analyze voice tournament results and recommend squad.

        Args:
            tournament_results: List of {model, score, strategy} from voice tournament
            current_squad: User's current squad selection

        Returns:
            Recommendation with reasoning
        """
        if not tournament_results:
            return {"recommendation": current_squad, "reason": "No tournament data"}

        # Find top performer
        sorted_results = sorted(tournament_results, key=lambda x: x.get("score", 0), reverse=True)
        top = sorted_results[0]
        top_model = top.get("model")
        top_score = top.get("score", 0)

        # Determine which tier the top model belongs to
        top_tier = None
        for tier, models in self.model_tiers.items():
            if top_model in models:
                top_tier = tier
                break

        # Generate recommendation
        recommendation = {
            "top_model": top_model,
            "top_score": top_score,
            "top_tier": top_tier,
            "current_squad": current_squad
        }

        # Logic: If premium model won significantly, recommend Pro Squad
        # If budget model performed comparably, recommend staying with Hybrid
        if top_tier == "premium" and top_score >= 85:
            recommendation["recommended_squad"] = "pro"
            recommendation["reason"] = (
                f"{top_model} achieved {top_score}% voice match. "
                f"Your writing style benefits from premium model capabilities. "
                f"Consider Pro Squad for best results."
            )
            recommendation["alternative"] = (
                f"Budget models scored within 10% - Hybrid Squad "
                f"offers good value if cost is a concern."
            )
        elif top_tier == "budget" or (top_tier == "premium" and top_score < 80):
            recommendation["recommended_squad"] = "hybrid"
            recommendation["reason"] = (
                f"Budget models performed well for your voice. "
                f"Hybrid Squad provides excellent quality at minimal cost."
            )
        else:
            recommendation["recommended_squad"] = current_squad
            recommendation["reason"] = "Your current squad is well-suited to your voice."

        # Save recommendation
        self.settings.set("squad.voice_recommendation", recommendation, project_id)

        return recommendation

    def estimate_tournament_cost(
        self,
        selected_models: List[str],
        num_strategies: int = 5,
        avg_tokens_per_variant: int = 2000
    ) -> Dict:
        """Estimate cost for a tournament run."""
        total_cost = 0.0
        breakdown = []

        for model_id in selected_models:
            info = self._get_model_info(model_id)
            cost_per_1k = info.get("cost", 0) / 1000
            model_cost = cost_per_1k * avg_tokens_per_variant * num_strategies
            total_cost += model_cost
            breakdown.append({
                "model": model_id,
                "variants": num_strategies,
                "cost": model_cost
            })

        return {
            "total_cost": round(total_cost, 4),
            "breakdown": breakdown,
            "total_variants": len(selected_models) * num_strategies
        }
```

### 3.2 New Service: HardwareService

**File**: `backend/services/hardware_service.py`

```python
"""
Hardware Service - Detects system capabilities for local model selection.
"""

import platform
import subprocess
import psutil
from dataclasses import dataclass, asdict
from typing import List, Optional
import json


@dataclass
class HardwareInfo:
    ram_gb: int
    available_ram_gb: int
    cpu_cores: int
    gpu_available: bool
    gpu_name: Optional[str]
    gpu_vram_gb: Optional[int]
    ollama_installed: bool
    ollama_version: Optional[str]
    ollama_models: List[str]
    recommended_max_params: str
    platform: str

    def to_dict(self) -> dict:
        return asdict(self)


class HardwareService:
    """Detects hardware capabilities for local model recommendations."""

    def detect(self) -> HardwareInfo:
        """Run full hardware detection."""
        ram_gb = self._get_ram_gb()
        available_ram = self._get_available_ram_gb()
        cpu_cores = psutil.cpu_count(logical=False) or 4

        gpu_info = self._detect_gpu()
        ollama_info = self._detect_ollama()

        # Calculate recommended model size
        max_params = self._calculate_max_params(ram_gb, gpu_info)

        return HardwareInfo(
            ram_gb=ram_gb,
            available_ram_gb=available_ram,
            cpu_cores=cpu_cores,
            gpu_available=gpu_info["available"],
            gpu_name=gpu_info.get("name"),
            gpu_vram_gb=gpu_info.get("vram_gb"),
            ollama_installed=ollama_info["installed"],
            ollama_version=ollama_info.get("version"),
            ollama_models=ollama_info.get("models", []),
            recommended_max_params=max_params,
            platform=platform.system().lower()
        )

    def _get_ram_gb(self) -> int:
        """Get total system RAM in GB."""
        return round(psutil.virtual_memory().total / (1024**3))

    def _get_available_ram_gb(self) -> int:
        """Get available RAM in GB."""
        return round(psutil.virtual_memory().available / (1024**3))

    def _detect_gpu(self) -> dict:
        """Detect GPU availability and specs."""
        result = {"available": False}

        # Check for Apple Silicon
        if platform.system() == "Darwin" and platform.machine() == "arm64":
            result["available"] = True
            result["name"] = "Apple Silicon (Unified Memory)"
            result["vram_gb"] = self._get_ram_gb()  # Unified memory
            return result

        # Check for NVIDIA GPU
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                stderr=subprocess.DEVNULL
            ).decode()
            if output.strip():
                parts = output.strip().split(",")
                result["available"] = True
                result["name"] = parts[0].strip()
                # Parse VRAM (e.g., "8192 MiB")
                vram_str = parts[1].strip().split()[0]
                result["vram_gb"] = int(vram_str) // 1024
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return result

    def _detect_ollama(self) -> dict:
        """Detect Ollama installation and models."""
        result = {"installed": False, "models": []}

        try:
            # Check version
            version_output = subprocess.check_output(
                ["ollama", "--version"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            result["installed"] = True
            result["version"] = version_output.split()[-1] if version_output else "unknown"

            # Get installed models
            models_output = subprocess.check_output(
                ["ollama", "list"],
                stderr=subprocess.DEVNULL
            ).decode()

            models = []
            for line in models_output.strip().split("\n")[1:]:  # Skip header
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            result["models"] = models

        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        return result

    def _calculate_max_params(self, ram_gb: int, gpu_info: dict) -> str:
        """
        Calculate recommended maximum model parameters.

        Rule of thumb:
        - 3B model: ~4GB RAM
        - 7B model: ~8GB RAM
        - 12B model: ~16GB RAM
        - 30B model: ~32GB RAM
        - 70B model: ~64GB RAM
        """
        # Use GPU VRAM if available, otherwise system RAM
        usable_memory = gpu_info.get("vram_gb") or ram_gb

        if usable_memory >= 64:
            return "70b"
        elif usable_memory >= 32:
            return "30b"
        elif usable_memory >= 16:
            return "12b"
        elif usable_memory >= 8:
            return "7b"
        else:
            return "3b"

    def is_ollama_running(self) -> bool:
        """Check if Ollama server is responding."""
        try:
            import httpx
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            return response.status_code == 200
        except:
            return False

    def get_recommended_local_models(self) -> List[dict]:
        """
        Get recommended local models based on hardware.

        Returns models that should run well on this system.
        """
        info = self.detect()
        max_params = info.recommended_max_params

        # Model recommendations by size tier
        recommendations = {
            "3b": [
                {"id": "llama3.2:3b", "name": "Llama 3.2 3B", "purpose": "Fast coordination"},
                {"id": "phi3:3b", "name": "Phi-3 Mini", "purpose": "Quick drafts"},
            ],
            "7b": [
                {"id": "mistral:7b", "name": "Mistral 7B", "purpose": "General purpose"},
                {"id": "llama3.1:8b", "name": "Llama 3.1 8B", "purpose": "Strong reasoning"},
                {"id": "neural-chat:7b", "name": "Neural Chat 7B", "purpose": "Conversational"},
            ],
            "12b": [
                {"id": "mistral-nemo:12b", "name": "Mistral Nemo 12B", "purpose": "Best local quality"},
                {"id": "solar:10.7b", "name": "Solar 10.7B", "purpose": "Strong prose"},
            ],
            "30b": [
                {"id": "mixtral:8x7b", "name": "Mixtral 8x7B", "purpose": "MoE efficiency"},
                {"id": "command-r:35b", "name": "Command R 35B", "purpose": "Professional"},
            ],
            "70b": [
                {"id": "llama3.1:70b", "name": "Llama 3.1 70B", "purpose": "Maximum local quality"},
                {"id": "qwen2:72b", "name": "Qwen2 72B", "purpose": "Multilingual"},
            ]
        }

        # Collect all models up to max_params tier
        available = []
        param_order = ["3b", "7b", "12b", "30b", "70b"]
        max_index = param_order.index(max_params)

        for i, tier in enumerate(param_order):
            if i <= max_index:
                for model in recommendations.get(tier, []):
                    model["installed"] = model["id"] in info.ollama_models
                    available.append(model)

        return available
```

### 3.3 Updates to Existing Services

#### 3.3.1 Update settings_service.py

Add new defaults:

```python
# Add to SettingsDefaults class (around line 170)

squad: Dict[str, Any] = {
    "active_squad": "hybrid",
    "course_mode": False,
    "setup_complete": False,
    "custom_tournament_models": None,
    "custom_foreman_strategic": None,
    "custom_foreman_coordinator": None,
    "local_models": {
        "available": [],
        "preferred_strategic": None,
        "preferred_quick": None,
    },
    "voice_recommendation": {
        "recommended_squad": None,
        "top_model": None,
        "top_model_score": None,
        "recommendation_reason": None,
    }
}
```

#### 3.3.2 Update scene_writer_service.py

Modify tournament to accept model selection:

```python
# Update generate_tournament around line 150

async def generate_tournament(
    self,
    scene_context: SceneContext,
    models: List[str] = None,  # NEW: Accept custom model list
    strategies: List[WritingStrategy] = None,
    project_id: str = None
) -> TournamentResult:
    """
    Generate tournament variants using specified or default models.

    Args:
        scene_context: Scene information and constraints
        models: List of model IDs to use (None = use squad defaults)
        strategies: Writing strategies to apply (None = all)
        project_id: For project-specific settings
    """
    # Get models from squad if not specified
    if models is None:
        from .squad_service import squad_service
        squad_models = squad_service.get_tournament_models(project_id)
        models = [m["id"] for m in squad_models if m["selected"]]

    # Fall back to defaults if still empty
    if not models:
        models = [m["model"] for m in DEFAULT_TOURNAMENT_MODELS]

    # Rest of implementation...
```

#### 3.3.3 Update voice_calibration_service.py

Similar changes to accept model selection and generate recommendations.

---

## 4. Frontend Implementation

### 4.1 Squad Builder Wizard

**File**: `frontend/src/lib/components/SquadBuilderWizard.svelte`

```svelte
<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  // State
  let step = 1; // 1: hardware, 2: select, 3: setup, 4: complete
  let hardwareInfo = null;
  let availableSquads = [];
  let selectedSquad = null;
  let setupProgress = 0;
  let error = null;

  // Course mode
  export let courseMode = false;

  onMount(async () => {
    await detectHardware();
  });

  async function detectHardware() {
    try {
      hardwareInfo = await apiClient.getHardwareInfo();
      availableSquads = await apiClient.getAvailableSquads();

      // Pre-select recommended squad
      selectedSquad = availableSquads.find(s => s.recommended && s.available)
        || availableSquads.find(s => s.available)
        || availableSquads[0];

      step = 2;
    } catch (e) {
      error = `Hardware detection failed: ${e.message}`;
    }
  }

  async function applySquad() {
    if (!selectedSquad) return;

    step = 3;
    setupProgress = 10;

    try {
      // Apply squad configuration
      setupProgress = 30;
      await apiClient.applySquad(selectedSquad.id);

      // Download local models if needed (Ollama pull)
      if (selectedSquad.requirements.ollama_required) {
        setupProgress = 50;
        // This would trigger Ollama downloads
        // await apiClient.ensureLocalModels(selectedSquad.default_models);
      }

      setupProgress = 100;
      step = 4;

      // Notify parent
      setTimeout(() => {
        dispatch('complete', { squad: selectedSquad.id });
      }, 1500);

    } catch (e) {
      error = `Setup failed: ${e.message}`;
      step = 2;
    }
  }

  function getTierBadge(tier: string) {
    switch (tier) {
      case 'free': return { text: 'FREE', class: 'badge-success' };
      case 'budget': return { text: 'BUDGET', class: 'badge-info' };
      case 'premium': return { text: 'PREMIUM', class: 'badge-warning' };
      default: return { text: tier, class: 'badge-secondary' };
    }
  }
</script>

<div class="squad-wizard">
  <!-- Step 1: Hardware Detection -->
  {#if step === 1}
    <div class="wizard-step">
      <h2>Scanning Your System...</h2>
      <div class="spinner"></div>
      <p>Detecting hardware capabilities</p>
    </div>
  {/if}

  <!-- Step 2: Squad Selection -->
  {#if step === 2}
    <div class="wizard-step">
      <h2>Choose Your Squad</h2>

      {#if hardwareInfo}
        <div class="hardware-summary">
          <span class="check">✓</span> {hardwareInfo.ram_gb}GB RAM
          {#if hardwareInfo.ollama_installed}
            <span class="check">✓</span> Ollama v{hardwareInfo.ollama_version}
          {:else}
            <span class="warn">!</span> Ollama not installed
          {/if}
          {#if hardwareInfo.gpu_available}
            <span class="check">✓</span> {hardwareInfo.gpu_name}
          {/if}
          <span class="info">Can run up to {hardwareInfo.recommended_max_params} models</span>
        </div>
      {/if}

      <div class="squad-options">
        {#each availableSquads as squad}
          <button
            class="squad-card"
            class:selected={selectedSquad?.id === squad.id}
            class:unavailable={!squad.available}
            disabled={!squad.available}
            on:click={() => selectedSquad = squad}
          >
            <div class="squad-header">
              <span class="squad-icon">{squad.icon}</span>
              <h3>{squad.name}</h3>
              <span class="badge {getTierBadge(squad.tier).class}">
                {getTierBadge(squad.tier).text}
              </span>
            </div>

            <p class="squad-description">{squad.description}</p>

            <div class="squad-models">
              <strong>Models:</strong>
              <ul>
                <li>Strategic: {squad.default_models.foreman_strategic}</li>
                <li>Tournament: {squad.default_models.tournament.length} models</li>
              </ul>
            </div>

            <div class="squad-cost">
              <span class="cost-amount">
                {squad.cost_estimate.weekly_usd === 0
                  ? 'Free'
                  : `~$${squad.cost_estimate.weekly_usd}/week`}
              </span>
            </div>

            {#if !squad.available}
              <div class="missing-requirements">
                {#each squad.missing_requirements as req}
                  <span class="missing">✗ {req}</span>
                {/each}
              </div>
            {/if}

            {#if squad.recommended && squad.available}
              <div class="recommended-badge">★ Recommended</div>
            {/if}
          </button>
        {/each}
      </div>

      <div class="wizard-actions">
        <button
          class="btn-primary"
          disabled={!selectedSquad?.available}
          on:click={applySquad}
        >
          Continue with {selectedSquad?.name || 'Selected Squad'}
        </button>
      </div>
    </div>
  {/if}

  <!-- Step 3: Setup Progress -->
  {#if step === 3}
    <div class="wizard-step">
      <h2>Setting Up {selectedSquad.name}</h2>
      <div class="progress-bar">
        <div class="progress-fill" style="width: {setupProgress}%"></div>
      </div>
      <p>
        {#if setupProgress < 30}
          Applying configuration...
        {:else if setupProgress < 70}
          Preparing models...
        {:else}
          Finalizing setup...
        {/if}
      </p>
    </div>
  {/if}

  <!-- Step 4: Complete -->
  {#if step === 4}
    <div class="wizard-step complete">
      <div class="success-icon">✓</div>
      <h2>{selectedSquad.name} Ready!</h2>
      <p>Your AI writing team is configured and ready to help.</p>
    </div>
  {/if}

  {#if error}
    <div class="error-message">{error}</div>
  {/if}
</div>

<style>
  .squad-wizard {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
  }

  .wizard-step {
    text-align: center;
  }

  .hardware-summary {
    background: var(--bg-secondary);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 2rem;
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .check { color: var(--success); }
  .warn { color: var(--warning); }
  .info { color: var(--info); font-style: italic; }

  .squad-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
  }

  .squad-card {
    background: var(--bg-primary);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }

  .squad-card:hover:not(:disabled) {
    border-color: var(--accent);
    transform: translateY(-2px);
  }

  .squad-card.selected {
    border-color: var(--accent);
    background: var(--bg-accent);
  }

  .squad-card.unavailable {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .squad-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .squad-icon {
    font-size: 1.5rem;
  }

  .badge {
    font-size: 0.7rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    margin-left: auto;
  }

  .badge-success { background: var(--success); color: white; }
  .badge-info { background: var(--info); color: white; }
  .badge-warning { background: var(--warning); color: black; }

  .recommended-badge {
    position: absolute;
    top: -10px;
    right: -10px;
    background: var(--accent);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
  }

  .progress-bar {
    width: 100%;
    height: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
    overflow: hidden;
    margin: 2rem 0;
  }

  .progress-fill {
    height: 100%;
    background: var(--accent);
    transition: width 0.3s;
  }

  .success-icon {
    font-size: 4rem;
    color: var(--success);
    margin-bottom: 1rem;
  }
</style>
```

### 4.2 Tournament Model Selector

**File**: `frontend/src/lib/components/TournamentModelSelector.svelte`

```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { apiClient } from '$lib/api_client';

  const dispatch = createEventDispatcher();

  export let selectedModels: string[] = [];
  export let availableModels: any[] = [];

  let costEstimate = { total_cost: 0, total_variants: 0 };

  $: {
    // Recalculate cost when selection changes
    if (selectedModels.length > 0) {
      updateCostEstimate();
    }
  }

  async function updateCostEstimate() {
    try {
      costEstimate = await apiClient.estimateTournamentCost(selectedModels);
    } catch (e) {
      console.error('Cost estimation failed:', e);
    }
  }

  function toggleModel(modelId: string) {
    if (selectedModels.includes(modelId)) {
      selectedModels = selectedModels.filter(m => m !== modelId);
    } else {
      selectedModels = [...selectedModels, modelId];
    }
    dispatch('change', { selected: selectedModels });
  }

  function selectAll(tier: string) {
    const tierModels = availableModels
      .filter(m => m.tier === tier && m.available)
      .map(m => m.id);
    selectedModels = [...new Set([...selectedModels, ...tierModels])];
    dispatch('change', { selected: selectedModels });
  }

  function clearAll() {
    selectedModels = [];
    dispatch('change', { selected: selectedModels });
  }

  // Group models by tier
  $: modelsByTier = {
    free: availableModels.filter(m => m.tier === 'free'),
    budget: availableModels.filter(m => m.tier === 'budget'),
    premium: availableModels.filter(m => m.tier === 'premium')
  };
</script>

<div class="tournament-selector">
  <div class="selector-header">
    <h3>Select Tournament Participants</h3>
    <div class="quick-actions">
      <button on:click={() => selectAll('budget')}>+ Budget</button>
      <button on:click={() => selectAll('premium')}>+ Premium</button>
      <button on:click={clearAll}>Clear</button>
    </div>
  </div>

  <!-- Free Tier -->
  {#if modelsByTier.free.length > 0}
    <div class="tier-section">
      <h4>🏠 Free (Local)</h4>
      <div class="model-grid">
        {#each modelsByTier.free as model}
          <label
            class="model-option"
            class:unavailable={!model.available}
          >
            <input
              type="checkbox"
              checked={selectedModels.includes(model.id)}
              disabled={!model.available}
              on:change={() => toggleModel(model.id)}
            />
            <span class="model-name">{model.name}</span>
            <span class="model-cost">$0</span>
          </label>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Budget Tier -->
  {#if modelsByTier.budget.length > 0}
    <div class="tier-section">
      <h4>💎 Budget</h4>
      <div class="model-grid">
        {#each modelsByTier.budget as model}
          <label
            class="model-option"
            class:unavailable={!model.available}
          >
            <input
              type="checkbox"
              checked={selectedModels.includes(model.id)}
              disabled={!model.available}
              on:change={() => toggleModel(model.id)}
            />
            <span class="model-name">{model.name}</span>
            <span class="model-cost">
              ${(model.cost_per_1k_tokens * 2).toFixed(3)}
            </span>
            {#if !model.available}
              <span class="unavailable-reason">No API key</span>
            {/if}
          </label>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Premium Tier -->
  {#if modelsByTier.premium.length > 0}
    <div class="tier-section">
      <h4>🚀 Premium</h4>
      <div class="model-grid">
        {#each modelsByTier.premium as model}
          <label
            class="model-option"
            class:unavailable={!model.available}
          >
            <input
              type="checkbox"
              checked={selectedModels.includes(model.id)}
              disabled={!model.available}
              on:change={() => toggleModel(model.id)}
            />
            <span class="model-name">{model.name}</span>
            <span class="model-cost">
              ${(model.cost_per_1k_tokens * 2).toFixed(3)}
            </span>
            {#if !model.available}
              <span class="unavailable-reason">No API key</span>
            {/if}
          </label>
        {/each}
      </div>
    </div>
  {/if}

  <!-- Cost Summary -->
  <div class="cost-summary">
    <div class="summary-row">
      <span>Selected:</span>
      <strong>{selectedModels.length} models</strong>
    </div>
    <div class="summary-row">
      <span>Variants:</span>
      <strong>{costEstimate.total_variants} (5 strategies each)</strong>
    </div>
    <div class="summary-row total">
      <span>Estimated Cost:</span>
      <strong>
        {costEstimate.total_cost === 0
          ? 'Free'
          : `$${costEstimate.total_cost.toFixed(4)}`}
      </strong>
    </div>
  </div>
</div>

<style>
  .tournament-selector {
    background: var(--bg-secondary);
    border-radius: 8px;
    padding: 1rem;
  }

  .selector-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .quick-actions {
    display: flex;
    gap: 0.5rem;
  }

  .quick-actions button {
    font-size: 0.8rem;
    padding: 0.25rem 0.5rem;
  }

  .tier-section {
    margin-bottom: 1rem;
  }

  .tier-section h4 {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
  }

  .model-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.5rem;
  }

  .model-option {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--bg-primary);
    border-radius: 4px;
    cursor: pointer;
  }

  .model-option:hover {
    background: var(--bg-hover);
  }

  .model-option.unavailable {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .model-name {
    flex: 1;
  }

  .model-cost {
    color: var(--text-secondary);
    font-size: 0.85rem;
  }

  .unavailable-reason {
    font-size: 0.7rem;
    color: var(--warning);
  }

  .cost-summary {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .summary-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
  }

  .summary-row.total {
    font-size: 1.1rem;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--border);
  }
</style>
```

### 4.3 API Client Updates

**File**: `frontend/src/lib/api_client.ts` (additions)

```typescript
// Add to ApiClient class

// Squad Management
async getHardwareInfo(): Promise<HardwareInfo> {
  return this.get('/system/hardware');
}

async getAvailableSquads(): Promise<SquadPreset[]> {
  return this.get('/squad/available');
}

async applySquad(squadId: string, projectId?: string): Promise<void> {
  return this.post('/squad/apply', { squad_id: squadId, project_id: projectId });
}

async getActiveSquad(projectId?: string): Promise<string> {
  return this.get('/squad/active', { project_id: projectId });
}

// Tournament Model Selection
async getTournamentModels(projectId?: string): Promise<TournamentModel[]> {
  return this.get('/squad/tournament-models', { project_id: projectId });
}

async estimateTournamentCost(models: string[]): Promise<CostEstimate> {
  return this.post('/squad/estimate-cost', { models });
}

async setTournamentModels(models: string[], projectId?: string): Promise<void> {
  return this.post('/squad/tournament-models', { models, project_id: projectId });
}

// Voice Recommendation
async getVoiceRecommendation(projectId?: string): Promise<VoiceRecommendation> {
  return this.get('/squad/voice-recommendation', { project_id: projectId });
}

// Types
interface HardwareInfo {
  ram_gb: number;
  available_ram_gb: number;
  cpu_cores: number;
  gpu_available: boolean;
  gpu_name?: string;
  gpu_vram_gb?: number;
  ollama_installed: boolean;
  ollama_version?: string;
  ollama_models: string[];
  recommended_max_params: string;
  platform: string;
}

interface SquadPreset {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: string;
  recommended: boolean;
  available: boolean;
  missing_requirements: string[];
  warnings: string[];
  default_models: {
    foreman_strategic: string;
    foreman_coordinator: string;
    tournament: string[];
    health_checks: Record<string, string>;
  };
  cost_estimate: {
    weekly_usd: number;
    monthly_usd: number;
  };
}

interface TournamentModel {
  id: string;
  name: string;
  tier: string;
  provider: string;
  available: boolean;
  selected: boolean;
  cost_per_1k_tokens: number;
  description: string;
}

interface CostEstimate {
  total_cost: number;
  total_variants: number;
  breakdown: Array<{
    model: string;
    variants: number;
    cost: number;
  }>;
}

interface VoiceRecommendation {
  recommended_squad: string;
  top_model: string;
  top_score: number;
  recommendation_reason: string;
  alternative?: string;
}
```

---

## 5. API Endpoints

### 5.1 New Endpoints

Add to `backend/api.py`:

```python
# ==================== SQUAD ENDPOINTS ====================

from services.squad_service import SquadService
from services.hardware_service import HardwareService

hardware_service = HardwareService()
squad_service = SquadService(settings_service, hardware_service)


@app.get("/system/hardware")
async def get_hardware_info():
    """Detect system hardware capabilities."""
    info = hardware_service.detect()
    return info.to_dict()


@app.get("/squad/available")
async def get_available_squads():
    """Get squads available based on hardware and API keys."""
    return squad_service.get_available_squads()


@app.post("/squad/apply")
async def apply_squad(request: ApplySquadRequest):
    """Apply a squad configuration."""
    return squad_service.apply_squad(request.squad_id, request.project_id)


@app.get("/squad/active")
async def get_active_squad(project_id: str = None):
    """Get currently active squad."""
    return {
        "squad": settings_service.get("squad.active_squad", project_id) or "hybrid"
    }


@app.get("/squad/tournament-models")
async def get_tournament_models(project_id: str = None):
    """Get models available for tournament selection."""
    return squad_service.get_tournament_models(project_id)


@app.post("/squad/tournament-models")
async def set_tournament_models(request: SetTournamentModelsRequest):
    """Set custom tournament model selection."""
    settings_service.set(
        "squad.custom_tournament_models",
        request.models,
        request.project_id
    )
    return {"status": "success"}


@app.post("/squad/estimate-cost")
async def estimate_tournament_cost(request: EstimateCostRequest):
    """Estimate cost for tournament with selected models."""
    return squad_service.estimate_tournament_cost(request.models)


@app.get("/squad/voice-recommendation")
async def get_voice_recommendation(project_id: str = None):
    """Get voice-based squad recommendation."""
    return settings_service.get("squad.voice_recommendation", project_id)


@app.post("/squad/voice-recommendation")
async def generate_voice_recommendation(request: VoiceRecommendationRequest):
    """Generate squad recommendation from voice tournament results."""
    return squad_service.generate_voice_recommendation(
        request.tournament_results,
        request.current_squad,
        request.project_id
    )


# Request models
class ApplySquadRequest(BaseModel):
    squad_id: str
    project_id: Optional[str] = None


class SetTournamentModelsRequest(BaseModel):
    models: List[str]
    project_id: Optional[str] = None


class EstimateCostRequest(BaseModel):
    models: List[str]
    num_strategies: int = 5
    avg_tokens_per_variant: int = 2000


class VoiceRecommendationRequest(BaseModel):
    tournament_results: List[Dict]
    current_squad: str
    project_id: Optional[str] = None
```

---

## 6. Migration Strategy

### 6.1 For New Users

1. App opens → Story Bible creation starts with DeepSeek V3 (subsidized)
2. After Story Bible complete → Squad Builder Wizard appears
3. User chooses squad → Configuration applied automatically
4. Voice Tournament runs → Smart recommendation shown
5. User confirms or adjusts → Ready to write

### 6.2 For Existing Users

1. On app update → "New: Squad System" banner shown
2. User clicks → Squad Builder Wizard
3. System detects current configuration → Suggests matching squad
4. User confirms → Migrated to new system
5. All existing settings preserved as "custom overrides"

### 6.3 Data Migration

```python
def migrate_to_squad_system(project_id: str = None):
    """Migrate existing configuration to squad system."""

    # Detect current configuration
    foreman_model = settings_service.get("foreman.coordinator_model", project_id)
    tournament_models = settings_service.get("tournament.models", project_id)

    # Determine best matching squad
    if any(m in str(tournament_models) for m in ["claude", "gpt-4"]):
        suggested_squad = "pro"
    elif foreman_model and "deepseek" in foreman_model:
        suggested_squad = "hybrid"
    else:
        suggested_squad = "local"

    # Store as custom overrides (don't lose existing config)
    settings_service.set("squad.custom_tournament_models", tournament_models, project_id)
    settings_service.set("squad.active_squad", suggested_squad, project_id)
    settings_service.set("squad.setup_complete", False, project_id)  # Show wizard

    return suggested_squad
```

---

## 7. Testing Plan

### 7.1 Unit Tests

```python
# tests/test_squad_service.py

def test_squad_availability_detection():
    """Test that squads are correctly marked available/unavailable."""
    pass

def test_apply_squad_updates_settings():
    """Test that applying a squad updates all relevant settings."""
    pass

def test_tournament_model_selection():
    """Test tournament model list respects squad configuration."""
    pass

def test_cost_estimation():
    """Test cost estimation accuracy."""
    pass

def test_voice_recommendation_generation():
    """Test smart recommendation logic."""
    pass
```

### 7.2 Integration Tests

```python
# tests/test_squad_integration.py

async def test_full_squad_workflow():
    """Test complete squad selection and tournament flow."""
    # 1. Detect hardware
    # 2. Get available squads
    # 3. Apply hybrid squad
    # 4. Run tournament with squad models
    # 5. Verify results
    pass
```

### 7.3 Manual Testing Checklist

- [ ] Hardware detection works on Mac/Windows/Linux
- [ ] Ollama detection works when running/not running
- [ ] Squad Builder Wizard displays correctly
- [ ] Unavailable squads are properly disabled
- [ ] Applying squad updates all settings
- [ ] Tournament respects selected models
- [ ] Cost estimation is accurate
- [ ] Voice recommendation appears after tournament
- [ ] Course mode toggle works
- [ ] Migration from existing config works

---

## 8. File Checklist

### 8.1 New Files to Create

| File | Purpose |
|------|---------|
| `backend/config/squad_presets.json` | Squad preset definitions |
| `backend/services/squad_service.py` | Squad management logic |
| `backend/services/hardware_service.py` | Hardware detection |
| `frontend/src/lib/components/SquadBuilderWizard.svelte` | Wizard UI |
| `frontend/src/lib/components/TournamentModelSelector.svelte` | Model selector |

### 8.2 Files to Modify

| File | Changes |
|------|---------|
| `backend/api.py` | Add squad endpoints |
| `backend/services/settings_service.py` | Add squad defaults |
| `backend/services/scene_writer_service.py` | Accept model selection |
| `backend/services/voice_calibration_service.py` | Accept model selection |
| `frontend/src/lib/api_client.ts` | Add squad API methods |
| `docs/CONFIGURABLE_MODEL_ASSIGNMENTS.md` | Update with squad info |

### 8.3 Implementation Order

1. **Phase 1: Backend Foundation**
   - [ ] Create `squad_presets.json`
   - [ ] Create `hardware_service.py`
   - [ ] Create `squad_service.py`
   - [ ] Add squad defaults to `settings_service.py`
   - [ ] Add API endpoints to `api.py`

2. **Phase 2: Tournament Integration**
   - [ ] Update `scene_writer_service.py`
   - [ ] Update `voice_calibration_service.py`
   - [ ] Add voice recommendation generation

3. **Phase 3: Frontend**
   - [ ] Update `api_client.ts`
   - [ ] Create `SquadBuilderWizard.svelte`
   - [ ] Create `TournamentModelSelector.svelte`
   - [ ] Integrate wizard into app flow

4. **Phase 4: Polish**
   - [ ] Migration script
   - [ ] Testing
   - [ ] Documentation update

---

## Appendix: Cost Estimates

### Model Pricing (per 1M tokens)

| Model | Input | Output | Tier |
|-------|-------|--------|------|
| mistral:7b | $0.00 | $0.00 | Free |
| llama3.2:3b | $0.00 | $0.00 | Free |
| deepseek-chat | $0.27 | $1.10 | Budget |
| qwen-plus | $0.40 | $1.20 | Budget |
| zhipu-glm4 | $0.50 | $0.50 | Budget |
| gemini-flash | $0.075 | $0.30 | Budget |
| claude-sonnet | $3.00 | $15.00 | Premium |
| gpt-4o | $2.50 | $10.00 | Premium |
| grok-2 | $2.00 | $10.00 | Premium |
| mistral-large | $2.00 | $6.00 | Premium |

### Weekly Cost Estimates (Heavy Usage)

| Squad | Tasks/Week | Est. Cost |
|-------|------------|-----------|
| Local | Unlimited | $0.00 |
| Hybrid | 500 | $0.40-0.60 |
| Pro | 500 | $3.00-5.00 |

---

*Document Version: 1.0*
*Created: November 25, 2025*
*Status: Ready for Implementation*
