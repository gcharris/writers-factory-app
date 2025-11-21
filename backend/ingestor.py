import os
import json
import asyncio
import sys
from typing import List, Dict, Any

# Add parent directory to path to allow imports if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.llm_service import LLMService

class GraphIngestor:
    def __init__(self):
        self.llm = LLMService()
        # Updated path to match user's structure: content/World Bible
        # Assuming script is in backend/, so .. -> root, then content/World Bible
        self.bible_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "World Bible")

    async def extract_graph_from_text(self, text: str) -> Dict[str, Any]:
        """Uses LLM to turn text into Nodes and Edges"""
        system_prompt = (
            "You are a Knowledge Graph Extractor for a novel. "
            "Analyze the text and extract:\n"
            "1. Nodes: Characters, Locations, Key Objects, Themes.\n"
            "2. Edges: Relationships between them (e.g., LOVES, KILLS, LOCATED_IN).\n"
            "Output strictly valid JSON with keys 'nodes' and 'edges'."
        )
        
        try:
            # Use a smart model for extraction
            response = await self.llm.generate_response(
                provider="openai", 
                model="gpt-4o", 
                system_role=system_prompt, 
                prompt=f"Extract graph data from this text:\n\n{text[:4000]}" # Limit chunk size
            )
            
            # Clean markdown formatting if present
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return {"nodes": [], "edges": []}

    async def run_ingestion(self):
        print(f"🧠 Scanning World Bible at: {self.bible_path}")
        
        if not os.path.exists(self.bible_path):
            print(f"⚠️ Path not found. Creating it...")
            os.makedirs(self.bible_path, exist_ok=True)
            # Create a dummy file to test
            with open(os.path.join(self.bible_path, "Mickey_Test.md"), "w") as f:
                f.write("# Mickey\nA cynical detective who hates the rain. He trusts no one except his cat, Luna.")

        master_graph = {"nodes": [], "edges": []}

        for root, _, files in os.walk(self.bible_path):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    print(f"   📄 Reading: {file}...")
                    with open(path, "r") as f:
                        text = f.read()
                        
                    data = await self.extract_graph_from_text(text)
                    
                    # Merge into master graph (Simplistic merge for now)
                    master_graph["nodes"].extend(data.get("nodes", []))
                    master_graph["edges"].extend(data.get("edges", []))
                    print(f"      ✅ Extracted {len(data.get('nodes', []))} nodes")

        # Save the "Brain" to disk
        output_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.json")
        with open(output_path, "w") as f:
            json.dump(master_graph, f, indent=2)
            
        print(f"\n💾 Knowledge Graph saved to: {output_path}")
        print(json.dumps(master_graph, indent=2))

if __name__ == "__main__":
    # Allow running this script directly to test
    ingestor = GraphIngestor()
    asyncio.run(ingestor.run_ingestion())

