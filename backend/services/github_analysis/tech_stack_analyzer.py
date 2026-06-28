import re
from typing import Any, Dict, List


README_FRAMEWORKS = {
    "React": r"\b(react|jsx|tsx)\b",
    "Vue.js": r"\b(vue|vuejs|vue\.js|nuxt)\b",
    "Angular": r"\bangular\b",
    "Svelte": r"\bsvelte\b",
    "Next.js": r"\b(next\.?js|nextjs)\b",
    "Nuxt": r"\bnuxt\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "FastAPI": r"\bfastapi\b",
    "Express": r"\bexpress\.?js\b",
    "Spring": r"\bspring\b",
    "Laravel": r"\blaravel\b",
    "Rails": r"\bruby on rails\b|\brails\b",
    "TensorFlow": r"\btensorflow\b",
    "PyTorch": r"\bpytorch\b",
    "MongoDB": r"\bmongodb\b",
    "PostgreSQL": r"\bpostgresql\b|\bpostgres\b",
    "MySQL": r"\bmysql\b",
    "Redis": r"\bredis\b",
    "AWS": r"\b(aws|amazon web services)\b",
    "Azure": r"\bazure\b",
    "GCP": r"\b(gcp|google cloud)\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "GraphQL": r"\bgraphql\b",
    "REST API": r"\brest\s*api\b|\brestful\b",
    "gRPC": r"\bgrpc\b",
    "WebSockets": r"\bwebsocket\b",
    "Vite": r"\bvite\b",
    "Webpack": r"\bwebpack\b",
    "Tailwind": r"\btailwind\b",
    "TypeScript": r"\btypescript\b",
    "Rust": r"\brust\b",
    "Go": r"\bgolang\b|\bgo\b",
    "Kafka": r"\bkafka\b",
    "RabbitMQ": r"\brabbitmq\b",
    "Elasticsearch": r"\belasticsearch\b",
    "Prometheus": r"\bprometheus\b",
    "Grafana": r"\bgrafana\b",
    "Nginx": r"\bnginx\b",
    "Firebase": r"\bfirebase\b",
    "Supabase": r"\bsupabase\b",
    "Stripe": r"\bstripe\b",
    "OpenAI": r"\bopenai\b",
    "LangChain": r"\blangchain\b",
    "LlamaIndex": r"\bllama[-\s]?index\b",
    "ChromaDB": r"\bchromadb\b|\bchroma\b",
    "FAISS": r"\bfaiss\b",
    "Pinecone": r"\bpinecone\b",
    "Neo4j": r"\bneo4j\b",
    "Hugging Face": r"\bhugging\s*face\b|\bhuggingface\b",
}


def analyze_tech_stack(
    languages: dict,
    readme: str,
    structure: dict,
    dependencies: dict,
    tree: list,
) -> dict:
    frontend = list(set(dependencies.get("frontend", [])))
    backend = list(set(dependencies.get("backend", [])))
    database = list(set(dependencies.get("database", [])))
    ai_ml = list(set(dependencies.get("ai_ml", [])))
    devops = list(set(dependencies.get("devops", [])))
    testing = list(set(dependencies.get("testing", [])))
    utilities = list(set(dependencies.get("utilities", [])))
    cloud = []
    auth = []
    api = []
    message_queue = []
    vector_db = []

    if languages:
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
        for lang, _ in sorted_langs[:5]:
            if lang not in frontend and lang not in backend:
                backend.append(lang)

    if structure.get("has_dockerfile"):
        devops.append("Docker")
    if structure.get("has_package_json"):
        if "Node.js" not in backend:
            backend.append("Node.js")

    readme_lower = readme.lower() if readme else ""
    for tech, pattern in README_FRAMEWORKS.items():
        if re.search(pattern, readme_lower, re.IGNORECASE):
            tech_lower = tech.lower()
            if tech_lower in ("docker", "kubernetes"):
                if tech not in devops:
                    devops.append(tech)
            elif tech_lower in ("aws", "azure", "gcp", "firebase", "supabase"):
                if tech not in cloud:
                    cloud.append(tech)
            elif tech_lower in ("redis", "mongodb", "postgresql", "postgres", "mysql", "elasticsearch"):
                if tech not in database:
                    database.append(tech)
            elif tech_lower in ("openai", "langchain", "llama-index", "tensorflow", "pytorch", "hugging face", "chromadb", "faiss", "pinecone"):
                if tech_lower in ("chromadb", "faiss", "pinecone"):
                    if tech not in vector_db:
                        vector_db.append(tech)
                elif tech_lower in ("kafka", "rabbitmq"):
                    if tech not in message_queue:
                        message_queue.append(tech)
                else:
                    if tech not in ai_ml:
                        ai_ml.append(tech)
            elif tech_lower in ("react", "vue.js", "angular", "svelte", "next.js", "nuxt", "tailwind"):
                if tech not in frontend:
                    frontend.append(tech)
            elif tech_lower in ("django", "flask", "fastapi", "express", "spring", "laravel", "rails"):
                if tech not in backend:
                    backend.append(tech)
            elif tech_lower in ("graphql", "rest api", "grpc", "websockets"):
                if tech not in api:
                    api.append(tech)
            else:
                if tech not in utilities:
                    utilities.append(tech)

    for item in tree or []:
        path = item.get("path", "")
        fname = path.split("/")[-1].lower()
        if "auth" in fname or "jwt" in fname or "oauth" in fname or "session" in fname:
            if "Authentication" not in auth:
                auth.append("Authentication")

    return {
        "frontend": frontend[:15],
        "backend": backend[:15],
        "database": database[:10],
        "ai_ml": ai_ml[:10],
        "cloud": cloud[:5],
        "devops": devops[:5],
        "authentication": auth[:5],
        "api": api[:5],
        "testing": testing[:10],
        "deployment": devops[:5],
        "utilities": utilities[:10],
        "vector_db": vector_db[:5],
        "message_queue": message_queue[:5],
    }
