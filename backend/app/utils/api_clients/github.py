from typing import Optional

import httpx


async def fetch_github_activity(github_url: str) -> Optional[dict]:
    """Fetch GitHub activity data from a repository URL."""
    if not github_url:
        return None

    repo_name = github_url.rstrip("/").split("/")[-2:]  # Extract `owner/repo`
    if len(repo_name) != 2:
        return None

    repo_path = "/".join(repo_name)
    api_url = f"https://api.github.com/repos/{repo_path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)

        if response.status_code != 200:
            return None

        data = response.json()
        return {
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "open_issues": data.get("open_issues_count"),
            "last_commit": data.get("pushed_at"),
        }
