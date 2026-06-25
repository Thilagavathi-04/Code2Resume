import re
from services.project_classifier import CATEGORIES

CATEGORY_ALIASES = {}
for cat in CATEGORIES:
    CATEGORY_ALIASES[cat.lower()] = cat

ALIAS_OVERRIDES = {
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Machine Learning",
    "artificial intelligence": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "llm": "NLP",
    "fullstack": "Full Stack",
    "full stack": "Full Stack",
    "full-stack": "Full Stack",
    "frontend": "Frontend",
    "front-end": "Frontend",
    "front end": "Frontend",
    "ui": "Frontend",
    "ux": "Frontend",
    "backend": "Backend",
    "back-end": "Backend",
    "back end": "Backend",
    "api": "Backend",
    "server": "Backend",
    "mobile": "Mobile App",
    "android": "Mobile App",
    "ios": "Mobile App",
    "flutter": "Mobile App",
    "react native": "Mobile App",
    "data science": "Data Science",
    "data analysis": "Data Science",
    "analytics": "Data Science",
    "security": "Cybersecurity",
    "cybersecurity": "Cybersecurity",
    "penetration": "Cybersecurity",
    "devops": "DevOps",
    "ci/cd": "DevOps",
    "cloud": "Cloud Computing",
    "aws": "Cloud Computing",
    "gcp": "Cloud Computing",
    "azure": "Cloud Computing",
    "iot": "IoT",
    "internet of things": "IoT",
    "arduino": "IoT",
    "blockchain": "Blockchain",
    "web3": "Blockchain",
    "defi": "Blockchain",
}

TECH_SEARCH_PATTERNS = [
    r"(?:best|top|good|great)\s+(.+?)\s+(?:project|app|tool|solution)",
    r"(?:show|list|find|get)\s+(.+?)\s+(?:project|app|tool|solution)",
    r"(?:project|app|tool|solution)\s+(?:using|with|in|built)\s+(.+)",
    r"(?:using|with|in|built)\s+(.+?)\s+(?:project|app|tool|solution)",
    r"(.+?)\s+project",
]

DIFFICULTY_PATTERNS = {
    "beginner": r"\b(beginner|easy|simple|basic|starter|learning|tutorial)\b",
    "intermediate": r"\b(intermediate|medium|moderate)\b",
    "advanced": r"\b(advanced|complex|difficult|hard|expert|senior)\b",
}

CATEGORY_SEARCH_PATTERNS = [
    r"(?:list|show|find|get|search|what are|tell me about|all)\s+(?:my\s+)?(.+?)(?:\s+project|\s+app|\s+s|\s*$)",
    r"(?:my\s+)?(.+?)(?:\s+project|\s+app|\s+s)\b",
]


def detect_intent(query: str) -> dict:
    q = query.lower().strip()
    result = {
        "intent": "general",
        "category": None,
        "technology": None,
        "difficulty": None,
        "is_list_request": False,
        "is_best_request": False,
        "is_count_request": False,
        "search_terms": [],
    }

    list_words = ["list", "show", "find", "search", "get", "display", "give me", "what are", "tell me"]
    result["is_list_request"] = any(w in q for w in list_words) or "all " in q

    best_words = ["best", "top", "greatest", "most impressive", "favorite", "strongest"]
    result["is_best_request"] = any(w in q for w in best_words)

    count_words = ["how many", "count", "number of"]
    result["is_count_request"] = any(w in q for w in count_words)

    for level, pattern in DIFFICULTY_PATTERNS.items():
        if re.search(pattern, q):
            result["difficulty"] = level
            result["intent"] = "difficulty_search"
            break

    for alias, category in ALIAS_OVERRIDES.items():
        if alias in q:
            result["category"] = category
            result["intent"] = "category_search"
            break

    if not result["category"]:
        for alias, category in CATEGORY_ALIASES.items():
            if alias in q:
                result["category"] = category
                result["intent"] = "category_search"
                break

    if not result["category"]:
        for pattern in CATEGORY_SEARCH_PATTERNS:
            match = re.search(pattern, q)
            if match:
                term = match.group(1).strip()
                if term in ALIAS_OVERRIDES:
                    result["category"] = ALIAS_OVERRIDES[term]
                    result["intent"] = "category_search"
                    break

    tech_keywords = [
        "react", "vue", "angular", "svelte", "nextjs", "next.js",
        "django", "flask", "fastapi", "express", "node.js",
        "tensorflow", "pytorch", "keras", "scikit-learn",
        "docker", "kubernetes", "terraform",
        "postgresql", "mysql", "mongodb", "redis",
        "python", "javascript", "typescript", "go", "rust", "java",
        "flutter", "react native",
        "arduino", "raspberry pi",
        "solidity", "ethereum",
    ]
    for tech in tech_keywords:
        if tech in q:
            result["technology"] = tech
            if not result["intent"] == "category_search":
                result["intent"] = "technology_search"
            break

    if result["is_best_request"] and result["category"]:
        result["intent"] = "best_category_search"
    elif result["is_best_request"]:
        result["intent"] = "best_search"

    words = q.split()
    stop_words = {
        "list", "show", "find", "get", "my", "me", "all", "the", "a", "an",
        "project", "projects", "app", "apps", "tool", "tools", "solution",
        "best", "top", "good", "great", "what", "are", "tell", "about",
        "using", "with", "in", "built", "and", "or", "for", "of", "is",
    }
    search_terms = [w for w in words if w not in stop_words and len(w) > 2]
    result["search_terms"] = search_terms

    if result["intent"] == "general":
        if result["is_list_request"]:
            result["intent"] = "list_all"
        elif result["is_count_request"]:
            result["intent"] = "count"

    return result
