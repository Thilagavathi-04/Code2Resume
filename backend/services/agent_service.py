import re
from services.llm_service import get_llm
from .rag_service import RAGService

from app.core.config import settings

CATEGORY_MAP = {
    "ml": "Machine Learning", "machine learning": "Machine Learning", "ai": "Machine Learning",
    "deep learning": "Deep Learning", "nlp": "NLP", "llm": "NLP",
    "computer vision": "Computer Vision", "cv": "Computer Vision",
    "full stack": "Full Stack", "fullstack": "Full Stack",
    "frontend": "Frontend", "front-end": "Frontend",
    "backend": "Backend", "api": "Backend",
    "mobile": "Mobile App", "android": "Mobile App", "ios": "Mobile App",
    "data science": "Data Science", "data": "Data Science",
    "devops": "DevOps", "cloud": "Cloud Computing",
    "blockchain": "Blockchain", "web3": "Blockchain",
    "iot": "IoT", "security": "Cybersecurity",
}


class AgentService:
    def __init__(self):
        self.rag = RAGService()

    def _detect_project_filter(self, query: str):
        q = query.lower()
        for keyword, category in CATEGORY_MAP.items():
            if keyword in q:
                return category
        return None

    def _build_project_summary(self, repos: list) -> str:
        if not repos:
            return "No projects found."

        lines = []
        for r in repos:
            name = r.get("name", "Unknown")
            desc = r.get("description", "")
            techs = r.get("tech_stack", [])
            if isinstance(techs, str):
                techs = [t.strip() for t in techs.split(",") if t.strip()]
            category = r.get("category", r.get("domain", ""))
            difficulty = r.get("difficulty", "")
            score = r.get("final_score", 0)
            arch = r.get("architecture_type", "")
            is_ai = r.get("is_ai_project", False)
            ai_caps = r.get("ai_capabilities", [])
            deployment = r.get("deployment_readiness", "")
            has_testing = r.get("has_testing", False)

            tech_str = ", ".join(techs[:5]) if techs else "N/A"
            line = f"**{name}**"
            if category:
                line += f" [{category}]"
            if difficulty:
                line += f" ({difficulty})"
            line += f"\n  Tech: {tech_str}"
            if desc:
                line += f"\n  {desc[:120]}"
            if is_ai and ai_caps:
                line += f"\n  AI Capabilities: {', '.join(ai_caps[:3])}"
            if arch:
                line += f"\n  Architecture: {arch}"
            extras = []
            if has_testing:
                extras.append("Tested")
            if deployment and deployment != "none":
                extras.append(f"Deploy:{deployment}")
            if score:
                extras.append(f"Score:{score}")
            if extras:
                line += f"\n  [{' | '.join(extras)}]"
            lines.append(line)

        return "\n\n".join(lines)

    def _smart_query(self, query: str, username: str):
        category = self._detect_project_filter(query)

        if category:
            results = self.rag.get_user_repos_by_category(username, category)
            if results:
                return results, f"Filtered by category: {category}"

        results = self.rag.query(query, username=username, n_results=20)
        docs = results.get('documents', [[]])[0]
        metas = results.get('metadatas', [[]])[0]

        repos = []
        for doc, meta in zip(docs, metas):
            if not isinstance(meta, dict):
                continue
            techs = []
            for line in doc.split("\n"):
                if line.startswith("Tech Stack:"):
                    techs = [t.strip() for t in line.replace("Tech Stack:", "").strip().split(",") if t.strip()]
            repos.append({
                "name": meta.get("name", "unknown"),
                "description": meta.get("description", ""),
                "tech_stack": techs,
                "category": meta.get("category", ""),
                "difficulty": meta.get("difficulty", ""),
                "final_score": meta.get("final_score", 0),
                "architecture_type": meta.get("architecture_type", ""),
                "is_ai_project": meta.get("is_ai_project", "False") == "True",
                "ai_capabilities": json.loads(meta.get("ai_capabilities", "[]")),
                "deployment_readiness": meta.get("deployment_readiness", "none"),
                "has_testing": meta.get("has_testing", "False") == "True",
                "readme": meta.get("readme", ""),
            })

        return repos, "Semantic search"

    def ask(self, query: str, username: str, model: str = None, user_profile: dict = None):
        model = model or settings.DEFAULT_MODEL
        if "resume" in query.lower() or "cv" in query.lower():
            result = self.generate_resume(query, username, model, user_profile=user_profile)
            if isinstance(result, dict):
                return result.get("latex", str(result))
            return result

        repos, source = self._smart_query(query, username)
        context = self._build_project_summary(repos)

        max_context_chars = 8000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n... (truncated)"

        profile = user_profile or {}
        profile_info = ""
        if profile.get("email"):
            profile_info += f"Email: {profile['email']}\n"
        if profile.get("github"):
            profile_info += f"GitHub: {profile['github']}\n"
        if profile.get("phone"):
            profile_info += f"Phone: {profile['phone']}\n"

        is_project_query = any(w in query.lower() for w in [
            "project", "repo", "repository", "github", "tech stack",
            "what do i have", "my project", "list", "show", "best",
            "ml", "ai", "full stack", "frontend", "backend",
        ])

        prompt = f"""You are a helpful AI assistant with knowledge about the user's GitHub projects.

User: {username}
{profile_info}
Project Data ({source}, {len(repos)} projects):
{context}

User Request: {query}

Instructions:
- {"If the question is about projects, use the project data above." if is_project_query else "Answer using your knowledge. You can also reference the user's projects if relevant."}
- {"List projects with their name, tech stack, and a brief description." if is_project_query else ""}
- {"Group by category when possible. Include architecture, AI capabilities, and testing status." if is_project_query else ""}
- For general questions, answer directly using your knowledge.
- Format output clearly with Markdown.
- Be specific, helpful, and accurate."""

        print(f"Agent: {len(repos)} repos, source={source}, context={len(context)} chars")
        try:
            messages = [
                {'role': 'system', 'content': 'You are a helpful AI coding assistant with access to the user\'s GitHub project data. Answer questions about their projects using the provided data. Also answer general programming questions.'},
                {'role': 'user', 'content': prompt},
            ]
            return get_llm().generate_response(messages)
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def ask_stream(self, query: str, username: str, model: str = None, user_profile: dict = None):
        model = model or settings.DEFAULT_MODEL
        if "resume" in query.lower() or "cv" in query.lower():
            yield self.generate_resume(query, username, model, user_profile=user_profile)
            return

        repos, source = self._smart_query(query, username)
        context = self._build_project_summary(repos)

        max_context_chars = 8000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n... (truncated)"

        profile = user_profile or {}
        profile_info = ""
        if profile.get("email"):
            profile_info += f"Email: {profile['email']}\n"
        if profile.get("github"):
            profile_info += f"GitHub: {profile['github']}\n"
        if profile.get("phone"):
            profile_info += f"Phone: {profile['phone']}\n"

        is_project_query = any(w in query.lower() for w in [
            "project", "repo", "repository", "github", "tech stack",
            "what do i have", "my project", "list", "show", "best",
            "ml", "ai", "full stack", "frontend", "backend",
        ])

        prompt = f"""You are a helpful AI assistant with knowledge about the user's GitHub projects.

User: {username}
{profile_info}
Project Data ({source}, {len(repos)} projects):
{context}

User Request: {query}

Instructions:
- {"If the question is about projects, use the project data above." if is_project_query else "Answer using your knowledge. You can also reference the user's projects if relevant."}
- {"List projects with their name, tech stack, and a brief description." if is_project_query else ""}
- {"Group by category when possible. Include architecture, AI capabilities, and testing status." if is_project_query else ""}
- For general questions, answer directly using your knowledge.
- Format output clearly with Markdown.
- Be specific, helpful, and accurate."""

        print(f"Agent streaming: {len(repos)} repos, source={source}, context={len(context)} chars")
        try:
            messages = [
                {'role': 'system', 'content': 'You are a helpful AI coding assistant with access to the user\'s GitHub project data. Answer questions about their projects using the provided data. Also answer general programming questions.'},
                {'role': 'user', 'content': prompt},
            ]
            for chunk in get_llm().generate_response_stream(messages):
                yield chunk
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def generate_resume(self, query: str, username: str, model: str, user_profile=None):
        from services.resume_engine import ResumeEngine
        engine = ResumeEngine(self.rag)

        target_domain, target_role = engine._detect_domain(query)

        requested_projects = []
        match = re.search(r'(?:add|include|use|with)\s+(?:project\s+)?["\']?([^"\']+)["\']?', query, re.IGNORECASE)
        if match:
            requested_projects = [match.group(1).strip()]

        result = engine.generate_resume(query, username, model, user_profile=user_profile, requested_projects=requested_projects)
        return result
