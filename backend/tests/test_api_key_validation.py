import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

# =============================================================================
# Test Data
# =============================================================================

PROVIDERS = [
    ("google", "https://generativelanguage.googleapis.com/v1beta/models"),
    ("deepseek", "https://api.deepseek.com/models"),
    ("openai", "https://api.openai.com/v1/models"),
    ("anthropic", "https://api.anthropic.com/v1/messages"),
    ("qwen", "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"),
    ("xai", "https://api.x.ai/v1/chat/completions"),
    ("mistral", "https://api.mistral.ai/v1/models"),
]

# =============================================================================
# Success Cases
# =============================================================================

@pytest.mark.parametrize("provider, url", PROVIDERS)
def test_api_key_validation_success(provider, url):
    """Test that a valid API key returns success for each provider."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        response = client.post(
            "/api-keys/test",
            json={"provider": provider, "api_key": "valid_key_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["provider"] == provider

        # Verify the correct method was called based on provider
        if provider in ["anthropic", "qwen", "xai"]:
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == url
        else:
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert args[0] == url


def test_api_key_validation_gemini_alias():
    """Test that 'gemini' works as an alias for 'google'."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = client.post(
            "/api-keys/test",
            json={"provider": "gemini", "api_key": "valid_key_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["provider"] == "google"


def test_api_key_validation_grok_alias():
    """Test that 'grok' works as an alias for 'xai'."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = client.post(
            "/api-keys/test",
            json={"provider": "grok", "api_key": "valid_key_123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["provider"] == "xai"


# =============================================================================
# Error Cases
# =============================================================================

@pytest.mark.parametrize("provider, url", PROVIDERS)
def test_api_key_validation_invalid_key(provider, url):
    """Test that an invalid API key returns valid=False."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock 401 Unauthorized response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response

        response = client.post(
            "/api-keys/test",
            json={"provider": provider, "api_key": "invalid_key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "error" in data
        assert "401" in data["error"]


def test_api_key_empty():
    """Test validation with empty API key."""
    response = client.post(
        "/api-keys/test",
        json={"provider": "openai", "api_key": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["error"] == "API key is empty"


def test_api_key_whitespace():
    """Test validation with whitespace-only API key."""
    response = client.post(
        "/api-keys/test",
        json={"provider": "openai", "api_key": "   "}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["error"] == "API key is empty"


def test_unknown_provider():
    """Test validation with unknown provider."""
    response = client.post(
        "/api-keys/test",
        json={"provider": "unknown_provider", "api_key": "some_key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "Unknown provider" in data["error"]


def test_network_error():
    """Test handling of network exceptions."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection timed out")

        response = client.post(
            "/api-keys/test",
            json={"provider": "openai", "api_key": "valid_key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Connection timed out" in data["error"]
