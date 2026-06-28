import json
import re
from typing import Any, Dict, List, Optional

from .client import GitHubClient


DEP_FILE_NAMES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
    "composer.json", "Gemfile", "environment.yml",
    "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
}


async def analyze_dependencies(client: GitHubClient, owner: str, repo: str, tree: list) -> dict:
    if not tree:
        return _empty()

    found_files = set()
    for item in tree:
        path = item.get("path", "")
        fname = path.split("/")[-1] if path else ""
        if fname in DEP_FILE_NAMES and item.get("type") == "blob":
            found_files.add(path)

    result: Dict[str, Any] = {
        "found_files": sorted(found_files),
        "package_managers": [],
        "frontend": [],
        "backend": [],
        "database": [],
        "devops": [],
        "testing": [],
        "ai_ml": [],
        "utilities": [],
        "build_tools": [],
        "languages": [],
    }

    for fpath in found_files:
        content = await client.get_file_content(owner, repo, fpath)
        if not content:
            continue

        fname = fpath.split("/")[-1]

        if fname == "package.json":
            _parse_package_json(content, result)
        elif fname == "requirements.txt":
            _parse_requirements_txt(content, result)
        elif fname == "pyproject.toml":
            _parse_pyproject_toml(content, result)
        elif fname == "Pipfile":
            _parse_pipfile(content, result)
        elif fname == "Cargo.toml":
            _parse_cargo_toml(content, result)
        elif fname == "go.mod":
            _parse_go_mod(content, result)
        elif fname == "pom.xml":
            _parse_pom_xml(content, result)
        elif fname == "build.gradle":
            _parse_build_gradle(content, result)
        elif fname == "composer.json":
            _parse_composer_json(content, result)
        elif fname == "Gemfile":
            _parse_gemfile(content, result)
        elif fname == "Dockerfile":
            _parse_dockerfile(content, result)
        elif fname in ("docker-compose.yml", "docker-compose.yaml"):
            _parse_docker_compose(content, result)

    for pm in result["package_managers"]:
        if pm not in result["build_tools"]:
            result["build_tools"].append(pm)

    return result


KNOWN_FRONTEND = {
    "react", "react-dom", "next", "nuxt", "vue", "angular", "@angular/core",
    "svelte", "solid-js", "preact", "remix", "gatsby",
    "tailwindcss", "@mui/material", "@chakra-ui/react", "antd",
    "styled-components", "emotion", "sass", "less", "postcss",
    "vite", "webpack", "parcel", "esbuild", "rollup",
    "react-router-dom", "next/router", "vue-router",
    "redux", "zustand", "jotai", "recoil", "mobx", "pinia", "vuex",
    "framer-motion", "gsap", "three", "@react-three/fiber",
}

KNOWN_BACKEND = {
    "fastapi", "flask", "django", "express", "koa", "hono",
    "nest", "@nestjs/core", "spring-boot", "spring",
    "rails", "laravel", "gin", "fiber", "actix-web", "axum",
    "uvicorn", "gunicorn", "hypercorn",
    "celery", "bull", "bee-queue",
    "passport", "jsonwebtoken", "bcryptjs",
    "sqlalchemy", "prisma", "typeorm", "sequelize", "drizzle-orm",
    "alembic", "migrate", "flyway",
    "graphql", "apollo-server", "mercurius",
    "socket.io", "ws",
}

KNOWN_DATABASE = {
    "mongoose", "pg", "mysql2", "mysql", "sqlite3", "better-sqlite3",
    "redis", "ioredis", "mongodb", "pymongo", "psycopg2", "asyncpg",
    "aiosqlite", "sqlalchemy", "prisma", "neo4j-driver",
    "chromadb", "pinecone-client", "qdrant-client", "faiss-cpu",
    "milvus", "elasticsearch", "opensearch-py",
}

