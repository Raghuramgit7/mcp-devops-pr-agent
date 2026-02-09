from mcp.server.fastmcp import FastMCP
from github import Github, Auth, GithubIntegration
import os
import requests
import io
import zipfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../agent_service/.env'))

# Constants
APP_ID = os.getenv("APP_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

mcp = FastMCP("CI Tools", dependencies=["PyGithub", "requests"])

def get_auth():
    pk_path = PRIVATE_KEY_PATH
    if not os.path.isabs(pk_path):
        pk_path = os.path.join(os.path.dirname(__file__), '../../', PRIVATE_KEY_PATH)
    with open(pk_path, "r") as f:
        private_key = f.read()
    return Auth.AppAuth(app_id=APP_ID, private_key=private_key)

def get_integration():
    """Returns the GithubIntegration object."""
    auth = get_auth()
    return GithubIntegration(auth=auth)

def get_installation_client(owner: str, repo: str) -> Github:
    integration = get_integration()
    installation = integration.get_repo_installation(owner, repo)
    return integration.get_github_for_installation(installation.id)

@mcp.tool()
def get_workflow_run_logs(owner: str, repo: str, run_id: int) -> str:
    """
    Fetches the logs for a specific GitHub Actions workflow run.
    """
    try:
        gh = get_installation_client(owner, repo)
        repository = gh.get_repo(f"{owner}/{repo}")
        run = repository.get_workflow_run(run_id)
        
        # Download logs zip
        log_url = run.logs_url
        
        # We need the installation token for the manual request
        integration = get_integration()
        installation = integration.get_repo_installation(owner, repo)
        token = integration.get_access_token(installation.id).token
        
        response = requests.get(log_url, headers={"Authorization": f"token {token}"})
        
        if response.status_code != 200:
            return f"Error downloading logs: {response.status_code}"
            
        # Parse zip
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Get all log files (usually one per step/job)
            all_logs = []
            for name in z.namelist():
                if name.endswith(".txt"):
                    with z.open(name) as f:
                        content = f.read().decode('utf-8')
                        all_logs.append(f"--- LOG: {name} ---\n{content}\n")
            
            return "\n".join(all_logs) if all_logs else "No logs found in zip."
            
    except Exception as e:
        return f"Error fetching logs: {str(e)}"

if __name__ == "__main__":
    mcp.run()
