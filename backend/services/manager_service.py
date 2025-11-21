import ollama
import os
from typing import List, Dict, Optional

class ManagerService:
    """
    The 'Writer's Cursor' - Local Integrated Agent.
    Uses Ollama to provide zero-latency, private assistance.
    """
    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.context_history: List[int] = [] # Stores context tokens for continuity
        self.system_prompt = (
            "You are the Manager, a local AI assistant for a novelist. "
            "You have direct access to the file system and knowledge graph. "
            "Be concise, helpful, and focused on the text."
        )

    def check_status(self) -> bool:
        """Ping Ollama to see if it's running."""
        try:
            # Simple list command to check connection
            ollama.list()
            return True
        except Exception:
            return False

    def chat(self, message: str, file_context: Optional[str] = None) -> str:
        """
        Send a chat message to the local model.
        
        Args:
            message: User's question/command.
            file_context: Optional text content from the active file.
        """
        try:
            prompt = message
            if file_context:
                prompt = f"CONTEXT FROM ACTIVE FILE:\n{file_context}\n\nUSER QUERY:\n{message}"

            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return response['message']['content']
        except Exception as e:
            return f"Manager Error: Is Ollama running? ({str(e)})"

    def summarize_file(self, content: str) -> str:
        """Quickly summarize a text block (useful for Graph ingestion)."""
        try:
            response = ollama.generate(
                model=self.model,
                prompt=f"Summarize the following scene logic and character developments in 3 bullet points:\n\n{content}"
            )
            return response['response']
        except Exception as e:
            return f"Error summarizing: {str(e)}"

