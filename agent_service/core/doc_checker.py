import os
import logging
import json
import re
import asyncio
from google import genai
from .mcp_client import call_repo_tool
from .github_client import post_comment, get_github_client

logger = logging.getLogger(__name__)

async def check_pr_docs(installation_id: int, repo_name: str, pr_number: int):
    """
    Analyzes the PR diff to see if documentation (docstrings, README) needs updates.
    If simple documentation fixes are identified, it attempts to apply them.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    try:
        logger.info(f"Checking documentation for {repo_name}#{pr_number}")
        
        # 1. Fetch PR details for branch info
        gh = get_github_client(installation_id)
        repository = gh.get_repo(repo_name)
        pull = repository.get_pull(pr_number)
        branch_name = pull.head.ref

        # 2. Fetch Diff via MCP
        owner, repo = repo_name.split("/")
        diff_result = await call_repo_tool("get_pr_diff", {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        })
        
        diff_text = diff_result.content[0].text if diff_result.content else ""
        if not diff_text:
            return

        # 3. Analyze with Gemini (with retry for 429s)
        prompt = f"""
        You are a meticulous technical writer and engineer. Review the Pull Request diff below.
        Check for the following:
        1. Are there new functions or classes missing docstrings?
        2. Are there major logic changes that should be reflected in the README.md?
        
        If you find missing docstrings that can be easily added, provide them in a structured JSON block.
        
        JSON Structure:
        ```json
        {{
          "file_path": "path/to/file",
          "new_content": "entire new content of the file WITH THE DOCSTRINGS ADDED",
          "commit_message": "docs: added missing docstrings"
        }}
        ```
        
        PR Diff:
        {diff_text}
        
        If there are documentation gaps, provide a concise list of suggestions. 
        If everything looks well-documented, just return "Documentation looks great!".
        
        Format your response in Markdown.
        """
        
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
                    wait_time = (attempt + 1) * 40 # Staggered
                    logger.warning(f"Rate limit hit in doc_checker. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        if not response:
            logger.error("Failed to get response from Gemini after retries")
            return

        ai_response = response.text

        # 4. Parse and Apply Auto-Docs Fix if available
        fix_applied = False
        json_match = re.search(r"```json\s+(.*?)\s+```", ai_response, re.DOTALL)
        if json_match:
            try:
                fix_data = json.loads(json_match.group(1))
                file_path = fix_data.get("file_path")
                new_content = fix_data.get("new_content")
                commit_msg = fix_data.get("commit_message", "docs: AI auto-generated docstrings")
                
                if file_path and new_content:
                    logger.info(f"Attempting auto-docs fix for {file_path} on {branch_name}")
                    await call_repo_tool("update_file", {
                        "owner": owner,
                        "repo": repo,
                        "path": file_path,
                        "content": new_content,
                        "message": commit_msg,
                        "branch": branch_name
                    })
                    fix_applied = True
            except Exception as json_err:
                logger.error(f"Failed to apply auto-docs JSON: {json_err}")

        # 5. Post Comment
        suggestions = ai_response
        if "Documentation looks great!" not in suggestions or fix_applied:
            review_body = suggestions
            if fix_applied:
                review_body += f"\n\n---\n**📝 AI Documentation Fix Applied**: I have added missing docstrings to `{file_path}` on branch `{branch_name}`. Please review."
            
            msg = f"## 📚 Documentation Review\n\n{review_body}"
            post_comment(installation_id, repo_name, pr_number, msg)
            logger.info(f"Posted documentation report for PR #{pr_number}")
        else:
            logger.info("Documentation check passed.")

    except Exception as e:
        logger.error(f"Failed to check documentation: {e}")
