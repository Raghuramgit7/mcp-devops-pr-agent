import os
import logging
import asyncio
from google import genai
from .mcp_client import call_repo_tool
from .github_client import post_comment

logger = logging.getLogger(__name__)

async def run_quality_review(installation_id: int, repo_name: str, pr_number: int):
    """
    Runs security and quality scans via MCP, and uses Gemini to explain the findings.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    model_id = "gemini-3-flash-preview"

    try:
        logger.info(f"Starting quality review for {repo_name}#{pr_number}")
        
        # 1. Run Quality Checks via MCP
        owner, repo = repo_name.split("/")
        quality_result = await call_repo_tool("run_quality_checks", {
            "owner": owner,
            "repo": repo
        })
        
        # FastMCP might wrap the result
        quality_text = quality_result.content[0].text if hasattr(quality_result, 'content') else str(quality_result)

        # 2. Analyze with Gemini (with retry for 429s)
        prompt = f"""
        You are a senior security engineer and code quality lead. 
        Below are the raw results from `flake8` and `bandit` for a recent Pull Request.
        
        Raw Results:
        {quality_text}
        
        Please summarize the most critical security vulnerabilities and significant code quality issues.
        - Ignore minor style warnings if they are overwhelming.
        - Focus on things like hardcoded secrets, insecure function calls, or critical logic errors.
        - Provide a clear, actionable summary for the developer.
        
        If no significant issues are found, return "Code quality and security look solid!".
        
        Format your response in Markdown.
        """
        
        # Simple retry logic for 429 errors
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
                    wait_time = (attempt + 1) * 45
                    logger.warning(f"Rate limit hit in quality_checker. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        if not response:
            logger.error("Failed to get response from Gemini after retries")
            return

        summary = response.text

        if "Code quality and security look solid!" not in summary:
            msg = f"## 🛡️ Security & Quality Report\n\n{summary}"
            post_comment(installation_id, repo_name, pr_number, msg)
            logger.info(f"Posted quality & security report for PR #{pr_number}")
        else:
            logger.info("Quality review passed.")

    except Exception as e:
        logger.error(f"Failed to run quality review: {e}")
