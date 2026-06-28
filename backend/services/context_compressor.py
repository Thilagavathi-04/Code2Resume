from .token_counter import count_tokens, truncate_at_sentence_boundary
from typing import Optional


class ContextCompressor:
    def __init__(self, max_tokens: int = 4000, tokenizer_model: str = "cl100k_base"):
        self.max_tokens = max_tokens
        self.tokenizer_model = tokenizer_model

    def compress_repos(self, repos: list[dict], profile: Optional[dict] = None) -> str:
        print(f"\n[ContextCompressor] Compressing {len(repos)} repos (max_tokens={self.max_tokens})")
        profile_text = ""
        profile_tokens = 0
        if profile:
            profile_text = self._format_profile(profile)
            profile_tokens = count_tokens(profile_text, self.tokenizer_model)
            print(f"[ContextCompressor] Profile tokens: {profile_tokens}")

        budget = self.max_tokens - profile_tokens - 200
        if budget < 500:
            budget = 500

        sections = []
        if profile_text:
            sections.append(profile_text)

        per_repo_budget = budget // max(len(repos), 1)
        print(f"[ContextCompressor] Per-repo token budget: {per_repo_budget}")
        for i, repo in enumerate(repos):
            name = repo.get("name", "Unknown")
            section = self._format_repo(repo, per_repo_budget)
            if section:
                sections.append(section)
                print(f"[ContextCompressor]   [{i+1}] {name}: {len(section)} chars")
            else:
                print(f"[ContextCompressor]   [{i+1}] {name}: SKIPPED (empty)")

        result = "\n\n---\n\n".join(sections)
        print(f"[ContextCompressor] Total context: {len(result)} chars, {len(sections)} sections")
        return result

    def _format_profile(self, profile: dict) -> str:
        parts = ["Developer Profile:"]
        for key, label in [("name", "Name"), ("email", "Email"), ("github", "GitHub"),
                           ("phone", "Phone"), ("education_institution", "Education")]:
            if profile.get(key):
                parts.append(f"{label}: {profile[key]}")
        return "\n".join(parts)

    def _format_repo(self, repo: dict, budget: int) -> str:
        name = repo.get("name", "Unknown")
        techs = ", ".join(repo.get("tech_stack", [])[:5])
        core = f"Project: {name}\nTech Stack: {techs}"
        core_tokens = count_tokens(core, self.tokenizer_model)
        remaining = budget - core_tokens

        if remaining <= 0:
            return core

        extras = []
        for field in ["resume_description", "summary", "description"]:
            text = repo.get(field, "")
            if not text:
                continue
            tokens = count_tokens(text, self.tokenizer_model)
            if tokens <= remaining:
                extras.append(text)
                remaining -= tokens
            else:
                truncated = truncate_at_sentence_boundary(text, remaining, self.tokenizer_model)
                if truncated:
                    extras.append(truncated)
                break

        bullets = repo.get("bullet_points", [])
        if bullets and remaining > 50:
            bullet_text = "Highlights:\n" + "\n".join(f"- {b}" for b in bullets)
            tokens = count_tokens(bullet_text, self.tokenizer_model)
            if tokens <= remaining:
                extras.append(bullet_text)
                remaining -= tokens

        readme = repo.get("readme", "")
        if readme and remaining > 100:
            readme_preview = readme[:500].replace("\n", " ").strip()
            tokens = count_tokens(readme_preview, self.tokenizer_model)
            if tokens <= remaining:
                extras.append(f"Readme: {readme_preview}")
            else:
                truncated = truncate_at_sentence_boundary(readme_preview, remaining, self.tokenizer_model)
                if truncated:
                    extras.append(f"Readme: {truncated}")

        full = core + "\n" + "\n".join(extras) if extras else core
        return full

    def get_token_usage(self, text: str) -> dict:
        tokens = count_tokens(text, self.tokenizer_model)
        return {
            "tokens": tokens,
            "budget": self.max_tokens,
            "utilization": round(tokens / self.max_tokens * 100, 1),
            "remaining": self.max_tokens - tokens,
        }
