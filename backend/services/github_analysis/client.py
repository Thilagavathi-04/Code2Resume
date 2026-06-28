import asyncio
import time
import base64
from typing import Any, Dict, Optional

import httpx


class GitHubClient:
    def __init__(self, token: str = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Code2Resume/2.0",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        self._cache: Dict[str, tuple] = {}
        self._cache_ttl = 300
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=15,
                headers=self.headers,
                follow_redirects=True,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _is_cached(self, key: str) -> bool:
        if key in self._cache:
            ts, _ = self._cache[key]
            if time.time() - ts < self._cache_ttl:
                return True
            del self._cache[key]
        return False

    async def _get(self, url: str, timeout: int = 15) -> Optional[Any]:
        if self._is_cached(url):
            return self._cache[url][1]
        try:
            client = await self._get_client()
            resp = await client.get(url, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                self._cache[url] = (time.time(), data)
                return data
            if resp.status_code in (403, 429):
                print(f"[GitHubClient] Rate limited ({resp.status_code}) on {url}")
                return None
            if resp.status_code == 404:
                print(f"[GitHubClient] Not found (404): {url}")
                return None
            print(f"[GitHubClient] Unexpected status {resp.status_code} on {url}")
            return None
        except httpx.TimeoutException:
            print(f"[GitHubClient] Timeout fetching {url}")
            return None
        except Exception as e:
            print(f"[GitHubClient] Error fetching {url}: {e}")
            return None

    async def _get_text(self, url: str, timeout: int = 15) -> Optional[str]:
        if self._is_cached(url):
            return self._cache[url][1]
        try:
            client = await self._get_client()
            resp = await client.get(url, timeout=timeout)
            if resp.status_code == 200:
                content_data = resp.json()
                if content_data.get("encoding") == "base64":
                    text = base64.b64decode(content_data["content"]).decode("utf-8")
                    self._cache[url] = (time.time(), text)
                    return text
            if resp.status_code != 404:
                print(f"[GitHubClient] Text fetch status {resp.status_code}: {url}")
        except httpx.TimeoutException:
            print(f"[GitHubClient] Timeout fetching text {url}")
        except Exception as e:
            print(f"[GitHubClient] Error fetching text {url}: {e}")
        return None

    async def get_repo(self, owner: str, repo: str) -> dict:
        data = await self._get(f"{self.base_url}/repos/{owner}/{repo}")
        return data or {}

    async def get_languages(self, owner: str, repo: str) -> dict:
        data = await self._get(f"{self.base_url}/repos/{owner}/{repo}/languages")
        return data or {}

    async def get_readme(self, owner: str, repo: str) -> str:
        for name in ["README.md", "readme.md", "README.txt", "README.rst", "README"]:
            text = await self._get_text(
                f"{self.base_url}/repos/{owner}/{repo}/contents/{name}"
            )
            if text:
                return text[:8000]
        return ""

    async def get_tree(self, owner: str, repo: str) -> list:
        repo_data = await self.get_repo(owner, repo)
        default_branch = repo_data.get("default_branch", "main")
        sha = None
        branch_data = await self._get(f"{self.base_url}/repos/{owner}/{repo}/branches/{default_branch}")
        if branch_data and "commit" in branch_data:
            sha = branch_data["commit"]["sha"]
        if not sha:
            print(f"[GitHubClient] Could not get SHA for {owner}/{repo} branch {default_branch}")
            return []
        data = await self._get(
            f"{self.base_url}/repos/{owner}/{repo}/git/trees/{sha}?recursive=1",
            timeout=30,
        )
        if data and "tree" in data:
            truncated = data.get("truncated", False)
            if truncated:
                print(f"[GitHubClient] Tree truncated for {owner}/{repo}, some files may be missing")
            return data["tree"]
        print(f"[GitHubClient] No tree data for {owner}/{repo}")
        return []

    async def get_contents(self, owner: str, repo: str, path: str) -> Optional[dict]:
        return await self._get(f"{self.base_url}/repos/{owner}/{repo}/contents/{path}")

    async def get_commits(self, owner: str, repo: str, per_page: int = 100, page: int = 1) -> list:
        data = await self._get(
            f"{self.base_url}/repos/{owner}/{repo}/commits?per_page={per_page}&page={page}"
        )
        return data if isinstance(data, list) else []

    async def get_commit_activity(self, owner: str, repo: str) -> list:
        data = await self._get(f"{self.base_url}/repos/{owner}/{repo}/stats/commit_activity")
        return data if isinstance(data, list) else []

    async def get_contributors(self, owner: str, repo: str) -> list:
        data = await self._get(f"{self.base_url}/repos/{owner}/{repo}/contributors")
        return data if isinstance(data, list) else []

    async def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        return await self._get_text(f"{self.base_url}/repos/{owner}/{repo}/contents/{path}")

    async def fetch_all(self, owner: str, repo: str) -> tuple:
        print(f"[GitHubClient] Fetching all data for {owner}/{repo}...")
        t0 = time.time()
        repo_data, readme, languages, tree = await asyncio.gather(
            self.get_repo(owner, repo),
            self.get_readme(owner, repo),
            self.get_languages(owner, repo),
            self.get_tree(owner, repo),
        )
        elapsed = round(time.time() - t0, 2)
        print(f"[GitHubClient] Fetched {owner}/{repo} in {elapsed}s: repo={bool(repo_data)}, readme={len(readme)} chars, langs={len(languages)}, tree={len(tree)} items")
        return repo_data, readme, languages, tree
