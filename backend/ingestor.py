"""
Local-First Knowledge Graph Ingestor
Engine: Ollama (Llama 3.2)
Function: Reads Markdown -> Extracts Entities -> Updates Graph JSON

This is the "Stomach" of the Metabolism system - it digests raw text
into structured knowledge graph data using a LOCAL LLM (zero cost).
"""
import os
import json
import asyncio
import sys
import aiohttp
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GraphIngestor:
    def __init__(self, content_path: str = None, max_files: int = None):
        # Configuration - LOCAL Ollama instance
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "llama3.2:3b"

        # Paths: Go up one level from backend/ to root
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Allow custom path or default to content/ (scans all subdirs including World Bible)
        if content_path:
            self.bible_path = content_path
        else:
            # Default: scan the entire content/ folder (scenes, characters, world bible)
            self.bible_path = os.path.join(self.root_dir, "content")

        self.output_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")

        # Limit number of files to process (None = all files)
        self.max_files = max_files

    async def query_ollama(self, prompt: str, system_prompt: str) -> Dict:
        """Direct call to Ollama Llama 3.2 in JSON mode."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "format": "json",
            "stream": False,
            "options": {
                "temperature": 0.1  # Low temperature for consistent extraction
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ollama_url, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result.get("message", {}).get("content", "{}")
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON Parse Error: {e}")
                            print(f"   Raw content: {content[:200]}...")
                            return {"nodes": [], "edges": []}
                    else:
                        error_text = await response.text()
                        print(f"⚠️ Ollama Error {response.status}: {error_text}")
                        return {"nodes": [], "edges": []}
        except asyncio.TimeoutError:
            print(f"⏱️ Ollama request timed out (120s)")
            return {"nodes": [], "edges": []}
        except aiohttp.ClientConnectorError:
            print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
            print(f"   Make sure Ollama is running: ollama serve")
            return {"nodes": [], "edges": []}
        except Exception as e:
            print(f"❌ Connection to Ollama failed: {e}")
            return {"nodes": [], "edges": []}

    async def extract_graph_from_text(self, text: str, filename: str) -> Dict[str, Any]:
        """Uses local Llama 3.2 to extract entities and relationships."""
        system_prompt = """You are an expert Literary Data Analyst. Convert the narrative text into a Knowledge Graph.

Return ONLY valid JSON with this exact structure:
{
  "nodes": [
    {"id": "ExactName", "type": "CHARACTER", "desc": "Short description"},
    {"id": "LocationName", "type": "LOCATION", "desc": "Short description"},
    {"id": "ObjectName", "type": "OBJECT", "desc": "Short description"}
  ],
  "edges": [
    {"source": "id1", "target": "id2", "relation": "LOVES", "desc": "context"},
    {"source": "id1", "target": "id3", "relation": "LOCATED_IN", "desc": "context"}
  ]
}

Node types: CHARACTER, LOCATION, OBJECT, EVENT, ORGANIZATION, THEME
Relation types: LOVES, HATES, KNOWS, LOCATED_IN, OWNS, PART_OF, CAUSES, CONFLICTS_WITH

Be precise. Extract only explicitly mentioned entities. Do not infer or hallucinate."""

        # Chunking: Limit text to ~6000 chars to fit context window
        chunk = text[:6000]
        print(f"      ...Analyzing {filename} ({len(chunk)} chars)...")

        user_prompt = f"Extract all entities and relationships from this text:\n\n{chunk}"

        return await self.query_ollama(user_prompt, system_prompt)

    async def run_ingestion(self) -> Dict[str, Any]:
        """Main ingestion pipeline - scans World Bible and builds knowledge graph."""
        print(f"🚀 Starting Knowledge Graph Ingestion (Engine: {self.model})...")
        print(f"   📁 Source: {self.bible_path}")

        # Ensure the content directory exists
        if not os.path.exists(self.bible_path):
            print(f"⚠️ Content path not found: {self.bible_path}")
            print(f"   Create the folder and add .md files to ingest.")
            os.makedirs(self.bible_path, exist_ok=True)

        # Initialize the master graph with metadata
        master_graph = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "engine": f"ollama/{self.model}",
                "source_path": self.bible_path
            },
            "nodes": [],
            "edges": []
        }

        # Track unique nodes to avoid duplicates
        seen_node_ids = set()
        files_processed = 0

        # Collect all markdown files first
        md_files = []
        for root, _, files in os.walk(self.bible_path):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))

        # Apply max_files limit if set
        total_files = len(md_files)
        if self.max_files and self.max_files < total_files:
            md_files = md_files[:self.max_files]
            print(f"   ⚡ Quick mode: Processing {self.max_files} of {total_files} files")
        else:
            print(f"   📚 Found {total_files} markdown files to process")

        # Process each file
        for i, path in enumerate(md_files):
            file = os.path.basename(path)
            print(f"\n   📄 [{i+1}/{len(md_files)}] Processing: {file}")

            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            if not text.strip():
                print(f"      ⏭️ Skipping empty file")
                continue

            data = await self.extract_graph_from_text(text, file)

            if data:
                # Add nodes (with deduplication)
                new_nodes = 0
                for node in data.get("nodes", []):
                    node_id = node.get("id", "").strip()
                    if node_id and node_id not in seen_node_ids:
                        seen_node_ids.add(node_id)
                        master_graph["nodes"].append(node)
                        new_nodes += 1

                # Add edges
                new_edges = data.get("edges", [])
                master_graph["edges"].extend(new_edges)

                print(f"      ✅ Extracted {new_nodes} nodes, {len(new_edges)} edges")
                files_processed += 1

        # Save the knowledge graph to disk
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(master_graph, f, indent=2)

        print(f"\n{'='*50}")
        print(f"💾 Knowledge Graph saved to: {self.output_path}")
        print(f"   📊 Total nodes: {len(master_graph['nodes'])}")
        print(f"   🔗 Total edges: {len(master_graph['edges'])}")
        print(f"   📄 Files processed: {files_processed}")
        print(f"{'='*50}")

        return master_graph


# Allow running this script directly to test
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧠 Writers Factory - Knowledge Graph Ingestor")
    print("="*50 + "\n")

    ingestor = GraphIngestor()
    asyncio.run(ingestor.run_ingestion())
