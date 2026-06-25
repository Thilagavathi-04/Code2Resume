CATEGORIES = {
    "Machine Learning": {
        "tech_keywords": [
            "scikit-learn", "sklearn", "tensorflow", "tf", "pytorch", "keras",
            "xgboost", "lightgbm", "catboost", "mlpack", "shogun",
            "ml", "machine learning", "model", "predict", "regression",
            "classification", "clustering", "training", "inference",
            "supervised", "unsupervised", "reinforcement learning",
            "neural network", "deep learning", "gradient", "decision tree",
            "random forest", "svm", "naive bayes", "knn", "k-means",
            "gAN", "GAN", "autoencoder", "transformer model",
        ],
        "description_keywords": [
            "machine learning", "ml model", "prediction", "predictive",
            "train", "trained", "accuracy", "loss", "epoch", "dataset",
            "feature engineering", "model training", "data pipeline",
        ],
        "weight": 1.0,
    },
    "Deep Learning": {
        "tech_keywords": [
            "tensorflow", "pytorch", "keras", "caffe", "theano", "mxnet",
            "deep learning", "cnn", "rnn", "lstm", "gru", "GAN", "vae",
            "autoencoder", "neural network", "backpropagation",
            "convolutional", "recurrent", "attention mechanism",
            "resnet", "vgg", "inception", "mobilenet", "yolo",
            "bert", "gpt", "transformer", "huggingface", "hugging face",
        ],
        "description_keywords": [
            "deep learning", "neural network", "cnn", "rnn", "lstm",
            "image recognition", "object detection", "segmentation",
        ],
        "weight": 0.9,
    },
    "Computer Vision": {
        "tech_keywords": [
            "opencv", "cv2", "pillow", "pil", "imageio", "scikit-image",
            "yolo", "yolov5", "yolov8", "ssd", "faster rcnn", "mask rcnn",
            "image classification", "object detection", "segmentation",
            "face detection", "face recognition", "ocr", "tesseract",
            "image processing", "video processing", "camera",
        ],
        "description_keywords": [
            "image", "video", "camera", "detection", "recognition",
            "segmentation", "vision", "visual", "face", "object",
        ],
        "weight": 1.0,
    },
    "NLP": {
        "tech_keywords": [
            "nltk", "spacy", "gensim", "transformers", "bert", "gpt",
            "llm", "langchain", "openai", "huggingface", "tokenization",
            "text classification", "sentiment analysis", "named entity",
            "ner", "text summarization", "machine translation",
            "chatbot", "language model", "word2vec", "fasttext",
            "tfidf", "bag of words", "word embedding",
        ],
        "description_keywords": [
            "natural language", "text", "nlp", "language", "sentiment",
            "summarization", "translation", "chatbot", "conversation",
        ],
        "weight": 1.0,
    },
    "Full Stack": {
        "tech_keywords": [
            "react", "vue", "angular", "nextjs", "next.js", "nuxt",
            "django", "flask", "fastapi", "express", "node.js", "nodejs",
            "postgres", "postgresql", "mysql", "mongodb", "redis",
            "graphql", "rest api", "restapi", "tailwind", "bootstrap",
            "html", "css", "javascript", "typescript",
        ],
        "description_keywords": [
            "full stack", "fullstack", "full-stack", "web application",
            "web app", "website", "saas", "dashboard", "portal",
        ],
        "weight": 0.6,
    },
    "Frontend": {
        "tech_keywords": [
            "react", "vue", "angular", "svelte", "nextjs", "nuxt",
            "tailwind", "bootstrap", "material-ui", "mui", "chakra",
            "html", "css", "scss", "sass", "javascript", "typescript",
            "redux", "zustand", "vuex", "pinia", "webpack", "vite",
        ],
        "description_keywords": [
            "frontend", "front-end", "ui", "ux", "user interface",
            "responsive", "animation", "component", "landing page",
        ],
        "weight": 0.7,
    },
    "Backend": {
        "tech_keywords": [
            "django", "flask", "fastapi", "express", "node.js", "nodejs",
            "spring", "springboot", "laravel", "rails", "gin", "fiber",
            "postgres", "postgresql", "mysql", "mongodb", "redis",
            "graphql", "grpc", "rest api", "restapi", "websocket",
            "celery", "rabbitmq", "kafka",
        ],
        "description_keywords": [
            "backend", "back-end", "api", "server", "microservice",
            "database", "authentication", "authorization", "middleware",
        ],
        "weight": 0.7,
    },
    "Mobile App": {
        "tech_keywords": [
            "flutter", "dart", "react native", "kotlin", "swift",
            "android", "ios", "xamarin", "ionic", "capacitor",
            "jetpack compose", "swiftui", "uikit",
        ],
        "description_keywords": [
            "mobile", "android", "ios", "app", "phone", "tablet",
            "cross-platform", "flutter", "react native",
        ],
        "weight": 1.0,
    },
    "Data Science": {
        "tech_keywords": [
            "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
            "jupyter", "notebook", "data analysis", "data visualization",
            "statistical", "statistics", "EDA", "exploratory",
            "data cleaning", "data wrangling", "feature engineering",
        ],
        "description_keywords": [
            "data science", "data analysis", "analytics", "visualization",
            "dashboard", "report", "insight", "trend", "statistical",
        ],
        "weight": 0.8,
    },
    "Cybersecurity": {
        "tech_keywords": [
            "security", "penetration", "vulnerability", "exploit",
            "firewall", "encryption", "cryptography", "hashing",
            "nmap", "wireshark", "metasploit", "burp", "owasp",
            "intrusion", "malware", "phishing", "forensics",
        ],
        "description_keywords": [
            "security", "cybersecurity", "penetration", "vulnerability",
            "encryption", "firewall", "attack", "defense", "audit",
        ],
        "weight": 1.0,
    },
    "DevOps": {
        "tech_keywords": [
            "docker", "kubernetes", "k8s", "jenkins", "gitlab ci",
            "github actions", "terraform", "ansible", "puppet", "chef",
            "ci/cd", "cicd", "pipeline", "infrastructure", "nginx",
            "apache", "linux", "bash", "shell", "monitoring", "prometheus",
            "grafana", "elk", "terraform", "pulumi",
        ],
        "description_keywords": [
            "devops", "deployment", "ci/cd", "pipeline", "infrastructure",
            "container", "orchestration", "automation", "monitoring",
        ],
        "weight": 1.0,
    },
    "Cloud Computing": {
        "tech_keywords": [
            "aws", "amazon web services", "gcp", "google cloud",
            "azure", "cloud", "lambda", "ec2", "s3", "dynamodb",
            "cloud functions", "cloud run", "app engine", "heroku",
            "vercel", "netlify", "firebase", "supabase",
        ],
        "description_keywords": [
            "cloud", "aws", "gcp", "azure", "serverless", "saas",
            "paas", "iaas", "hosting", "deployment",
        ],
        "weight": 0.8,
    },
    "IoT": {
        "tech_keywords": [
            "arduino", "raspberry pi", "esp32", "esp8266", "iot",
            "mqtt", "zigbee", "bluetooth le", "ble", "sensors",
            "actuator", "embedded", "microcontroller", "firmware",
        ],
        "description_keywords": [
            "iot", "internet of things", "sensor", "embedded",
            "microcontroller", "arduino", "raspberry", "smart home",
        ],
        "weight": 1.0,
    },
    "Blockchain": {
        "tech_keywords": [
            "ethereum", "solidity", "web3", "web3js", "ethers",
            "smart contract", "defi", "nft", "blockchain",
            "hyperledger", "ipfs", "metamask", "truffle", "hardhat",
        ],
        "description_keywords": [
            "blockchain", "web3", "defi", "nft", "smart contract",
            "decentralized", "crypto", "token",
        ],
        "weight": 1.0,
    },
}

