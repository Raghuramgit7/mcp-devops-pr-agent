import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_service.core.quality_checker import run_quality_review

async def test_quality_checker():
    print("Testing Quality Checker Analysis with Gemini")
    
    # Configuration
    installation_id = 60321281 # Use the ID from logs or a placeholder if testing logic only
    repo_name = "Raghuramgit7/mcp-devops-pr-agent"
    pr_number = 1
    
    # Note: run_quality_review requires installation_id to fetch PR details and post comment.
    # To test locally without actual GitHub calls, we would need to mock github_client.
    # For now, let's run it and see it fail gracefully or succeed if keys are valid.
    
    try:
        await run_quality_review(installation_id, repo_name, pr_number)
        print("Success: Quality review process completed.")
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    # Load env vars
    load_dotenv('agent_service/.env')
    asyncio.run(test_quality_checker())
