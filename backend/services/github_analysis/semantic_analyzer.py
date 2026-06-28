from typing import Any, Dict


async def analyze_semantics(
    repo_data: dict,
    readme: str,
    tech_stack: dict,
    structure: dict,
    architecture: dict,
    classification: dict,
    aiml: dict,
    deployment: dict,
    databases: dict,
    testing: dict,
    services: dict,
    quality_metrics: dict,
    knowledge_graph: dict,
) -> dict:
    from services.llm_service import get_llm

    all_tech = []
    for cat in tech_stack.values():
        if isinstance(cat, list):
            all_tech.extend(cat)

    knowledge_text = "Project Knowledge Graph:\n"
    for category, items in knowledge_graph.items():
        if items:
            knowledge_text += f"  {category}: {', '.join(items)}\n"

    system_msg = (
        "You are a senior software engineer analyzing a GitHub repository. "
        "You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no text before or after the JSON. "
        "Do NOT hallucinate or invent technologies that are not listed in the provided data."
    )

    user_msg = f"""Analyze this GitHub repository and generate structured insights.

Repository: {repo_data.get('name', 'Unknown')}
Description: {repo_data.get('description', 'No description')}
Stars: {repo_data.get('stargazers_count', 0)}
Primary Language: {repo_data.get('language', 'Unknown')}
Created: {repo_data.get('created_at', 'Unknown')}
Updated: {repo_data.get('updated_at', 'Unknown')}

Detected Technologies:
{knowledge_text}

Architecture: {architecture.get('type', 'Unknown')} ({architecture.get('pattern', 'Unknown')})
Classification: {classification.get('primary', 'Unknown')} (confidence: {classification.get('confidence', 0)})

AI/ML Capabilities: {', '.join(aiml.get('detected_libraries', []) or ['None'])}
AI Capabilities: {', '.join(aiml.get('capabilities', []) or ['None'])}

Deployment: {', '.join(deployment.get('detected_technologies', []) or ['None'])}
Databases: {', '.join(databases.get('relational', []) + databases.get('nosql', []) or ['None'])}
Testing: {', '.join(testing.get('frameworks', []) or ['None'])}
External Services: {', '.join(services.get('detected_services', []) or ['None'])}

Quality Metrics:
  Documentation: {quality_metrics.get('documentation_score', 0)}/10
  Complexity: {quality_metrics.get('codebase_complexity', 0)}/10
  Maintainability: {quality_metrics.get('maintainability_score', 0)}/10
  Health: {quality_metrics.get('project_health_score', 0)}/10

README (first 3000 chars):
{readme[:3000] if readme else 'No README available'}

Generate the following JSON structure:

{{
  "executive_summary": "2-3 sentence overview of what this project does and why it matters",
  "problem_statement": "What problem does this project solve",
  "solution": "How does the project solve it technically",
  "target_users": "Who would use this project",
  "domain": "Primary domain (e.g., Web Development, AI/ML, DevOps)",
  "industry": "Industry applicability (e.g., Tech, Finance, Healthcare)",
  "technical_challenges": ["list of technical challenges addressed"],
  "key_features": ["list of 3-5 key features"],
  "architecture_summary": "How the system is structured",
  "development_complexity": "low|medium|high",
  "innovation_score": "1-10 rating of innovation",
  "resume_description": "Professional 2-sentence project description suitable for a resume",
  "ats_keywords": ["list of 5-10 ATS-friendly keywords from this project"],
  "resume_bullet_points": ["3-4 resume bullet points starting with action verbs"],
  "portfolio_description": "Engaging 2-sentence description for portfolio display",
  "interview_questions": ["3-3 technical interview questions about this project"],
  "recruiter_summary": "1-sentence pitch a recruiter could use",
  "suggested_skills": ["skills demonstrated by this project"],
  "estimated_experience_level": "beginner|intermediate|advanced|expert"
}}

Rules:
- Use ONLY technologies listed in the detected data above
- Do NOT invent features or technologies not present in the codebase
- Keep descriptions accurate and grounded in the actual code
- Make resume content professional and ATS-optimized
- Return ONLY the JSON"""

    try:
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
        content = get_llm().generate_response(messages)

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        import json
        import re
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {}

        return result
    except Exception as e:
        print(f"[SemanticAnalyzer] LLM analysis failed: {e}")
        return {}