DIFFICULTY_KEYWORDS = {
    "beginner": [
        "todo", "calculator", "weather app", "blog", "portfolio",
        "landing page", "crud", "hello world", "tutorial", "learning",
        "basic", "simple", "starter", "template", "boilerplate",
    ],
    "intermediate": [
        "rest api", "authentication", "dashboard", "e-commerce",
        "chat", "real-time", "websocket", "dashboard", "admin",
        "cms", "social", "booking", "payment",
    ],
    "advanced": [
        "distributed", "microservice", "machine learning", "deep learning",
        "compiler", "operating system", "database engine", "blockchain",
        "real-time", "scalable", "high availability", "load balancer",
        "kubernetes", "terraform", "ci/cd pipeline",
    ],
}


def classify_project(name: str, description: str, tech_stack: list, readme: str = "") -> dict:
    text = f"{name} {description} {' '.join(tech_stack)} {readme}".lower()
    scores = {}

    for category, config in CATEGORIES.items():
        score = 0
        matched_techs = []
        matched_desc = []

        for keyword in config["tech_keywords"]:
            if keyword.lower() in text:
                score += 2
                matched_techs.append(keyword)

        for keyword in config["description_keywords"]:
            if keyword.lower() in text:
                score += 1
                matched_desc.append(keyword)

        if score > 0:
            scores[category] = {
                "score": score * config["weight"],
                "matched_techs": matched_techs,
                "matched_desc": matched_desc,
            }

    if not scores:
        return {
            "category": "Other",
            "subcategories": [],
            "confidence": 0,
            "matched_keywords": [],
        }

    sorted_cats = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    primary = sorted_cats[0]
    subcategories = [cat for cat, _ in sorted_cats[1:3]]

    total_possible = len(CATEGORIES[primary[0]]["tech_keywords"]) * 2 + len(CATEGORIES[primary[0]]["description_keywords"])
    confidence = min(1.0, primary[1]["score"] / max(total_possible * 0.3, 1))

    return {
        "category": primary[0],
        "subcategories": subcategories,
        "confidence": round(confidence, 2),
        "matched_keywords": primary[1]["matched_techs"] + primary[1]["matched_desc"],
    }


