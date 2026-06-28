import re

TESTING_FRAMEWORKS = {
    "pytest": [r"pytest", r"conftest\.py", r"test_.*\.py", r"\.pytest"],
    "unittest": [r"unittest", r"import unittest"],
    "Jest": [r"jest", r"\.test\.js", r"\.spec\.js", r"jest\.config"],
    "Vitest": [r"vitest", r"\.test\.ts", r"\.spec\.ts", r"vitest\.config"],
    "Mocha": [r"mocha", r"\.mocharc"],
    "Chai": [r"chai", r"expect\("],
    "Cypress": [r"cypress", r"cypress\.config", r"cypress/e2e"],
    "Playwright": [r"playwright", r"playwright\.config", r"playwright\.ts"],
    "Selenium": [r"selenium", r"webdriver", r"chromedriver"],
    "JUnit": [r"junit", r"@Test", r"junit\.xml"],
    "RSpec": [r"rspec", r"\_spec\.rb"],
    "phpunit": [r"phpunit"],
    "Robot Framework": [r"robotframework", r"\.robot"],
}

COVERAGE_TOOLS = {
    "coverage.py": [r"coverage", r"\.coveragerc", r"--cov"],
    "Istanbul/nyc": [r"istanbul", r"nyc", r"coverage"],
    "Jest Coverage": [r"jest.*coverage", r"coverageDirectory"],
    "Codecov": [r"codecov", r"\.codecov"],
    "Coveralls": [r"coveralls"],
}


def analyze_testing(tree: list, dependencies: dict, readme: str) -> dict:
    frameworks_found = []
    coverage_tools = []
    test_dirs = []
    has_test_config = False
    estimated_level = "none"

    all_paths = [item.get("path", "") for item in tree or []]
    for path in all_paths:
        parts = path.split("/")
        for part in parts:
            if any(p in part.lower() for p in ("test", "tests", "__tests__", "spec", "e2e")):
                if part not in test_dirs:
                    test_dirs.append(part)
        fname = path.split("/")[-1].lower()
        if any(p in fname for p in ("test", "spec", "e2e")):
            if not any(d in path for d in test_dirs):
                test_dirs.append(path.rsplit("/", 1)[0] if "/" in path else ".")

    all_deps = []
    for cat in dependencies.values():
        if isinstance(cat, list):
            all_deps.extend(cat)
    dep_text = " ".join(all_deps).lower()

    readme_lower = readme.lower() if readme else ""
    combined = f"{dep_text} {readme_lower}"

    for framework, patterns in TESTING_FRAMEWORKS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                if framework not in frameworks_found:
                    frameworks_found.append(framework)
                break

    for tool, patterns in COVERAGE_TOOLS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                if tool not in coverage_tools:
                    coverage_tools.append(tool)
                break

    for path in all_paths:
        fname = path.split("/")[-1].lower()
        if fname in ("jest.config.js", "jest.config.ts", "vitest.config.ts", "vitest.config.js",
                      ".pytest.ini", "pytest.ini", "setup.cfg", "pyproject.toml",
                      "cypress.config.js", "playwright.config.ts"):
            has_test_config = True

    test_file_count = sum(1 for p in all_paths if "test" in p.lower() or "spec" in p.lower())

    if test_file_count > 20 or (frameworks_found and len(coverage_tools) > 0):
        estimated_level = "comprehensive"
    elif test_file_count > 5 or frameworks_found:
        estimated_level = "moderate"
    elif test_file_count > 0:
        estimated_level = "basic"

    return {
        "frameworks": frameworks_found[:5],
        "coverage_tools": coverage_tools[:3],
        "test_dirs": test_dirs[:5],
        "has_test_config": has_test_config,
        "test_file_count": test_file_count,
        "estimated_testing_level": estimated_level,
        "has_testing": len(frameworks_found) > 0 or test_file_count > 0,
    }
