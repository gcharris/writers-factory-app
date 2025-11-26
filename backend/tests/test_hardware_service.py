"""
Tests for HardwareService - System Capability Detection for Local Models

This service detects:
1. RAM (total and available)
2. CPU cores
3. GPU availability (Apple Silicon, NVIDIA)
4. Ollama installation, version, and installed models
5. Recommended model size based on hardware

Test Coverage:
- Hardware detection (RAM, CPU, GPU)
- Ollama detection and model listing
- Model size recommendations
- Fallback mechanisms when dependencies are unavailable
- Edge cases (missing tools, timeouts, etc.)
"""

import pytest
import platform
from unittest.mock import Mock, patch, MagicMock
import subprocess

from backend.services.hardware_service import (
    HardwareService,
    HardwareInfo,
)

# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def hardware_service():
    """Create HardwareService instance for testing."""
    return HardwareService()


@pytest.fixture
def mock_darwin_system():
    """Mock macOS system."""
    with patch('platform.system', return_value='Darwin'), \
         patch('platform.machine', return_value='arm64'):
        yield


@pytest.fixture
def mock_linux_system():
    """Mock Linux system."""
    with patch('platform.system', return_value='Linux'):
        yield


@pytest.fixture
def mock_windows_system():
    """Mock Windows system."""
    with patch('platform.system', return_value='Windows'):
        yield


# =============================================================================
# Test: Hardware Detection
# =============================================================================

class TestHardwareDetection:
    """Test hardware detection methods."""

    def test_detect_returns_complete_info(self, hardware_service):
        """Test that detect() returns HardwareInfo with all fields."""
        info = hardware_service.detect()

        assert isinstance(info, HardwareInfo)
        assert info.ram_gb > 0
        assert info.available_ram_gb >= 0
        assert info.cpu_cores > 0
        assert isinstance(info.gpu_available, bool)
        assert isinstance(info.ollama_installed, bool)
        assert isinstance(info.ollama_models, list)
        assert info.recommended_max_params in ["3b", "7b", "12b", "30b", "70b"]
        assert info.platform in ["darwin", "linux", "windows"]

    def test_get_ram_with_psutil(self, hardware_service):
        """Test RAM detection with psutil available."""
        mock_memory = Mock()
        mock_memory.total = 16 * (1024**3)  # 16GB

        mock_psutil = Mock()
        mock_psutil.virtual_memory.return_value = mock_memory

        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            ram = hardware_service._get_ram_gb()

            assert ram == 16

    def test_get_ram_fallback_darwin(self, hardware_service, mock_darwin_system):
        """Test RAM detection fallback on macOS."""
        # Mock psutil to raise ImportError
        with patch.dict('sys.modules', {'psutil': None}), \
             patch('subprocess.check_output', return_value=b'17179869184\n'):  # 16GB in bytes
            ram = hardware_service._get_ram_gb()

            assert ram == 16

    def test_get_ram_fallback_linux(self, hardware_service, mock_linux_system):
        """Test RAM detection fallback on Linux."""
        meminfo_content = """MemTotal:       16384000 kB
MemFree:          8192000 kB
MemAvailable:    12288000 kB"""

        with patch.dict('sys.modules', {'psutil': None}), \
             patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value = meminfo_content.split('\n')
            ram = hardware_service._get_ram_gb()

            assert ram == 15  # 16384000 KB / (1024**2)

    def test_get_ram_fallback_default(self, hardware_service):
        """Test RAM detection returns default on failure."""
        with patch.dict('sys.modules', {'psutil': None}), \
             patch('subprocess.check_output', side_effect=Exception):
            ram = hardware_service._get_ram_gb()

            assert ram == 8  # Default fallback

    def test_get_available_ram_with_psutil(self, hardware_service):
        """Test available RAM detection with psutil."""
        mock_memory = Mock()
        mock_memory.available = 8 * (1024**3)  # 8GB available

        mock_psutil = Mock()
        mock_psutil.virtual_memory.return_value = mock_memory

        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            available_ram = hardware_service._get_available_ram_gb()

            assert available_ram == 8

    def test_get_available_ram_fallback(self, hardware_service):
        """Test available RAM fallback (half of total)."""
        with patch.dict('sys.modules', {'psutil': None}), \
             patch.object(hardware_service, '_get_ram_gb', return_value=16):
            available_ram = hardware_service._get_available_ram_gb()

            assert available_ram == 8  # Half of 16GB

    def test_get_cpu_cores_with_psutil(self, hardware_service):
        """Test CPU core detection with psutil."""
        mock_psutil = Mock()
        mock_psutil.cpu_count.return_value = 8

        with patch.dict('sys.modules', {'psutil': mock_psutil}):
            cores = hardware_service._get_cpu_cores()

            assert cores == 8

    def test_get_cpu_cores_fallback(self, hardware_service):
        """Test CPU core detection fallback with os.cpu_count()."""
        with patch.dict('sys.modules', {'psutil': None}), \
             patch('os.cpu_count', return_value=4):
            cores = hardware_service._get_cpu_cores()

            assert cores == 4

    def test_get_cpu_cores_default(self, hardware_service):
        """Test CPU core detection returns default on failure."""
        with patch.dict('sys.modules', {'psutil': None}), \
             patch('os.cpu_count', return_value=None):
            cores = hardware_service._get_cpu_cores()

            assert cores == 4  # Default fallback


