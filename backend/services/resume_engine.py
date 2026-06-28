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

    def _fetch_context(self, username, target_domain, user_profile=None):
        query = f"{target_domain} projects" if target_domain else "All projects"

        print(f"\n[ResumeEngine] Fetching context for '{query}'")
        repos = self.rag.get_user_repos(username)
        print(f"[ResumeEngine] Found {len(repos)} repos for {username}")

        if not repos:
            print(f"[ResumeEngine] No repos found, returning empty context")
            return "No project data found."

        if target_domain:
            matching = [r for r in repos if target_domain.lower() in (r.get("category", "") + " " + r.get("domain", "")).lower()]
            if matching:
                repos = matching
                print(f"[ResumeEngine] Filtered to {len(repos)} repos matching '{target_domain}'")

        repos = sorted(repos, key=lambda r: r.get("final_score", 0) or r.get("resume_strength", 0) or 0, reverse=True)[:12]

        from services.context_compressor import ContextCompressor
        from app.core.config import settings
        compressor = ContextCompressor(max_tokens=settings.MAX_CONTEXT_TOKENS)
        context = compressor.compress_repos(repos, profile=user_profile)

        print(f"[ResumeEngine] Context built: {len(context)} chars, {len(repos)} repos")
        for i, repo in enumerate(repos[:10]):
            name = repo.get("name", "?")
            cat = repo.get("category", "?")
            techs = repo.get("tech_stack", [])
            tech_str = ", ".join(techs[:5]) if isinstance(techs, list) else str(techs)[:50]
            print(f"[ResumeEngine]   [{i+1}] {name} (cat={cat}, techs=[{tech_str}])")

        return context

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
        phone = profile.get("phone", "")
        edu_institution = profile.get("education_institution", "")
        edu_degree = profile.get("education_degree", "")
        edu_field = profile.get("education_field", "")
        edu_start = profile.get("education_start_date", "")
        edu_end = profile.get("education_end_date", "")
        edu_gpa = profile.get("education_gpa", "")
        skills = []
        skill_pattern = re.findall(r'(?:Python|JavaScript|TypeScript|React|Node\.?js|Flask|Django|FastAPI|PostgreSQL|MongoDB|MySQL|Docker|Kubernetes|AWS|Git|TensorFlow|PyTorch|Scikit-learn|OpenCV|Pandas|NumPy|HTML|CSS|Java|C\+\+|Go|Rust|Ruby|PHP|Swift|Kotlin|Flutter|Redis|GraphQL|REST|API|LLM|NLP|Machine Learning|Deep Learning|AI|Data Science|Spark|Hadoop|Airflow|Linux|Bash|Shell|CI/CD|Terraform|Ansible)', context, re.I)
        seen_skills = set()
        for s in skill_pattern:
            if s.lower() not in seen_skills:
                seen_skills.add(s.lower())
                cat = "Programming Languages" if s.lower() in ("python", "javascript", "typescript", "java", "c++", "go", "rust", "ruby", "php", "swift", "kotlin", "html", "css", "bash", "shell", "sql") else \
                      "Core Areas" if s.lower() in ("machine learning", "deep learning", "AI", "data science", "nlp", "llm", "computer vision", "rag") else \
                      "Libraries & Frameworks" if s.lower() in ("react", "node.js", "nodejs", "flask", "django", "fastapi", "flutter", "graphql", "tensorflow", "pytorch", "scikit-learn", "opencv", "pandas", "numpy", "langchain", "faiss") else \
                      "Tools & Platforms" if s.lower() in ("docker", "kubernetes", "aws", "Git", "linux", "ci/cd", "terraform", "ansible", "spark", "hadoop", "airflow", "rest", "api", "firebase", "ollama", "postgresql", "mongodb", "mysql", "redis") else "Other"
                skills.append({"name": s, "category": cat})

        projects = []
        repo_blocks = context.split("---")
        for block in repo_blocks[:5]:
            name_match = re.search(r'Project:\s*(.+)', block)
            if not name_match:
                continue
            name = name_match.group(1).strip()

            desc_lines = []
            desc_match = re.search(r'Description:\s*(.+?)(?:\n|$)', block)
            if desc_match and desc_match.group(1).strip():
                desc_lines.append(desc_match.group(1).strip())

            features_match = re.search(r'Features:\s*(.+?)(?:\n|$)', block)
            if features_match and features_match.group(1).strip() and features_match.group(1).strip() != "None":
                desc_lines.append(f"Key features include {features_match.group(1).strip()}.")

            readme_match = re.search(r'README:\s*([\s\S]+?)(?:\nProject:|\n---|$)', block)
            if readme_match:
                readme_text = readme_match.group(1).strip()[:500]
                sentences = re.split(r'[.!?\n]+', readme_text)
                for s in sentences[:3]:
                    s = s.strip()
                    if len(s) > 20 and not s.startswith('#'):
                        desc_lines.append(s)

            if not desc_lines:
                desc_lines = [
                    f"A software project built with modern technologies.",
                    f"Developed as part of {username}'s portfolio demonstrating technical skills.",
                ]

            description = " ".join(desc_lines[:2])
            if len(description) > 300:
                description = description[:297] + "..."

            tech_match = re.search(r'Tech Stack:\s*(.+?)(?:\n|$)', block)
            techs = [t.strip() for t in tech_match.group(1).split(",")] if tech_match and tech_match.group(1).strip() else []
            tech_str = ", ".join(techs[:4]) if techs else "modern technologies"

            highlights = [
                f"Architected and developed {name} using {tech_str}",
                f"Implemented core features with focus on performance and code quality",
                f"Deployed and maintained the application with CI/CD best practices",
            ]

            projects.append({
                "name": f"{name} – {desc_lines[0][:60] if desc_lines else 'Software Project'}",
                "description": description,
                "technologies": techs[:6],
                "highlights": highlights,
                "github_url": "",
            })

        return {
            "personal": {"name": username, "email": email, "phone": phone, "location": "", "linkedin": linkedin, "github": github, "website": leetcode},
            "summary": f"Results-driven {target_role} with hands-on experience in {', '.join(list(seen_skills)[:6])}. Proven track record of building scalable applications and delivering end-to-end solutions. Passionate about leveraging modern technologies to solve complex technical challenges and drive measurable impact.",
            "skills": skills or [{"name": s, "category": cat} for s, cat in [("Python", "Programming Languages"), ("JavaScript", "Programming Languages"), ("React", "Libraries & Frameworks"), ("Node.js", "Libraries & Frameworks"), ("Docker", "Tools & Platforms")]],
            "experience": [],
            "education": [{"institution": edu_institution, "degree": edu_degree, "field": edu_field, "startDate": edu_start, "endDate": edu_end, "gpa": edu_gpa}] if edu_institution else [],
            "projects": projects[:5],
            "certifications": [],
            "section_order": ["summary", "skills", "projects", "education", "certifications"],
        }

    def _ensure_education(self, resume_data, user_profile=None):
        education = resume_data.get("education", [])
        if not education or not education[0].get("institution"):
            profile = user_profile or {}
            inst = profile.get("education_institution", "")
            if inst:
                resume_data["education"] = [{
                    "institution": inst,
                    "degree": profile.get("education_degree", ""),
                    "field": profile.get("education_field", ""),
                    "startDate": profile.get("education_start_date", ""),
                    "endDate": profile.get("education_end_date", ""),
                    "gpa": profile.get("education_gpa", ""),
                }]

    def _call_llm(self, model, system_msg, user_msg):
        from services.llm_service import get_llm
        messages = [
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_msg},
        ]
        return get_llm().generate_response(messages)

    def generate_structured_resume(self, query, username, model, user_profile=None, requested_projects=None):
        target_domain, target_role = self._detect_domain(query)
        context = self._fetch_context(username, target_domain, user_profile=user_profile)

        if requested_projects:
            filtered = []
            for line in context.split("\n---\n"):
                for rp in requested_projects:
                    if rp.lower() in line.lower():
                        filtered.append(line)
                        break
            if filtered:
                context = "\n---\n".join(filtered)
                print(f"[ResumeEngine] Filtered to {len(filtered)} requested projects: {requested_projects}")

        profile = user_profile or {}
        email = profile.get("email", "")
        github = profile.get("github", "")
        linkedin = profile.get("linkedin", "")
        leetcode = profile.get("leetcode", "")
        phone = profile.get("phone", "")
        edu_institution = profile.get("education_institution", "")
        edu_degree = profile.get("education_degree", "")
        edu_field = profile.get("education_field", "")
        edu_start = profile.get("education_start_date", "")
        edu_end = profile.get("education_end_date", "")
        edu_gpa = profile.get("education_gpa", "")

        edu_section = ""
        if edu_institution:
            edu_section = f"\nEducation: {edu_degree} in {edu_field} from {edu_institution} ({edu_start} to {edu_end}), GPA: {edu_gpa or 'N/A'}"

        system_msg = "You are a professional resume writer. You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no text before or after the JSON."

        user_msg = f"""Generate a resume JSON for role: {target_role}

User: {username}
Email: {email or 'not provided'}
Phone: {phone or 'not provided'}
GitHub: {github or 'not provided'}
LinkedIn: {linkedin or 'not provided'}
LeetCode: {leetcode or 'not provided'}
{edu_section}

Below is the raw project data extracted from the user's ACTUAL GitHub repositories:

{context}

CRITICAL RULES - VIOLATION WILL REJECT YOUR OUTPUT:

1. PROJECTS - You MUST ONLY use projects that appear in the context above. NEVER invent, create, rename, or fabricate any project. Every project name MUST match a "Project: <name>" line from the context exactly. If you include a project not in the context, the output is INVALID.

2. SKILLS - Extract skills ONLY from the tech stacks and descriptions in the context above. Do not add skills that are not mentioned in the context.

3. SKILLS FORMAT - Categorize skills exactly like this:
   - "Programming Languages": Python, SQL, JavaScript, TypeScript, etc.
   - "Core Areas": Machine Learning, NLP, Generative AI, RAG, LLM Applications, Computer Vision, etc.
   - "Libraries & Frameworks": LangChain, FAISS, TensorFlow, Scikit-learn, Flask, React, etc.
   - "Tools & Platforms": Git, GitHub, VS Code, Google Colab, Firebase, Docker, AWS, Ollama, etc.
   Each skill object must use these EXACT category names.

4. PROJECTS FORMAT - For each project:
   - "name": "PROJECT_NAME – Short one-line description" (use the exact PROJECT_NAME from the context)
   - "description": "1-2 sentences: what was built and the technical approach"
   - "technologies": ["Tech1", "Tech2", "Tech3"] (the main technologies used)
   - "highlights": ["Built X using Y achieving Z", "Implemented A with B reducing C by D%"] (2-3 bullet points with strong action verbs)
   - "github_url": the repo URL if available

5. If Resume Description or Bullet Points are provided for a project, use them as the primary source.

6. Include ONLY real projects from the context (or up to 6 best ones if there are many). Do NOT add any project not listed above.

7. ALWAYS include email, phone, GitHub in personal section.

8. Write a detailed 3-4 sentence professional summary.

Return this JSON structure exactly:
{{"personal":{{"name":"{username}","email":"{email}","phone":"{phone}","location":"","linkedin":"{linkedin}","github":"{github}","website":"{leetcode}"}},"summary":"3-4 sentence summary for {target_role}","skills":[{{"name":"Python","category":"Programming Languages"}},{{"name":"Machine Learning","category":"Core Areas"}},{{"name":"LangChain","category":"Libraries & Frameworks"}},{{"name":"Git","category":"Tools & Platforms"}}],"experience":[{{"company":"Co","position":"Title","startDate":"2024-01","endDate":"2024-06","highlights":["Built X using Y reducing Z by N%"]}}],"education":[{{"institution":"{edu_institution or 'Uni'}","degree":"{edu_degree or 'BS'}","field":"{edu_field or 'CS'}","startDate":"{edu_start or '2022'}","endDate":"{edu_end or '2026'}","gpa":"{edu_gpa or ''}"}}],"projects":[{{"name":"PROJECT_NAME – Short Description","description":"1-2 sentences about what was built and how","technologies":["Tech1","Tech2"],"highlights":["Built X using Y achieving Z","Implemented A with B"],"github_url":""}}],"certifications":[{{"name":"Cert","issuer":"Org"}}],"section_order":["summary","skills","projects","education","certifications"]}}

Return ONLY the JSON."""

        print(f"\n[ResumeEngine] === DATA PASSED TO LLM ===")
        print(f"[ResumeEngine] Target role: {target_role}")
        print(f"[ResumeEngine] User: {username}")
        print(f"[ResumeEngine] Email: {email or 'not provided'}")
        print(f"[ResumeEngine] Phone: {phone or 'not provided'}")
        print(f"[ResumeEngine] GitHub: {github or 'not provided'}")
        print(f"[ResumeEngine] LinkedIn: {linkedin or 'not provided'}")
        print(f"[ResumeEngine] Education: {edu_institution or 'none'}")
        print(f"[ResumeEngine] Context length: {len(context)} chars")
        print(f"[ResumeEngine] Context preview:\n{context[:1500]}")
        print(f"[ResumeEngine] === END DATA ===\n")
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
                    self._ensure_skills(resume_data, context)
                    self._ensure_projects(resume_data, username, context)
                    self._validate_projects(resume_data, context)
                    self._ensure_project_descriptions(resume_data, username)
                    self._ensure_education(resume_data, user_profile)
                    return resume_data
                print(f"[ResumeEngine] Attempt {attempt + 1}: invalid JSON, retrying...")
            except Exception as e:
                print(f"[ResumeEngine] Attempt {attempt + 1} failed: {e}")

        print("[ResumeEngine] All LLM attempts failed, using fallback parser")
        return self._build_fallback_resume(username, target_role, context, user_profile=user_profile)

    def _validate_projects(self, resume_data, context):
        real_names = set()
        for match in re.finditer(r'Project:\s*(.+)', context):
            real_names.add(match.group(1).strip().lower())

        projects = resume_data.get("projects", [])
        valid = []
        for proj in projects:
            proj_name = proj.get("name", "")
            proj_name_lower = proj_name.split("–")[0].strip().lower() if "–" in proj_name else proj_name.lower()
            if proj_name_lower in real_names:
                valid.append(proj)
            else:
                print(f"[ResumeEngine] FILTERED OUT fake project: '{proj_name}' (not in context)")
        if len(valid) < len(projects):
            print(f"[ResumeEngine] Projects: {len(projects)} -> {len(valid)} after validation")
        resume_data["projects"] = valid

    def _ensure_skills(self, resume_data, context):
        skills = resume_data.get("skills", [])
        if skills:
            return
        skill_pattern = re.findall(
            r'(?:Python|JavaScript|TypeScript|React|Node\.?js|Flask|Django|FastAPI|PostgreSQL|MongoDB|MySQL|Docker|Kubernetes|AWS|Git|GitHub|TensorFlow|PyTorch|Scikit-learn|OpenCV|Pandas|NumPy|HTML|CSS|Java|C\+\+|Go|Rust|Ruby|PHP|Swift|Kotlin|Flutter|Redis|GraphQL|REST|API|LLM|NLP|Machine Learning|Deep Learning|AI|Data Science|Spark|Hadoop|Airflow|Linux|Bash|Shell|CI/CD|Terraform|Ansible|LangChain|FAISS|Ollama)',
            context, re.I,
        )
        seen = set()
        for s in skill_pattern:
            if s.lower() not in seen:
                seen.add(s.lower())
                cat = (
                    "Programming Languages" if s.lower() in ("python", "javascript", "typescript", "java", "c++", "go", "rust", "ruby", "php", "swift", "kotlin", "html", "css", "bash", "shell", "sql") else
                    "Core Areas" if s.lower() in ("machine learning", "deep learning", "ai", "data science", "nlp", "llm", "computer vision", "rag") else
                    "Libraries & Frameworks" if s.lower() in ("react", "node.js", "nodejs", "flask", "django", "fastapi", "flutter", "graphql", "tensorflow", "pytorch", "scikit-learn", "opencv", "pandas", "numpy", "langchain", "faiss") else
                    "Tools & Platforms"
                )
                skills.append({"name": s, "category": cat})
        resume_data["skills"] = skills

    def _ensure_projects(self, resume_data, username, context):
        projects = resume_data.get("projects", [])
        if projects:
            return
        repo_blocks = re.split(r'\n---\n', context)
        for block in repo_blocks[:6]:
            name_match = re.search(r'Project:\s*(.+)', block)
            if not name_match:
                continue
            name = name_match.group(1).strip()
            tech_match = re.search(r'Tech Stack:\s*(.+?)(?:\n|$)', block)
            techs = [t.strip() for t in tech_match.group(1).split(",")] if tech_match and tech_match.group(1).strip() else []
            lines = block.strip().split("\n")
            desc_lines = []
            for line in lines[2:]:
                line = line.strip()
                if not line or line.startswith("Tech Stack:") or line.startswith("Project:") or line.startswith("Readme:"):
                    break
                desc_lines.append(line)
            desc = " ".join(desc_lines)[:200] if desc_lines else ""
            readme_match = re.search(r'Readme:\s*([\s\S]+?)(?:\nProject:|\n---|$)', block, re.IGNORECASE)
            highlights = []
            if readme_match:
                sentences = re.split(r'[.!?\n]+', readme_match.group(1).strip()[:500])
                for s in sentences[:3]:
                    s = s.strip()
                    if len(s) > 20 and not s.startswith('#'):
                        highlights.append(s)
            if not highlights:
                highlights = [
                    f"Architected and developed {name} using {', '.join(techs[:3]) if techs else 'modern technologies'}",
                    "Implemented core features with focus on performance and code quality",
                ]
            projects.append({
                "name": f"{name} – {desc[:60] if desc else 'Software Project'}",
                "description": desc or f"A software project built with {', '.join(techs[:3]) if techs else 'modern technologies'}.",
                "technologies": techs[:6],
                "highlights": highlights,
                "github_url": "",
            })
        resume_data["projects"] = projects

    def _ensure_project_descriptions(self, resume_data, username):
        projects = resume_data.get("projects", [])
        for proj in projects:
            desc = (proj.get("description") or "").strip()
            name = proj.get("name", "this project")
            techs = proj.get("technologies", [])
            tech_str = ", ".join(techs[:3]) if techs else "modern technologies"
            highlights = proj.get("highlights", [])

            if len(desc) < 20:
                if highlights:
                    proj["description"] = f"{highlights[0].rstrip('.')}. Built with {tech_str} to deliver a robust and scalable solution."
                else:
                    proj["description"] = f"A software project built with {tech_str}. Developed with focus on performance, scalability, and code quality."

            if not highlights or len(highlights) < 2:
                proj["highlights"] = highlights or [
                    f"Architected and developed {name.split('–')[0].strip()} using {tech_str}",
                    "Implemented core features with focus on performance and code quality",
                ]

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

    def generate_resume(self, query, username, model=None, template="modern", user_profile=None, requested_projects=None):
        from app.core.config import settings
        model = model or settings.DEFAULT_MODEL
        target_domain, target_role = self._detect_domain(query)
        print(f"[ResumeEngine] target_domain={target_domain}, target_role={target_role}")

        resume_data = self.generate_structured_resume(query, username, model, user_profile=user_profile, requested_projects=requested_projects)

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
