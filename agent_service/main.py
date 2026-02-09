from fastapi import FastAPI, Request, HTTPException
import os
import logging
import asyncio
from dotenv import load_dotenv

# Load .env file from the same directory as this file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Depending on how we run (module vs script), imports might vary.
# Try relative import first, then absolute if that fails (for safe execution)
from core.github_client import post_comment
from core.reviewer import review_pr
from core.fixer import analyze_ci_failure
from core.doc_checker import check_pr_docs
from core.quality_checker import run_quality_review
from core.mcp_client import call_repo_tool, call_ci_tool

# Configure logging at root level
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s:%(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "MCP DevOps Agent Service is running"}

@app.post("/webhook")
async def distinct_webhook(request: Request):
    """
    Handle incoming webhooks from GitHub.
    """
    event_type = request.headers.get("X-GitHub-Event")
    if not event_type:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

    payload = await request.json()
    logger.info(f"Received event: {event_type}")

    # Extract installation ID
    installation = payload.get("installation")
    installation_id = installation.get("id") if installation else None
    
    if event_type == "pull_request":
        action = payload.get("action")
        pr_number = payload.get("number")
        repo_info = payload.get("repository", {})
        repo_name = repo_info.get("full_name")
        
        logger.info(f"PR #{pr_number} in {repo_name} was {action}")

        if action in ["opened", "synchronize", "reopened"]:
            # 1. Post a "Hello World" greeting
            if action == "opened" and installation_id and repo_name and pr_number:
                try:
                    owner, repo = repo_name.split("/")
                    try:
                        readme_content = await call_repo_tool("read_file", {
                            "owner": owner, 
                            "repo": repo, 
                            "path": "README.md"
                        })
                        readme_snippet = readme_content.content[0].text[:200] if hasattr(readme_content, 'content') and readme_content.content else "No content"
                        
                        msg = (f"Hello from the MCP DevOps Agent! I see you opened a PR.\n\n"
                               f"I was able to read your README using my MCP tool:\n"
                               f"```\n{readme_snippet}...\n```")
                    except Exception as mcp_error:
                        logger.error(f"MCP Tool call failed: {mcp_error}")
                        msg = f"Hello! I tried to read your README but failed: {mcp_error}"

                    post_comment(installation_id, repo_name, pr_number, msg)
                except Exception as e:
                    logger.error(f"Failed to post greeting: {e}")
            
            # 2. Trigger AI Review tasks with staggered delays to avoid 429 Rate Limits
            if installation_id and repo_name and pr_number:
                logger.info(f"Scheduling staggered AI tasks for PR #{pr_number}")
                
                async def run_staggered():
                    # 1. Reviewer starts first
                    await asyncio.sleep(5) 
                    asyncio.create_task(review_pr(installation_id, repo_name, pr_number))
                    
                    # 2. Doc Checker starts at T+35
                    await asyncio.sleep(30) 
                    asyncio.create_task(check_pr_docs(installation_id, repo_name, pr_number))
                    
                    # 3. Quality Checker starts at T+65
                    await asyncio.sleep(30)
                    asyncio.create_task(run_quality_review(installation_id, repo_name, pr_number))

                asyncio.create_task(run_staggered())
            else:
                logger.warning("Skipping AI review: missing installation_id, repo_name, or pr_number")
        
    elif event_type == "workflow_run":
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})
        run_id = workflow_run.get("id")
        conclusion = workflow_run.get("conclusion")
        repo_name = payload.get("repository", {}).get("full_name")
        
        logger.info(f"Workflow Run {run_id} {action} with conclusion {conclusion}")

        if action == "completed" and conclusion == "failure":
            pull_requests = workflow_run.get("pull_requests", [])
            pr_number = None
            if pull_requests:
                pr_number = pull_requests[0].get("number")
            else:
                branch = workflow_run.get("head_branch")
                logger.debug(f"Workflow Run {run_id} failed on branch {branch}, but no PR found.")
            
            if pr_number:
                logger.info(f"CI Failure detected in PR #{pr_number}. Triggering Fixer with stagger...")
                async def run_fixer_staggered():
                    await asyncio.sleep(10) # Avoid overlapping with other AI tasks
                    asyncio.create_task(analyze_ci_failure(installation_id, repo_name, run_id, pr_number))
                
                asyncio.create_task(run_fixer_staggered())

    return {"status": "received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
