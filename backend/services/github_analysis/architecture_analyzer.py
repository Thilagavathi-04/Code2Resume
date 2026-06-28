def analyze_architecture(structure: dict, dependencies: dict, tech_stack: dict) -> dict:
    backend_dirs = structure.get("backend_dirs", [])
    frontend_dirs = structure.get("frontend_dirs", [])
    test_dirs = structure.get("test_dirs", [])
    config_files = structure.get("config_files", [])

    all_backend = []
    all_frontend = []
    for cat in [dependencies.get("backend", []), tech_stack.get("backend", [])]:
        if isinstance(cat, list):
            all_backend.extend(cat)
    for cat in [dependencies.get("frontend", []), tech_stack.get("frontend", [])]:
        if isinstance(cat, list):
            all_frontend.extend(cat)

    has_backend = len(backend_dirs) > 0 or len(all_backend) > 0
    has_frontend = len(frontend_dirs) > 0 or len(all_frontend) > 0
    has_api = any("api" in d.lower() for d in backend_dirs) or any(
        "api" in t.lower() for t in tech_stack.get("api", [])
    )
    has_microservices = any(
        d.lower() in ("services", "microservices", "packages", "apps")
        for d in structure.get("root_directories", [])
    )
    has_models = any("model" in d.lower() for d in backend_dirs)
    has_routes = any("route" in d.lower() or "controller" in d.lower() for d in backend_dirs)
    has_middleware = any("middleware" in d.lower() for d in backend_dirs)

    is_full_stack = has_backend and has_frontend
    is_frontend_only = has_frontend and not has_backend
    is_backend_only = has_backend and not has_frontend
    is_cli = not has_backend and not has_frontend

    architecture_type = "Software Project"
    architecture_pattern = "Unknown"

    if has_microservices:
        architecture_type = "Microservices"
        architecture_pattern = "Microservices"
    elif is_full_stack:
        architecture_type = "Full Stack"
        if has_routes and has_models:
            architecture_pattern = "MVC"
        elif has_middleware:
            architecture_pattern = "Layered"
        else:
            architecture_pattern = "Frontend + Backend"
    elif is_backend_only:
        architecture_type = "Backend Service"
        if has_api:
            architecture_pattern = "REST API"
        elif has_routes and has_models:
            architecture_pattern = "MVC"
        elif has_middleware:
            architecture_pattern = "Layered"
        else:
            architecture_pattern = "Monolith"
    elif is_frontend_only:
        architecture_type = "Frontend Application"
        architecture_pattern = "SPA"
    elif is_cli:
        architecture_type = "CLI Tool"
        architecture_pattern = "CLI"

    ai_ml = tech_stack.get("ai_ml", [])
    if ai_ml:
        architecture_type = "AI Application"
        if has_backend and has_frontend:
            architecture_pattern = "AI Web Application"
        elif has_backend:
            architecture_pattern = "AI Pipeline"
        else:
            architecture_pattern = "AI Script"

    is_monolith = architecture_pattern in ("Monolith", "MVC", "Layered", "SPA")
    is_clean = has_routes and has_models and has_middleware
    has_tests = structure.get("has_tests", False)

    maturity = "basic"
    if has_tests and has_api and is_clean:
        maturity = "mature"
    elif has_api and (has_routes or has_models):
        maturity = "moderate"

    return {
        "type": architecture_type,
        "pattern": architecture_pattern,
        "is_full_stack": is_full_stack,
        "has_backend": has_backend,
        "has_frontend": has_frontend,
        "has_api": has_api,
        "has_microservices": has_microservices,
        "has_mvc_pattern": has_routes and has_models,
        "has_clean_architecture": is_clean,
        "maturity": maturity,
        "backend_dirs": backend_dirs[:5],
        "frontend_dirs": frontend_dirs[:5],
    }
