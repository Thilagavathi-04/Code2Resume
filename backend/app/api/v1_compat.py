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
        print(f"[REPOS] No user or github_url for {current_user_id}")
        return []

    try:
        from services.rag_service import RAGService
        rag_service = RAGService()
        repos = rag_service.get_user_repos(user.username)
        if repos:
            print(f"[REPOS] Returning {len(repos)} repos from RAG for {user.username}")
            return repos
        print(f"[REPOS] RAG empty for {user.username}, falling back to GitHub API")
    except Exception as e:
        print(f"[REPOS] RAG fetch failed for {user.username}: {e}, falling back to GitHub API")

    try:
        from services.github_service import GitHubService
        gh = GitHubService(user.github_token)
        parsed = urlparse(user.github_url)
        parts = parsed.path.strip('/').split('/')
        owner = parts[0] if parts else (user.username or "")

        repos_url = f"{gh.base_url}/user/repos?per_page=100&sort=updated&affiliation=owner"
        print(f"[REPOS] Fetching from GitHub API (private repos included): {repos_url}")
        response = await asyncio.to_thread(
            lambda: __import__('requests').get(repos_url, headers=gh.headers, timeout=15)
        )
        if response.status_code != 200:
            print(f"[REPOS] GitHub API returned status {response.status_code}")
            return []

        raw_repos = response.json()
        repos = []
        for r in raw_repos:
            repos.append({
                "name": r.get("name", ""),
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
                "readme": "",
            })
        print(f"[REPOS] Returning {len(repos)} repos from GitHub API for {owner}")
        return repos
    except Exception as e:
        print(f"[REPOS] GitHub API fetch failed: {e}")
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
                print(f"\n[ANALYZE] Starting single repo analysis for {target_url}")
                t0 = datetime.now()
                result = await gh.analyze_repository(target_url)
                elapsed = (datetime.now() - t0).total_seconds()
                print(f"[ANALYZE] Completed {result.get('name', '?')} in {round(elapsed, 1)}s: arch={result.get('architecture', {}).get('type', '?')}, class={result.get('classification', {}).get('primary', '?')}")
                analysis_jobs[job_id].update(
                    status="completed", progress="Done!", result=result
                )
                try:
                    from services.knowledge_graph import KnowledgeGraph
                    kg = KnowledgeGraph()
                    kg.add_repo(username, result)
                    print(f"[ANALYZE] Knowledge graph updated: {result.get('name', '?')}")
                except Exception as kg_err:
                    print(f"[ANALYZE] Knowledge graph failed: {kg_err}")
                try:
                    rag = RAGService()
                    rag.add_repo_data(result, username)
                    print(f"[ANALYZE] RAG indexed: {result.get('name', '?')}")
                except Exception as rag_err:
                    print(f"[ANALYZE] RAG indexing failed: {rag_err}")
            except Exception as e:
                print(f"[ANALYZE] FAILED: {e}")
                import traceback
                traceback.print_exc()
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
            t_job_start = datetime.now()
            try:
                gh = GitHubService(user_token)
                parsed = urlparse(user.github_url)
                parts = parsed.path.strip('/').split('/')
                owner = parts[0] if parts else username

                print(f"\n{'='*60}")
                print(f"[SYNC] Starting bulk analysis for user={username}, owner={owner}")
                print(f"[SYNC] GitHub token: {'provided' if user_token else 'NOT provided (unauthenticated)'}")

                repos_url = f"{gh.base_url}/user/repos?per_page=100&sort=updated&affiliation=owner"
                print(f"[SYNC] Fetching repos (private repos included): {repos_url}")
                response = await asyncio.to_thread(
                    lambda: __import__('requests').get(repos_url, headers=gh.headers, timeout=15)
                )
                if response.status_code != 200:
                    error_msg = f"GitHub API error: status {response.status_code}"
                    print(f"[SYNC] FAILED to list repos: {error_msg}")
                    analysis_jobs[job_id].update(status="failed", error=error_msg)
                    return

                repos = response.json()
                print(f"[SYNC] Found {len(repos)} repositories for {owner}")
                results = []
                rag = RAGService()

                succeeded = 0
                failed = 0
                for i, repo in enumerate(repos):
                    repo_name = repo.get('name', 'unknown')
                    repo_url = repo.get("html_url", "")
                    analysis_jobs[job_id]["progress"] = f"Analyzing {i+1}/{len(repos)}: {repo_name}"
                    print(f"[SYNC] [{i+1}/{len(repos)}] Analyzing {repo_name}...")

                    if not repo_url:
                        print(f"[SYNC] [{i+1}/{len(repos)}] SKIP {repo_name}: no html_url")
                        failed += 1
                        continue

                    try:
                        t_repo = datetime.now()
                        result = await gh.analyze_repository(repo_url, skip_semantic=True)
                        result["stars"] = repo.get("stargazers_count", 0)
                        elapsed = (datetime.now() - t_repo).total_seconds()

                        tech_count = len(result.get("tech_stack_flat", []))
                        arch_type = result.get("architecture", {}).get("type", "?")
                        classification = result.get("classification", {}).get("primary", "?")
                        has_semantic = bool(result.get("semantic_analysis"))

                        print(f"[SYNC] [{i+1}/{len(repos)}] OK {repo_name} ({round(elapsed, 1)}s): arch={arch_type}, class={classification}, techs={tech_count}, semantic={'yes' if has_semantic else 'no'}")

                        results.append(result)

                        try:
                            from services.knowledge_graph import KnowledgeGraph
                            kg = KnowledgeGraph()
                            kg.add_repo(username, result)
                            print(f"[SYNC] [{i+1}/{len(repos)}] Knowledge graph updated: {repo_name}")
                        except Exception as kg_err:
                            print(f"[SYNC] [{i+1}/{len(repos)}] Knowledge graph FAILED for {repo_name}: {kg_err}")
                        try:
                            rag.add_repo_data(result, username)
                            print(f"[SYNC] [{i+1}/{len(repos)}] RAG indexed: {repo_name}")
                        except Exception as rag_err:
                            print(f"[SYNC] [{i+1}/{len(repos)}] RAG FAILED for {repo_name}: {rag_err}")

                        succeeded += 1
                    except Exception as e:
                        elapsed = (datetime.now() - t_repo).total_seconds()
                        print(f"[SYNC] [{i+1}/{len(repos)}] FAILED {repo_name} ({round(elapsed, 1)}s): {e}")
                        failed += 1

                total_elapsed = (datetime.now() - t_job_start).total_seconds()
                print(f"[SYNC] Bulk analysis complete: {succeeded} succeeded, {failed} failed, {len(results)} results, {round(total_elapsed, 1)}s total")
                print(f"{'='*60}\n")

                analysis_jobs[job_id].update(
                    status="completed", progress="Done!", result=results
                )
            except Exception as e:
                total_elapsed = (datetime.now() - t_job_start).total_seconds()
                print(f"[SYNC] FATAL error after {round(total_elapsed, 1)}s: {e}")
                import traceback
                traceback.print_exc()
                analysis_jobs[job_id].update(status="failed", error=str(e))

        asyncio.create_task(run_bulk_job())
    except Exception as e:
        print(f"[SYNC] Failed to start bulk job: {e}")
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
    user_profile = {
        "email": user.email if user else "",
        "github": user.github_url if user else "",
        "linkedin": user.linkedin_id if user else "",
        "leetcode": user.leetcode_id if user else "",
        "phone": user.mobile_number if user else "",
        "education_institution": user.education_institution if user else "",
        "education_degree": user.education_degree if user else "",
        "education_field": user.education_field if user else "",
        "education_start_date": user.education_start_date if user else "",
        "education_end_date": user.education_end_date if user else "",
        "education_gpa": user.education_gpa if user else "",
    }
    try:
        from services.agent_service import AgentService
        agent = AgentService()
        response = await asyncio.to_thread(agent.ask, request.query, username=username, user_profile=user_profile)
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
    user_profile = {
        "email": user.email if user else "",
        "github": user.github_url if user else "",
        "linkedin": user.linkedin_id if user else "",
        "leetcode": user.leetcode_id if user else "",
        "phone": user.mobile_number if user else "",
        "education_institution": user.education_institution if user else "",
        "education_degree": user.education_degree if user else "",
        "education_field": user.education_field if user else "",
        "education_start_date": user.education_start_date if user else "",
        "education_end_date": user.education_end_date if user else "",
        "education_gpa": user.education_gpa if user else "",
    }
    try:
        from services.agent_service import AgentService
        agent = AgentService()

        def generate():
            for token in agent.ask_stream(request.query, username=username, user_profile=user_profile):
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
    user_profile = {
        "email": user.email if user else "",
        "github": user.github_url if user else "",
        "linkedin": user.linkedin_id if user else "",
        "leetcode": user.leetcode_id if user else "",
        "phone": user.mobile_number if user else "",
        "education_institution": user.education_institution if user else "",
        "education_degree": user.education_degree if user else "",
        "education_field": user.education_field if user else "",
        "education_start_date": user.education_start_date if user else "",
        "education_end_date": user.education_end_date if user else "",
        "education_gpa": user.education_gpa if user else "",
    }
    try:
        from services.agent_service import AgentService
        agent = AgentService()
        result = await asyncio.to_thread(
            agent.generate_resume, request.query, username, settings.DEFAULT_MODEL, user_profile
        )

        if isinstance(result, str):
            if result.startswith("Error"):
                detail = result
                if "connect" in result.lower() or "refused" in result.lower():
                    detail = "Ollama server is not running. Start it with: ollama serve"
                raise HTTPException(status_code=500, detail=detail)
            raise HTTPException(status_code=500, detail="Unexpected response format from resume engine")

        latex_content = result["latex"]
        resume_data = result["resume_data"]
        template_used = result.get("template", "modern")
        section_order = result.get("section_order", [])
        validation = result.get("validation", {})

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
            "resume_data": resume_data,
            "latex": latex_content,
            "template_used": template_used,
            "section_order": section_order,
            "validation": validation,
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {e}")


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


