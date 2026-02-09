from mcp.server.fastmcp import FastMCP
from github import Github, Auth, GithubIntegration
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../agent_service/.env'))

# Constants
APP_ID = os.getenv("APP_ID")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")

mcp = FastMCP("Repo Tools", dependencies=["PyGithub"])

def get_auth():
    """Returns the AppAuth object."""
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
    """Helper to get an authenticated client for a specific repo."""
    integration = get_integration()
    installation = integration.get_repo_installation(owner, repo)
    return integration.get_github_for_installation(installation.id)

@mcp.tool()
def read_file(owner: str, repo: str, path: str, branch: str = None) -> str:
    """
    Reads the content of a file from a GitHub repository.
    
    Args:
        owner: The owner of the repository (e.g., 'octocat')
        repo: The name of the repository (e.g., 'Hello-World')
        path: The path to the file within the repository
        branch: The branch or commit SHA to read from (optional, defaults to default branch)
    """
    # Note: For now, we'll just use the App's access. 
    # In a real scenario, we might need an installation ID passed in context,
    # or we can look up the installation ID for the repo first.
    
    try:
        gh = get_installation_client(owner, repo)
        repository = gh.get_repo(f"{owner}/{repo}")
        
        # Helper to get file content
        ref = branch if branch else repository.default_branch
        content = repository.get_contents(path, ref=ref)
        return content.decoded_content.decode('utf-8')
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def list_files(owner: str, repo: str, path: str = "/") -> str:
    """
    Lists files in a directory of a GitHub repository.
    """
    try:
        gh = get_installation_client(owner, repo)
        repository = gh.get_repo(f"{owner}/{repo}")
        contents = repository.get_contents(path)
        
        file_list = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repository.get_contents(file_content.path))
            else:
                file_list.append(file_content.path)
        
        return "\n".join(file_list)
    except Exception as e:
        return f"Error listing files: {str(e)}"

@mcp.tool()
def get_pr_diff(owner: str, repo: str, pr_number: int) -> str:
    """
    Gets the diff of a Pull Request.
    """
    try:
        gh = get_installation_client(owner, repo)
        repository = gh.get_repo(f"{owner}/{repo}")
        pull = repository.get_pull(pr_number)
        
        # PyGithub doesn't give raw diff easily via object, but we can request it via headers
        # Or just iterate files
        
        diff_output = []
        for file in pull.get_files():
            diff_output.append(f"--- {file.filename}")
            diff_output.append(f"+++ {file.filename}")
            if file.patch:
                diff_output.append(file.patch)
            else:
                diff_output.append("(Binary or large file)")
            diff_output.append("\n")
            
        return "\n".join(diff_output)
    except Exception as e:
        return f"Error getting PR diff: {str(e)}"

@mcp.tool()
def update_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = None) -> str:
    """
    Updates the content of a file in a GitHub repository (creates a commit).
    
    Args:
        owner: The owner of the repository
        repo: The name of the repository
        path: The path to the file
        content: The new content for the file
        message: The commit message
        branch: The branch to commit to (optional, defaults to default branch)
    """
    try:
        gh = get_installation_client(owner, repo)
        repository = gh.get_repo(f"{owner}/{repo}")
        
        ref = branch if branch else repository.default_branch
        
        # We need the current file SHA to update it
        try:
            current_file = repository.get_contents(path, ref=ref)
            sha = current_file.sha
        except Exception:
            # If file doesn't exist, we can't 'update' it this way in PyGithub
            # but we could 'create' it. For now, let's just handle updates.
            return f"Error: File {path} not found on branch {ref}. Use a creation tool if needed."

        repository.update_file(path, message, content, sha, branch=ref)
        return f"Successfully updated {path} on branch {ref}."
    except Exception as e:
        return f"Error updating file: {str(e)}"

@mcp.tool()
def run_quality_checks(owner: str, repo: str) -> str:
    """
    Runs linting (flake8) and security scans (bandit) on the repository.
    
    Args:
        owner: The owner of the repository
        repo: The name of the repository
    """
    # Note: In a real scenario, this would run against the *local* checkout
    # of the repo. Since we are an MCP server, we assume we have a way to 
    # run these commands in the environment where the repo is accessible.
    
    import subprocess
    
    results = []
    
    # 1. Run Flake8
    try:
        lint_result = subprocess.run(
            ["flake8", "."], 
            capture_output=True, 
            text=True,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        )
        results.append("### Linting Results (flake8)\n")
        results.append(lint_result.stdout if lint_result.stdout else "No linting issues found.")
    except Exception as e:
        results.append(f"Error running flake8: {str(e)}")
        
    results.append("\n---\n")
    
    # 2. Run Bandit
    try:
        sec_result = subprocess.run(
            ["bandit", "-r", "."], 
            capture_output=True, 
            text=True,
            cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        )
        results.append("### Security Scan Results (bandit)\n")
        results.append(sec_result.stdout if sec_result.stdout else "No security issues found.")
    except Exception as e:
        results.append(f"Error running bandit: {str(e)}")
        
    return "\n".join(results)

if __name__ == "__main__":
    mcp.run()