def detect_difficulty(name: str, description: str, tech_stack: list, readme: str = "") -> str:
    text = f"{name} {description} {' '.join(tech_stack)} {readme}".lower()
    scores = {"beginner": 0, "intermediate": 0, "advanced": 0}

    for level, keywords in DIFFICULTY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[level] += 1

    tech_count = len(tech_stack)
    if tech_count >= 6:
        scores["advanced"] += 2
    elif tech_count >= 3:
        scores["intermediate"] += 1
    else:
        scores["beginner"] += 1

    if readme and len(readme) > 1000:
        scores["advanced"] += 1

    return max(scores, key=scores.get)


def extract_tags(name: str, description: str, tech_stack: list) -> list[str]:
    text = f"{name} {description}".lower()
    tags = set()

    tag_patterns = {
        "api": r"\bapi\b",
        "web": r"\bweb\b",
        "mobile": r"\bmobile\b",
        "desktop": r"\bdesktop\b",
        "cli": r"\bcli\b",
        "library": r"\blibrary\b",
        "tool": r"\btool\b",
        "automation": r"\bautomat",
        "real-time": r"\breal.?time\b",
        "open-source": r"\bopen.?source\b",
        "tutorial": r"\btutorial\b",
        "portfolio": r"\bportfolio\b",
        "hackathon": r"\bhackathon\b",
        "production": r"\bproduction\b",
    }

    for tag, pattern in tag_patterns.items():
        if re.search(pattern, text):
            tags.add(tag)

    for tech in tech_stack:
        tags.add(tech.lower())

    return sorted(tags)[:15]


def compute_scores(name: str, description: str, tech_stack: list, readme: str = "", stars: int = 0) -> dict:
    text = f"{name} {description} {' '.join(tech_stack)} {readme}".lower()

    completeness = 0
    if description and len(description) > 20:
        completeness += 2
    if readme and len(readme) > 100:
        completeness += 3
    if tech_stack:
        completeness += min(len(tech_stack), 3)
    if len(readme) > 500:
        completeness += 2
    relevance_score = min(10, completeness)

    popularity = min(10, stars)
    if "popular" in text or "download" in text or "star" in text:
        popularity += 2
    popularity_score = min(10, popularity)

    complexity = 0
    complex_techs = {"kubernetes", "terraform", "tensorflow", "pytorch", "blockchain",
                     "ethereum", "solidity", "grpc", "kafka", "elasticsearch",
                     "compiler", "distributed", "microservice", "cuda", "webgl"}
    for tech in tech_stack:
        if tech.lower() in complex_techs:
            complexity += 2
    if tech_stack and len(tech_stack) > 5:
        complexity += 2
    if readme and len(readme) > 1000:
        complexity += 1
    complexity_score = min(10, complexity)

    final_score = (relevance_score * 0.5) + (popularity_score * 0.3) + (complexity_score * 0.2)

    return {
        "relevance_score": relevance_score,
        "popularity_score": popularity_score,
        "complexity_score": complexity_score,
        "final_score": round(final_score, 2),
    }


import re
