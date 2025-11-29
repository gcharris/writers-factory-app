"""
Embedded API Keys for MVP Distribution

This file contains base64-encoded API keys for cheap providers that are
baked into the app for student use. Premium providers (OpenAI, Anthropic,
xAI) require users to provide their own keys.

IMPORTANT:
- These keys are for the Writers Factory course MVP only
- Keys are lightly obfuscated (base64) to prevent casual copying
- For production, migrate to key server (Phase 3B)
- Do NOT commit real keys to git - use embedded_keys_private.py

Usage:
    from backend.config.embedded_keys import get_embedded_key

    key = get_embedded_key("deepseek")
    if key:
        # Use the key
        pass

Key Tiers:
    EMBEDDED (baked-in, free for students):
        - deepseek
        - qwen
        - mistral
        - gemini (Google provides generous free tier)

    USER_PROVIDED (students enter their own):
        - openai
        - anthropic
        - xai
"""

import os
import base64
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# --- Key Categories ---
# Embedded providers have keys baked into the app for MVP students
EMBEDDED_PROVIDERS = ["deepseek", "qwen", "mistral", "moonshot", "zhipu", "yandex"]
# User providers require user's own API keys
USER_PROVIDERS = ["openai", "anthropic", "xai", "gemini"]

# --- Embedded Keys (Base64 Encoded) ---
# To encode a key: base64.b64encode("sk-xxx".encode()).decode()
# To decode: base64.b64decode("c2steHh4").decode()

# These are PLACEHOLDER values - replace with real keys in embedded_keys_private.py
_EMBEDDED_KEYS: Dict[str, str] = {
    # DeepSeek - Primary cheap provider ($0.27/1M tokens)
    "deepseek": "",  # base64 encoded

    # Qwen (Alibaba) - Very cheap ($0.40/1M tokens)
    "qwen": "",  # base64 encoded

    # Mistral - European provider, good quality
    "mistral": "",  # base64 encoded

    # Moonshot Kimi - Chinese AI
    "moonshot": "",  # base64 encoded

    # Zhipu AI ChatGLM
    "zhipu": "",  # base64 encoded

    # Yandex YandexGPT
    "yandex": "",  # base64 encoded
}

# --- Private Keys Override ---
# Try to load real keys from private file (not committed to git)
try:
    from backend.config.embedded_keys_private import PRIVATE_KEYS
    _EMBEDDED_KEYS.update(PRIVATE_KEYS)
    logger.info("Loaded embedded keys from private config")
except ImportError:
    logger.debug("No private embedded keys found - using placeholders")


def get_embedded_key(provider: str) -> Optional[str]:
    """
    Get an embedded API key for a provider.

    Resolution order:
    1. Environment variable (allows override)
    2. Embedded key (base64 decoded)
    3. None

    Args:
        provider: Provider name (lowercase)

    Returns:
        Decoded API key or None
    """
    provider = provider.lower()

    # 1. Check environment variable first (always takes precedence)
    env_var = f"{provider.upper()}_API_KEY"
    env_key = os.getenv(env_var)
    if env_key and env_key != f"your_{provider}_key_here":
        return env_key

    # 2. Check embedded keys
    if provider not in EMBEDDED_PROVIDERS:
        return None

    encoded_key = _EMBEDDED_KEYS.get(provider, "")
    if not encoded_key:
        return None

    try:
        decoded = base64.b64decode(encoded_key).decode()
        return decoded if decoded else None
    except Exception as e:
        logger.error(f"Failed to decode embedded key for {provider}: {e}")
        return None


def get_available_embedded_providers() -> list[str]:
    """Get list of providers that have embedded keys configured."""
    return [p for p in EMBEDDED_PROVIDERS if get_embedded_key(p)]


def is_embedded_provider(provider: str) -> bool:
    """Check if a provider is in the embedded (free for students) tier."""
    return provider.lower() in EMBEDDED_PROVIDERS


def is_user_provider(provider: str) -> bool:
    """Check if a provider requires user's own key."""
    return provider.lower() in USER_PROVIDERS


def get_key_status() -> Dict[str, dict]:
    """
    Get status of all provider keys.

    Returns dict like:
    {
        "deepseek": {"available": True, "source": "embedded"},
        "openai": {"available": True, "source": "env"},
        "anthropic": {"available": False, "source": None}
    }
    """
    all_providers = EMBEDDED_PROVIDERS + USER_PROVIDERS
    status = {}

    for provider in all_providers:
        # Handle providers with alternate env var names
        if provider == "moonshot":
            env_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
        elif provider == "gemini":
            env_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif provider == "qwen":
            env_key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        else:
            env_var = f"{provider.upper()}_API_KEY"
            env_key = os.getenv(env_var)

        if env_key and env_key != f"your_{provider}_key_here":
            status[provider] = {"available": True, "source": "env"}
        elif provider in EMBEDDED_PROVIDERS and get_embedded_key(provider):
            status[provider] = {"available": True, "source": "embedded"}
        else:
            status[provider] = {"available": False, "source": None}

    return status