# =============================================================================
# Test: GPU Detection
# =============================================================================

class TestGPUDetection:
    """Test GPU detection methods."""

    def test_detect_gpu_apple_silicon(self, hardware_service, mock_darwin_system):
        """Test Apple Silicon GPU detection."""
        with patch.object(hardware_service, '_get_ram_gb', return_value=16):
            gpu_info = hardware_service._detect_gpu()

            assert gpu_info["available"] is True
            assert "Apple Silicon" in gpu_info["name"]
            assert gpu_info["vram_gb"] == 16  # Unified memory

    def test_detect_gpu_nvidia(self, hardware_service):
        """Test NVIDIA GPU detection."""
        nvidia_output = b"NVIDIA GeForce RTX 3080, 10240 MiB\n"

        with patch('platform.system', return_value='Linux'), \
             patch('subprocess.check_output', return_value=nvidia_output):
            gpu_info = hardware_service._detect_gpu()

            assert gpu_info["available"] is True
            assert "RTX 3080" in gpu_info["name"]
            assert gpu_info["vram_gb"] == 10  # 10240 MiB / 1024

    def test_detect_gpu_none(self, hardware_service):
        """Test GPU detection when no GPU is present."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.machine', return_value='x86_64'), \
             patch('subprocess.check_output', side_effect=FileNotFoundError):
            gpu_info = hardware_service._detect_gpu()

            assert gpu_info["available"] is False
            assert "name" not in gpu_info
            assert "vram_gb" not in gpu_info

    def test_detect_gpu_nvidia_timeout(self, hardware_service):
        """Test GPU detection handles nvidia-smi timeout."""
        with patch('platform.system', return_value='Linux'), \
             patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired('nvidia-smi', 5)):
            gpu_info = hardware_service._detect_gpu()

            assert gpu_info["available"] is False


# =============================================================================
# Test: Ollama Detection
# =============================================================================

class TestOllamaDetection:
    """Test Ollama detection methods."""

    def test_detect_ollama_installed_with_models(self, hardware_service):
        """Test Ollama detection when installed with models."""
        version_output = b"ollama version 0.12.10\n"
        models_output = b"""NAME                 ID              SIZE      MODIFIED
mistral:7b          abc123          4.1 GB    2 days ago
llama3.2:3b         def456          2.0 GB    1 week ago
"""

        with patch('subprocess.check_output', side_effect=[version_output, models_output]):
            ollama_info = hardware_service._detect_ollama()

            assert ollama_info["installed"] is True
            assert ollama_info["version"] == "0.12.10"
            assert "mistral:7b" in ollama_info["models"]
            assert "llama3.2:3b" in ollama_info["models"]
            assert len(ollama_info["models"]) == 2

    def test_detect_ollama_installed_no_models(self, hardware_service):
        """Test Ollama detection when installed but no models."""
        version_output = b"ollama version 0.12.10\n"
        models_output = b"""NAME                 ID              SIZE      MODIFIED