@router.post("/rebuild-knowledge-graph")
async def rebuild_knowledge_graph(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user_by_id(db, current_user_id)
    username = user.username if user else "unknown"

    try:
        from services.rag_service import RAGService
        from services.knowledge_graph import KnowledgeGraph

        rag = RAGService()
        repos = rag.get_user_repos(username)
        if not repos:
            raise HTTPException(status_code=400, detail="No indexed repos found. Analyze repos first.")

        print(f"\n[KG-REBUILD] Rebuilding knowledge graph for {username} from {len(repos)} repos")
        kg = KnowledgeGraph()
        count = 0
        for repo in repos:
            repo_url = repo.get("url") or repo.get("html_url") or ""
            repo_name = repo.get("name", "")
            if not repo_name:
                continue

            repo_data = {
                "name": repo_name,
                "description": repo.get("description", ""),
                "tech_stack": repo.get("tech_stack", {}),
                "classification": {"primary": repo.get("category", repo.get("domain", "Other"))},
                "architecture": {"type": repo.get("architecture_type", ""), "pattern": repo.get("architecture_pattern", "")},
                "deployment": {"detected_technologies": [repo.get("deployment_readiness", "")] if repo.get("deployment_readiness") and repo.get("deployment_readiness") != "none" else []},
                "ai_ml": {"is_ai_project": repo.get("is_ai_project", False), "capabilities": repo.get("ai_capabilities", [])},
                "quality_metrics": {"resume_strength_score": repo.get("resume_strength", 0), "portfolio_strength_score": repo.get("portfolio_strength", 0)},
            }
            print(f"[KG-REBUILD]   [{count+1}] {repo_name}: cat={repo_data['classification']['primary']}, techs={list(repo_data['tech_stack'].keys()) if isinstance(repo_data['tech_stack'], dict) else repo_data['tech_stack']}")
            kg.add_repo(username, repo_data)
            count += 1

        stats = kg.get_graph_stats(username)
        print(f"[KG-REBUILD] Done: {count} repos, nodes={stats['total_nodes']}, edges={stats['total_edges']}")
        print(f"[KG-REBUILD] Node types: {stats['node_types']}")
        print(f"[KG-REBUILD] Edge types: {stats['edge_types']}")
        return {
            "success": True,
            "message": f"Knowledge graph rebuilt from {count} repos",
            "stats": stats,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rebuild knowledge graph: {str(e)}")


class ResumeExportRequest(BaseModel):
    resume_data: dict
    format: str = "pdf"


@router.post("/export-resume")
async def export_resume(
    request: ResumeExportRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
):
    import fitz

    resume = request.resume_data
    personal = resume.get("personal", {})
    summary = resume.get("summary", "")
    skills = resume.get("skills", [])
    experience = resume.get("experience", [])
    education = resume.get("education", [])
    projects = resume.get("projects", [])
    certifications = resume.get("certifications", [])

    doc = fitz.open()
    page_holder = [doc.new_page(width=595, height=842)]
    margin_left = 50
    margin_right = 50
    margin_top = 40
    y_holder = [margin_top]
    page_width = 595 - margin_left - margin_right
    blue = (0.2, 0.45, 0.91)

    def new_page():
        page_holder[0] = doc.new_page(width=595, height=842)
        y_holder[0] = margin_top

    def draw_text(text, x=None, fontname="helv", fontsize=10, color=(0, 0, 0)):
        if x is None:
            x = margin_left
        if not text:
            return
        text = str(text)
        for line_text in text.split("\n"):
            line_text = line_text.strip()
            if not line_text:
                y_holder[0] += fontsize + 2
                continue
            if y_holder[0] > 800:
                new_page()
            tw = fitz.get_text_length(line_text, fontname=fontname, fontsize=fontsize)
            if tw > page_width:
                words = line_text.split()
                cur = ""
                for w in words:
                    test = f"{cur} {w}".strip()
                    if fitz.get_text_length(test, fontname=fontname, fontsize=fontsize) > page_width:
                        if cur:
                            page_holder[0].insert_text((margin_left, y_holder[0]), cur, fontname=fontname, fontsize=fontsize, color=color)
                            y_holder[0] += fontsize + 3
                        cur = w
                    else:
                        cur = test
                if cur:
                    page_holder[0].insert_text((margin_left, y_holder[0]), cur, fontname=fontname, fontsize=fontsize, color=color)
                    y_holder[0] += fontsize + 3
            else:
                page_holder[0].insert_text((x, y_holder[0]), line_text, fontname=fontname, fontsize=fontsize, color=color)
                y_holder[0] += fontsize + 3

    def draw_section_heading(text):
        y_holder[0] += 8
        if y_holder[0] > 800:
            new_page()
        page_holder[0].insert_text((margin_left, y_holder[0]), text.upper(), fontname="helv", fontsize=11, color=blue)
        y_holder[0] += 3
        page_holder[0].draw_line((margin_left, y_holder[0]), (595 - margin_right, y_holder[0]), color=blue, width=0.5)
        y_holder[0] += 8

    def draw_bullet(text, indent=10):
        if not text:
            return
        text = str(text)
        if y_holder[0] > 800:
            new_page()
        bullet_x = margin_left + indent
        page_holder[0].insert_text((bullet_x, y_holder[0]), "•", fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
        words = text.split()
        cur = ""
        line_x = bullet_x + 8
        for w in words:
            test = f"{cur} {w}".strip()
            if fitz.get_text_length(test, fontname="helv", fontsize=9) > page_width - indent - 8:
                if cur:
                    page_holder[0].insert_text((line_x, y_holder[0]), cur, fontname="helv", fontsize=9)
                    y_holder[0] += 12
                    if y_holder[0] > 800:
                        new_page()
                cur = w
            else:
                cur = test
        if cur:
            page_holder[0].insert_text((line_x, y_holder[0]), cur, fontname="helv", fontsize=9)
            y_holder[0] += 12

    name = personal.get("name", "")
    if name:
        page_holder[0].insert_text((margin_left, y_holder[0] + 16), name, fontname="helv", fontsize=18, color=blue)
        y_holder[0] += 30

    contact_parts = []
    for field in ["email", "phone", "location", "linkedin", "github", "website"]:
        val = personal.get(field, "")
        if val:
            contact_parts.append(str(val))
    if contact_parts:
        contact_line = " | ".join(contact_parts)
        page_holder[0].insert_text((margin_left, y_holder[0]), contact_line, fontname="helv", fontsize=8, color=(0.4, 0.4, 0.4))
        y_holder[0] += 14

    if summary:
        draw_section_heading("Summary")
        draw_text(summary)

    if skills:
        draw_section_heading("Technical Skills")
        categories = {}
        for s in skills:
            cat = s.get("category", "Other") if isinstance(s, dict) else "Other"
            name_val = s.get("name", s) if isinstance(s, dict) else s
            categories.setdefault(cat, []).append(name_val)
        for cat, items in categories.items():
            draw_text(f"{cat}: {', '.join(str(i) for i in items)}", fontsize=9)
            y_holder[0] += 2

    if experience:
        draw_section_heading("Experience")
        for exp in experience:
            pos = str(exp.get("position", ""))
            company = str(exp.get("company", ""))
            start = str(exp.get("startDate", exp.get("start_date", "")))
            end = str(exp.get("endDate", exp.get("end_date", "")))
            if y_holder[0] > 800:
                new_page()
            page_holder[0].insert_text((margin_left, y_holder[0]), pos, fontname="helv", fontsize=10)
            date_str = f"{start} – {end}"
            page_holder[0].insert_text((595 - margin_right - fitz.get_text_length(date_str, fontname="helv", fontsize=9), y_holder[0]),
                             date_str, fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
            y_holder[0] += 12
            page_holder[0].insert_text((margin_left, y_holder[0]), company, fontname="hebo", fontsize=9, color=(0.3, 0.3, 0.3))
            y_holder[0] += 12
            for h in (exp.get("highlights", [])):
                draw_bullet(h)
            y_holder[0] += 4

    if projects:
        draw_section_heading("Projects")
        for proj in projects:
            pname = str(proj.get("name", ""))
            techs = proj.get("technologies", [])
            if isinstance(techs, list):
                techs = ", ".join(str(t) for t in techs)
            if y_holder[0] > 800:
                new_page()
            page_holder[0].insert_text((margin_left, y_holder[0]), pname, fontname="helv", fontsize=10)
            if techs:
                page_holder[0].insert_text((595 - margin_right - fitz.get_text_length(str(techs), fontname="helv", fontsize=8), y_holder[0]),
                                 str(techs), fontname="helv", fontsize=8, color=(0.4, 0.4, 0.4))
            y_holder[0] += 12
            desc = proj.get("description", "")
            if desc:
                draw_text(desc, fontsize=9)
            for h in (proj.get("highlights", [])):
                draw_bullet(h)
            y_holder[0] += 4

    if education:
        draw_section_heading("Education")
        for edu in education:
            inst = str(edu.get("institution", ""))
            degree = str(edu.get("degree", ""))
            field = str(edu.get("field", edu.get("field_of_study", "")))
            start = str(edu.get("startDate", edu.get("start_date", "")))
            end = str(edu.get("endDate", edu.get("end_date", "")))
            gpa = str(edu.get("gpa", ""))
            if y_holder[0] > 800:
                new_page()
            page_holder[0].insert_text((margin_left, y_holder[0]), inst, fontname="helv", fontsize=10)
            date_str = f"{start} – {end}" if start or end else ""
            if date_str:
                page_holder[0].insert_text((595 - margin_right - fitz.get_text_length(date_str, fontname="helv", fontsize=9), y_holder[0]),
                                 date_str, fontname="helv", fontsize=9, color=(0.4, 0.4, 0.4))
            y_holder[0] += 12
            degree_line = degree + (f" in {field}" if field else "")
            if gpa:
                degree_line += f" | GPA: {gpa}"
            page_holder[0].insert_text((margin_left, y_holder[0]), degree_line, fontname="helv", fontsize=9, color=(0.3, 0.3, 0.3))
            y_holder[0] += 14

    if certifications:
        draw_section_heading("Certifications")
        for cert in certifications:
            cname = str(cert.get("name", ""))
            issuer = str(cert.get("issuer", ""))
            draw_bullet(f"{cname}" + (f" — {issuer}" if issuer else ""))

    pdf_bytes = doc.tobytes()
    doc.close()

    from fastapi.responses import Response
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"},
    )


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
