"""
NotebookLM MCP Client (Desktop Edition)

Updated to use standard MCP "tools/call" protocol.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


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

        root = Path(__file__).resolve().parents[1]
        self.config_path = root / "mcp_config.json"
        self.server_config: Dict[str, any] = {}
        self._process: Optional[asyncio.subprocess.Process] = None
        self._load_config()
        self._initialized = True

    def _load_config(self):
        if self.config_path.exists():
            with self.config_path.open() as f:
                config = json.load(f)
            self.server_config = config.get("mcpServers", {}).get("notebooklm", {})
        if not self.server_config:
            base_path = Path(__file__).resolve().parents[2]  # Adjusted for backend/services nesting
            self.server_config = {
                "command": "node",
                "args": [str(base_path / "external" / "notebooklm-mcp" / "dist" / "index.js")],
                "env": {}
            }

    async def ensure_started(self):
        if self._process and self._process.returncode is None:
            return

        command = self.server_config.get("command")
        args = self.server_config.get("args", [])
        env = os.environ.copy()
        env.update(self.server_config.get("env", {}))

        self._process = await asyncio.create_subprocess_exec(
            command,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**env, "HEADLESS": "false"},
        )
        await asyncio.sleep(2)

    async def _call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Executes an MCP tool call using the standard JSON-RPC 2.0 format.
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
            raise RuntimeError("NotebookLM MCP server process not running")

        try:
            self._process.stdin.write(json.dumps(request).encode() + b"\n")
            await self._process.stdin.drain()
            
            # Read lines until we get a valid JSON response
            while True:
                response_line = await self._process.stdout.readline()
                if not response_line:
                    # End of stream
                    err = await self._process.stderr.read(1024)
                    raise RuntimeError(f"MCP Server closed stream. Stderr: {err.decode()}")
                
                line = response_line.decode().strip()
                if not line:
                    continue
                    
                # Skip banner/log lines that aren't JSON
                if not line.startswith("{"):
                    logger.info(f"MCP STDOUT (ignored): {line}")
                    continue
                    
                try:
                    response = json.loads(line)
                    # If it's a valid JSON-RPC response matching our ID, break
                    if response.get("id") == 1 or "error" in response or "result" in response:
                        break
                except json.JSONDecodeError:
                    logger.info(f"MCP STDOUT (parse error): {line}")
                    continue
            
            if "error" in response:
                raise RuntimeError(f"MCP Error: {response['error']}")
                
            # MCP tool result structure: result: { content: [{ type: "text", text: "..." }] }
            result = response.get("result", {})
            content_list = result.get("content", [])
            
            if not content_list:
                return {}
                
            # Parse the inner JSON often returned in the text field
            text_content = content_list[0].get("text", "{}")
            try:
                return json.loads(text_content)
            except json.JSONDecodeError:
                return {"raw_text": text_content}

        except Exception as e:
            logger.error(f"MCP Call Failed: {e}")
            raise e

    async def list_notebooks(self) -> List[NotebookInfo]:
        # The MCP server has 'list_notebooks' tool
        data = await self._call_tool("list_notebooks", {})
        # The tool returns a list of notebooks directly or wrapped
        notebooks_data = data if isinstance(data, list) else data.get("notebooks", [])
        
        results = []
        for nb in notebooks_data:
            results.append(NotebookInfo(
                id=nb.get("id", ""),
                title=nb.get("title", "Untitled"),
                source_count=nb.get("sourceCount", 0)
            ))
        return results

    async def query_notebook(self, notebook_id: str, query: str, max_sources: int = 5) -> NotebookResponse:
        # The MCP server has 'ask_question' tool
        args = {
            "query": query,
            "notebook_id": notebook_id,
            # "max_sources": max_sources # Check if supported by tool schema
        }
        
        result = await self._call_tool("ask_question", args)
        
        return NotebookResponse(
            answer=result.get("answer", ""),
            sources=result.get("citations", []), # Map 'citations' to 'sources'
            notebook_id=notebook_id,
            query=query,
        )

    async def stop_server(self):
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None

    async def is_available(self) -> bool:
        try:
            await self.ensure_started()
            return True
        except Exception as exc:
            logger.error("NotebookLM MCP unavailable: %s", exc)
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
