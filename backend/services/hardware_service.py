"""
Hardware Service - Detects system capabilities for local model selection.

This service scans the user's hardware to determine:
1. RAM available for loading models
2. GPU availability (NVIDIA or Apple Silicon)
3. Ollama installation status and installed models
4. Recommended maximum model size

Used by SquadService to determine which squads are available.
"""

import platform
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class HardwareInfo:
    """Complete hardware profile for model selection decisions."""

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
    """
    Detects hardware capabilities for local model recommendations.

    This service helps the Squad system determine:
    - Which local models can run on this machine
    - Whether Ollama is available
    - What size models are recommended
    """

    def detect(self) -> HardwareInfo:
        """
        Run full hardware detection.

        Returns:
            HardwareInfo with all detected capabilities
        """
        ram_gb = self._get_ram_gb()
        available_ram = self._get_available_ram_gb()
        cpu_cores = self._get_cpu_cores()

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
        try:
            import psutil
            return round(psutil.virtual_memory().total / (1024**3))
        except ImportError:
            # Fallback without psutil
            return self._get_ram_fallback()

    def _get_ram_fallback(self) -> int:
        """Fallback RAM detection without psutil."""
        system = platform.system()

        try:
            if system == "Darwin":
                # macOS
                output = subprocess.check_output(
                    ["sysctl", "-n", "hw.memsize"],
                    stderr=subprocess.DEVNULL
                ).decode().strip()
                return int(output) // (1024**3)
            elif system == "Linux":
                # Linux
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        if line.startswith("MemTotal:"):
                            kb = int(line.split()[1])
                            return kb // (1024**2)
            elif system == "Windows":
                # Windows
                output = subprocess.check_output(
                    ["wmic", "ComputerSystem", "get", "TotalPhysicalMemory"],
                    stderr=subprocess.DEVNULL
                ).decode()
                lines = [l.strip() for l in output.split("\n") if l.strip().isdigit()]
                if lines:
                    return int(lines[0]) // (1024**3)
        except Exception as e:
            logger.warning(f"RAM detection fallback failed: {e}")

        return 8  # Conservative default

    def _get_available_ram_gb(self) -> int:
        """Get available RAM in GB."""
        try:
            import psutil
            return round(psutil.virtual_memory().available / (1024**3))
        except ImportError:
            # Assume half of total is available
            return self._get_ram_gb() // 2

    def _get_cpu_cores(self) -> int:
        """Get CPU core count."""
        try:
            import psutil
            return psutil.cpu_count(logical=False) or 4
        except ImportError:
            import os
            return os.cpu_count() or 4

    def _detect_gpu(self) -> dict:
        """
        Detect GPU availability and specs.

        Checks for:
        1. Apple Silicon (unified memory)
        2. NVIDIA GPU (via nvidia-smi)
        """
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
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode()
            if output.strip():
                parts = output.strip().split(",")
                result["available"] = True
                result["name"] = parts[0].strip()
                # Parse VRAM (e.g., "8192 MiB")
                vram_str = parts[1].strip().split()[0]
                result["vram_gb"] = int(vram_str) // 1024
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return result

    def _detect_ollama(self) -> dict:
        """
        Detect Ollama installation and installed models.

        Returns:
            dict with 'installed', 'version', and 'models' keys
        """
        result = {"installed": False, "models": []}

        try:
            # Check version
            version_output = subprocess.check_output(
                ["ollama", "--version"],
                stderr=subprocess.DEVNULL,
                timeout=5
            ).decode().strip()
            result["installed"] = True

            # Parse version (format: "ollama version 0.1.45")
            parts = version_output.split()
            result["version"] = parts[-1] if parts else "unknown"

            # Get installed models
            try:
                models_output = subprocess.check_output(
                    ["ollama", "list"],
                    stderr=subprocess.DEVNULL,
                    timeout=10
                ).decode()

                models = []
                lines = models_output.strip().split("\n")
                for line in lines[1:]:  # Skip header row
                    if line.strip():
                        # Format: "NAME ID SIZE MODIFIED"
                        model_name = line.split()[0]
                        models.append(model_name)
                result["models"] = models
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.warning("Could not list Ollama models")

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.info("Ollama not installed or not responding")

        return result

    def _calculate_max_params(self, ram_gb: int, gpu_info: dict) -> str:
        """
        Calculate recommended maximum model parameters.

        Rule of thumb for quantized models (Q4_K_M):
        - 3B model: ~2-3GB RAM
        - 7B model: ~4-5GB RAM
        - 12B model: ~8-10GB RAM
        - 30B model: ~20GB RAM
        - 70B model: ~40GB RAM

        Args:
            ram_gb: Total system RAM
            gpu_info: GPU detection results

        Returns:
            Recommended max params: "3b", "7b", "12b", "30b", or "70b"
        """
        # Use GPU VRAM if available and substantial, otherwise system RAM
        if gpu_info.get("available"):
            vram = gpu_info.get("vram_gb", 0)
            # For Apple Silicon, use ~75% of unified memory for models
            if "Apple Silicon" in gpu_info.get("name", ""):
                usable_memory = int(ram_gb * 0.75)
            else:
                # For discrete GPU, can use VRAM + some system RAM
                usable_memory = vram + min(ram_gb // 4, 8)
        else:
            # CPU-only: use ~60% of RAM (need room for OS and app)
            usable_memory = int(ram_gb * 0.6)

        # Map memory to max model size
        if usable_memory >= 40:
            return "70b"
        elif usable_memory >= 20:
            return "30b"
        elif usable_memory >= 10:
            return "12b"
        elif usable_memory >= 5:
            return "7b"
        else:
            return "3b"

    def is_ollama_running(self) -> bool:
        """
        Check if Ollama server is responding.

        Returns:
            True if Ollama API is reachable
        """
        try:
            import httpx
            response = httpx.get(
                "http://localhost:11434/api/tags",
                timeout=2.0
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_recommended_local_models(self) -> List[dict]:
        """
        Get recommended local models based on hardware.

        Returns models that should run well on this system,
        organized by purpose.

        Returns:
            List of model recommendations with metadata
        """
        info = self.detect()
        max_params = info.recommended_max_params

        # Model recommendations by size tier
        recommendations = {
            "3b": [
                {
                    "id": "llama3.2:3b",
                    "name": "Llama 3.2 3B",
                    "purpose": "Fast coordination",
                    "size_gb": 2.0
                },
                {
                    "id": "phi3:3b",
                    "name": "Phi-3 Mini",
                    "purpose": "Quick drafts",
                    "size_gb": 2.3
                },
            ],
            "7b": [
                {
                    "id": "mistral:7b",
                    "name": "Mistral 7B",
                    "purpose": "General purpose",
                    "size_gb": 4.1
                },
                {
                    "id": "llama3.1:8b",
                    "name": "Llama 3.1 8B",
                    "purpose": "Strong reasoning",
                    "size_gb": 4.7
                },
                {
                    "id": "neural-chat:7b",
                    "name": "Neural Chat 7B",
                    "purpose": "Conversational",
                    "size_gb": 4.1
                },
            ],
            "12b": [
                {
                    "id": "mistral-nemo:12b",
                    "name": "Mistral Nemo 12B",
                    "purpose": "Best local quality",
                    "size_gb": 7.1
                },
                {
                    "id": "solar:10.7b",
                    "name": "Solar 10.7B",
                    "purpose": "Strong prose",
                    "size_gb": 6.1
                },
            ],
            "30b": [
                {
                    "id": "mixtral:8x7b",
                    "name": "Mixtral 8x7B",
                    "purpose": "MoE efficiency",
                    "size_gb": 26.0
                },
                {
                    "id": "command-r:35b",
                    "name": "Command R 35B",
                    "purpose": "Professional quality",
                    "size_gb": 20.0
                },
            ],
            "70b": [
                {
                    "id": "llama3.1:70b",
                    "name": "Llama 3.1 70B",
                    "purpose": "Maximum local quality",
                    "size_gb": 40.0
                },
                {
                    "id": "qwen2:72b",
                    "name": "Qwen2 72B",
                    "purpose": "Multilingual excellence",
                    "size_gb": 41.0
                },
            ]
        }

        # Collect all models up to max_params tier
        available = []
        param_order = ["3b", "7b", "12b", "30b", "70b"]
        max_index = param_order.index(max_params)

        for i, tier in enumerate(param_order):
            if i <= max_index:
                for model in recommendations.get(tier, []):
                    model_copy = model.copy()
                    model_copy["installed"] = model["id"] in info.ollama_models
                    model_copy["tier"] = tier
                    available.append(model_copy)

        return available

    async def pull_model(self, model_id: str) -> dict:
        """
        Trigger Ollama to pull a model.

        This is an async operation - the model downloads in the background.

        Args:
            model_id: Ollama model ID to pull

        Returns:
            Status dict with 'success' and 'message' keys
        """
        try:
            # Start the pull process
            process = subprocess.Popen(
                ["ollama", "pull", model_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Don't wait for completion - return immediately
            return {
                "success": True,
                "message": f"Started downloading {model_id}",
                "model_id": model_id
            }
        except FileNotFoundError:
            return {
                "success": False,
                "message": "Ollama not installed",
                "model_id": model_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "model_id": model_id
            }


# Singleton instance
hardware_service = HardwareService()
