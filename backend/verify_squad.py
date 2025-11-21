import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Adjust this import path based on your actual folder structure
from services.llm_service import LLMService

# Load environment variables
load_dotenv()

async def test_provider(service, provider, model):
    print(f"🔵 Testing {provider} ({model})...", end=" ", flush=True)
    try:
        # Simple hello prompt
        response = await service.generate_response(
            provider=provider,
            model=model,
            system_role="You are a connection tester.",
            prompt="Say 'OK'"
        )
        
        if response and "Error" not in response:
            print(f"✅ SUCCESS")
            return True
        else:
            print(f"❌ FAILED")
            if response:
                 print(f"   Response: {response}")
            return False

    except Exception as e:
        print(f"❌ FAILED")
        print(f"   Error: {str(e)}")
        return False

async def main():
    print("--- 🤖 STARTING SQUAD CONNECTION CHECK ---")
    
    # Initialize the service (it should pick up keys from .env)
    try:
        llm_service = LLMService()
    except Exception as e:
        print(f"Critical Error initializing Service: {e}")
        return

    # Define the roster to test
    # Ensure these match the providers defined in your LLMService
    roster = [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-3-7-sonnet-20250219"),
        ("xai", "grok-2"),
        
        # Extended Roster
        ("deepseek", "deepseek-chat"),
        ("qwen", "qwen-turbo"),
        ("kimi", "moonshot-v1-8k"),
        ("zhipu", "glm-4"),
        ("tencent", "hunyuan-pro"),
        ("mistral", "mistral-large-latest"),
    ]

    success_count = 0
    for provider, model in roster:
        # Check if the key is set before testing to avoid obvious failures
        key_var = f"{provider.upper()}_API_KEY"
        # Handle special case for Kimi (MOONSHOT/KIMI naming)
        if provider == "kimi":
             key_var = "KIMI_API_KEY"
             
        if os.getenv(key_var):
            if await test_provider(llm_service, provider, model):
                success_count += 1
        else:
             print(f"⚪ Skipping {provider} (Key not set)")

    print("\n----------------------------------------")
    print(f"Testing Complete: {success_count} Providers Operational")
    print("----------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
