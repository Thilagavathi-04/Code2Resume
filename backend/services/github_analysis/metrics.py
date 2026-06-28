def compute_quality_metrics(
    documentation: dict,
    structure: dict,
    dependencies: dict,
    commits: dict,
    tech_stack: dict,
    architecture: dict,
    deployment: dict,
    testing: dict,
    classification: dict,
) -> dict:
    doc_score = documentation.get("quality_score", 0)
    has_tests = testing.get("has_testing", False)
    test_level = testing.get("estimated_testing_level", "none")
    test_count = testing.get("test_file_count", 0)

    all_tech = []
    for cat in tech_stack.values():
        if isinstance(cat, list):
            all_tech.extend(cat)
    tech_count = len(set(all_tech))

    total_files = structure.get("total_files", 0)
    total_dirs = structure.get("total_dirs", 0)

    complexity = 0
    if total_files > 100:
        complexity += 3
    elif total_files > 30:
        complexity += 2
    elif total_files > 10:
        complexity += 1
    if total_dirs > 20:
        complexity += 2
    elif total_dirs > 10:
        complexity += 1
    if tech_count > 8:
        complexity += 2
    elif tech_count > 4:
        complexity += 1
    codebase_complexity = min(10.0, complexity)

    maintainability = 5.0
    if has_tests:
        maintainability += 1.5
    if documentation.get("completeness_score", 0) > 50:
        maintainability += 1.0
    if architecture.get("maturity") == "mature":
        maintainability += 1.5
    elif architecture.get("maturity") == "moderate":
        maintainability += 0.5
    if structure.get("has_docs"):
        maintainability += 0.5
    maintainability = min(10.0, maintainability)

    commit_health = commits.get("health_score", 0)
    project_health = commit_health

    tech_diversity = min(10.0, tech_count * 1.2)

    arch_maturity = 3.0
    arch_type = architecture.get("pattern", "")
    if arch_type in ("Microservices", "Clean Architecture", "MVC"):
        arch_maturity = 8.0
    elif arch_type in ("REST API", "Layered", "Frontend + Backend"):
        arch_maturity = 6.5
    elif arch_type in ("Full Stack", "Backend Service"):
        arch_maturity = 5.5
    elif arch_type in ("SPA", "CLI Tool"):
        arch_maturity = 4.0

    deploy_readiness = 2.0
    deploy_level = deployment.get("readiness_level", "none")
    if deploy_level == "high":
        deploy_readiness = 9.0
    elif deploy_level == "medium":
        deploy_readiness = 7.0
    elif deploy_level == "low":
        deploy_readiness = 4.0

    testing_maturity = 1.0
    if test_level == "comprehensive":
        testing_maturity = 9.0
    elif test_level == "moderate":
        testing_maturity = 6.0
    elif test_level == "basic":
        testing_maturity = 3.0

    resume_strength = 4.0
    if tech_count > 5:
        resume_strength += 1.5
    if has_tests:
        resume_strength += 1.0
    if doc_score > 5:
        resume_strength += 1.0
    if commit_health > 5:
        resume_strength += 1.0
    if deploy_level in ("medium", "high"):
        resume_strength += 1.0
    resume_strength = min(10.0, resume_strength)

    portfolio_strength = 3.0
    if doc_score > 5:
        portfolio_strength += 1.5
    if documentation.get("has_images"):
        portfolio_strength += 1.0
    if documentation.get("has_badges"):
        portfolio_strength += 0.5
    if tech_count > 4:
        portfolio_strength += 1.0
    if deploy_level in ("medium", "high"):
        portfolio_strength += 1.0
    if architecture.get("type") not in ("CLI Tool", "Software Project"):
        portfolio_strength += 1.0
    portfolio_strength = min(10.0, portfolio_strength)

    return {
        "documentation_score": round(doc_score, 1),
        "codebase_complexity": round(codebase_complexity, 1),
        "maintainability_score": round(maintainability, 1),
        "project_health_score": round(project_health, 1),
        "technology_diversity": round(tech_diversity, 1),
        "architecture_maturity": round(arch_maturity, 1),
        "deployment_readiness": round(deploy_readiness, 1),
        "testing_maturity": round(testing_maturity, 1),
        "resume_strength_score": round(resume_strength, 1),
        "portfolio_strength_score": round(portfolio_strength, 1),
    }
