from sentence_transformers import CrossEncoder

_reranker_cache: dict[str, CrossEncoder] = {}


class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self) -> CrossEncoder:
        if self._model is None:
            if self.model_name not in _reranker_cache:
                print(f"[Reranker] Loading cross-encoder model: {self.model_name}")
                _reranker_cache[self.model_name] = CrossEncoder(self.model_name)
                print(f"[Reranker] Model loaded successfully")
            self._model = _reranker_cache[self.model_name]
        return self._model

    def rerank(self, query: str, repos: list[dict], top_k: int = 5) -> list[dict]:
        if not repos:
            return []
        if len(repos) <= top_k:
            for repo in repos:
                repo["rerank_score"] = repo.get("composite_score", 0)
            return repos

        pairs = [(query, self._repo_to_text(r)) for r in repos]
        scores = self.model.predict(pairs)

        for repo, score in zip(repos, scores):
            repo["rerank_score"] = float(score)

        repos.sort(key=lambda r: r["rerank_score"], reverse=True)
        return repos[:top_k]

    def _repo_to_text(self, repo: dict) -> str:
        parts = [
            repo.get("name", ""),
            repo.get("description", ""),
            " ".join(repo.get("tech_stack", [])),
            repo.get("resume_description", ""),
            " ".join(repo.get("ats_keywords", [])),
            repo.get("domain", ""),
        ]
        return " ".join(p for p in parts if p)
