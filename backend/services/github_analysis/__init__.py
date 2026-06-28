import time

from .client import GitHubClient
from .structure_analyzer import analyze_structure
from .dependency_analyzer import analyze_dependencies
from .tech_stack_analyzer import analyze_tech_stack
from .aiml_analyzer import analyze_aiml
from .service_analyzer import analyze_services
from .deployment_analyzer import analyze_deployment
from .database_analyzer import analyze_databases
from .testing_analyzer import analyze_testing
from .cicd_analyzer import analyze_cicd
from .commit_analyzer import analyze_commits
from .documentation_analyzer import analyze_documentation
from .architecture_analyzer import analyze_architecture
from .classifier import classify_project
from .knowledge_graph import generate_knowledge_graph
from .metrics import compute_quality_metrics
from .semantic_analyzer import analyze_semantics

__all__ = [
    "GitHubClient", "analyze_repository", "analyze_structure",
    "analyze_dependencies", "analyze_tech_stack", "analyze_aiml",
    "analyze_services", "analyze_deployment", "analyze_databases",
    "analyze_testing", "analyze_cicd", "analyze_commits",
    "analyze_documentation", "analyze_architecture", "classify_project",
    "generate_knowledge_graph", "compute_quality_metrics",
    "analyze_semantics",
]


