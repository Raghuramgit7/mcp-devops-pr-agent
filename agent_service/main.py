import asyncio
import logging
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException

from core.github_client import post_comment
from core.reviewer import review_pr
from core.fixer import analyze_ci_failure
from core.doc_checker import check_pr_docs
from core.quality_checker import run_quality_review
from core.mcp_client import call_repo_tool

# Load .env file from the same directory as this file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

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

        # Generate conversation ID for end-to-end tracing
        conversation_id = str(uuid.uuid4())
        logger.info(f"[{conversation_id}] PR #{pr_number} in {repo_name} was {action}")

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
                        content_text = readme_content.content[0].text
                        readme_snippet = content_text[:200]
                        msg = (
                            f"Hello from the MCP DevOps Agent! I see you opened a PR.\n\n"
                            f"I was able to read your README using my MCP tool:\n"
                            f"```\n{readme_snippet}...\n```"
                        )
                    except Exception as mcp_error:
                        logger.error(
                            f"[{conversation_id}] MCP Tool call failed: {mcp_error}"
                        )
                        msg = f"Hello! I tried to read your README but failed: {mcp_error}"

                    post_comment(installation_id, repo_name, pr_number, msg)
                except Exception as e:
                    logger.error(f"[{conversation_id}] Failed to post greeting: {e}")

            # 2. Trigger AI Review tasks with staggered delays to avoid 429 Rate Limits
            if installation_id and repo_name and pr_number:
                logger.info(
                    f"[{conversation_id}] Scheduling staggered AI tasks for PR #{pr_number}"
                )

                async def run_staggered():
                    # 1. Reviewer starts first
                    await asyncio.sleep(5)
                    asyncio.create_task(
                        review_pr(
                            installation_id, repo_name, pr_number, conversation_id
                        )
                    )

                    # 2. Doc Checker starts at T+35
                    await asyncio.sleep(30)
                    asyncio.create_task(
                        check_pr_docs(
                            installation_id, repo_name, pr_number, conversation_id
                        )
                    )

                    # 3. Quality Checker starts at T+65
                    await asyncio.sleep(30)
                    asyncio.create_task(
                        run_quality_review(
                            installation_id, repo_name, pr_number, conversation_id
                        )
                    )

                asyncio.create_task(run_staggered())
            else:
                logger.warning(
                    f"[{conversation_id}] Skipping AI review: missing metadata"
                )

    elif event_type == "workflow_run":
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})
        run_id = workflow_run.get("id")
        conclusion = workflow_run.get("conclusion")
        repo_name = payload.get("repository", {}).get("full_name")
        installation_id = installation.get("id") if installation else None

        # Generate conversation ID for end-to-end tracing of CI failures
        conversation_id = str(uuid.uuid4())
        logger.info(
            f"[{conversation_id}] Workflow {run_id} {action}: {conclusion}"
        )

        if action == "completed" and conclusion == "failure":
            pull_requests = workflow_run.get("pull_requests", [])
            pr_number = None
            if pull_requests:
                pr_number = pull_requests[0].get("number")
            else:
                branch = workflow_run.get("head_branch")
                logger.debug(
                    f"[{conversation_id}] Run {run_id} failed on {branch}, no PR found."
                )

            if pr_number:
                logger.info(
                    f"[{conversation_id}] CI Failure in PR #{pr_number}. Triggering Fixer..."
                )

                async def run_fixer_staggered():
                    # Avoid overlapping with other AI tasks
                    await asyncio.sleep(10)
                    asyncio.create_task(
                        analyze_ci_failure(
                            installation_id, repo_name, run_id, pr_number, conversation_id
                        )
                    )

                asyncio.create_task(run_fixer_staggered())

    return {"status": "received"}


if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 to allow tunneling / exposure
    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec B104
