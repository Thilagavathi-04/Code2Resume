import re

DEPLOYMENT_TECH = {
    "Docker": [r"Dockerfile", r"docker-compose"],
    "Docker Compose": [r"docker-compose\.ya?ml"],
    "Kubernetes": [r"\.yaml$", r"k8s", r"helm", r"charts"],
    "Vercel": [r"vercel\.json", r"vercel"],
    "Netlify": [r"netlify\.toml", r"_redirects"],
    "Railway": [r"railway\.json", r"railway\.toml"],
    "Render": [r"render\.yaml", r"render\.json"],
    "Fly.io": [r"fly\.toml"],
    "Gunicorn": [r"gunicorn", r"gunicorn\.conf"],
    "Uvicorn": [r"uvicorn"],
    "Nginx": [r"nginx", r"nginx\.conf"],
    "Apache": [r"\.htaccess", r"httpd\.conf"],
    "GitHub Pages": [r"gh-pages", r"\.nojekyll"],
    "AWS": [r"aws", r"cloudformation", r"sam\.yaml", r"serverless\.yml"],
    "Azure": [r"azure-pipelines", r"ARM template"],
    "Google Cloud": [r"app\.yaml", r"cloudbuild"],
    "PM2": [r"ecosystem\.config", r"pm2"],
    "systemd": [r"\.service$"],
    "Procfile": [r"Procfile"],
}


def analyze_deployment(tree: list, dependencies: dict, readme: str) -> dict:
    detected = []
    all_paths = [item.get("path", "") for item in tree or []]
    all_text = " ".join(all_paths).lower()

    readme_lower = readme.lower() if readme else ""
    combined = f"{all_text} {readme_lower}"

    all_deps = []
    for cat in dependencies.values():
        if isinstance(cat, list):
            all_deps.extend(cat)
    dep_text = " ".join(all_deps).lower()
    combined = f"{combined} {dep_text}"

    for tech, patterns in DEPLOYMENT_TECH.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                if tech not in detected:
                    detected.append(tech)
                break

    has_containerization = any(t in ("Docker", "Docker Compose", "Kubernetes") for t in detected)
    has_cloud = any(t in ("AWS", "Azure", "Google Cloud", "Vercel", "Netlify", "Railway", "Render", "Fly.io") for t in detected)
    has_server = any(t in ("Gunicorn", "Uvicorn", "Nginx", "Apache", "PM2") for t in detected)

    readiness = "none"
    if has_containerization and has_cloud:
        readiness = "high"
    elif has_containerization or has_cloud:
        readiness = "medium"
    elif has_server:
        readiness = "low"

    return {
        "detected_technologies": detected[:10],
        "has_containerization": has_containerization,
        "has_cloud_deployment": has_cloud,
        "has_server_config": has_server,
        "readiness_level": readiness,
    }
