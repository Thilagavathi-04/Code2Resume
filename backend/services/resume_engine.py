import json
import os
import re
from jinja2 import Environment, FileSystemLoader
from .rag_service import RAGService


LATEX_ESCAPE = {
    '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
    '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
    '\\': r'\textbackslash{}', '<': r'\textless{}', '>': r'\textgreater{}',
}


def escape_latex(value):
    if value is None:
        return ""
    s = str(value)
    for char, replacement in LATEX_ESCAPE.items():
        s = s.replace(char, replacement)
    return s


class ResumeEngine:
    def __init__(self, rag=None):
        self.rag = rag or RAGService()
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            block_start_string=r"<%",
            block_end_string=r"%>",
            variable_start_string=r"<<",
            variable_end_string=r">>",
            comment_start_string=r"<#",
            comment_end_string=r"#>",
            autoescape=False,
            keep_trailing_newline=True,
        )
        self.jinja_env.filters['escape_latex'] = escape_latex

    def _detect_domain(self, query):
        query_lower = query.lower()
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
                target_role = domain + " Engineer" if domain != "Full Stack" else "Full Stack Developer"
                return domain, target_role
        return None, "Software Engineer"

    def _fetch_context(self, username, target_domain):
        if target_domain:
            results = self.rag.query(f"{target_domain} projects", username=username, n_results=50)
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

        return "\n---\n".join(documents) if documents else "No project data found."

    def _parse_json_response(self, content):
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        return None

    def _build_fallback_resume(self, username, target_role, context, user_profile=None):
        profile = user_profile or {}
        email = profile.get("email", "")
        github = profile.get("github", "")
        linkedin = profile.get("linkedin", "")
        leetcode = profile.get("leetcode", "")
        skills = []
        skill_pattern = re.findall(r'(?:Python|JavaScript|TypeScript|React|Node\.?js|Flask|Django|FastAPI|PostgreSQL|MongoDB|MySQL|Docker|Kubernetes|AWS|Git|TensorFlow|PyTorch|Scikit-learn|OpenCV|Pandas|NumPy|HTML|CSS|Java|C\+\+|Go|Rust|Ruby|PHP|Swift|Kotlin|Flutter|Redis|GraphQL|REST|API|LLM|NLP|Machine Learning|Deep Learning|AI|Data Science|Spark|Hadoop|Airflow|Linux|Bash|Shell|CI/CD|Terraform|Ansible)', context, re.I)
        seen_skills = set()
        for s in skill_pattern:
            if s.lower() not in seen_skills:
                seen_skills.add(s.lower())
                cat = "Languages" if s.lower() in ("python", "javascript", "typescript", "java", "c++", "go", "rust", "ruby", "php", "swift", "kotlin", "html", "css", "bash", "shell") else \
                      "Frameworks" if s.lower() in ("react", "node.js", "nodejs", "flask", "django", "fastapi", "flutter", "graphql") else \
                      "Databases" if s.lower() in ("postgresql", "mongodb", "mysql", "redis") else \
                      "ML/AI" if s.lower() in ("tensorflow", "pytorch", "scikit-learn", "opencv", "pandas", "numpy", "llm", "nlp", "machine learning", "deep learning", "ai", "data science") else \
                      "Tools" if s.lower() in ("docker", "kubernetes", "aws", "git", "linux", "ci/cd", "terraform", "ansible", "spark", "hadoop", "airflow", "rest", "api") else "Other"
                skills.append({"name": s, "category": cat})

        projects = []
        repo_blocks = context.split("---")
        for block in repo_blocks[:5]:
            name_match = re.search(r'Project:\s*(.+)', block)
            desc_match = re.search(r'Description:\s*(.+)', block)
            tech_match = re.search(r'Tech Stack:\s*(.+)', block)
            if name_match:
                name = name_match.group(1).strip()
                desc = desc_match.group(1).strip() if desc_match else ""
                techs = [t.strip() for t in tech_match.group(1).split(",")] if tech_match else []
                tech_str = ", ".join(techs[:4]) if techs else "modern technologies"
                projects.append({
                    "name": name,
                    "description": f"{desc} Built using {tech_str} to ensure scalability and maintainability.",
                    "technologies": techs[:6],
                    "highlights": [
                        f"Architected and developed {name} using {tech_str}",
                        f"Implemented core features with focus on performance and code quality",
                        f"Deployed and maintained the application with CI/CD best practices",
                    ],
                    "github_url": "",
                })

        return {
            "personal": {"name": username, "email": email, "phone": "", "location": "", "linkedin": linkedin, "github": github, "website": leetcode},
            "summary": f"Results-driven {target_role} with hands-on experience in {', '.join(list(seen_skills)[:6])}. Proven track record of building scalable applications and delivering end-to-end solutions. Passionate about leveraging modern technologies to solve complex technical challenges and drive measurable impact.",
            "skills": skills or [{"name": s, "category": cat} for s, cat in [("Python", "Languages"), ("JavaScript", "Languages"), ("React", "Frameworks"), ("Node.js", "Frameworks"), ("Docker", "Tools")]],
            "experience": [],
            "education": [],
            "projects": projects[:5],
            "certifications": [],
            "section_order": ["summary", "skills", "projects", "education", "certifications"],
        }

    def _call_llm(self, model, system_msg, user_msg):
        from app.core.config import settings
        from ollama import Client
        client = Client(host=settings.OLLAMA_HOST, timeout=settings.LLM_TIMEOUT)
        response = client.chat(model=model, messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_msg},
        ], options={'num_gpu': 99, 'temperature': 0.3})
        return response['message']['content']

    def generate_structured_resume(self, query, username, model, user_profile=None):
        target_domain, target_role = self._detect_domain(query)
        context = self._fetch_context(username, target_domain)

        profile = user_profile or {}
        email = profile.get("email", "")
        github = profile.get("github", "")
        linkedin = profile.get("linkedin", "")
        leetcode = profile.get("leetcode", "")

        system_msg = "You are a professional resume writer. You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no text before or after the JSON."

        user_msg = f"""Generate a resume JSON for role: {target_role}

User: {username}
Email: {email or 'not provided'}
GitHub: {github or 'not provided'}
LinkedIn: {linkedin or 'not provided'}
LeetCode: {leetcode or 'not provided'}

Projects:
{context}

Return this JSON structure exactly:
{{"personal":{{"name":"{username}","email":"{email}","phone":"","location":"","linkedin":"{linkedin}","github":"{github}","website":"{leetcode}"}},"summary":"3-4 sentence summary for {target_role} highlighting key skills, experience domains, and career objectives","skills":[{{"name":"Skill","category":"Languages"}}],"experience":[{{"company":"Co","position":"Title","startDate":"2024-01","endDate":"2024-06","highlights":["Built X using Y reducing Z by N%"]}}],"education":[{{"institution":"Uni","degree":"BS","field":"CS","startDate":"2022","endDate":"2026","gpa":""}}],"projects":[{{"name":"Proj","description":"Two-line description: first sentence explains what the project does and its purpose, second sentence describes the technical approach and key features implemented","technologies":["Python","React"],"highlights":["Architected and built X using Y achieving Z","Implemented A feature with B reducing C by D%","Optimized E resulting in F improvement"],"github_url":""}}],"certifications":[{{"name":"Cert","issuer":"Org"}}],"section_order":["summary","skills","projects","education","certifications"]}}

Rules:
- Use the user's actual email, GitHub, LinkedIn, and LeetCode URLs in the personal section
- Extract skills from projects and categorize them properly
- Select ALL available projects (up to 5). Each project MUST have a 2-sentence description (what it does + how it was built)
- Each project MUST have 3-4 bullet points starting with strong action verbs (Architected, Implemented, Designed, Developed, Optimized, Deployed, Led)
- Write a detailed 3-4 sentence summary
- If no experience, set experience to [] and add more projects with richer descriptions
- Make the resume detailed enough to fill one full page
- Return ONLY the JSON."""

        print(f"[ResumeEngine] Generating structured resume for {target_role} with {model}...")

        for attempt in range(2):
            try:
                content = self._call_llm(model, system_msg, user_msg)
                resume_data = self._parse_json_response(content)
                if resume_data and isinstance(resume_data, dict) and "personal" in resume_data:
                    required_keys = ["personal", "summary", "skills", "experience", "education", "projects", "certifications", "section_order"]
                    for key in required_keys:
                        if key not in resume_data:
                            resume_data[key] = [] if key not in ("personal", "summary", "section_order") else {} if key == "personal" else ""
                    return resume_data
                print(f"[ResumeEngine] Attempt {attempt + 1}: invalid JSON, retrying...")
            except Exception as e:
                print(f"[ResumeEngine] Attempt {attempt + 1} failed: {e}")

        print("[ResumeEngine] All LLM attempts failed, using fallback parser")
        return self._build_fallback_resume(username, target_role, context, user_profile=user_profile)

    def render_latex(self, resume_data, template_name="modern"):
        template_file = f"resume_{template_name}.tex.j2"
        try:
            template = self.jinja_env.get_template(template_file)
        except Exception:
            template = self.jinja_env.get_template("resume_modern.tex.j2")

        return template.render(
            personal=resume_data.get("personal", {}),
            summary=resume_data.get("summary", ""),
            skills=resume_data.get("skills", []),
            experience=resume_data.get("experience", []),
            education=resume_data.get("education", []),
            projects=resume_data.get("projects", []),
            certifications=resume_data.get("certifications", []),
            section_order=resume_data.get("section_order", ["summary", "skills", "projects", "education"]),
        )

    def validate_one_page(self, latex_content):
        warnings = []
        suggestions = []
        lines = latex_content.split('\n')
        non_empty = [l for l in lines if l.strip() and not l.strip().startswith('%')]

        if len(non_empty) > 320:
            warnings.append(f"Resume has {len(non_empty)} content lines; may overflow to page 2")
            suggestions.append("Consider reducing project bullet points or removing lower-priority sections")

        if len(non_empty) < 150:
            warnings.append(f"Resume has only {len(non_empty)} content lines; may appear sparse")
            suggestions.append("Consider adding more project details or expanding skills section")

        if "\\begin{document}" not in latex_content:
            warnings.append("Missing \\begin{document}")
        if "\\end{document}" not in latex_content:
            warnings.append("Missing \\end{document}")

        sections = re.findall(r'\\section\*?\{([^}]+)\}', latex_content)
        if len(sections) < 2:
            warnings.append(f"Only {len(sections)} sections found; resume may be incomplete")

        return {
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
            "suggestions": suggestions,
            "line_count": len(non_empty),
            "sections": sections,
        }

    def generate_resume(self, query, username, model=None, template="modern", user_profile=None):
        from app.core.config import settings
        model = model or settings.DEFAULT_MODEL
        target_domain, target_role = self._detect_domain(query)
        print(f"[ResumeEngine] target_domain={target_domain}, target_role={target_role}")

        resume_data = self.generate_structured_resume(query, username, model, user_profile=user_profile)

        resume_data["personal"]["name"] = username

        latex = self.render_latex(resume_data, template)

        validation = self.validate_one_page(latex)

        if not validation["is_valid"]:
            print(f"[ResumeEngine] Validation warnings: {validation['warnings']}")

        return {
            "latex": latex,
            "resume_data": resume_data,
            "template": template,
            "section_order": resume_data.get("section_order", []),
            "validation": validation,
        }
