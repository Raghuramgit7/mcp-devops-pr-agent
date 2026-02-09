import os
from github import Github, Auth, GithubIntegration
import logging

logger = logging.getLogger(__name__)

def get_github_client(installation_id: int) -> Github:
    """
    Returns a PyGithub client authenticated for the given installation ID.
    Reads credentials from environment variables.
    """
    app_id = os.getenv("APP_ID")
    private_key_path = os.getenv("PRIVATE_KEY_PATH")
    
    if not app_id:
        raise ValueError("APP_ID environment variable is not set")
    if not private_key_path:
        raise ValueError("PRIVATE_KEY_PATH environment variable is not set")
        
    # Ensure full path if relative is provided
    if not os.path.isabs(private_key_path):
        # Assuming run from project root or agent_service root, this might be tricky.
        # Let's try to resolve it relative to CWD first.
        if not os.path.exists(private_key_path):
             # Try relative to the location of this file/module if needed, 
             # but for now rely on CWD being project root.
             pass

    try:
        with open(private_key_path, "r") as f:
            private_key = f.read()
    except FileNotFoundError:
        logger.error(f"Private key file not found at {private_key_path}")
        raise

    auth = Auth.AppAuth(app_id=app_id, private_key=private_key)
    integration = GithubIntegration(auth=auth)
    
    # Get a client authenticated as the installation
    # This automatically handles token refresh
    return integration.get_github_for_installation(installation_id)

def post_comment(installation_id: int, repo_name: str, issue_number: int, body: str):
    """
    Post a comment on a PR or Issue.
    """
    try:
        gh = get_github_client(installation_id)
        repo = gh.get_repo(repo_name)
        issue = repo.get_issue(issue_number)
        comment = issue.create_comment(body)
        logger.info(f"Posted comment {comment.id} on {repo_name}#{issue_number}")
        return comment
    except Exception as e:
        logger.error(f"Failed to post comment: {e}")
        raise
