import asyncio
import httpx
import os
import sys

# Add parent directory to path to import settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_fetch(username: str, token: str = None):
    print(f"Testing fetch for user: {username}")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
        print("Using provided token.")
    else:
        print("No token provided. Using unauthenticated requests (rate limit: 60/hr).")

    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        # 1. Fetch Repos
        url = f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated"
        print(f"Fetching: {url}")
        resp = await client.get(url)
        
        if resp.status_code != 200:
            print(f"❌ Failed to fetch repos. Status: {resp.status_code}")
            print(f"Response: {resp.text}")
            return

        repos = resp.json()
        print(f"✅ Found {len(repos)} repos.")
        
        if not repos:
            print("No repositories found.")
            return

        # 2. Fetch Details for first repo
        repo = repos[0]
        print(f"\nTesting details for repo: {repo['name']}")
        
        # README
        readme_url = f"https://api.github.com/repos/{username}/{repo['name']}/readme"
        print(f"Fetching README: {readme_url}")
        readme_resp = await client.get(readme_url)
        
        if readme_resp.status_code == 200:
            print("✅ README found.")
        else:
            print(f"⚠️ README not found. Status: {readme_resp.status_code}")

        # Languages
        lang_url = f"https://api.github.com/repos/{username}/{repo['name']}/languages"
        print(f"Fetching Languages: {lang_url}")
        lang_resp = await client.get(lang_url)
        
        if lang_resp.status_code == 200:
            print(f"✅ Languages: {lang_resp.json()}")
        else:
            print(f"⚠️ Languages fetch failed. Status: {lang_resp.status_code}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_fetch.py <github_username> [token]")
    else:
        username = sys.argv[1]
        token = sys.argv[2] if len(sys.argv) > 2 else None
        asyncio.run(test_fetch(username, token))
