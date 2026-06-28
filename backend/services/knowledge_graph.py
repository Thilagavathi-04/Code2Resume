import networkx as nx
import json
import os


class KnowledgeGraph:
    def __init__(self, storage_dir: str = "data/knowledge_graphs"):
        self.storage_dir = storage_dir
        self.graphs: dict[str, nx.DiGraph] = {}
        os.makedirs(storage_dir, exist_ok=True)

    def _get_graph(self, username: str) -> nx.DiGraph:
        if username not in self.graphs:
            self.graphs[username] = self._load(username)
        return self.graphs[username]

    def _load(self, username: str) -> nx.DiGraph:
        path = os.path.join(self.storage_dir, f"{username}.json")
        G = nx.DiGraph()
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
            G = nx.node_link_graph(data)
        return G

    def _save(self, username: str):
        path = os.path.join(self.storage_dir, f"{username}.json")
        data = nx.node_link_data(self.graphs[username])
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def add_repo(self, username: str, repo_data: dict):
        G = self._get_graph(username)
        repo_name = repo_data.get("name", "unknown")

        print(f"[KG] Adding repo '{repo_name}' for {username}")

        G.add_node(repo_name, type="repo",
                    description=repo_data.get("description", ""),
                    category=repo_data.get("classification", {}).get("primary", "Other"),
                    quality_score=repo_data.get("quality_metrics", {}).get("resume_strength_score", 0))

        tech_stack = repo_data.get("tech_stack", {})
        tech_count = 0
        if isinstance(tech_stack, dict):
            for cat, techs in tech_stack.items():
                if not isinstance(techs, list):
                    continue
                for tech in techs:
                    G.add_node(tech, type="technology", category=cat)
                    G.add_edge(repo_name, tech, relation="USES")
                    tech_count += 1
        print(f"[KG]   Tech nodes: {tech_count}")

        arch = repo_data.get("architecture", {})
        arch_type = arch.get("pattern", "")
        if arch_type:
            G.add_node(arch_type, type="arch_pattern")
            G.add_edge(repo_name, arch_type, relation="IMPLEMENTS")
            print(f"[KG]   Arch pattern: {arch_type}")

        deployment = repo_data.get("deployment", {})
        deploy_count = 0
        for target in deployment.get("detected_technologies", []):
            G.add_node(target, type="deployment_target")
            G.add_edge(repo_name, target, relation="DEPLOYS_ON")
            deploy_count += 1
        if deploy_count:
            print(f"[KG]   Deployment targets: {deploy_count}")

        category = repo_data.get("classification", {}).get("primary", "Other")
        G.add_node(category, type="domain")
        G.add_edge(repo_name, category, relation="BELONGS_TO")
        print(f"[KG]   Domain: {category}")

        self._save(username)
        print(f"[KG]   Saved to data/knowledge_graphs/{username}.json")

    def get_related_tech(self, username: str, repo_name: str) -> list[str]:
        G = self._get_graph(username)
        if repo_name not in G:
            return []
        techs = set()
        for _, tech, data in G.out_edges(repo_name, data=True):
            if data.get("relation") == "USES" and G.nodes[tech].get("type") == "technology":
                techs.add(tech)
        shared = []
        for tech in techs:
            for other_repo in G.predecessors(tech):
                if other_repo != repo_name and G.nodes.get(other_repo, {}).get("type") == "repo":
                    shared.append(tech)
                    break
        return list(shared)

    def get_domain_repos(self, username: str, domain: str) -> list[str]:
        G = self._get_graph(username)
        repos = []
        for repo, data in G.nodes(data=True):
            if data.get("type") == "repo" and data.get("category") == domain:
                repos.append(repo)
        return repos

    def get_repo_context(self, username: str, repo_name: str) -> dict:
        G = self._get_graph(username)
        if repo_name not in G:
            return {}
        outgoing = {(t, d.get("relation")) for _, t, d in G.out_edges(repo_name, data=True)}
        return {
            "techs": [t for t, r in outgoing if r == "USES"],
            "arch": [t for t, r in outgoing if r == "IMPLEMENTS"],
            "deployment": [t for t, r in outgoing if r == "DEPLOYS_ON"],
            "domain": [t for t, r in outgoing if r == "BELONGS_TO"],
        }

    def find_similar_repos(self, username: str, repo_name: str) -> list[tuple[str, float]]:
        G = self._get_graph(username)
        scores = {}
        ctx = self.get_repo_context(username, repo_name)
        my_techs = set(ctx.get("techs", []))
        for other in G.nodes:
            if other == repo_name or G.nodes[other].get("type") != "repo":
                continue
            other_ctx = self.get_repo_context(username, other)
            other_techs = set(other_ctx.get("techs", []))
            if my_techs or other_techs:
                union = my_techs | other_techs
                intersection = my_techs & other_techs
                jaccard = len(intersection) / len(union) if union else 0
                scores[other] = jaccard
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def get_all_repos(self, username: str) -> list[str]:
        G = self._get_graph(username)
        return [n for n, d in G.nodes(data=True) if d.get("type") == "repo"]

    def get_graph_stats(self, username: str) -> dict:
        G = self._get_graph(username)
        node_types = {}
        for _, data in G.nodes(data=True):
            t = data.get("type", "unknown")
            node_types[t] = node_types.get(t, 0) + 1
        edge_types = {}
        for _, _, data in G.edges(data=True):
            r = data.get("relation", "unknown")
            edge_types[r] = edge_types.get(r, 0) + 1
        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "node_types": node_types,
            "edge_types": edge_types,
        }
