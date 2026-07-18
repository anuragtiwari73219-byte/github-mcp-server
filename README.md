# GitHub MCP Server

An MCP (Model Context Protocol) server that connects Claude Desktop to GitHub - letting Claude list repos, read issues, and create issues directly from chat.

## Tools

- **list_repos** - Lists public repositories for the configured GitHub user, paginated (30/page by default; pass `page` for more)
- **list_issues** - Lists issues for a given repository; `state` can be `open` (default), `closed`, or `all`. Pull requests are filtered out of the results.
- **create_issue** - Creates a new issue in a given repository

All tools return a readable error message instead of crashing if a call fails - covers invalid repo names, missing/empty repo, bad token, network timeouts, connection failures, and GitHub API rate limiting.

## Tech Stack

- Python 3.11
- [MCP](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol SDK
- [httpx](https://www.python-httpx.org/) - Async HTTP client for GitHub API calls
- GitHub REST API v3
- pytest + pytest-httpx for automated testing

## Setup

**1. Clone and create virtual environment**
```bash
git clone https://github.com/anuragtiwari73219-byte/github-mcp-server.git
cd github-mcp-server
python -m venv venv
venv\Scripts\activate  # Windows
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add API credentials**

Copy `.env.example` to `.env` and fill in your values:
```bash
copy .env.example .env
```
Get a token from: https://github.com/settings/tokens (classic, `repo` scope)

**4. Connect to Claude Desktop**

Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "github-mcp-server": {
      "command": "path/to/venv/Scripts/python.exe",
      "args": ["path/to/server.py"]
    }
  }
}
```

## Running Tests

```bash
venv\Scripts\python.exe -m pytest -v
```
10 tests cover success paths, error handling, rate limiting, and edge cases (empty repo name, empty title, invalid state).

## Demo

Once connected, Claude Desktop can:
- "List my GitHub repos" -> calls `list_repos`
- "Show open issues in crew-blog-agent" -> calls `list_issues`
- "Create an issue in ai-email-triage-agent titled 'Fix urgency bug'" -> calls `create_issue`
