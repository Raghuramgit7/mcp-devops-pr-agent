import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Path to the server scripts
REPO_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), '../../mcp_servers/repo/server.py')
CI_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), '../../mcp_servers/ci/server.py')

@asynccontextmanager
async def get_mcp_client(server_script: str):
    """
    Generic context manager for MCP ClientSession.
    """
    python_executable = sys.executable
    server_params = StdioServerParameters(
        command=python_executable,
        args=[server_script],
        env=os.environ.copy()
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call_repo_tool(tool_name: str, arguments: dict) -> Any:
    """Helper to call a tool on the repo MCP server."""
    async with get_mcp_client(REPO_SERVER_SCRIPT) as session:
        return await session.call_tool(tool_name, arguments)

async def call_ci_tool(tool_name: str, arguments: dict) -> Any:
    """Helper to call a tool on the CI MCP server."""
    async with get_mcp_client(CI_SERVER_SCRIPT) as session:
        return await session.call_tool(tool_name, arguments)
