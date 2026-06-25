from services.project_classifier import classify_project, detect_difficulty, extract_tags, compute_scores
from services.intent_detector import detect_intent


def search_projects(repos: list, query: str) -> dict:
    intent = detect_intent(query)

    enriched = []
    for repo in repos:
        name = repo.get("name", "")
        description = repo.get("description", "") or repo.get("what_it_does", "")
        tech_stack = repo.get("tech_stack", [])
        if isinstance(tech_stack, str):
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]
        readme = repo.get("readme", "")
        stars = repo.get("stars", 0)

        classification = classify_project(name, description, tech_stack, readme)
        difficulty = detect_difficulty(name, description, tech_stack, readme)
        tags = extract_tags(name, description, tech_stack)
        scores = compute_scores(name, description, tech_stack, readme, stars)

        enriched.append({
            **repo,
            "category": classification["category"],
            "subcategories": classification["subcategories"],
            "classification_confidence": classification["confidence"],
            "matched_keywords": classification["matched_keywords"],
            "difficulty": difficulty,
            "tags": tags,
            "relevance_score": scores["relevance_score"],
            "popularity_score": scores["popularity_score"],
            "complexity_score": scores["complexity_score"],
            "final_score": scores["final_score"],
        })

    filtered = apply_filters(enriched, intent)
    ranked = rank_projects(filtered, intent)

    return {
        "intent": intent,
        "total_found": len(ranked),
        "projects": ranked,
    }


def apply_filters(projects: list, intent: dict) -> list:
    result = projects

    if intent["category"]:
        category_lower = intent["category"].lower()
        result = [
            p for p in result
            if p["category"].lower() == category_lower
            or any(sc.lower() == category_lower for sc in p.get("subcategories", []))
        ]

    if intent["difficulty"]:
        result = [p for p in result if p["difficulty"] == intent["difficulty"]]

    if intent["technology"]:
        tech_lower = intent["technology"].lower()
        result = [
            p for p in result
            if any(tech_lower in t.lower() for t in p.get("tags", []))
            or any(tech_lower in kw.lower() for kw in p.get("matched_keywords", []))
        ]

    if intent["search_terms"]:
        term_matched = []
        for p in result:
            text = f"{p.get('name', '')} {p.get('description', '')} {' '.join(p.get('tags', []))}".lower()
            if any(term in text for term in intent["search_terms"]):
                term_matched.append(p)
        if term_matched:
            result = term_matched

    return result


def rank_projects(projects: list, intent: dict) -> list:
    if intent["is_best_request"]:
        projects.sort(key=lambda p: p["final_score"], reverse=True)
    elif intent["intent"] == "category_search":
        projects.sort(key=lambda p: (p["final_score"], p["classification_confidence"]), reverse=True)
    elif intent["intent"] == "technology_search":
        projects.sort(key=lambda p: p["relevance_score"], reverse=True)
    else:
        projects.sort(key=lambda p: p["final_score"], reverse=True)

    return projects


def format_response(search_result: dict, query: str) -> str:
    intent = search_result["intent"]
    projects = search_result["projects"]
    total = search_result["total_found"]

    if total == 0:
        return _format_no_results(intent, query)

    category_label = intent.get("category", "")
    difficulty_label = intent.get("difficulty", "")
    tech_label = intent.get("technology", "")

    if intent["intent"] == "count":
        return f"You have **{total}** projects in total."

    header = _build_header(total, category_label, difficulty_label, tech_label, intent)

    grouped = {}
    for p in projects:
        cat = p.get("category", "Other")
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(p)

    body_parts = []
    if len(grouped) > 1 and not intent["category"]:
        for cat, cat_projects in grouped.items():
            body_parts.append(f"\n### {cat} ({len(cat_projects)})")
            for i, p in enumerate(cat_projects, 1):
                body_parts.append(_format_project(p, i))
    else:
        for i, p in enumerate(projects, 1):
            body_parts.append(_format_project(p, i))

    explanation = _build_explanation(intent, total)

    return header + "\n".join(body_parts) + "\n" + explanation


def _build_header(total, category, difficulty, tech, intent):
    parts = [f"Found **{total}** project"]
    if total != 1:
        parts[0] += "s"

    descriptors = []
    if category:
        descriptors.append(category)
    if difficulty:
        descriptors.append(difficulty.capitalize())
    if tech:
        descriptors.append(f"using {tech}")

    if descriptors:
        parts.append(f" matching **{', '.join(descriptors)}**")
    elif intent["is_best_request"]:
        parts.append(" ranked by score")

    parts.append(":\n")
    return "".join(parts)


def _format_project(p, index):
    name = p.get("name", "Unnamed")
    desc = p.get("description", "") or p.get("what_it_does", "")
    if len(desc) > 120:
        desc = desc[:117] + "..."

    category = p.get("category", "")
    difficulty = p.get("difficulty", "")
    score = p.get("final_score", 0)
    techs = p.get("tech_stack", [])
    if isinstance(techs, str):
        techs = [t.strip() for t in techs.split(",") if t.strip()]

    line = f"{index}. **{name}**"
    if category:
        line += f" — `{category}`"
    if difficulty:
        line += f" [{difficulty}]"
    line += f" (Score: {score})"
    if desc:
        line += f"\n   {desc}"
    if techs:
        line += f"\n   Tech: {', '.join(techs[:5])}"
    return line


def _build_explanation(intent, total):
    parts = ["\n---\n*Selection criteria: "]
    reasons = []
    if intent["category"]:
        reasons.append(f"filtered by category ({intent['category']})")
    if intent["difficulty"]:
        reasons.append(f"filtered by difficulty ({intent['difficulty']})")
    if intent["technology"]:
        reasons.append(f"filtered by technology ({intent['technology']})")
    if intent["is_best_request"]:
        reasons.append("ranked by overall score (relevance 50%, popularity 30%, complexity 20%)")
    elif intent["is_list_request"]:
        reasons.append("showing all matching projects")
    if not reasons:
        reasons.append("semantic search match")
    parts.append(", ".join(reasons))
    parts.append("*")
    return "".join(parts)


def _format_no_results(intent, query):
    parts = ["No projects found"]
    if intent["category"]:
        parts.append(f" for category **{intent['category']}**")
    if intent["difficulty"]:
        parts.append(f" with difficulty **{intent['difficulty']}**")
    if intent["technology"]:
        parts.append(f" using **{intent['technology']}**")
    parts.append(".\n\nTry:\n")
    parts.append("- Analyzing more GitHub repositories first\n")
    parts.append("- Using different search terms\n")
    parts.append("- Checking your project categories in the GitHub Analysis page")
    return "".join(parts)
