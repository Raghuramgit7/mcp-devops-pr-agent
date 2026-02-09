import os
import logging
import asyncio
from google import genai
from .mcp_client import call_repo_tool
from .github_client import post_comment

logger = logging.getLogger(__name__)

async def review_pr(installation_id: int, repo_name: str, pr_number: int):
    """
    Fetches the PR diff using MCP, analyzes it with Gemini 2.5 Flash, and posts a review comment.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found in environment")
        return

    # Initialize New Gemini SDK
    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    try:
        logger.info(f"Starting review process for {repo_name}#{pr_number}")
        # 1. Fetch Diff via MCP
        owner, repo = repo_name.split("/")
        logger.info(f"Calling MCP tool 'get_pr_diff' for {owner}/{repo}")
        diff_result = await call_repo_tool("get_pr_diff", {
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        })
        
        diff_text = diff_result.content[0].text if diff_result.content else ""
        if not diff_text:
            logger.warning(f"No diff found for PR #{pr_number}")
            return
        
        logger.info(f"Diff fetched successfully ({len(diff_text)} chars). Querying Gemini...")

        # 2. Analyze with Gemini 2.5 Flash (with retry for 429s)
        prompt = f"""
        You are an expert software engineer reviewing a Pull Request.
        Below is the diff of the changes. 
        Please provide a concise review identifying potential bugs, security issues, or performance bottlenecks.
        If the code looks good, briefly explain why.
        
        PR Diff:
        {diff_text}
        
        Format your response in Markdown. Keep it under 300 words.
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
                    wait_time = (attempt + 1) * 35 # Staggered reviewer backoff
                    logger.warning(f"Rate limit hit in reviewer. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        if not response:
            logger.error("Failed to get review from Gemini after retries")
            return

        review_text = response.text

        # 3. Post Comment
        msg = f"## 🤖 AI Code Review (Gemini 2.5 Flash)\n\n{review_text}"
        post_comment(installation_id, repo_name, pr_number, msg)
        logger.info(f"Posted AI review for PR #{pr_number}")

    except Exception as e:
        logger.error(f"Failed to review PR #{pr_number}: {e}")