KNOWN_AI_ML = {
    "tensorflow", "torch", "pytorch", "keras", "scikit-learn", "sklearn",
    "transformers", "huggingface-hub", "sentence-transformers",
    "langchain", "llama-index", "openai", "anthropic", "google-generativeai",
    "ollama", "langsmith", "langfuse",
    "opencv-python", "opencv-contrib-python", "pillow",
    "xgboost", "lightgbm", "catboost",
    "spacy", "nltk", "gensim",
    "ultralytics", "yolov8",
    "diffusers", "accelerate", "peft", "bitsandbytes",
    "chromadb", "pinecone-client", "qdrant-client", "faiss-cpu",
    "langchain-community", "langchain-core", "langchain-openai",
    "llama-index-core", "llama-index-llms-openai",
    "vllm", "ctransformers", "llama-cpp-python",
}

KNOWN_TESTING = {
    "jest", "mocha", "chai", "vitest", "jasmine",
    "pytest", "unittest2", "nose2",
    "cypress", "playwright", "@playwright/test",
    "selenium", "webdriverio", "nightwatch",
    "supertest", "httpx",
}

KNOWN_DEVOPS = {
    "docker", "kubernetes", "terraform", "ansible",
    "github-actions", "circleci",
}

KNOWN_UTILITIES = {
    "axios", "node-fetch", "got", "request", "urllib3", "httpx",
    "lodash", "ramda", "date-fns", "moment", "dayjs",
    "dotenv", "cross-env", "concurrently",
    "typescript", "eslint", "prettier", "black", "isort", "ruff",
    "mypy", "pylint", "flake8",
    "husky", "lint-staged", "commitlint",
}


def _add_dep(result: dict, name: str, category: str):
    name_lower = name.lower().strip()
    if name_lower not in [d.lower() for d in result[category]]:
        result[category].append(name.strip())


def _categorize_dep(name: str, result: dict):
    nl = name.lower().strip()
    if nl in KNOWN_FRONTEND or any(k in nl for k in ["react", "vue", "angular", "svelte", "next", "nuxt", "tailwind", "vite"]):
        _add_dep(result, name, "frontend")
    elif nl in KNOWN_BACKEND or any(k in nl for k in ["fastapi", "flask", "django", "express", "nest", "spring", "rails", "laravel", "gin", "uvicorn", "gunicorn"]):
        _add_dep(result, name, "backend")
    elif nl in KNOWN_DATABASE or any(k in nl for k in ["mongo", "postgres", "mysql", "sqlite", "redis", "neo4j", "elastic", "chroma", "pinecone", "qdrant", "faiss"]):
        _add_dep(result, name, "database")
    elif nl in KNOWN_AI_ML or any(k in nl for k in ["torch", "tensorflow", "keras", "sklearn", "transformers", "langchain", "openai", "llama", "cv2", "opencv", "ultralytics"]):
        _add_dep(result, name, "ai_ml")
    elif nl in KNOWN_TESTING or any(k in nl for k in ["jest", "pytest", "cypress", "playwright", "mocha", "vitest"]):
        _add_dep(result, name, "testing")
    elif nl in KNOWN_DEVOPS or any(k in nl for k in ["docker", "kubernetes", "terraform", "ansible"]):
        _add_dep(result, name, "devops")
    elif nl in KNOWN_UTILITIES or any(k in nl for k in ["axios", "lodash", "dotenv", "typescript", "eslint", "prettier"]):
        _add_dep(result, name, "utilities")


def _parse_package_json(content: str, result: dict):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return

    result["package_managers"].append("npm")

    deps = data.get("dependencies", {})
    dev_deps = data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}
    result["languages"].append("JavaScript")

    scripts = data.get("scripts", {})
    if any("typescript" in str(v) for v in scripts.values()) or "typescript" in all_deps:
        if "TypeScript" not in result["languages"]:
            result["languages"].append("TypeScript")
    if any("next" in str(v) for v in scripts.values()) or "next" in all_deps:
        result["package_managers"].append("next")
    if any("vite" in str(v) for v in scripts.values()) or "vite" in all_deps:
        result["build_tools"].append("vite")
    if any("webpack" in str(v) for v in scripts.values()) or "webpack" in all_deps:
        result["build_tools"].append("webpack")

    for dep_name in all_deps:
        _categorize_dep(dep_name, result)


