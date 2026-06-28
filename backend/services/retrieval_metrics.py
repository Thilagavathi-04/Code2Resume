import time
import json
import os
import math


class RetrievalLogger:
    def __init__(self, log_dir: str = "data/retrieval_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log_retrieval(self, username: str, query: str, results: list[dict],
                      stage_timings: dict = None):
        entry = {
            "timestamp": time.time(),
            "username": username,
            "query": query,
            "result_count": len(results),
            "top_score": results[0].get("composite_score", 0) if results else 0,
            "avg_score": sum(r.get("composite_score", 0) for r in results) / max(len(results), 1),
            "rerank_scores": [r.get("rerank_score", 0) for r in results[:5]],
            "bm25_scores": [r.get("bm25_score", 0) for r in results[:5]],
            "embedding_scores": [r.get("embedding_score", 0) for r in results[:5]],
            "categories": list(set(r.get("category", "") for r in results)),
            "timings": stage_timings or {},
        }

        date_str = time.strftime("%Y-%m-%d")
        log_path = os.path.join(self.log_dir, f"{date_str}.jsonl")
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def compute_precision_at_k(self, retrieved: list[dict], relevant_names: set, k: int) -> float:
        top_k = [r["name"] for r in retrieved[:k]]
        hits = sum(1 for name in top_k if name in relevant_names)
        return hits / k if k > 0 else 0

    def compute_mrr(self, retrieved: list[dict], relevant_names: set) -> float:
        for i, r in enumerate(retrieved):
            if r["name"] in relevant_names:
                return 1.0 / (i + 1)
        return 0.0

    def compute_ndcg_at_k(self, retrieved: list[dict], relevance_scores: dict, k: int) -> float:
        dcg = 0.0
        for i, r in enumerate(retrieved[:k]):
            rel = relevance_scores.get(r["name"], 0)
            dcg += rel / math.log2(i + 2)
        ideal = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal))
        return dcg / idcg if idcg > 0 else 0.0

    def get_daily_summary(self, date_str: str) -> dict:
        log_path = os.path.join(self.log_dir, f"{date_str}.jsonl")
        if not os.path.exists(log_path):
            return {}
        entries = []
        with open(log_path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        if not entries:
            return {}
        return {
            "total_queries": len(entries),
            "avg_top_score": sum(e["top_score"] for e in entries) / len(entries),
            "avg_result_count": sum(e["result_count"] for e in entries) / len(entries),
            "queries": [e["query"] for e in entries[:10]],
        }
