"""
NotebookLM MCP Client (Desktop Edition) - Architect Patched Version
Fixes: Timeout handling, Auth delays, and Stream parsing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

# Configure logging to show up in console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotebookLM")

# --- Constants ---
AUTH_TIMEOUT_SECONDS = 120  # Generous time for first-time Google Login
QUERY_TIMEOUT_SECONDS = 45  # Time for standard queries

class NotebookInfo(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source_count: int = 0
    created_at: str = ""
    updated_at: str = ""


class NotebookResponse(BaseModel):
    answer: str
    sources: List[Dict[str, str]]
    notebook_id: str
    query: str


class NotebookLMMCPClient:
    _instance: Optional["NotebookLMMCPClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        # Calculate paths relative to: backend/services/notebooklm_service.py
        # We need to reach: backend/external/notebooklm-mcp/dist/index.js
        current_file = Path(__file__).resolve()
        self.backend_root = current_file.parents[1] # backend/
        
        self.server_script_path = self.backend_root / "external" / "notebooklm-mcp" / "dist" / "index.js"
        
        self._process: Optional[asyncio.subprocess.Process] = None
        self._initialized = True
        
        logger.info(f"🔌 NotebookLM Client Initialized.")
        logger.info(f"   Target Node Script: {self.server_script_path}")

    async def ensure_started(self):
        """Launches the Node.js MCP Server if not running."""
        if self._process and self._process.returncode is None:
            return

        if not self.server_script_path.exists():
            logger.error(f"❌ MCP Server not found at: {self.server_script_path}")
            raise FileNotFoundError(f"Could not find notebooklm-mcp at {self.server_script_path}")

        command = "node"
        args = [str(self.server_script_path)]
        env = os.environ.copy()
        
        # CRITICAL: Set HEADLESS=false so user can see the Auth Popup
        env["HEADLESS"] = "false" 

        logger.info("🚀 Launching NotebookLM MCP Server...")
        self._process = await asyncio.create_subprocess_exec(
            command,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        
        # --- MCP HANDSHAKE ---
        logger.info("🤝 Performing MCP Handshake...")
        
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "writer-factory", "version": "1.0"}
            }
        }
        self._process.stdin.write(json.dumps(init_req).encode() + b"\n")
        await self._process.stdin.drain()
        
        # Read Init Response
        init_resp = await self._read_json_response()
        if "error" in init_resp:
            raise RuntimeError(f"Handshake failed: {init_resp['error']}")
            
        # 2. Initialized Notification
        notify_req = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self._process.stdin.write(json.dumps(notify_req).encode() + b"\n")
        await self._process.stdin.drain()
        
        logger.info("✅ MCP Handshake Complete.")

    async def _call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Executes an MCP tool call with robust timeout handling.
        """
        await self.ensure_started()
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        if not self._process or not self._process.stdin or not self._process.stdout:
            raise RuntimeError("MCP process is dead.")

        # Send Request
        logger.info(f"📤 Sending Request: {tool_name}")
        try:
            self._process.stdin.write(json.dumps(request).encode() + b"\n")
            await self._process.stdin.drain()
        except BrokenPipeError:
            logger.error("❌ Broken Pipe. Server crashed?")
            self._process = None
            raise RuntimeError("NotebookLM Server crashed unexpectedly.")

        # Read Response Loop
        # We use a longer timeout for the FIRST call (likely auth)
        timeout = AUTH_TIMEOUT_SECONDS if tool_name == "list_notebooks" else QUERY_TIMEOUT_SECONDS
        
        try:
            response_data = await asyncio.wait_for(self._read_json_response(), timeout=timeout)
            return response_data
        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout waiting for NotebookLM ({timeout}s). Is a login popup open?")
            raise RuntimeError("NotebookLM timed out. Please check if a browser window is waiting for login.")

    async def _read_json_response(self) -> Dict:
        """Reads stdout line-by-line, skipping noise until JSON arrives."""
        while True:
            try:
                # Wait for a line from stdout
                line_bytes = await self._process.stdout.readline()
            except Exception:
                line_bytes = b""

            if not line_bytes:
                # Process died? Check return code
                if self._process.returncode is not None:
                    err = await self._process.stderr.read(1024)
                    logger.error(f"💀 Server exit code {self._process.returncode}. Stderr: {err.decode()}")
                    raise RuntimeError("Server disconnected.")
                # If process is still alive but stdout closed, that's bad too
                await asyncio.sleep(0.1)
                continue

            line = line_bytes.decode().strip()
            if not line:
                continue

            # DEBUG: Print what Node is saying (helps troubleshooting)
            # logger.debug(f"MCP RAW: {line}")

            if not line.startswith("{"):
                # Likely a log message like "Puppeteer launching..."
                logger.info(f"   [MCP Log] {line}")
                continue

            try:
                response = json.loads(line)
                if response.get("id") == 0 or response.get("id") == 1 or "result" in response or "error" in response:
                    if "error" in response:
                        raise RuntimeError(f"MCP Error: {response['error']}")
                    
                    if "result" in response:
                        # Handshake or Tool Result
                        return response["result"]
                    return response
            except json.JSONDecodeError:
                continue

    async def setup_auth(self) -> Dict:
        """
        Triggers the authentication flow (browser launch).
        """
        logger.info("🔐 Triggering Setup Auth...")
        return await self._call_tool("setup_auth", {})

    async def list_notebooks(self) -> List[NotebookInfo]:
        logger.info("📚 Fetching Notebook list...")
        data = await self._call_tool("list_notebooks", {})
        
        # Handle different return structures
        notebooks_data = data if isinstance(data, list) else data.get("notebooks", [])
        
        results = []
        for nb in notebooks_data:
            results.append(NotebookInfo(
                id=nb.get("id", ""),
                title=nb.get("title", "Untitled"),
                source_count=nb.get("sourceCount", 0)
            ))
        return results

    async def query_notebook(self, notebook_id: str, query: str) -> NotebookResponse:
        logger.info(f"🔍 Querying Notebook {notebook_id[:5]}...")
        args = {
            "query": query,
            "notebook_id": notebook_id,
        }
        result = await self._call_tool("ask_question", args)
        
        # DEBUG: Inspect what the MCP server actually returned
        logger.info(f"🐞 MCP RAW RESPONSE: {json.dumps(result, indent=2)}")
        
        return NotebookResponse(
            answer=result.get("answer", ""),
            sources=result.get("citations", []),
            notebook_id=notebook_id,
            query=query,
        )
    
    async def is_available(self) -> bool:
        try:
            await self.ensure_started()
            return True
        except Exception:
            return False

    # ... wrapper methods for higher level logic ...
    async def extract_character_profile(self, notebook_id: str, character_name: str) -> Dict:
        query = f"Generate a character profile for {character_name} based on this notebook."
        resp = await self.query_notebook(notebook_id, query)
        return {
            "character_name": character_name,
            "profile": resp.answer,
            "sources": resp.sources,
            "notebook_id": notebook_id,
        }

    async def extract_world_building(self, notebook_id: str, aspect: str) -> Dict:
        query = f"Describe the world-building aspect: {aspect}."
        resp = await self.query_notebook(notebook_id, query)
        return {
            "aspect": aspect,
            "details": resp.answer,
            "sources": resp.sources,
            "notebook_id": notebook_id,
        }

    async def query_for_context(self, notebook_id: str, entity_name: str, entity_type: str) -> str:
        query = f"What do we know about the {entity_type} named {entity_name}?"
        resp = await self.query_notebook(notebook_id, query)
        return resp.answer

def get_notebooklm_client() -> NotebookLMMCPClient:
    return NotebookLMMCPClient()
