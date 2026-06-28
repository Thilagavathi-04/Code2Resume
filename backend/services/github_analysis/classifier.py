import re


CATEGORY_DEFINITIONS = {
    "Machine Learning": {
        "indicators": ["machine learning", "ml model", "training", "inference", "dataset", "accuracy", "loss", "epoch"],
        "weight": 1.0,
    },
    "Deep Learning": {
        "indicators": ["deep learning", "neural network", "cnn", "rnn", "lstm", "transformer"],
        "weight": 0.9,
    },
    "Computer Vision": {
        "indicators": ["image", "video", "detection", "recognition", "segmentation", "vision", "opencv"],
        "weight": 1.0,
    },
    "NLP": {
        "indicators": ["nlp", "natural language", "text", "sentiment", "summarization", "translation", "chatbot"],
        "weight": 1.0,
    },
    "LLM Application": {
        "indicators": ["llm", "large language", "openai", "gpt", "claude", "gemini", "langchain", "prompt"],
        "weight": 1.0,
    },
    "RAG Application": {
        "indicators": ["rag", "retrieval augmented", "vector store", "embedding", "knowledge base"],
        "weight": 1.0,
    },
    "Agentic AI": {
        "indicators": ["agent", "agentic", "autonomous", "tool use", "function calling", "reasoning"],
        "weight": 1.0,
    },
    "Full Stack Web Application": {
        "indicators": ["full stack", "fullstack", "full-stack", "web app", "saas", "dashboard"],
        "weight": 0.6,
    },
    "Frontend Application": {
        "indicators": ["frontend", "front-end", "ui", "ux", "landing page", "responsive"],
        "weight": 0.7,
    },
    "Backend Service": {
        "indicators": ["api", "server", "microservice", "backend", "service", "rest", "graphql"],
        "weight": 0.7,
    },
    "Mobile Application": {
        "indicators": ["mobile", "android", "ios", "flutter", "react native"],
        "weight": 1.0,
    },
    "Data Science": {
        "indicators": ["data science", "data analysis", "visualization", "dashboard", "analytics"],
        "weight": 0.8,
    },
    "DevOps Tool": {
        "indicators": ["devops", "ci/cd", "deployment", "infrastructure", "container", "monitoring"],
        "weight": 1.0,
    },
    "Developer Tool": {
        "indicators": ["cli", "tool", "utility", "library", "package", "sdk", "framework"],
        "weight": 0.8,
    },
    "Game": {
        "indicators": ["game", "gaming", "unity", "unreal", "godot"],
        "weight": 1.0,
    },
    "Blockchain": {
        "indicators": ["blockchain", "web3", "defi", "nft", "smart contract", "ethereum", "solidity"],
        "weight": 1.0,
    },
}


def classify_project(name: str, description: str, tech_stack: dict, readme: str) -> dict:
    text = f"{name} {description} {readme}".lower()
    for cat_list in tech_stack.values():
        if isinstance(cat_list, list):
            text += " " + " ".join(cat_list).lower()

    scores = {}
    for category, config in CATEGORY_DEFINITIONS.items():
        score = 0
        matched = []
        for indicator in config["indicators"]:
            if indicator.lower() in text:
                score += 2
                matched.append(indicator)
        if score > 0:
            scores[category] = {
                "score": score * config["weight"],
                "matched": matched,
            }

    if not scores:
        return {
            "primary": "Software Project",
            "secondary": [],
            "confidence": 0.3,
            "matched_keywords": [],
        }

    sorted_cats = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    primary = sorted_cats[0]
    secondary = [cat for cat, _ in sorted_cats[1:4]]

    max_possible = len(CATEGORY_DEFINITIONS[primary[0]]["indicators"]) * 2
    confidence = min(1.0, primary[1]["score"] / max(max_possible * 0.3, 1))

    return {
        "primary": primary[0],
        "secondary": secondary,
        "confidence": round(confidence, 2),
        "matched_keywords": primary[1]["matched"],
    }
