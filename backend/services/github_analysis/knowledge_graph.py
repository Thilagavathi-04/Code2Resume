def generate_knowledge_graph(tech_stack: dict, architecture: dict, deployment: dict, aiml: dict) -> dict:
    graph = {}

    frontend = tech_stack.get("frontend", [])
    if frontend:
        graph["Frontend"] = frontend[:8]

    backend = tech_stack.get("backend", [])
    if backend:
        graph["Backend"] = backend[:8]

    ai_ml = tech_stack.get("ai_ml", []) or aiml.get("detected_libraries", [])
    if ai_ml:
        graph["AI/ML"] = ai_ml[:8]

    database = tech_stack.get("database", [])
    databases = tech_stack.get("databases", [])
    if database:
        graph["Database"] = database[:5]

    deployment_tech = deployment.get("detected_technologies", [])
    if deployment_tech:
        graph["Deployment"] = deployment_tech[:5]

    testing = tech_stack.get("testing", [])
    if testing:
        graph["Testing"] = testing[:5]

    devops = tech_stack.get("devops", [])
    if devops:
        graph["DevOps"] = devops[:5]

    cloud = tech_stack.get("cloud", [])
    if cloud:
        graph["Cloud"] = cloud[:5]

    api = tech_stack.get("api", [])
    if api:
        graph["API"] = api[:3]

    vector_db = tech_stack.get("vector_db", [])
    if vector_db:
        graph["Vector Database"] = vector_db[:3]

    utilities = tech_stack.get("utilities", [])
    if utilities:
        graph["Utilities"] = utilities[:5]

    arch_type = architecture.get("type", "")
    arch_pattern = architecture.get("pattern", "")
    if arch_type:
        graph["Architecture"] = [arch_type]
        if arch_pattern and arch_pattern != arch_type:
            graph["Architecture"].append(arch_pattern)

    return graph
