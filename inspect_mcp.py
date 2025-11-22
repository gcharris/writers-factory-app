import asyncio
import sys
import os
import json

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.notebooklm_service import get_notebooklm_client

async def inspect_tools():
    client = get_notebooklm_client()
    
    print("🕵️ Inspecting MCP Tools...")
    
    try:
        # Standard MCP method to list tools
        # We need to construct the raw request manually since the client doesn't expose list_tools directly
        await client.ensure_started()
        
        request = {
            "jsonrpc": "2.0",
            "id": 99,
            "method": "tools/list",
            "params": {}
        }
        
        client._process.stdin.write(json.dumps(request).encode() + b"\n")
        await client._process.stdin.drain()
        
        # Read response using our robust reader
        response = await client._read_json_response()
        
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_tools())

