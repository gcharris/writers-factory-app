import sys
import os
from dotenv import load_dotenv
load_dotenv()
# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.bridges.gemini_cli import GeminiBridge

def read_docs():
    docs = []
    for f in ["01_architecture.md", "02_scene_pipeline.md"]:
        path = os.path.join("docs", f)
        if os.path.exists(path):
            with open(path, "r") as file: docs.append(file.read())
    return "\n".join(docs)

def main():
    bridge = GeminiBridge()
    context = read_docs()
    
    print("👷 Writers Factory Architect Ready.")
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default=None, help="The prompt for the architect.")
    args = parser.parse_args()
    
    if args.prompt:
        request = args.prompt
    else:
        print("What code do you need generated?")
        request = input("> ")
    
    full_prompt = f"""
    ACT AS: Senior Python Architect.
    CONTEXT: {context}
    TASK: {request}
    OUTPUT: Python code only. No markdown formatting.
    """
    
    print("...Generating...")
    for chunk in bridge.send_message(full_prompt):
        print(chunk, end="", flush=True)
    
    bridge.close()

if __name__ == "__main__":
    main()