def _parse_requirements_txt(content: str, result: dict):
    result["package_managers"].append("pip")
    result["languages"].append("Python")
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[]", line)[0].strip()
        if name:
            _categorize_dep(name, result)


def _parse_pyproject_toml(content: str, result: dict):
    result["package_managers"].append("pip")
    result["languages"].append("Python")
    in_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("dependencies") and "=" in stripped:
            in_deps = True
            continue
        if in_deps:
            if stripped.startswith("]"):
                in_deps = False
                continue
            name = re.split(r"[>=<!\[]", stripped.strip('",[] '))[0].strip()
            if name:
                _categorize_dep(name, result)
    if "poetry" in content.lower():
        result["package_managers"].append("poetry")
    if "[tool.pytest" in content or "pytest" in content:
        _add_dep(result, "pytest", "testing")


def _parse_pipfile(content: str, result: dict):
    result["package_managers"].append("pipenv")
    result["languages"].append("Python")
    for line in content.splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("["):
            name = line.split("=")[0].strip().strip('"')
            if name and name not in ("name", "url", "verify_ssl"):
                _categorize_dep(name, result)


def _parse_cargo_toml(content: str, result: dict):
    result["package_managers"].append("cargo")
    result["languages"].append("Rust")
    for line in content.splitlines():
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("[") and not stripped.startswith("#"):
            name = stripped.split("=")[0].strip()
            if name and name not in ("name", "version", "edition", "authors", "description", "license", "readme", "repository"):
                _categorize_dep(name, result)


def _parse_go_mod(content: str, result: dict):
    result["package_managers"].append("go modules")
    result["languages"].append("Go")
    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("require"):
            in_require = True
            parts = stripped.split()
            if len(parts) > 1 and not stripped.endswith("("):
                name = parts[1].split("/")[0] if "/" in parts[1] else parts[1]
                _categorize_dep(name, result)
            continue
        if in_require:
            if stripped == ")":
                in_require = False
                continue
            parts = stripped.split()
            if parts:
                name = parts[0].split("/")[-1]
                _categorize_dep(name, result)


def _parse_pom_xml(content: str, result: dict):
    result["package_managers"].append("maven")
    result["languages"].append("Java")
    for match in re.finditer(r"<artifactId>(.*?)</artifactId>", content):
        name = match.group(1).strip()
        if name and not name.endswith("-plugin"):
            _categorize_dep(name, result)


def _parse_build_gradle(content: str, result: dict):
    result["package_managers"].append("gradle")
    result["languages"].append("Java")
    for match in re.finditer(r"implementation ['\"]([^'\"]+)['\"]", content):
        name = match.group(1).split(":")[-1] if ":" in match.group(1) else match.group(1)
        _categorize_dep(name, result)


def _parse_composer_json(content: str, result: dict):
    result["package_managers"].append("composer")
    result["languages"].append("PHP")
    try:
        data = json.loads(content)
        deps = data.get("require", {})
        for name in deps:
            _categorize_dep(name, result)
    except json.JSONDecodeError:
        pass


def _parse_gemfile(content: str, result: dict):
    result["package_managers"].append("bundler")
    result["languages"].append("Ruby")
    for match in re.finditer(r"gem ['\"]([^'\"]+)['\"]", content):
        _categorize_dep(match.group(1), result)


def _parse_dockerfile(content: str, result: dict):
    result["devops"].append("Docker")
    for match in re.finditer(r"FROM\s+(\S+)", content):
        image = match.group(1).split(":")[0].lower()
        if image not in ("scratch", "busybox"):
            _add_dep(result, image, "devops")


def _parse_docker_compose(content: str, result: dict):
    result["devops"].append("Docker Compose")


def _empty() -> dict:
    return {
        "found_files": [],
        "package_managers": [],
        "frontend": [], "backend": [], "database": [],
        "devops": [], "testing": [], "ai_ml": [],
        "utilities": [], "build_tools": [], "languages": [],
    }
