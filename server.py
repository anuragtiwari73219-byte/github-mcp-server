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


def _resolve_repo(repo: str) -> str:
    """Accepts 'owner/repo' or just 'repo' (defaults to GITHUB_USERNAME)."""
    return repo if "/" in repo else f"{GITHUB_USERNAME}/{repo}"


async def _github_request(method: str, url: str, **kwargs) -> tuple[bool, object]:
    """Shared request helper. Returns (ok, data_or_error_message)."""
    async with httpx.AsyncClient(verify=certifi.where()) as client:
        response = await client.request(method, url, headers=HEADERS, **kwargs)

    if response.status_code >= 400:
        try:
            message = response.json().get("message", response.text)
        except ValueError:
            message = response.text
        return False, f"GitHub API error ({response.status_code}): {message}"

    return True, response.json()


@mcp.tool()
async def list_repos(page: int = 1, per_page: int = 30) -> str:
    """List public repositories for the configured GitHub user.

    GitHub paginates at 30 repos per page by default. If a user has more
    repos than one page, call again with an incremented `page` to see more.
    """
    if not GITHUB_USERNAME:
        return "Error: GITHUB_USERNAME is not set in the environment."

    ok, data = await _github_request(
        "GET",
        f"https://api.github.com/users/{GITHUB_USERNAME}/repos",
        params={"page": page, "per_page": per_page},
    )
    if not ok:
        return data

    if not data:
        return f"No repos found on page {page}."

    lines = [f"- {r['name']}: {r['description'] or 'No description'}" for r in data]
    footer = f"\n\n(page {page}, {len(data)} repos shown -- call again with page={page + 1} for more)" \
        if len(data) == per_page else ""
    return "\n".join(lines) + footer


@mcp.tool()
async def list_issues(repo: str, state: str = "open") -> str:
    """List issues for a repository.

    Args:
        repo: Repository as 'owner/repo', or just 'repo' to use the
            configured GITHUB_USERNAME as owner.
        state: One of 'open', 'closed', or 'all'. Defaults to 'open'.
    """
    if state not in ("open", "closed", "all"):
        return "Error: state must be one of 'open', 'closed', or 'all'."

    owner_repo = _resolve_repo(repo)
    ok, data = await _github_request(
        "GET",
        f"https://api.github.com/repos/{owner_repo}/issues",
        params={"state": state},
    )
    if not ok:
        return data

    # The issues endpoint also returns pull requests; filter those out.
    issues = [i for i in data if "pull_request" not in i]
    if not issues:
        return f"No {state} issues found in {owner_repo}."

    return "\n".join(f"#{i['number']} {i['title']} ({i['state']})" for i in issues)


@mcp.tool()
async def create_issue(repo: str, title: str, body: str = "") -> str:
    """Create a new issue in a repository.

    Args:
        repo: Repository as 'owner/repo', or just 'repo' to use the
            configured GITHUB_USERNAME as owner.
        title: Issue title.
        body: Optional issue body/description.
    """
    if not title.strip():
        return "Error: title cannot be empty."

    owner_repo = _resolve_repo(repo)
    ok, data = await _github_request(
        "POST",
        f"https://api.github.com/repos/{owner_repo}/issues",
        json={"title": title, "body": body},
    )
    if not ok:
        return data

    return f"Created issue #{data['number']}: {data['html_url']}"


if __name__ == '__main__':
    mcp.run()
