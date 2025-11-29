#!/usr/bin/env python3
"""
Quick API key tester - checks which keys in .env are working
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_openai():
    """Test OpenAI API key"""
    key = os.getenv("OPENAI_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_anthropic():
    """Test Anthropic API key"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={"model": "claude-3-haiku-20240307", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]},
                timeout=15
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_xai():
    """Test xAI (Grok) API key"""
    key = os.getenv("XAI_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.x.ai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_gemini():
    """Test Google Gemini API key"""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={key}",
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_deepseek():
    """Test DeepSeek API key"""
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.deepseek.com/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_qwen():
    """Test Alibaba Qwen API key (International/Singapore edition)"""
    key = os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            # Alibaba DashScope INTERNATIONAL API (note the -intl in URL)
            resp = await client.post(
                "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-turbo",
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1
                },
                timeout=15
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_mistral():
    """Test Mistral API key"""
    key = os.getenv("MISTRAL_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.mistral.ai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_moonshot():
    """Test Moonshot Kimi API key"""
    key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        async with httpx.AsyncClient() as client:
            # Use api.moonshot.ai (not .cn) for international
            resp = await client.get(
                "https://api.moonshot.ai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_zhipu():
    """Test Zhipu AI (ChatGLM) API key"""
    key = os.getenv("ZHIPU_API_KEY")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    try:
        # Zhipu uses JWT-style auth
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": "hi"}],
                    "max_tokens": 1
                },
                timeout=15
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_yandex():
    """Test Yandex AI API key"""
    key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")
    if not key or key.startswith("your_"):
        return "NOT CONFIGURED"
    if not folder_id:
        return "MISSING FOLDER_ID"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers={
                    "Authorization": f"Api-Key {key}",
                    "x-folder-id": folder_id,
                    "Content-Type": "application/json"
                },
                json={
                    "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
                    "completionOptions": {"maxTokens": 1},
                    "messages": [{"role": "user", "text": "hi"}]
                },
                timeout=15
            )
            return "PASSED" if resp.status_code == 200 else f"FAILED ({resp.status_code})"
    except Exception as e:
        return f"ERROR: {str(e)[:50]}"

async def test_ollama():
    """Test local Ollama"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return f"PASSED ({len(models)} models)"
            return f"FAILED ({resp.status_code})"
    except Exception as e:
        return "NOT RUNNING"

async def main():
    print("\n" + "="*60)
    print("  API KEY TEST RESULTS")
    print("="*60 + "\n")

    tests = [
        ("OpenAI", test_openai),
        ("Anthropic", test_anthropic),
        ("xAI (Grok)", test_xai),
        ("Google Gemini", test_gemini),
        ("DeepSeek", test_deepseek),
        ("Alibaba Qwen", test_qwen),
        ("Mistral", test_mistral),
        ("Moonshot Kimi", test_moonshot),
        ("Zhipu ChatGLM", test_zhipu),
        ("Yandex", test_yandex),
        ("Ollama (local)", test_ollama),
    ]

    # Group by category
    print("--- US PREMIUM ---")
    for name, test_fn in tests[:4]:
        result = await test_fn()
        status = "✓" if "PASSED" in result else "✗" if "FAILED" in result or "ERROR" in result else "○"
        print(f"  {status} {name:20} {result}")

    print("\n--- CHINA / ASIA ---")
    for name, test_fn in tests[4:9]:  # DeepSeek, Qwen, Mistral, Moonshot, Zhipu
        result = await test_fn()
        status = "✓" if "PASSED" in result else "✗" if "FAILED" in result or "ERROR" in result else "○"
        print(f"  {status} {name:20} {result}")

    print("\n--- EUROPE ---")
    # Mistral is in China/Asia section since we're using tests[4:9]

    print("\n--- RUSSIA ---")
    result = await tests[9][1]()  # Yandex
    status = "✓" if "PASSED" in result else "✗" if "FAILED" in result or "ERROR" in result else "○"
    print(f"  {status} {'Yandex':20} {result}")

    print("\n--- LOCAL ---")
    result = await tests[10][1]()  # Ollama
    status = "✓" if "PASSED" in result else "✗" if "NOT RUNNING" in result else "○"
    print(f"  {status} {'Ollama':20} {result}")

    print("\n" + "="*60)
    print("Legend: ✓ Working  ✗ Failed  ○ Not configured/skipped")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
