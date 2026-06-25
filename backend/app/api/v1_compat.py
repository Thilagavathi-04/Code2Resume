import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_current_user, create_access_token
from app.services import user_service

router = APIRouter(tags=["v1-compat"])

analysis_jobs = {}


class RepoRequest(BaseModel):
    url: Optional[str] = None


class AskRequest(BaseModel):
    query: str


class ResumeRequest(BaseModel):
    query: str
    domain: Optional[str] = None


@router.get("/repos")
async def get_user_repos(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    if not user or not user.github_url:
        return []

    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        repos = rag_service.get_user_repos(user.username)
        if repos:
            return repos
    except Exception as e:
        print(f"RAG fetch failed, falling back to GitHub API: {e}")

    try:
        from services.github_service import GitHubService
        gh = GitHubService(user.github_token)
        parsed = urlparse(user.github_url)
        parts = parsed.path.strip('/').split('/')
        owner = parts[0] if parts else (user.username or "")

        repos_url = f"{gh.base_url}/users/{owner}/repos?per_page=100&sort=updated"
        response = await asyncio.to_thread(
            lambda: __import__('requests').get(repos_url, headers=gh.headers, timeout=15)
        )
        if response.status_code != 200:
            print(f"GitHub API returned status {response.status_code}")
            return []

        raw_repos = response.json()
        repos = []
        for r in raw_repos:
            repo_name = r.get("name", "")
            readme = ""
            try:
                readme_url = f"{gh.base_url}/repos/{owner}/{repo_name}/readme"
                readme_resp = await asyncio.to_thread(
                    lambda url=readme_url: __import__('requests').get(url, headers={**gh.headers, 'Accept': 'application/vnd.github.v3.raw'}, timeout=10)
                )
                if readme_resp.status_code == 200:
                    readme = readme_resp.text[:3000] if readme_resp.text else ""
            except Exception:
                pass

            repos.append({
                "name": repo_name,
                "description": r.get("description", "") or "",
                "language": r.get("language", ""),
                "stars": r.get("stargazers_count", 0),
                "tech_stack": [r.get("language", "")] if r.get("language") else [],
                "skills": [],
                "frameworks": [],
                "domain": "",
                "category": "Other",
                "url": r.get("html_url", ""),
                "updated_at": r.get("updated_at", ""),
                "readme": readme,
            })
        return repos
    except Exception as e:
        print(f"GitHub API fetch failed: {e}")
        return []


@router.post("/analyze")
async def analyze_repo(
    request: RepoRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    target_url = request.url or (user.github_url if user else None)
    if not target_url:
        raise HTTPException(status_code=400, detail="No GitHub URL provided")

    job_id = f"{current_user_id}_{int(datetime.now().timestamp() * 1000)}"
    analysis_jobs[job_id] = {
        "status": "processing",
        "progress": "Starting analysis...",
        "result": None,
        "error": None,
    }

    try:
        from services.github_service import GitHubService
        from services.rag_service import RAGService

        user_token = user.github_token if user else None
        username = user.username if user else "unknown"

        async def run_job():
            try:
                gh = GitHubService(user_token)
                result = await gh.analyze_repository(target_url)
                analysis_jobs[job_id].update(
                    status="completed", progress="Done!", result=result
                )
                try:
                    rag = RAGService()
                    rag.add_repo_data(result, username)
                except Exception as rag_err:
                    print(f"RAG indexing failed: {rag_err}")
            except Exception as e:
                analysis_jobs[job_id].update(status="failed", error=str(e))

        asyncio.create_task(run_job())
    except Exception as e:
        analysis_jobs[job_id].update(status="failed", error=str(e))

    return {"job_id": job_id, "status": "started"}


@router.post("/analyze-all")
async def analyze_all_repos(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    if not user or not user.github_url:
        raise HTTPException(status_code=400, detail="No GitHub URL configured")

    job_id = f"{current_user_id}_all_{int(datetime.now().timestamp() * 1000)}"
    analysis_jobs[job_id] = {
        "status": "processing",
        "progress": "Fetching repositories...",
        "result": None,
        "error": None,
    }

    try:
        from services.github_service import GitHubService
        from services.rag_service import RAGService

        user_token = user.github_token if user else None
        username = user.username if user else "unknown"

        async def run_bulk_job():
            try:
                gh = GitHubService(user_token)
                parsed = urlparse(user.github_url)
                parts = parsed.path.strip('/').split('/')
                owner = parts[0] if parts else username

                repos_url = f"{gh.base_url}/users/{owner}/repos?per_page=100&sort=updated"
                response = await asyncio.to_thread(
                    lambda: __import__('requests').get(repos_url, headers=gh.headers, timeout=15)
                )
                if response.status_code != 200:
                    analysis_jobs[job_id].update(status="failed", error=f"GitHub API error: {response.status_code}")
                    return

                repos = response.json()
                results = []
                rag = RAGService()

                for i, repo in enumerate(repos):
                    analysis_jobs[job_id]["progress"] = f"Analyzing {i+1}/{len(repos)}: {repo.get('name', '')}"
                    try:
                        repo_url = repo.get("html_url", "")
                        if repo_url:
                            result = await gh.analyze_repository(repo_url)
                            result["stars"] = repo.get("stargazers_count", 0)
                            results.append(result)
                            try:
                                rag.add_repo_data(result, username)
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"Failed to analyze {repo.get('name')}: {e}")

                analysis_jobs[job_id].update(
                    status="completed", progress="Done!", result=results
                )
            except Exception as e:
                analysis_jobs[job_id].update(status="failed", error=str(e))

        asyncio.create_task(run_bulk_job())
    except Exception as e:
        analysis_jobs[job_id].update(status="failed", error=str(e))

    return {"job_id": job_id, "status": "started"}


@router.get("/github-repos")
async def fetch_github_repos(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    if not user or not user.github_url:
        return []

    try:
        from services.github_service import GitHubService
        gh = GitHubService(user.github_token)
        parsed = urlparse(user.github_url)
        parts = parsed.path.strip('/').split('/')
        owner = parts[0] if parts else (user.username or "")

        repos_url = f"{gh.base_url}/users/{owner}/repos?per_page=100&sort=updated"
        response = await asyncio.to_thread(
            lambda: __import__('requests').get(repos_url, headers=gh.headers, timeout=15)
        )
        if response.status_code != 200:
            return []

        repos = response.json()
        return [
            {
                "name": r.get("name", ""),
                "description": r.get("description", ""),
                "language": r.get("language", ""),
                "stars": r.get("stargazers_count", 0),
                "url": r.get("html_url", ""),
                "updated_at": r.get("updated_at", ""),
            }
            for r in repos
        ]
    except Exception as e:
        print(f"Error fetching GitHub repos: {e}")
        return []


@router.get("/analysis-status/{job_id}")
async def get_analysis_status(
    job_id: str,
    current_user_id: uuid.UUID = Depends(get_current_user),
):
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return analysis_jobs[job_id]


@router.post("/ask")
async def ask_agent(
    request: AskRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"
    try:
        from services.agent_service import AgentService
        agent = AgentService()
        response = await asyncio.to_thread(agent.ask, request.query, username=username)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask/stream")
async def ask_agent_stream(
    request: AskRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"
    try:
        from services.agent_service import AgentService
        agent = AgentService()

        def generate():
            for token in agent.ask_stream(request.query, username=username):
                yield f"data: {json.dumps({'token': token})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-resume")
async def generate_resume_file(
    request: ResumeRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"
    try:
        from services.agent_service import AgentService
        agent = AgentService()
        latex_content = await asyncio.to_thread(
            agent.generate_resume, request.query, username, "mistral:latest"
        )
        if latex_content.startswith("Error"):
            raise HTTPException(status_code=500, detail=latex_content)

        resumes_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "data",
            "resumes",
        )
        os.makedirs(resumes_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{username}_{timestamp}.tex"
        filepath = os.path.join(resumes_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)

        return {
            "success": True,
            "filename": filename,
            "message": "Resume generated successfully!",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resumes")
async def list_resumes_v1(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directories = [
        os.path.join(base_dir, "tmp"),
        os.path.join(base_dir, "data", "resumes"),
    ]

    user_files = []
    for directory in directories:
        if not os.path.exists(directory):
            continue
        for filename in os.listdir(directory):
            if filename.startswith(f"resume_{username}_") and filename.endswith(".tex"):
                filepath = os.path.join(directory, filename)
                stats = os.stat(filepath)
                parts = filename[:-4].split("_", 3)
                query = parts[3].replace("_", " ") if len(parts) > 3 else "Resume"
                user_files.append(
                    {
                        "filename": filename,
                        "query": query,
                        "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        "size": stats.st_size,
                    }
                )

    user_files.sort(key=lambda x: x["created_at"], reverse=True)
    return user_files


@router.get("/download-resume/{filename}")
async def download_resume_v1(
    filename: str,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"

    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.startswith(f"resume_{username}_"):
        raise HTTPException(status_code=403, detail="Access denied")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directories = [
        os.path.join(base_dir, "tmp"),
        os.path.join(base_dir, "data", "resumes"),
    ]

    for directory in directories:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            return FileResponse(
                path=filepath,
                filename=filename,
                media_type="application/x-tex",
            )

    raise HTTPException(status_code=404, detail="File not found")


@router.delete("/delete-resume/{filename}")
async def delete_resume_v1(
    filename: str,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"

    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not filename.startswith(f"resume_{username}_"):
        raise HTTPException(status_code=403, detail="Access denied")

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    directories = [
        os.path.join(base_dir, "tmp"),
        os.path.join(base_dir, "data", "resumes"),
    ]

    for directory in directories:
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"success": True, "message": "Resume deleted"}

    raise HTTPException(status_code=404, detail="File not found")
