from typing import Any, Dict, List


SOURCE_PATTERNS = {"src", "lib", "app", "core", "main", "pkg", "cmd", "internal"}
BACKEND_PATTERNS = {"backend", "server", "api", "routes", "controllers", "services", "models", "db", "migrations", "middleware"}
FRONTEND_PATTERNS = {"frontend", "client", "web", "ui", "components", "pages", "views", "public", "static", "assets", "styles"}
TEST_PATTERNS = {"test", "tests", "__tests__", "spec", "specs", "e2e", "cypress", "playwright", "test_"}

DOCKER_PATTERNS = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".dockerignore"}
CI_PATTERNS = {".github", ".gitlab-ci.yml", "Jenkinsfile", ".circleci", ".travis.yml", "azure-pipelines.yml"}
CONFIG_FILES = {
    "package.json", "tsconfig.json", "vite.config.js", "vite.config.ts",
    "webpack.config.js", "next.config.js", "next.config.mjs",
    "pyproject.toml", "setup.py", "setup.cfg", "Cargo.toml", "go.mod",
    "pom.xml", "build.gradle", "Gemfile", "composer.json",
    "Makefile", "makefile", "CMakeLists.txt", "justfile",
    "alembic.ini", ".env.example", "config.py", "config.js", "config.ts",
}
DOC_DIRS = {"docs", "doc", "documentation", "wiki", "guides"}
SCRIPT_DIRS = {"scripts", "bin", "tools", "utils", "devtools"}
ASSET_DIRS = {"assets", "images", "img", "icons", "fonts", "media", "public"}


def analyze_structure(tree: list) -> dict:
    if not tree:
        return _empty()

    root_files = []
    root_dirs = set()
    all_paths = []
    dir_files: Dict[str, List[str]] = {}

    for item in tree:
        path = item.get("path", "")
        item_type = item.get("type", "")
        all_paths.append(path)

        parts = path.split("/")
        if len(parts) == 1 and item_type == "blob":
            root_files.append(parts[0])
        elif len(parts) >= 1 and item_type == "tree":
            root_dirs.add(parts[0])

        top_dir = parts[0] if parts else ""
        if top_dir not in dir_files:
            dir_files[top_dir] = []
        if item_type == "blob":
            dir_files[top_dir].append(parts[-1] if parts else "")

    source_dirs = []
    backend_dirs = []
    frontend_dirs = []
    test_dirs = []
    docker_files = []
    ci_cd_files = []
    config_files = []
    doc_dirs = []
    script_dirs = []
    asset_dirs = []

    for d in root_dirs:
        dl = d.lower()
        if any(p in dl for p in TEST_PATTERNS):
            test_dirs.append(d)
        elif any(p in dl for p in BACKEND_PATTERNS):
            backend_dirs.append(d)
        elif any(p in dl for p in FRONTEND_PATTERNS):
            frontend_dirs.append(d)
        elif any(p in dl for p in SOURCE_PATTERNS):
            source_dirs.append(d)
        elif any(p in dl for p in DOC_DIRS):
            doc_dirs.append(d)
        elif any(p in dl for p in SCRIPT_DIRS):
            script_dirs.append(d)
        elif any(p in dl for p in ASSET_DIRS):
            asset_dirs.append(d)

    for f in root_files:
        if f in DOCKER_PATTERNS or f.startswith("Dockerfile"):
            docker_files.append(f)
        elif f in CI_PATTERNS or f.endswith(".yml") and "ci" in f.lower():
            ci_cd_files.append(f)
        elif f in CONFIG_FILES or f.endswith((".config.js", ".config.ts", ".config.mjs", ".rc", ".rc.js")):
            config_files.append(f)

    for path in all_paths:
        parts = path.split("/")
        fname = parts[-1] if parts else ""
        if fname in CI_PATTERNS or ".github/workflows" in path:
            if fname not in ci_cd_files:
                ci_cd_files.append(fname)

    has_package_json = "package.json" in root_files
    has_requirements_txt = "requirements.txt" in root_files
    has_dockerfile = any("Dockerfile" in f for f in root_files)
    has_makefile = any(f.lower() == "makefile" for f in root_files)
    has_tests = len(test_dirs) > 0
    has_docs = len(doc_dirs) > 0

    return {
        "root_files": root_files,
        "root_directories": sorted(root_dirs),
        "source_dirs": source_dirs,
        "backend_dirs": backend_dirs,
        "frontend_dirs": frontend_dirs,
        "test_dirs": test_dirs,
        "doc_dirs": doc_dirs,
        "script_dirs": script_dirs,
        "asset_dirs": asset_dirs,
        "docker_files": docker_files,
        "ci_cd_files": ci_cd_files,
        "config_files": config_files,
        "has_package_json": has_package_json,
        "has_requirements_txt": has_requirements_txt,
        "has_dockerfile": has_dockerfile,
        "has_makefile": has_makefile,
        "has_tests": has_tests,
        "has_docs": has_docs,
        "total_files": len([t for t in tree if t.get("type") == "blob"]),
        "total_dirs": len([t for t in tree if t.get("type") == "tree"]),
    }


def _empty() -> dict:
    return {
        "root_files": [], "root_directories": [], "source_dirs": [],
        "backend_dirs": [], "frontend_dirs": [], "test_dirs": [],
        "doc_dirs": [], "script_dirs": [], "asset_dirs": [],
        "docker_files": [], "ci_cd_files": [], "config_files": [],
        "has_package_json": False, "has_requirements_txt": False,
        "has_dockerfile": False, "has_makefile": False,
        "has_tests": False, "has_docs": False,
        "total_files": 0, "total_dirs": 0,
    }
