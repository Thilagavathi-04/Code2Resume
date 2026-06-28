from rank_bm25 import BM25Okapi
import json
import re
from typing import Optional


class HybridRetriever:
    def __init__(self, rag_service, settings):
        self.rag = rag_service
        self.settings = settings
        self.bm25_indices: dict[str, BM25Okapi] = {}
        self.bm25_docs: dict[str, list[dict]] = {}
        self.bm25_ids: dict[str, list[str]] = {}

    def build_bm25_index(self, username: str):
        repos = self.rag.get_user_repos(username)
        if not repos:
            return

        tokenized_corpus = []
        docs = []
        ids = []
        for repo in repos:
            text = self._repo_to_text(repo)
            tokens = self._tokenize(text)
            tokenized_corpus.append(tokens)
            docs.append(repo)
            ids.append(repo.get("name", ""))

        self.bm25_indices[username] = BM25Okapi(tokenized_corpus)
        self.bm25_docs[username] = docs
        self.bm25_ids[username] = ids

    def _repo_to_text(self, repo: dict) -> str:
        parts = [
            repo.get("name", ""),
            repo.get("description", ""),
            " ".join(repo.get("tech_stack", [])) if isinstance(repo.get("tech_stack"), list) else "",
            repo.get("resume_description", ""),
            " ".join(repo.get("ats_keywords", [])) if isinstance(repo.get("ats_keywords"), list) else "",
            " ".join(repo.get("tags", [])) if isinstance(repo.get("tags"), list) else "",
            repo.get("domain", ""),
            repo.get("category", ""),
        ]
        return " ".join(p for p in parts if p)

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        return [t for t in text.split() if len(t) > 1]

    def bm25_search(self, username: str, query: str, top_n: int = 20) -> list[dict]:
        self.build_bm25_index(username)
        if username not in self.bm25_indices:
            return []

        idx = self.bm25_indices[username]
        tokens = self._tokenize(query)
        scores = idx.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_n]

        results = []
        for i, score in ranked:
            repo = self.bm25_docs[username][i].copy()
            repo["bm25_score"] = float(score)
            results.append(repo)
        return results

    def semantic_search(self, username: str, query: str, top_n: int = 20) -> list[dict]:
        self.rag._ensure_init()
        if self.rag.collection.count() == 0:
            return []

        results = self.rag.collection.query(
            query_texts=[query],
            n_results=top_n,
            where={"username": username}
        )

        repos = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                repo = self._meta_to_repo(meta, doc)
                repo["embedding_score"] = max(0.0, 1.0 - dist)
                repos.append(repo)
        return repos

    def _meta_to_repo(self, meta: dict, doc: str) -> dict:
        techs = []
        for line in doc.split("\n"):
            if line.startswith("Tech Stack:"):
                techs = [t.strip() for t in line.replace("Tech Stack:", "").strip().split(",") if t.strip()]

        ats_raw = meta.get("ats_keywords", "[]")
        tags_raw = meta.get("tags", "[]")
        subcats_raw = meta.get("subcategories", "[]")
        ai_caps_raw = meta.get("ai_capabilities", "[]")

        return {
            "name": meta.get("name", "unknown"),
            "description": meta.get("description", ""),
            "tech_stack": techs,
            "category": meta.get("category", "Other"),
            "subcategories": json.loads(subcats_raw) if isinstance(subcats_raw, str) else [],
            "difficulty": meta.get("difficulty", "intermediate"),
            "final_score": meta.get("final_score", 0),
            "resume_strength": meta.get("resume_strength", 0),
            "portfolio_strength": meta.get("portfolio_strength", 0),
            "is_ai_project": meta.get("is_ai_project", "False") == "True",
            "ai_capabilities": json.loads(ai_caps_raw) if isinstance(ai_caps_raw, str) else [],
            "readme": meta.get("readme", ""),
            "resume_description": meta.get("resume_description", ""),
            "ats_keywords": json.loads(ats_raw) if isinstance(ats_raw, str) else [],
            "tags": json.loads(tags_raw) if isinstance(tags_raw, str) else [],
            "domain": meta.get("domain", ""),
            "deployment_readiness": meta.get("deployment_readiness", "none"),
            "has_testing": meta.get("has_testing", "False") == "True",
            "architecture_type": meta.get("architecture_type", ""),
            "architecture_pattern": meta.get("architecture_pattern", ""),
        }

    def hybrid_search(self, username: str, query: str,
                      top_n: int = 20,
                      filters: Optional[dict] = None) -> list[dict]:
        bm25_results = self.bm25_search(username, query, top_n)
        semantic_results = self.semantic_search(username, query, top_n)

        merged = {}
        for r in bm25_results:
            name = r["name"]
            merged[name] = r

        for r in semantic_results:
            name = r["name"]
            if name in merged:
                merged[name]["embedding_score"] = r.get("embedding_score", 0)
            else:
                merged[name] = r

        w_bm25 = self.settings.RETRIEVAL_BM25_WEIGHT
        w_emb = self.settings.RETRIEVAL_EMBEDDING_WEIGHT
        w_qual = self.settings.RETRIEVAL_QUALITY_WEIGHT

        max_bm25 = max((r.get("bm25_score", 0) for r in merged.values()), default=1.0)
        if max_bm25 <= 0:
            max_bm25 = 1.0

        for name, repo in merged.items():
            bm25_raw = repo.get("bm25_score", 0)
            emb_raw = repo.get("embedding_score", 0)
            qual = (repo.get("resume_strength", 0) + repo.get("portfolio_strength", 0)) / 20.0

            bm25_norm = min(bm25_raw / max_bm25, 1.0) if bm25_raw > 0 else 0

            repo["composite_score"] = (
                w_bm25 * bm25_norm +
                w_emb * emb_raw +
                w_qual * qual
            )

        results = list(merged.values())
        if filters:
            results = [r for r in results if self._matches_filters(r, filters)]

        results.sort(key=lambda r: r["composite_score"], reverse=True)
        return results[:top_n]

    def _matches_filters(self, repo: dict, filters: dict) -> bool:
        if "category" in filters and repo.get("category") != filters["category"]:
            return False
        if "is_ai_project" in filters and repo.get("is_ai_project") != filters["is_ai_project"]:
            return False
        if "has_testing" in filters and repo.get("has_testing") != filters["has_testing"]:
            return False
        if "tech" in filters:
            tech_filter = filters["tech"].lower()
            if not any(tech_filter in t.lower() for t in repo.get("tech_stack", [])):
                return False
        if "difficulty" in filters and repo.get("difficulty") != filters["difficulty"]:
            return False
        return True
