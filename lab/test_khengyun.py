import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_server():
    print(f"🧪 Testing Khengyun Python MCP Server...")
    
    # We use the current python executable to run the installed module
    # Entry point defined in pyproject.toml: notebooklm-mcp = "notebooklm_mcp.cli:main"
    # We can call it via -m notebooklm_mcp.cli
    
    cmd = sys.executable
    args = ["-m", "notebooklm_mcp.cli", "server"]
    
    print(f"Running: {cmd} {' '.join(args)}")

    server_params = StdioServerParameters(
        command=cmd,
        args=args,
        env={
            "HEADLESS": "false", # Force visible browser
            "PATH": os.environ["PATH"] # Inherit path
        } 
    )

    try:
        async with stdio_client(server_params) as (read, write):
            print("🔌 Connected to Stdio...")
            async with ClientSession(read, write) as session:
                print("🤝 Initializing...")
                await session.initialize()
                print("✅ Handshake Successful!")
                
                tools = await session.list_tools()
                print(f"🛠️  Available Tools: {[t.name for t in tools.tools]}")
                
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server())
