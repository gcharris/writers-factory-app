import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.notebooklm_service import get_notebooklm_client

async def register_notebook():
    client = get_notebooklm_client()
    
    # The URL for "Advanced Fiction Writing" (from your screenshot)
    url = "https://notebooklm.google.com/notebook/8b1f262a-fe2a-45f3-8c3b-39689c9d3123"
    
    print(f"📚 Registering Notebook: {url}")
    print("⚠️  Please ensure the Automation Chrome Window is OPEN and LOGGED IN before running this!")
    
    try:
        # This calls the 'add_notebook' tool on the MCP server
        result = await client._call_tool("add_notebook", {"url": url})
        print("\n✅ Registration Result:")
        print(result)
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(register_notebook())
