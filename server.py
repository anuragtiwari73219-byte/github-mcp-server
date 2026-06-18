import os
import httpx
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
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            f"https://api.github.com/users/{GITHUB_USERNAME}/repos",
            headers=HEADERS
        )
        repos = response.json()
        return "\n".join([f"- {r['name']}: {r['description'] or 'No description'}" for r in repos])

@mcp.tool()
async def list_issues(repo_name: str) -> str:
    """List open issues for a given repository."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/issues",
            headers=HEADERS
        )
        issues = response.json()
        if not issues:
            return "No open issues found."
        return "\n".join([f"#{i['number']}: {i['title']}" for i in issues])

@mcp.tool()
async def create_issue(repo_name: str, title: str, body: str) -> str:
    """Create a new issue in a given repository."""
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/issues",
            headers=HEADERS,
            json={"title": title, "body": body}
        )
        issue = response.json()
        return f"Issue created: #{issue['number']} - {issue['title']}\nURL: {issue['html_url']}"

if __name__ == "__main__":
    mcp.run()