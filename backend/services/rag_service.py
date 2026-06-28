import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import os
import json
from services.project_classifier import classify_project, detect_difficulty, extract_tags, compute_scores


class RAGService:
    _initialized = False

    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        self.embedding_fn = None
        self.collection = None
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)

        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        self.collection = self.client.get_or_create_collection(
            name="github_repos",
            embedding_function=self.embedding_fn
        )
        RAGService._initialized = True
        self._initialized = True

    def add_repo_data(self, repo_data: dict, username: str):
        self._ensure_init()
        repo_name = repo_data.get("name", "unknown")
        description = repo_data.get("description", "")
        stars = repo_data.get("stars", 0)

        tech_stack = repo_data.get("tech_stack", {})
        if isinstance(tech_stack, dict):
            tech_stack_flat = repo_data.get("tech_stack_flat", [])
            if not tech_stack_flat:
                tech_stack_flat = []
                for cat in tech_stack.values():
                    if isinstance(cat, list):
                        tech_stack_flat.extend(cat)
            tech_stack_str = ", ".join(tech_stack_flat[:10])
        else:
            tech_stack_flat = tech_stack if isinstance(tech_stack, list) else [t.strip() for t in str(tech_stack).split(",") if t.strip()]
            tech_stack_str = ", ".join(tech_stack_flat)

        if not description and tech_stack_flat:
            top_techs = ", ".join(tech_stack_flat[:3])
            classification = repo_data.get("classification", {})
            cat = classification.get("primary", classification.get("category", "Software"))
            description = f"{cat} project built with {top_techs}"

        readme = repo_data.get("readme_content", "")
        semantic = repo_data.get("semantic_analysis", {})

        resume_desc = semantic.get("resume_description", "")
        if not resume_desc:
            top_techs = ", ".join(tech_stack_flat[:4]) if tech_stack_flat else "modern technologies"
            readme_preview = (readme or "")[:200].replace("\n", " ").strip()
            if description and readme_preview:
                resume_desc = f"{description}. {readme_preview[:150]}"
            elif description:
                resume_desc = f"{description}. Built with {top_techs} to deliver a robust solution."
            else:
                resume_desc = f"A software project built with {top_techs}."

        classification = repo_data.get("classification", {})
        if not classification or "category" not in classification:
            legacy_class = classify_project(repo_name, description, tech_stack_flat, readme)
            classification = {
                "category": legacy_class.get("category", "Other"),
                "subcategories": legacy_class.get("subcategories", []),
                "primary": legacy_class.get("category", "Other"),
                "secondary": legacy_class.get("subcategories", []),
                "confidence": legacy_class.get("confidence", 0),
            }
        category = classification.get("category", classification.get("primary", "Other"))
        subcategories = classification.get("subcategories", classification.get("secondary", []))

        difficulty = detect_difficulty(repo_name, description, tech_stack_flat, readme)
        tags = extract_tags(repo_name, description, tech_stack_flat)
        scores = compute_scores(repo_name, description, tech_stack_flat, readme, stars)

        architecture = repo_data.get("architecture", {})
        quality_metrics = repo_data.get("quality_metrics", {})
        aiml = repo_data.get("ai_ml", {})
        deployment = repo_data.get("deployment", {})
        databases = repo_data.get("databases", {})
        testing_info = repo_data.get("testing", {})

        text_content = f"Project: {repo_name}\nDescription: {description}\nTech Stack: {tech_stack_str}"
        if resume_desc:
            text_content += f"\nResume Description: {resume_desc}"
        bullet_points = semantic.get("resume_bullet_points", [])
        if bullet_points:
            text_content += f"\nBullet Points: {'; '.join(bullet_points[:3])}"
        if readme:
            readme_preview = readme[:500].replace("\n", " ").strip()
            if readme_preview:
                text_content += f"\nReadme: {readme_preview}"

        kg = repo_data.get("knowledge_graph", {})
        if kg:
            kg_parts = []
            for cat, items in kg.items():
                if items:
                    kg_parts.append(f"{cat}: {', '.join(items[:5])}")
            if kg_parts:
                text_content += f"\nKnowledge Graph: {' | '.join(kg_parts)}"

        documents = [text_content]
        metadatas = [{
            "name": repo_name,
            "type": "repo_summary",
            "username": username,
            "category": category,
            "subcategories": json.dumps(subcategories if isinstance(subcategories, list) else []),
            "difficulty": difficulty,
            "tags": json.dumps(tags[:15]),
            "relevance_score": scores["relevance_score"],
            "popularity_score": scores["popularity_score"],
            "complexity_score": scores["complexity_score"],
            "final_score": scores["final_score"],
            "readme": readme[:3000] if readme else "",
            "description": description,
            "architecture_type": architecture.get("type", ""),
            "architecture_pattern": architecture.get("pattern", ""),
            "resume_strength": quality_metrics.get("resume_strength_score", 0),
            "portfolio_strength": quality_metrics.get("portfolio_strength_score", 0),
            "is_ai_project": str(aiml.get("is_ai_project", False)),
            "ai_capabilities": json.dumps(aiml.get("capabilities", [])),
            "deployment_readiness": deployment.get("readiness_level", "none"),
            "has_testing": str(testing_info.get("has_testing", False)),
            "resume_description": semantic.get("resume_description", ""),
            "ats_keywords": json.dumps(semantic.get("ats_keywords", [])),
            "domain": semantic.get("domain", category),
        }]
        ids = [f"{username}_{repo_name}_summary"]

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[RAG] Indexed {repo_name} for user {username}: category={category}, difficulty={difficulty}, score={scores['final_score']}, arch={architecture.get('type', '?')}, doc_len={len(text_content)}")

    def query(self, query_text: str, username: str, n_results: int = 3,
              filters: dict = None, use_reranker: bool = True):
        import time
        from app.core.config import settings

        timings = {}
        t0 = time.time()

        self._ensure_init()
        if self.collection.count() == 0:
            return {"repos": [], "context": "No project data found.", "token_usage": {}, "count": 0}

        from services.hybrid_retriever import HybridRetriever
        retriever = HybridRetriever(self, settings)
        timings["bm25_index"] = time.time() - t0

        t1 = time.time()
        top_n = settings.RETRIEVAL_TOP_N
        candidates = retriever.hybrid_search(username, query_text, top_n=top_n, filters=filters)
        timings["hybrid_search"] = time.time() - t1

        t2 = time.time()
        threshold = settings.RETRIEVAL_SIMILARITY_THRESHOLD
        candidates = [r for r in candidates if r.get("composite_score", 0) >= threshold]
        timings["threshold_filter"] = time.time() - t2

        t3 = time.time()
        if use_reranker and len(candidates) > settings.RETRIEVAL_TOP_K:
            from services.reranker import Reranker
            reranker = Reranker(settings.RERANKER_MODEL)
            candidates = reranker.rerank(query_text, candidates, top_k=settings.RETRIEVAL_TOP_K)
        timings["reranking"] = time.time() - t3

        t4 = time.time()
        from services.context_compressor import ContextCompressor
        compressor = ContextCompressor(max_tokens=settings.MAX_CONTEXT_TOKENS)
        context = compressor.compress_repos(candidates)
        token_usage = compressor.get_token_usage(context)
        timings["compression"] = time.time() - t4

        timings["total"] = time.time() - t0

        try:
            from services.retrieval_metrics import RetrievalLogger
            logger = RetrievalLogger()
            logger.log_retrieval(username, query_text, candidates, timings)
        except Exception:
            pass

        print(f"[RAG] Hybrid retrieval for '{query_text}': {len(candidates)} repos, {token_usage.get('tokens', 0)} tokens, {timings['total']:.3f}s")

        return {
            "repos": candidates,
            "context": context,
            "token_usage": token_usage,
            "count": len(candidates),
        }

    def get_user_repos(self, username: str):
        self._ensure_init()
        if self.collection.count() == 0:
            print(f"[RAG] Collection empty, returning no repos for {username}")
            return []

        results = self.collection.get(
            where={"$and": [{"username": username}, {"type": "repo_summary"}]}
        )

        repos = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                doc = results['documents'][i] if results['documents'] else ""
                readme = metadata.get("readme", "")
                description = metadata.get("description", "")

                tech_stack = []
                for line in doc.split("\n"):
                    if line.startswith("Tech Stack:"):
                        tech_str = line.replace("Tech Stack:", "").strip()
                        tech_stack = [t.strip() for t in tech_str.split(",") if t.strip()]

                repo_info = {
                    "name": metadata.get("name", "unknown"),
                    "description": description,
                    "tech_stack": tech_stack,
                    "skills": [],
                    "frameworks": [],
                    "domain": metadata.get("domain", metadata.get("category", "")),
                    "category": metadata.get("category", "Other"),
                    "subcategories": json.loads(metadata.get("subcategories", "[]")),
                    "difficulty": metadata.get("difficulty", "intermediate"),
                    "tags": json.loads(metadata.get("tags", "[]")),
                    "relevance_score": metadata.get("relevance_score", 0),
                    "popularity_score": metadata.get("popularity_score", 0),
                    "complexity_score": metadata.get("complexity_score", 0),
                    "final_score": metadata.get("final_score", 0),
                    "what_it_does": description,
                    "readme": readme,
                    "architecture_type": metadata.get("architecture_type", ""),
                    "architecture_pattern": metadata.get("architecture_pattern", ""),
                    "resume_strength": metadata.get("resume_strength", 0),
                    "portfolio_strength": metadata.get("portfolio_strength", 0),
                    "is_ai_project": metadata.get("is_ai_project", "False") == "True",
                    "ai_capabilities": json.loads(metadata.get("ai_capabilities", "[]")),
                    "deployment_readiness": metadata.get("deployment_readiness", "none"),
                    "has_testing": metadata.get("has_testing", "False") == "True",
                    "resume_description": metadata.get("resume_description", ""),
                    "ats_keywords": json.loads(metadata.get("ats_keywords", "[]")),
                }

                repos.append(repo_info)

        print(f"[RAG] get_user_repos({username}): returning {len(repos)} repos")
        return repos

    def get_user_repos_by_category(self, username: str, category: str):
        self._ensure_init()
        if self.collection.count() == 0:
            return []

        results = self.collection.get(
            where={
                "$and": [
                    {"username": username},
                    {"type": "repo_summary"},
                    {"category": category},
                ]
            }
        )

        repos = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                doc = results['documents'][i] if results['documents'] else ""
                readme = metadata.get("readme", "")
                description = metadata.get("description", "")

                tech_stack = []
                for line in doc.split("\n"):
                    if line.startswith("Tech Stack:"):
                        tech_str = line.replace("Tech Stack:", "").strip()
                        tech_stack = [t.strip() for t in tech_str.split(",") if t.strip()]

                repo_info = {
                    "name": metadata.get("name", "unknown"),
                    "description": description,
                    "tech_stack": tech_stack,
                    "category": metadata.get("category", "Other"),
                    "difficulty": metadata.get("difficulty", "intermediate"),
                    "tags": json.loads(metadata.get("tags", "[]")),
                    "final_score": metadata.get("final_score", 0),
                    "what_it_does": description,
                    "readme": readme,
                }
                repos.append(repo_info)

        return repos
