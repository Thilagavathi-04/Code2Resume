import ollama
import os
from .rag_service import RAGService


from app.core.config import settings


class AgentService:
    def __init__(self):
        self.rag = RAGService()

    def ask(self, query: str, username: str, model: str = None):
        model = model or settings.DEFAULT_MODEL
        if "resume" in query.lower() or "cv" in query.lower():
            result = self.generate_resume(query, username, model)
            if isinstance(result, dict):
                return result.get("latex", str(result))
            return result

        n_results = 50
        results = self.rag.query(query, username=username, n_results=n_results)
        documents = results.get('documents', [[]])[0]

        if not documents:
            return "No project information found. Try analyzing your GitHub repositories first."

        context = "\n---\n".join(documents)

        prompt = f"""You are an intelligent assistant helping a developer with their portfolio.
Use the following context about the user's projects to answer accurately.

Context from analyzed repositories:
{context}

User Request: {query}

Instructions:
- Use ONLY the provided context to answer.
- If listing projects, include ALL matching projects from the context.
- Group results by category when possible.
- Do NOT include projects that don't match the user's request.
- Format output clearly with Markdown.
- Be specific about technologies and project details."""

        print(f"Agent querying {model} with context length {len(context)}")
        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt},
            ], options={'num_gpu': 99})
            return response['message']['content']
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def ask_stream(self, query: str, username: str, model: str = None):
        model = model or settings.DEFAULT_MODEL
        if "resume" in query.lower() or "cv" in query.lower():
            yield self.generate_resume(query, username, model)
            return

        n_results = 50
        results = self.rag.query(query, username=username, n_results=n_results)
        documents = results.get('documents', [[]])[0]

        if not documents:
            yield "No project information found. Try analyzing your GitHub repositories first."
            return

        context = "\n---\n".join(documents)

        prompt = f"""You are an intelligent assistant helping a developer with their portfolio.
Use the following context about the user's projects to answer accurately.

Context from analyzed repositories:
{context}

User Request: {query}

Instructions:
- Use ONLY the provided context to answer.
- If listing projects, include ALL matching projects from the context.
- Group results by category when possible.
- Do NOT include projects that don't match the user's request.
- Format output clearly with Markdown.
- Be specific about technologies and project details."""

        print(f"Agent streaming from {model} with context length {len(context)}")
        try:
            stream = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True,
                options={'num_gpu': 99}
            )
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def generate_resume(self, query: str, username: str, model: str, user_profile=None):
        from services.resume_engine import ResumeEngine
        engine = ResumeEngine(self.rag)

        target_domain, target_role = engine._detect_domain(query)
        print(f"Resume generation: target_domain={target_domain}, target_role={target_role}")

        result = engine.generate_resume(query, username, model, user_profile=user_profile)
        return result
