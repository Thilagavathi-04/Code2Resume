import asyncio
from typing import Optional


class IndexingPipeline:
    def __init__(self):
        self._active_jobs: dict[str, dict] = {}

    async def index_repo(self, username: str, repo_url: str, user_token: str = None) -> dict:
        repo_name = repo_url.rstrip("/").split("/")[-1]
        job_id = f"{username}_{repo_name}"
        self._active_jobs[job_id] = {"status": "running", "progress": "Starting..."}

        try:
            from services.github_analysis import analyze_repository
            from services.rag_service import RAGService
            from services.knowledge_graph import KnowledgeGraph
            from services.project_summarizer import generate_project_summary

            self._active_jobs[job_id]["progress"] = "Analyzing repository..."
            result = await analyze_repository(repo_url, user_token=user_token, skip_semantic=False)

            self._active_jobs[job_id]["progress"] = "Building knowledge graph..."
            kg = KnowledgeGraph()
            kg.add_repo(username, result)

            self._active_jobs[job_id]["progress"] = "Generating summary..."
            summary = generate_project_summary(result)
            result["project_summary"] = summary

            self._active_jobs[job_id]["progress"] = "Indexing..."
            rag = RAGService()
            rag.add_repo_data(result, username)

            self._active_jobs[job_id].update(status="completed", result=result)
            return result

        except Exception as e:
            self._active_jobs[job_id].update(status="failed", error=str(e))
            raise

    async def index_all_repos(self, username: str, repos: list[dict], user_token: str = None):
        from services.rag_service import RAGService
        rag = RAGService()

        for repo in repos:
            repo_url = repo.get("html_url") or repo.get("url", "")
            if not repo_url:
                continue
            try:
                await self.index_repo(username, repo_url, user_token)
            except Exception as e:
                print(f"[IndexingPipeline] Failed {repo.get('name', '?')}: {e}")
                continue

    def get_job_status(self, job_id: str) -> dict:
        return self._active_jobs.get(job_id, {"status": "not_found"})

    def get_all_jobs(self, username: str) -> list[dict]:
        return [
            {"job_id": k, **v}
            for k, v in self._active_jobs.items()
            if k.startswith(f"{username}_")
        ]
