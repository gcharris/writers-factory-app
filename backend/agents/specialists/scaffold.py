import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path to allow sibling imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# We will be mocking these, but in a real scenario they would be imported
# from backend.graph.graph_service import KnowledgeGraphService
# from backend.mcp.client import MCPClient # Assuming an MCP client exists

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SmartScaffoldAgent:
    """
    Generates a structured 'ACE Scaffold' for a scene using context from the
    knowledge graph and a research client (e.g., NotebookLM).
    """
    def __init__(self, graph_service: Any, mcp_client: Any, template_path: str):
        """
        Initializes the agent.

        Args:
            graph_service: An instance of KnowledgeGraphService (or a mock).
            mcp_client: A client for fetching research context (or a mock).
            template_path: The file path to the ACE scaffold template.
        """
        self.graph_service = graph_service
        self.mcp_client = mcp_client
        try:
            with open(template_path, 'r') as f:
                self.template = f.read()
            logging.info(f"Successfully loaded template from {template_path}")
        except FileNotFoundError:
            logging.error(f"Template file not found at: {template_path}")
            self.template = "TEMPLATE NOT FOUND"

    def generate_scaffold(self, scene_id: int) -> str:
        """
        Generates the scaffold markdown for a given scene ID.

        Args:
            scene_id: The ID of the scene to scaffold.

        Returns:
            A markdown string of the completed scaffold.
        """
        logging.info(f"Generating scaffold for scene_id: {scene_id}")

        # 1. Query graph for the scene node
        scene_node = self.graph_service.get_node(scene_id)
        if not scene_node:
            return f"Error: Scene node with ID {scene_id} not found in the graph."

        # 2. Create a data dictionary, combining real node data with mock data for this test
        scene_data = {
            "title": scene_node.name,
            "description": scene_node.description,
            # Mock data for attributes not yet in the schema
            "act": "Act II",
            "setting": "A dimly lit warehouse at midnight.",
            "word_count": 2500,
            "beats": [
                "Alice arrives and surveys the scene.",
                "Bob emerges from the shadows, presenting the package.",
                "A sudden noise outside startles them.",
                "They agree to move to a more secure location."
            ],
            "core_function": "To create the inciting incident for the final confrontation."
        }
        logging.info(f"Found scene node '{scene_data['title']}'. Supplementing with mock details for scaffold.")

        # 3. Query MCP client for NotebookLM context (mocked)
        research_context = self.mcp_client.get_context_for_scene(scene_id)

        # 4. Populate the template
        logging.info("Populating ACE template with fetched data...")
        
        scaffold = self.template
        placeholders = {
            "{{chapter_title}}": scene_data.get("title", "Untitled"),
            "{{act}}": scene_data.get("act", "TBD"),
            "{{setting}}": scene_data.get("setting", "Unknown"),
            "{{word_count}}": scene_data.get("word_count", 1500),
            "{{beats}}": "\n".join([f"- {beat}" for beat in scene_data.get("beats", [])]),
            "(Define the specific character state and narrative distance)": "Mickey's perspective, feeling trapped but observant.",
            "(What is the single narrative purpose of this scene?)": scene_data.get("core_function", "To introduce the new conflict."),
            "(A brief meta-note to the drafting agents explaining how to approach this scene)": research_context
        }

        for key, value in placeholders.items():
            scaffold = scaffold.replace(key, str(value))

        logging.info("Scaffold generation complete.")
        return scaffold


if __name__ == "__main__":
    logging.info("--- Running SmartScaffoldAgent Verification ---")

    # 1. Mock the dependencies (Graph Service and MCP Client)
    class MockGraphService:
        def get_scene_details(self, scene_id: int) -> Dict[str, Any]:
            logging.info(f"[MOCK] GraphService received request for scene_id: {scene_id}")
            return {
                "title": "Chapter 10: The Rendezvous",
                "act": "Act II",
                "setting": "A dimly lit warehouse at midnight.",
                "word_count": 2500,
                "beats": [
                    "Alice arrives and surveys the scene.",
                    "Bob emerges from the shadows, presenting the package.",
                    "A sudden noise outside startles them.",
                    "They agree to move to a more secure location."
                ],
                "core_function": "To create the inciting incident for the final confrontation."
            }

    class MockMCPClient:
        def get_context_for_scene(self, scene_id: int) -> str:
            logging.info(f"[MOCK] MCPClient received request for scene_id: {scene_id}")
            return "This scene must emphasize the tension and mistrust between Alice and Bob. Research notes suggest Alice is carrying a hidden transmitter. The package contains the MacGuffin blueprints."

    # 2. Define path to the template
    # Assumes this script is in backend/agents/specialists/
    template_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'ace_structure.md')

    # 3. Initialize the agent with mocked services
    mock_graph = MockGraphService()
    mock_mcp = MockMCPClient()
    scaffold_agent = SmartScaffoldAgent(
        graph_service=mock_graph, 
        mcp_client=mock_mcp,
        template_path=template_file_path
    )

    # 4. Run the scaffold generation and print the result
    generated_scaffold = scaffold_agent.generate_scaffold(scene_id=101)
    
    print("\n" + "="*50)
    print("    GENERATED SCAFFOLD    ")
    print("="*50 + "\n")
    print(generated_scaffold)
    print("\n" + "="*50)
    print("    VERIFICATION COMPLETE    ")
    print("="*50 + "\n")
