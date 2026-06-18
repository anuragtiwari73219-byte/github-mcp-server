# GitHub MCP Server

An MCP (Model Context Protocol) server that connects Claude Desktop to GitHub — letting Claude list repos, read issues, and create issues directly from chat.

## Tools

- **list_repos** — Lists all public repositories for the configured GitHub user
- **list_issues** — Lists open issues for a given repository
- **create_issue** — Creates a new issue in a given repository

## Tech Stack

- Python 3.11
- [MCP](https://github.com/modelcontextprotocol/python-sdk) — Model Context Protocol SDK
- [httpx](https://www.python-httpx.org/) — Async HTTP client for GitHub API calls
- GitHub REST API v3

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

Create a `.env` file:

GITHUB_TOKEN=your_github_token_here

GITHUB_USERNAME=your_github_username

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

## Demo

Once connected, Claude Desktop can:
- "List my GitHub repos" → calls `list_repos`
- "Show open issues in crew-blog-agent" → calls `list_issues`
- "Create an issue in ai-email-triage-agent titled 'Fix urgency bug'" → calls `create_issue` 