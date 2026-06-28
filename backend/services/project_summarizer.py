def generate_project_summary(repo_data: dict) -> dict:
    semantic = repo_data.get("semantic_analysis", {})
    tech_stack = repo_data.get("tech_stack", {})
    classification = repo_data.get("classification", {})

    all_tech = []
    if isinstance(tech_stack, dict):
        for v in tech_stack.values():
            if isinstance(v, list):
                all_tech.extend(v)

    summary = semantic.get("executive_summary", "")
    if not summary:
        desc = repo_data.get("description", "")
        top_techs = ", ".join(all_tech[:4]) if all_tech else "modern technologies"
        cat = classification.get("primary", classification.get("category", "Software"))
        summary = f"{cat} project: {desc}. Built with {top_techs}."

    bullet_points = semantic.get("resume_bullet_points", [])
    ats_keywords = semantic.get("ats_keywords", [])

    kg_summary_parts = []
    if isinstance(tech_stack, dict):
        for cat, items in tech_stack.items():
            if isinstance(items, list) and items:
                kg_summary_parts.append(f"{cat}: {', '.join(items[:5])}")

    return {
        "summary": summary,
        "bullet_points": bullet_points[:4],
        "ats_keywords": ats_keywords[:10],
        "resume_description": semantic.get("resume_description", ""),
        "portfolio_description": semantic.get("portfolio_description", ""),
        "domain": semantic.get("domain", classification.get("primary", "Other")),
        "industry": semantic.get("industry", ""),
        "key_features": semantic.get("key_features", []),
        "technical_challenges": semantic.get("technical_challenges", []),
        "suggested_skills": semantic.get("suggested_skills", []),
        "kg_summary": " | ".join(kg_summary_parts),
        "tech_stack_flat": all_tech[:15],
    }
