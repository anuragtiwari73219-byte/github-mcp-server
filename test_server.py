import os
os.environ.setdefault("GITHUB_TOKEN", "fake-token-for-tests")
os.environ.setdefault("GITHUB_USERNAME", "fakeuser")

import pytest
from server import list_repos, list_issues, create_issue, _resolve_repo


# ---------- _resolve_repo tests ----------

def test_resolve_repo_with_owner():
    assert _resolve_repo("someone/somerepo") == "someone/somerepo"


def test_resolve_repo_without_owner():
    assert _resolve_repo("somerepo") == "fakeuser/somerepo"


# ---------- list_repos tests ----------

@pytest.mark.asyncio
async def test_list_repos_success(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/users/fakeuser/repos?page=1&per_page=30",
        json=[
            {"name": "repo-one", "description": "First repo"},
            {"name": "repo-two", "description": None},
        ],
    )
    result = await list_repos()
    assert "repo-one: First repo" in result
    assert "repo-two: No description" in result


@pytest.mark.asyncio
async def test_list_repos_empty_page(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/users/fakeuser/repos?page=1&per_page=30",
        json=[],
    )
    result = await list_repos()
    assert "No repos found" in result


@pytest.mark.asyncio
async def test_list_repos_api_error(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/users/fakeuser/repos?page=1&per_page=30",
        status_code=404,
        json={"message": "Not Found"},
    )
    result = await list_repos()
    assert "404" in result
    assert "Not Found" in result


@pytest.mark.asyncio
async def test_list_repos_rate_limited(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/users/fakeuser/repos?page=1&per_page=30",
        status_code=403,
        headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"},
        json={"message": "rate limit exceeded"},
    )
    result = await list_repos()
    assert "rate limit exceeded" in result.lower()
    assert "1234567890" in result


# ---------- list_issues tests ----------

@pytest.mark.asyncio
async def test_list_issues_success(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/fakeuser/somerepo/issues?state=open",
        json=[
            {"number": 1, "title": "Bug A", "state": "open"},
            {"number": 2, "title": "PR not an issue", "state": "open", "pull_request": {}},
        ],
    )
    result = await list_issues("somerepo")
    assert "#1 Bug A" in result
    assert "#2" not in result  # pull requests filtered out


@pytest.mark.asyncio
async def test_list_issues_invalid_state():
    result = await list_issues("somerepo", state="bogus")
    assert "must be one of" in result


# ---------- create_issue tests ----------

@pytest.mark.asyncio
async def test_create_issue_success(httpx_mock):
    httpx_mock.add_response(
        url="https://api.github.com/repos/fakeuser/somerepo/issues",
        method="POST",
        json={"number": 42, "html_url": "https://github.com/fakeuser/somerepo/issues/42"},
    )
    result = await create_issue("somerepo", "Test title", "Test body")
    assert "#42" in result
    assert "https://github.com/fakeuser/somerepo/issues/42" in result


@pytest.mark.asyncio
async def test_create_issue_empty_title():
    result = await create_issue("somerepo", "   ")
    assert "cannot be empty" in result