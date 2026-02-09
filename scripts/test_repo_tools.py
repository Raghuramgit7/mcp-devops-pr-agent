import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_service.core.mcp_client import call_repo_tool

async def test_update_file():
    print("Testing Repo MCP Tool: update_file")
    
    # Configuration - using the playground_repo
    owner = "Raghuramgit7"
    repo = "mcp-devops-pr-agent" # The project itself for testing, or we can use the playground
    path = "requirements.txt"
    content = "flask\nrequests\npytest\npygithub\n" # Adding something
    message = "Test update from AI Agent Verification"
    branch = "main" # Or a test branch
    
    try:
        result = await call_repo_tool("update_file", {
            "owner": owner,
            "repo": repo,
            "path": path,
            "content": content,
            "message": message,
            "branch": branch
        })
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    # Load env vars
    load_dotenv('agent_service/.env')
    asyncio.run(test_update_file())
