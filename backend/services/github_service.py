import asyncio
import time
from typing import Any, Dict
from urllib.parse import urlparse

from app.core.config import settings
from services.github_analysis import analyze_repository as _analyze_repository


class GitHubService:
    """Service to interact with GitHub API and extract repository information"""

    def __init__(self, user_token: str = None):
        self.base_url = settings.GITHUB_API_BASE
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Code2Resume/2.0",
        }

        token = user_token or settings.GITHUB_TOKEN
        if token:
            self.headers["Authorization"] = f"token {token}"
        self.user_token = token

    async def analyze_repository(self, repo_url: str, skip_semantic: bool = False) -> Dict[str, Any]:
        """Extract comprehensive information from a GitHub repository"""
        parsed = urlparse(repo_url)
        repo_name = parsed.path.strip("/").split("/")[-1] if parsed.path else "?"
        print(f"[GitHubService] analyze_repository({repo_url}) skip_semantic={skip_semantic}")
        t0 = time.time()
        try:
            result = await _analyze_repository(repo_url, self.user_token, skip_semantic=skip_semantic)
            result["tech_stack_flat"] = _flatten_tech_stack(result.get("tech_stack", {}))
            elapsed = round(time.time() - t0, 2)
            tech_count = len(result.get("tech_stack_flat", []))
            arch = result.get("architecture", {}).get("type", "?")
            cls = result.get("classification", {}).get("primary", "?")
            print(f"[GitHubService] Analysis OK for {repo_name} in {elapsed}s: {tech_count} techs, arch={arch}, class={cls}")
            return result
        except Exception as e:
            elapsed = round(time.time() - t0, 2)
            print(f"[GitHubService] Analysis FAILED for {repo_name} in {elapsed}s: {e}")
            raise Exception(f"Failed to analyze repository: {str(e)}")

    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Extract owner and repo name from GitHub URL"""
        parsed = urlparse(repo_url)
        if parsed.netloc != "github.com":
            raise ValueError("Invalid GitHub URL")
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL format")
        return path_parts[0], path_parts[1]


def _flatten_tech_stack(tech_stack: dict) -> list:
    flat = []
    for category in tech_stack.values():
        if isinstance(category, list):
            for item in category:
                if item not in flat:
                    flat.append(item)
    return flat[:20]
