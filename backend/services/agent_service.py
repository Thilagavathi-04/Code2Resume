import ollama
import os
from .rag_service import RAGService


class AgentService:
    def __init__(self):
        self.rag = RAGService()

    def ask(self, query: str, username: str, model: str = "mistral:latest"):
        if "resume" in query.lower() or "cv" in query.lower():
            return self.generate_resume(query, username, model)

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

    def ask_stream(self, query: str, username: str, model: str = "mistral:latest"):
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

    def generate_resume(self, query: str, username: str, model: str):
        query_lower = query.lower()
        target_domain = None
        target_role = "Software Engineer"

        domain_keywords = {
            "Machine Learning": ["ml", "machine learning", "ai", "artificial intelligence", "deep learning", "neural network"],
            "Data Science": ["data scien", "data analy", "analytics", "data engineer"],
            "Full Stack": ["full stack", "fullstack", "full-stack"],
            "Frontend": ["frontend", "front-end", "ui", "ux", "react", "vue", "angular"],
            "Backend": ["backend", "back-end", "api", "server"],
            "Mobile App": ["mobile", "android", "ios", "flutter", "react native"],
            "DevOps": ["devops", "dev-ops", "infrastructure", "cloud", "kubernetes", "docker"],
            "Cybersecurity": ["security", "cybersecurity", "penetration", "encryption"],
        }

        for domain, keywords in domain_keywords.items():
            if any(kw in query_lower for kw in keywords):
                target_domain = domain
                target_role = domain + " Engineer" if domain != "Full Stack" else "Full Stack Developer"
                break

        print(f"Resume generation: target_domain={target_domain}, target_role={target_role}")

        if target_domain:
            search_query = f"{target_domain} projects"
            results = self.rag.query(search_query, username=username, n_results=50)
        else:
            results = self.rag.query("List all projects and their details", username=username, n_results=50)

        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]

        if target_domain and metadatas:
            filtered_docs = []
            for doc, meta in zip(documents, metadatas):
                if isinstance(meta, dict) and meta.get('type') == 'repo_summary':
                    filtered_docs.append(doc)
            documents = filtered_docs if filtered_docs else documents

        context = "\n---\n".join(documents) if documents else "No project data found."

        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "LateX_template", "main.tex")
        try:
            with open(template_path, "r") as f:
                template_content = f.read()
        except FileNotFoundError:
            return "Error: Resume template (main.tex) not found."

        domain_filter = f" Focus ONLY on {target_domain} projects." if target_domain else ""

        prompt = f"""
You are an expert Resume Writer and LaTeX developer.
The user wants a resume for: "{query}"
Target Role: {target_role}
{f"Target Domain: {target_domain}" if target_domain else ""}

Here is the user's project history (from GitHub):
{context}

Here is the LaTeX template to use (main.tex):
```tex
{template_content}
```

**CRITICAL INSTRUCTIONS:**

1. **Content Filling Only**: You are ONLY filling in the content. Keep the LaTeX structure, formatting, and commands EXACTLY as provided.

2. **Personal Information**: 
   - Replace "Mithrajith K S" with "{username}" (or keep if same user)
   - Keep contact details section structure (phone, LinkedIn, GitHub)

3. **Summary Section**: 
   - Write a 2-3 sentence professional summary for the "{target_role}" role
   - Highlight relevant skills from the projects
   - Keep it professional and concise

4. **Skills Section**:
   - Extract ALL technologies from the projects
   - Organize into: Languages, Frameworks, Databases, Machine Learning (if applicable), Tools, Other
   - Format: **Category:** item1, item2, item3

5. **Projects Section**{domain_filter}:
   - Select 4-6 MOST relevant projects from the context
   - For each project use this format:
     \\textbf{{Project Name}}  
     \\textit{{Main Technologies}}
     \\begin{{itemize}}
         \\item Bullet point 1 (achievement/feature)
         \\item Bullet point 2 (technical detail)
         \\item Bullet point 3 (impact/result)
     \\end{{itemize}}
   
   - **IMPORTANT**: If a project lacks description or features in the context, YOU MUST GENERATE them intelligently based on:
     * Project name (infer purpose)
     * Tech stack (infer functionality)
     * Common use cases for that technology
     * Best practices for that domain
   
   - Write 3 strong bullet points per project using action verbs (Built, Developed, Engineered, Designed, Implemented)
   - Focus on technical achievements and measurable impact

6. **Output Format**: 
   - Return ONLY the complete, valid LaTeX code
   - Start with \\documentclass and end with \\end{{document}}
   - NO markdown formatting (no ```tex or ```latex)
   - NO explanatory text before or after
   - Ready to compile as-is

Generate the resume now:
"""

        print(f"Generating {target_domain or 'general'} resume with {model}...")
        try:
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt},
            ], options={'num_gpu': 99})
            content = response['message']['content']

            if content.startswith("```tex"):
                content = content[6:]
            if content.startswith("```latex"):
                content = content[8:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            return content.strip()
        except Exception as e:
            return f"Error generating resume: {str(e)}"
