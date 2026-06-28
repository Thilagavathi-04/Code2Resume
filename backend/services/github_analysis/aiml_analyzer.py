import re
from typing import Any, Dict, List


MODEL_EXTENSIONS = {".pt", ".pth", ".onnx", ".keras", ".h5", ".ckpt", ".safetensors", ".pkl", ".joblib"}

AI_LIBRARIES = {
    "torch": "PyTorch",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "opencv": "OpenCV",
    "cv2": "OpenCV",
    "ultralytics": "Ultralytics",
    "transformers": "Transformers",
    "huggingface-hub": "Hugging Face",
    "sentence-transformers": "SentenceTransformers",
    "langchain": "LangChain",
    "langchain-core": "LangChain",
    "langchain-community": "LangChain",
    "langchain-openai": "LangChain",
    "llama-index": "LlamaIndex",
    "llama-index-core": "LlamaIndex",
    "faiss-cpu": "FAISS",
    "faiss-gpu": "FAISS",
    "qdrant-client": "Qdrant",
    "chromadb": "ChromaDB",
    "neo4j": "Neo4j",
    "pinecone-client": "Pinecone",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "google-generativeai": "Gemini",
    "ollama": "Ollama",
    "vllm": "vLLM",
    "llama-cpp-python": "llama.cpp",
    "nltk": "NLTK",
    "spacy": "spaCy",
    "gensim": "Gensim",
    "xgboost": "XGBoost",
    "lightgbm": "LightGBM",
    "catboost": "CatBoost",
    "diffusers": "Diffusers",
    "accelerate": "Accelerate",
    "peft": "PEFT",
    "bitsandbytes": "BitsAndBytes",
    "pillow": "Pillow",
    "imageio": "ImageIO",
    "scikit-image": "scikit-image",
}

CAPABILITY_KEYWORDS = {
    "Vision": ["opencv", "cv2", "image", "vision", "yolo", "object detection", "segmentation", "ocr", "tesseract"],
    "NLP": ["nlp", "nltk", "spacy", "tokenization", "text classification", "sentiment", "named entity", "summarization"],
    "LLM": ["llm", "large language", "openai", "gpt", "claude", "gemini", "ollama", "llama", "chat", "instruction"],
    "RAG": ["rag", "retrieval augmented", "langchain", "llama-index", "vector store", "embedding", "chroma", "faiss", "pinecone", "qdrant"],
    "Object Detection": ["yolo", "object detection", "ssd", "faster rcnn", "mask rcnn", "detection"],
    "Classification": ["classification", "classifier", "categor", "label"],
    "Segmentation": ["segmentation", "semantic", "instance", "panoptic"],
    "OCR": ["ocr", "tesseract", "optical character", "text extraction"],
    "Speech": ["speech", "voice", "audio", "whisper", "tts", "asr"],
    "Chatbot": ["chatbot", "chat", "conversation", "dialogue", "assistant"],
    "Agentic AI": ["agent", "agentic", "autonomous", "tool use", "function calling", "reasoning"],
    "Recommendation System": ["recommend", "collaborative filtering", "content-based", "suggestion"],
    "Time Series": ["time series", "forecast", "arima", "lstm", "prophet"],
    "Generative AI": ["generative", "diffusion", "stable diffusion", "dall-e", "midjourney", "gan"],
}


def analyze_aiml(tree: list, dependencies: dict, readme: str, tech_stack: dict) -> dict:
    model_files = []
    for item in tree or []:
        path = item.get("path", "")
        for ext in MODEL_EXTENSIONS:
            if path.lower().endswith(ext):
                model_files.append(path)
                break

    detected_libraries = []
    all_deps = (
        dependencies.get("ai_ml", [])
        + dependencies.get("backend", [])
        + dependencies.get("utilities", [])
    )
    for dep in all_deps:
        dep_lower = dep.lower().strip()
        for pattern, name in AI_LIBRARIES.items():
            if dep_lower == pattern or dep_lower.replace("-", "") == pattern.replace("-", ""):
                if name not in detected_libraries:
                    detected_libraries.append(name)

    all_tech = []
    for cat in tech_stack.values():
        if isinstance(cat, list):
            all_tech.extend(cat)
    for tech in all_tech:
        tech_lower = tech.lower()
        for pattern, name in AI_LIBRARIES.items():
            if tech_lower == pattern or tech_lower.replace(" ", "") == pattern.replace(" ", "").lower():
                if name not in detected_libraries:
                    detected_libraries.append(name)

    text = readme.lower() if readme else ""
    for pattern, name in AI_LIBRARIES.items():
        if pattern in text and name not in detected_libraries:
            detected_libraries.append(name)

    capabilities = []
    all_text = f"{readme or ''} {' '.join(all_tech)} {' '.join(all_deps)}".lower()
    for capability, keywords in CAPABILITY_KEYWORDS.items():
        if any(kw in all_text for kw in keywords):
            capabilities.append(capability)

    is_ai_project = len(detected_libraries) > 0 or len(model_files) > 0 or any(
        t.lower() in ("ai", "ml", "machine learning", "deep learning")
        for t in all_tech
    )

    return {
        "is_ai_project": is_ai_project,
        "model_files": model_files[:20],
        "detected_libraries": detected_libraries[:15],
        "capabilities": capabilities[:10],
    }
