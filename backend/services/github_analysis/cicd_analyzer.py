import re
import json


def analyze_cicd(tree: list, dependencies: dict) -> dict:
    providers = []
    capabilities = []
    config_files = []
    pipeline_count = 0

    all_paths = [item.get("path", "") for item in tree or []]

    for path in all_paths:
        path_lower = path.lower()

        if ".github/workflows/" in path_lower and path_lower.endswith((".yml", ".yaml")):
            if "GitHub Actions" not in providers:
                providers.append("GitHub Actions")
            config_files.append(path)
            pipeline_count += 1

        elif path_lower == ".gitlab-ci.yml":
            if "GitLab CI" not in providers:
                providers.append("GitLab CI")
            config_files.append(path)
            pipeline_count += 1

        elif path_lower == "azure-pipelines.yml":
            if "Azure Pipelines" not in providers:
                providers.append("Azure Pipelines")
            config_files.append(path)
            pipeline_count += 1

        elif ".circleci/config.yml" in path_lower:
            if "CircleCI" not in providers:
                providers.append("CircleCI")
            config_files.append(path)
            pipeline_count += 1

        elif path_lower == "jenkinsfile":
            if "Jenkins" not in providers:
                providers.append("Jenkins")
            config_files.append(path)
            pipeline_count += 1

    readme_indicators = {
        "github actions": "GitHub Actions",
        "gitlab ci": "GitLab CI",
        "azure pipelines": "Azure Pipelines",
        "circleci": "CircleCI",
        "jenkins": "Jenkins",
    }

    all_deps = []
    for cat in dependencies.values():
        if isinstance(cat, list):
            all_deps.extend(cat)
    dep_text = " ".join(all_deps).lower()

    for indicator, provider in readme_indicators.items():
        if indicator in dep_text and provider not in providers:
            providers.append(provider)

    return {
        "providers": providers[:5],
        "capabilities": capabilities[:10],
        "config_files": config_files[:10],
        "pipeline_count": pipeline_count,
        "has_cicd": len(providers) > 0,
    }