"""

        with patch('subprocess.check_output', side_effect=[version_output, models_output]):
            ollama_info = hardware_service._detect_ollama()

            assert ollama_info["installed"] is True
            assert ollama_info["version"] == "0.12.10"
            assert ollama_info["models"] == []

    def test_detect_ollama_not_installed(self, hardware_service):
        """Test Ollama detection when not installed."""
        with patch('subprocess.check_output', side_effect=FileNotFoundError):
            ollama_info = hardware_service._detect_ollama()

            assert ollama_info["installed"] is False
            assert ollama_info["models"] == []
            assert "version" not in ollama_info

    def test_detect_ollama_timeout(self, hardware_service):
        """Test Ollama detection handles timeout."""
        with patch('subprocess.check_output', side_effect=subprocess.TimeoutExpired('ollama', 5)):
            ollama_info = hardware_service._detect_ollama()

            assert ollama_info["installed"] is False

    def test_detect_ollama_list_fails(self, hardware_service):
        """Test Ollama detection when version works but list fails."""
        version_output = b"ollama version 0.12.10\n"

        with patch('subprocess.check_output', side_effect=[
            version_output,
            subprocess.CalledProcessError(1, 'ollama list')
        ]):
            ollama_info = hardware_service._detect_ollama()

            assert ollama_info["installed"] is True
            assert ollama_info["version"] == "0.12.10"
            assert ollama_info["models"] == []


# =============================================================================
# Test: Model Size Recommendations
# =============================================================================

class TestModelRecommendations:
    """Test model size recommendation logic."""

    def test_calculate_max_params_apple_silicon_16gb(self, hardware_service):
        """Test recommendation for Apple Silicon 16GB."""
        gpu_info = {
            "available": True,
            "name": "Apple Silicon (Unified Memory)",
            "vram_gb": 16
        }

        max_params = hardware_service._calculate_max_params(16, gpu_info)

        # 16GB * 0.75 = 12GB usable → "12b"
        assert max_params == "12b"

    def test_calculate_max_params_apple_silicon_64gb(self, hardware_service):
        """Test recommendation for Apple Silicon 64GB."""
        gpu_info = {
            "available": True,
            "name": "Apple Silicon (Unified Memory)",
            "vram_gb": 64
        }

        max_params = hardware_service._calculate_max_params(64, gpu_info)

        # 64GB * 0.75 = 48GB usable → "70b"
        assert max_params == "70b"

    def test_calculate_max_params_nvidia_10gb(self, hardware_service):
        """Test recommendation for NVIDIA GPU with 10GB VRAM + 16GB RAM."""
        gpu_info = {
            "available": True,
            "name": "NVIDIA RTX 3080",
            "vram_gb": 10
        }

        max_params = hardware_service._calculate_max_params(16, gpu_info)

        # 10GB VRAM + min(16/4, 8) = 10 + 4 = 14GB → "12b"
        assert max_params == "12b"

    def test_calculate_max_params_cpu_only_8gb(self, hardware_service):
        """Test recommendation for CPU-only with 8GB RAM."""
        gpu_info = {"available": False}

        max_params = hardware_service._calculate_max_params(8, gpu_info)

        # 8GB * 0.6 = 4.8GB usable → "3b"
        assert max_params == "3b"

    def test_calculate_max_params_cpu_only_32gb(self, hardware_service):
        """Test recommendation for CPU-only with 32GB RAM."""
        gpu_info = {"available": False}

        max_params = hardware_service._calculate_max_params(32, gpu_info)

        # 32GB * 0.6 = 19.2GB usable → "12b"
        assert max_params == "12b"

    def test_calculate_max_params_cpu_only_64gb(self, hardware_service):
        """Test recommendation for CPU-only with 64GB RAM."""
        gpu_info = {"available": False}

        max_params = hardware_service._calculate_max_params(64, gpu_info)

        # 64GB * 0.6 = 38.4GB usable → "30b"
        assert max_params == "30b"

    def test_calculate_max_params_cpu_only_128gb(self, hardware_service):
        """Test recommendation for CPU-only with 128GB RAM."""
        gpu_info = {"available": False}

        max_params = hardware_service._calculate_max_params(128, gpu_info)

        # 128GB * 0.6 = 76.8GB usable → "70b"
        assert max_params == "70b"


# =============================================================================
# Test: Ollama Server Status
# =============================================================================

class TestOllamaServerStatus:
    """Test Ollama server connectivity."""

    @pytest.mark.asyncio
    async def test_is_ollama_running_yes(self, hardware_service):
        """Test detecting running Ollama server."""
        mock_response = Mock()
        mock_response.status_code = 200

        with patch('httpx.get', return_value=mock_response):
            running = hardware_service.is_ollama_running()

            assert running is True

    @pytest.mark.asyncio
    async def test_is_ollama_running_no(self, hardware_service):
        """Test detecting Ollama server not running."""
        with patch('httpx.get', side_effect=Exception):
            running = hardware_service.is_ollama_running()

            assert running is False


# =============================================================================
# Test: Model Recommendations
# =============================================================================

class TestLocalModelRecommendations:
    """Test local model recommendation system."""

    def test_get_recommended_local_models_3b_system(self, hardware_service):
        """Test recommendations for 3B-capable system."""
        with patch.object(hardware_service, 'detect') as mock_detect:
            mock_detect.return_value = HardwareInfo(
                ram_gb=8,
                available_ram_gb=4,
                cpu_cores=4,
                gpu_available=False,
                gpu_name=None,
                gpu_vram_gb=None,
                ollama_installed=True,
                ollama_version="0.12.10",
                ollama_models=["llama3.2:3b"],
                recommended_max_params="3b",
                platform="darwin"
            )

            recommendations = hardware_service.get_recommended_local_models()

            # Should only recommend 3B models
            assert len(recommendations) == 2
            assert all(r["tier"] == "3b" for r in recommendations)
            assert any(r["id"] == "llama3.2:3b" for r in recommendations)

            # Check installed status
            llama_rec = next(r for r in recommendations if r["id"] == "llama3.2:3b")
            assert llama_rec["installed"] is True

    def test_get_recommended_local_models_7b_system(self, hardware_service):
        """Test recommendations for 7B-capable system."""
        with patch.object(hardware_service, 'detect') as mock_detect:
            mock_detect.return_value = HardwareInfo(
                ram_gb=16,
                available_ram_gb=8,
                cpu_cores=8,
                gpu_available=True,
                gpu_name="Apple Silicon",
                gpu_vram_gb=16,
                ollama_installed=True,
                ollama_version="0.12.10",
                ollama_models=["mistral:7b"],
                recommended_max_params="7b",
                platform="darwin"
            )

            recommendations = hardware_service.get_recommended_local_models()

            # Should recommend 3B + 7B models
            assert len(recommendations) == 5  # 2 × 3B + 3 × 7B
            tiers = {r["tier"] for r in recommendations}
            assert "3b" in tiers
            assert "7b" in tiers
            assert "12b" not in tiers

    def test_get_recommended_local_models_70b_system(self, hardware_service):
        """Test recommendations for 70B-capable system."""
        with patch.object(hardware_service, 'detect') as mock_detect:
            mock_detect.return_value = HardwareInfo(
                ram_gb=128,
                available_ram_gb=100,
                cpu_cores=32,
                gpu_available=True,
                gpu_name="Apple Silicon",
                gpu_vram_gb=128,
                ollama_installed=True,
                ollama_version="0.12.10",
                ollama_models=[],
                recommended_max_params="70b",
                platform="darwin"
            )

            recommendations = hardware_service.get_recommended_local_models()

            # Should recommend all tiers
            tiers = {r["tier"] for r in recommendations}
            assert tiers == {"3b", "7b", "12b", "30b", "70b"}

            # Should have at least 10 models
            assert len(recommendations) >= 10


# =============================================================================
# Test: Model Pulling
# =============================================================================

class TestModelPulling:
    """Test Ollama model pulling functionality."""

    @pytest.mark.asyncio
    async def test_pull_model_success(self, hardware_service):
        """Test successful model pull initiation."""
        mock_process = Mock()

        with patch('subprocess.Popen', return_value=mock_process):
            result = await hardware_service.pull_model("mistral:7b")

            assert result["success"] is True
            assert result["model_id"] == "mistral:7b"
            assert "Started downloading" in result["message"]

    @pytest.mark.asyncio
    async def test_pull_model_ollama_not_installed(self, hardware_service):
        """Test model pull when Ollama not installed."""
        with patch('subprocess.Popen', side_effect=FileNotFoundError):
            result = await hardware_service.pull_model("mistral:7b")

            assert result["success"] is False
            assert result["model_id"] == "mistral:7b"
            assert "not installed" in result["message"]

    @pytest.mark.asyncio
    async def test_pull_model_error(self, hardware_service):
        """Test model pull with generic error."""
        with patch('subprocess.Popen', side_effect=Exception("Generic error")):
            result = await hardware_service.pull_model("mistral:7b")

            assert result["success"] is False
            assert result["model_id"] == "mistral:7b"
            assert "Generic error" in result["message"]


# =============================================================================
# Test: Data Classes
# =============================================================================

class TestDataClasses:
    """Test HardwareInfo dataclass."""

    def test_hardware_info_to_dict(self):
        """Test HardwareInfo.to_dict() conversion."""
        info = HardwareInfo(
            ram_gb=16,
            available_ram_gb=8,
            cpu_cores=8,
            gpu_available=True,
            gpu_name="Apple Silicon",
            gpu_vram_gb=16,
            ollama_installed=True,
            ollama_version="0.12.10",
            ollama_models=["mistral:7b"],
            recommended_max_params="12b",
            platform="darwin"
        )

        data = info.to_dict()

        assert isinstance(data, dict)
        assert data["ram_gb"] == 16
        assert data["gpu_name"] == "Apple Silicon"
        assert data["ollama_models"] == ["mistral:7b"]
        assert data["recommended_max_params"] == "12b"
