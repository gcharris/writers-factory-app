import os
import requests
from typing import Generator, Optional
from dotenv import load_dotenv

load_dotenv()  # This forces Python to read your .env file

class GeminiBridge:
    """
    A simple, robust REST client for Gemini.
    Disables streaming to avoid JSON parsing errors.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in environment.")
        
        # Using Gemini 2.0 Flash for speed, or fallback to 1.5 Pro
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

    def send_message(self, user_input: str, context: Optional[str] = None) -> Generator[str, None, None]:
        """
        Sends a request and returns the full text response.
        """
        # 1. Construct the prompt
        full_prompt = user_input
        if context:
            full_prompt = f"SYSTEM CONTEXT:\n{context}\n\nUSER REQUEST:\n{user_input}"

        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }

        try:
            # 2. Send Request (Non-Streaming for reliability)
            response = requests.post(self.url, json=payload)
            response.raise_for_status()

            # 3. Parse Result
            data = response.json()
            
            # Extract text safely
            if "candidates" in data and data["candidates"]:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                # Yield the whole thing at once
                yield content
            else:
                yield "# Error: No content returned from Gemini."
                print(f"Full API Response: {data}")

        except Exception as e:
            yield f"# Critical Error calling API: {str(e)}"

    def close(self):
        pass

if __name__ == "__main__":
    # Simple Test
    bridge = GeminiBridge()
    print("Testing connection...")
    for chunk in bridge.send_message("Say 'System Online' if you can hear me."):
        print(chunk)