async def analyze_repository(repo_url: str, user_token: str = None, skip_semantic: bool = False) -> dict:
    from urllib.parse import urlparse

    parsed = urlparse(repo_url)
    if parsed.netloc != "github.com":
        raise ValueError("Invalid GitHub URL")

    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL format")

    owner, repo = path_parts[0], path_parts[1]
    print(f"[GitHubAnalysis] Starting analysis for {owner}/{repo}")
    t_start = time.time()

    client = GitHubClient(user_token)

    try:
        repo_data, readme_content, languages, tree = await client.fetch_all(owner, repo)
    finally:
        pass

    if not repo_data:
        raise Exception(f"Failed to fetch repo data for {owner}/{repo} (repo may not exist or is private)")

    t = time.time()
    structure = analyze_structure(tree)
    print(f"[GitHubAnalysis] Structure: {structure['total_files']} files, {structure['total_dirs']} dirs ({round(time.time()-t, 2)}s)")

    t = time.time()
    dependencies = await analyze_dependencies(client, owner, repo, tree)
    print(f"[GitHubAnalysis] Dependencies: {len(dependencies['found_files'])} files found ({round(time.time()-t, 2)}s)")

    t = time.time()
    tech_stack = analyze_tech_stack(languages, readme_content, structure, dependencies, tree)
    total_tech = sum(len(v) for v in tech_stack.values() if isinstance(v, list))
    print(f"[GitHubAnalysis] Tech stack: {total_tech} items across {len([k for k,v in tech_stack.items() if isinstance(v, list) and v])} categories ({round(time.time()-t, 2)}s)")

    t = time.time()
    aiml = analyze_aiml(tree, dependencies, readme_content, tech_stack)
    print(f"[GitHubAnalysis] AI/ML: is_ai={aiml['is_ai_project']}, libs={len(aiml['detected_libraries'])}, caps={len(aiml['capabilities'])} ({round(time.time()-t, 2)}s)")

    t = time.time()
    services = analyze_services(tree, dependencies, readme_content)
    print(f"[GitHubAnalysis] Services: {services['detected_services']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    deployment = analyze_deployment(tree, dependencies, readme_content)
    print(f"[GitHubAnalysis] Deployment: {deployment['detected_technologies']} readiness={deployment['readiness_level']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    databases = analyze_databases(tree, dependencies, readme_content, tech_stack)
    print(f"[GitHubAnalysis] Databases: relational={databases['relational']}, nosql={databases['nosql']}, vector={databases['vector_databases']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    testing = analyze_testing(tree, dependencies, readme_content)
    print(f"[GitHubAnalysis] Testing: frameworks={testing['frameworks']}, level={testing['estimated_testing_level']}, files={testing['test_file_count']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    cicd = analyze_cicd(tree, dependencies)
    print(f"[GitHubAnalysis] CI/CD: providers={cicd['providers']}, pipelines={cicd['pipeline_count']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    commits = await analyze_commits(client, owner, repo)
    print(f"[GitHubAnalysis] Commits: total={commits['total_commits']}, health={commits['health_score']}, active={commits['is_active']} ({round(time.time()-t, 2)}s)")

    t = time.time()
    documentation = analyze_documentation(readme_content)
    print(f"[GitHubAnalysis] Docs: sections={documentation['total_sections_found']}, quality={documentation['quality_score']}/10 ({round(time.time()-t, 2)}s)")

    t = time.time()
    architecture = analyze_architecture(structure, dependencies, tech_stack)
    print(f"[GitHubAnalysis] Architecture: type={architecture['type']}, pattern={architecture['pattern']}, maturity={architecture['maturity']} ({round(time.time()-t, 2)}s)")

    classification = classify_project(
        repo_data.get("name", ""),
        repo_data.get("description", ""),
        tech_stack,
        readme_content,
    )
    print(f"[GitHubAnalysis] Classification: primary={classification['primary']}, secondary={classification['secondary']}, confidence={classification['confidence']}")

    knowledge_graph = generate_knowledge_graph(tech_stack, architecture, deployment, aiml)
    quality_metrics = compute_quality_metrics(
        documentation, structure, dependencies, commits, tech_stack,
        architecture, deployment, testing, classification,
    )
    print(f"[GitHubAnalysis] Quality: resume={quality_metrics['resume_strength_score']}/10, portfolio={quality_metrics['portfolio_strength_score']}/10, health={quality_metrics['project_health_score']}/10")

    semantic_analysis = {}
    if skip_semantic:
        print(f"[GitHubAnalysis] Semantic analysis skipped (bulk mode)")
    else:
        try:
            print(f"[GitHubAnalysis] Running semantic analysis via LLM...")
            t = time.time()
            semantic_analysis = await analyze_semantics(
                repo_data=repo_data,
                readme=readme_content,
                tech_stack=tech_stack,
                structure=structure,
                architecture=architecture,
                classification=classification,
                aiml=aiml,
                deployment=deployment,
                databases=databases,
                testing=testing,
                services=services,
                quality_metrics=quality_metrics,
                knowledge_graph=knowledge_graph,
            )
            if semantic_analysis:
                print(f"[GitHubAnalysis] Semantic analysis completed in {round(time.time()-t, 2)}s: keys={list(semantic_analysis.keys())[:5]}...")
            else:
                print(f"[GitHubAnalysis] Semantic analysis returned empty (LLM unavailable)")
        except Exception as e:
            print(f"[GitHubAnalysis] Semantic analysis failed: {e}")

    total_time = round(time.time() - t_start, 2)
    print(f"[GitHubAnalysis] Analysis complete for {owner}/{repo} in {total_time}s")

    return {
        "name": repo_data.get("name", ""),
        "description": repo_data.get("description", ""),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "language": repo_data.get("language"),
        "languages": languages,
        "readme_content": readme_content,
        "topics": repo_data.get("topics", []),
        "created_at": repo_data.get("created_at"),
        "updated_at": repo_data.get("updated_at"),
        "size": repo_data.get("size", 0),
        "url": repo_data.get("html_url", ""),
        "structure": structure,
        "dependencies": dependencies,
        "tech_stack": tech_stack,
        "ai_ml": aiml,
        "services": services,
        "deployment": deployment,
        "databases": databases,
        "testing": testing,
        "cicd": cicd,
        "commits": commits,
        "documentation": documentation,
        "architecture": architecture,
        "classification": classification,
        "knowledge_graph": knowledge_graph,
        "quality_metrics": quality_metrics,
        "semantic_analysis": semantic_analysis,
    }
