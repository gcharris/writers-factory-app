"""
NotebookLM MCP Client (Desktop Edition)

Ported from the legacy writers-platform repository.
Manages subprocess connection to the Node-based MCP server located at
backend/external/notebooklm-mcp.
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
    created_at: str
    updated_at: str


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
            base_path = Path(__file__).resolve().parents[1]
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
            env=env,
        )
        await asyncio.sleep(2)

    async def list_notebooks(self) -> List[NotebookInfo]:
        await self.ensure_started()
        request = {"jsonrpc": "2.0", "id": 1, "method": "notebooks/list", "params": {}}
        return await self._send_request(request, result_key="notebooks", model=NotebookInfo)

    async def query_notebook(self, notebook_id: str, query: str, max_sources: int = 5) -> NotebookResponse:
        await self.ensure_started()
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "notebook/query",
            "params": {
                "notebook_id": notebook_id,
                "query": query,
                "max_sources": max_sources,
                "include_citations": True
            }
        }
        result = await self._send_request(request)
        return NotebookResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
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

    async def _send_request(self, request: Dict, result_key: Optional[str] = None, model=None):
        if not self._process or not self._process.stdin or not self._process.stdout:
            raise RuntimeError("NotebookLM MCP server process not running")

        self._process.stdin.write(json.dumps(request).encode() + b"\n")
        await self._process.stdin.drain()
        response_line = await self._process.stdout.readline()
        response = json.loads(response_line.decode())
        if "error" in response:
            raise RuntimeError(response["error"])

        result = response.get("result", {})
        if result_key:
            result = result.get(result_key, [])
        if model:
            return [model(**item) for item in result]
        return result

    async def extract_character_profile(self, notebook_id: str, character_name: str) -> Dict:
        query = f"""
        If {character_name} were a character in a novel, based on the
        research in this notebook, provide:

        1. **Backstory**: Their background and formative experiences
        2. **Voice**: Their speaking style, vocabulary, and mannerisms
        3. **Core Beliefs**: Their philosophical views and values
        4. **Character Arc**: Potential journey and transformation
        5. **Conflicts**: Internal and external struggles they might face
        6. **Relationships**: How they might relate to other characters

        Use specific examples from the notebook sources.
        Keep response concise but detailed (under 500 words).
        """
        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=10,
        )
        return {
            "character_name": character_name,
            "profile": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id,
        }

    async def extract_world_building(self, notebook_id: str, aspect: str) -> Dict:
        query = f"""
        Based on the research in this notebook, describe {aspect} for a
        fictional world. Include:

        1. **Key Characteristics**: Defining features and trends
        2. **Concrete Examples**: Specific scenarios and manifestations
        3. **Implications**: How this affects characters and plot
        4. **Conflicts**: Tensions and dilemmas arising from this aspect

        Ground your response in the notebook sources.
        Keep response concise but detailed (under 500 words).
        """
        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=8,
        )
        return {
            "aspect": aspect,
            "details": response.answer,
            "sources": response.sources,
            "notebook_id": notebook_id,
        }

    async def query_for_context(self, notebook_id: str, entity_name: str, entity_type: str) -> str:
        if entity_type == "character":
            query = f"What are the key traits and characteristics of {entity_name}?"
        elif entity_type == "location":
            query = f"Describe the key features and atmosphere of {entity_name}."
        elif entity_type == "object":
            query = f"What is {entity_name} and how does it work?"
        else:
            query = f"What is important to know about {entity_name}?"

        response = await self.query_notebook(
            notebook_id=notebook_id,
            query=query,
            max_sources=3,
        )
        return response.answer


def get_notebooklm_client() -> NotebookLMMCPClient:
    return NotebookLMMCPClient()

