import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
import os
import json
from services.project_classifier import classify_project, detect_difficulty, extract_tags, compute_scores


class RAGService:
    def __init__(self, persist_directory="./chroma_db"):
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

        self.collection = self.client.get_or_create_collection(
            name="github_repos",
            embedding_function=self.embedding_fn
        )

    def add_repo_data(self, repo_data: dict, username: str):
        repo_name = repo_data.get("name", "unknown")
        description = repo_data.get("description", "")
        tech_stack = repo_data.get("tech_stack", [])
        if isinstance(tech_stack, list):
            tech_stack_str = ", ".join(tech_stack)
        else:
            tech_stack_str = tech_stack
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]

        features = repo_data.get("features", [])
        if isinstance(features, list):
            features = "; ".join(features)

        readme = repo_data.get("readme_content", "")
        stars = repo_data.get("stars", 0)

        classification = classify_project(repo_name, description, tech_stack, readme)
        difficulty = detect_difficulty(repo_name, description, tech_stack, readme)
        tags = extract_tags(repo_name, description, tech_stack)
        scores = compute_scores(repo_name, description, tech_stack, readme, stars)

        text_content = f"Project: {repo_name}\nDescription: {description}\nTech Stack: {tech_stack_str}\nFeatures: {features}"
        if readme:
            text_content += f"\nREADME: {readme[:3000]}"

        documents = [text_content]
        metadatas = [{
            "name": repo_name,
            "type": "repo_summary",
            "username": username,
            "category": classification["category"],
            "subcategories": json.dumps(classification.get("subcategories", [])),
            "difficulty": difficulty,
            "tags": json.dumps(tags[:15]),
            "relevance_score": scores["relevance_score"],
            "popularity_score": scores["popularity_score"],
            "complexity_score": scores["complexity_score"],
            "final_score": scores["final_score"],
            "readme": readme[:3000] if readme else "",
            "description": description,
        }]
        ids = [f"{username}_{repo_name}_summary"]

        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Indexed {repo_name} for user {username} [category={classification['category']}, difficulty={difficulty}, score={scores['final_score']}]")

    def query(self, query_text: str, username: str, n_results: int = 3):
        if self.collection.count() == 0:
            return {"documents": [[]], "metadatas": [[]]}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"username": username}
        )
        return results

    def get_user_repos(self, username: str):
        if self.collection.count() == 0:
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
                skills = []
                frameworks = []
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
                    "domain": metadata.get("category", ""),
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
                }

                repos.append(repo_info)

        return repos

    def get_user_repos_by_category(self, username: str, category: str):
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
