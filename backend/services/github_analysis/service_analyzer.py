import re

SERVICE_PATTERNS = {
    "OpenAI": [r"openai", r"OPENAI_API_KEY", r"gpt-3", r"gpt-4"],
    "Gemini": [r"gemini", r"GEMINI_API_KEY", r"google.generativeai"],
    "Anthropic": [r"anthropic", r"ANTHROPIC_API_KEY", r"claude"],
    "OpenRouter": [r"openrouter", r"OPENROUTER"],
    "Firebase": [r"firebase", r"FIREBASE", r"firebase-admin"],
    "Supabase": [r"supabase", r"SUPABASE"],
    "AWS": [r"\baws\b", r"aws-sdk", r"AWS_ACCESS_KEY", r"boto3", r"amazon"],
    "Azure": [r"\bazure\b", r"AZURE_", r"azure-sdk"],
    "GCP": [r"google-cloud", r"GCP_", r"GOOGLE_APPLICATION_CREDENTIALS"],
    "Cloudinary": [r"cloudinary", r"CLOUDINARY"],
    "Stripe": [r"stripe", r"STRIPE"],
    "Twilio": [r"twilio", r"TWILIO"],
    "Pinecone": [r"pinecone", r"PINECONE"],
    "Redis": [r"redis", r"REDIS_URL"],
    "RabbitMQ": [r"rabbitmq", r"amqp"],
    "Kafka": [r"kafka", r"confluent"],
    "MongoDB Atlas": [r"mongodb\+srv", r"MONGODB_URI"],
    "SendGrid": [r"sendgrid", r"SENDGRID"],
    "Auth0": [r"auth0", r"AUTH0"],
    "Clerk": [r"clerk", r"CLERK"],
    "Vercel": [r"vercel", r"VERCEL"],
    "Netlify": [r"netlify", r"NETLIFY"],
    "Railway": [r"railway", r"RAILWAY"],
    "Render": [r"render\.com", r"RENDER"],
}


def analyze_services(tree: list, dependencies: dict, readme: str) -> dict:
    detected = []
    all_text_parts = []

    for item in tree or []:
        path = item.get("path", "")
        fname = path.split("/")[-1].lower()
        if any(p in fname for p in (".env", "config", "settings", "secrets", "credentials")):
            all_text_parts.append(fname)

    all_deps = []
    for cat in dependencies.values():
        if isinstance(cat, list):
            all_deps.extend(cat)

    readme_lower = readme.lower() if readme else ""
    dep_text = " ".join(all_deps).lower()
    combined = f"{readme_lower} {dep_text} {' '.join(all_text_parts)}"

    for service, patterns in SERVICE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                if service not in detected:
                    detected.append(service)
                break

    return {
        "detected_services": detected[:15],
        "has_external_integrations": len(detected) > 0,
    }
