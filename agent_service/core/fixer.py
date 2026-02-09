import os
import logging
import json
import re
import asyncio
from google import genai
from .mcp_client import call_ci_tool, call_repo_tool
from .github_client import post_comment, get_github_client

logger = logging.getLogger(__name__)

async def analyze_ci_failure(installation_id: int, repo_name: str, run_id: int, pr_number: int):
    """
    Triggered when CI fails. Fetches logs, analyzes with Gemini, and posts suggestion.
    If a clear fix is identified, it attempts to apply it.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    try:
        logger.info(f"Analyzing CI failure for run {run_id} in {repo_name}...")
        
        # 1. Fetch Logs via CI MCP
        owner, repo = repo_name.split("/")
        logs_result = await call_ci_tool("get_workflow_run_logs", {
            "owner": owner,
            "repo": repo,
            "run_id": run_id
        })
        
        logs_text = logs_result.content[0].text if logs_result.content else ""
        if not logs_text:
            logger.warning("No CI logs fetched.")
            return

        # 2. Fetch PR details to get branch name
        gh = get_github_client(installation_id)
        repository = gh.get_repo(repo_name)
        pull = repository.get_pull(pr_number)
        branch_name = pull.head.ref

        # 3. Analyze with Gemini
        snippet = logs_text[-8000:] # Focus on the end of the logs
        
        prompt = f"""
        You are an expert DevOps engineer. A GitHub Action just failed on branch '{branch_name}'.
        Below are the logs from the failure. 
        Identify the root cause and suggest a fix.
        
        IF AND ONLY IF the fix is a simple code change (e.g., fixing a syntax error, a small test bug, or an import), 
        provide the fix in a structured JSON block at the end of your response.
        
        JSON Structure:
        ```json
        {{
          "file_path": "path/to/file",
          "new_content": "entire new content of the file",
          "commit_message": "fixed syntax error in app.py"
        }}
        ```
        
        CI Logs Snippet:
        {snippet}
        
        Format your response as a PR comment in Markdown.
        """
        
        # 2. Analyze with Gemini (with retry for 429s)
        # The original prompt already includes the logs, so msg_context is not directly used in the prompt itself.
        # log_text is equivalent to snippet here.
        
        response = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt
                )
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    wait_time = (attempt + 1) * 50 # Fixer often has large logs, longer wait
                    logger.warning(f"Rate limit hit in fixer. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        if not response:
            logger.error("Failed to get diagnosis from Gemini after retries")
            return

        analysis = response.text

        # 4. Parse Structured Fix if available
        fix_applied = False
        json_match = re.search(r"```json\s+(.*?)\s+```", analysis, re.DOTALL) # Changed ai_response to analysis
        if json_match:
            try:
                fix_data = json.loads(json_match.group(1))
                file_path = fix_data.get("file_path")
                new_content = fix_data.get("new_content")
                commit_msg = fix_data.get("commit_message", "AI auto-fix for CI failure")
                
                if file_path and new_content:
                    logger.info(f"Attempting auto-fix for {file_path} on {branch_name}")
                    result = await call_repo_tool("update_file", {
                        "owner": owner,
                        "repo": repo,
                        "path": file_path,
                        "content": new_content,
                        "message": commit_msg,
                        "branch": branch_name
                    })
                    logger.info(f"Auto-fix result: {result}")
                    fix_applied = True
            except Exception as json_err:
                logger.error(f"Failed to parse or apply auto-fix JSON: {json_err}")

        # 5. Post Comment
        review_body = analysis
        if fix_applied:
            review_body += f"\n\n---\n**🚀 AI Auto-Fix Applied**: I have attempted to fix the issue by updating `{file_path}` on branch `{branch_name}`. Please verify the changes."
        
        msg = f"## 🛠️ CI Failure Analysis\n\n{review_body}"
        post_comment(installation_id, repo_name, pr_number, msg)
        logger.info(f"Posted CI analysis for PR #{pr_number}")

    except Exception as e:
        logger.error(f"Failed to analyze CI failure: {e}")
