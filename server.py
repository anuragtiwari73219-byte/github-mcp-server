import os
import httpx
import certifi
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

mcp = FastMCP("GitHub MCP Server")

@mcp.tool()
async def list_repos() -> str:
    """List all public repositories for the GitHub user."""
    async with httpx.AsyncClient(verify=certifi.where()) as client:
        response = await client.get(
            f"https://api.github.com/users/{GITHUB_USERNAME}/repos",
            headers=HEADERS
        )
        repos = response.json()
        return "\n".join([f"- {r['name']}: {r['description'] or 'No description'}" for r in repos])