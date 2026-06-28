import re
from typing import Any, Dict, List


SECTION_PATTERNS = {
    "overview": [
        r"^#{1,3}\s*(overview|about|description|introduction|what is|summary)",
    ],
    "problem_statement": [
        r"^#{1,3}\s*(problem|challenge|issue|motivation|why|背景)",
    ],
    "features": [
        r"^#{1,3}\s*(features|highlights|key features|what it does|capabilities)",
    ],
    "installation": [
        r"^#{1,3}\s*(installation|install|setup|getting started|quick start|prerequisites)",
    ],
    "usage": [
        r"^#{1,3}\s*(usage|how to use|examples|demo|quick start)",
    ],
    "architecture": [
        r"^#{1,3}\s*(architecture|structure|design|system design|components)",
    ],
    "api": [
        r"^#{1,3}\s*(api|endpoints|routes|rest|graphql|reference)",
    ],
    "screenshots": [
        r"^#{1,3}\s*(screenshots?|images?|preview|demo|visualization|media)",
    ],
    "demo": [
        r"^#{1,3}\s*(demo|live|playground|try it)",
    ],
    "license": [
        r"^#{1,3}\s*(license|licence|legal)",
    ],
    "contributing": [
        r"^#{1,3}\s*(contributing|contribution|how to contribute|development)",
    ],
    "changelog": [
        r"^#{1,3}\s*(changelog|release notes|updates|history)",
    ],
    "acknowledgments": [
        r"^#{1,3}\s*(acknowledgments?|credits|thanks|shoutout)",
    ],
    "roadmap": [
        r"^#{1,3}\s*(roadmap|future|plans|todo|upcoming)",
    ],
    "contact": [
        r"^#{1,3}\s*(contact|reach out|support|help)",
    ],
}


def analyze_documentation(readme: str) -> dict:
    if not readme:
        return _empty()

    sections_found = []
    section_content = {}

    lines = readme.split("\n")
    for i, line in enumerate(lines):
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, line.strip(), re.IGNORECASE):
                    if section_name not in sections_found:
                        sections_found.append(section_name)
                        content_lines = []
                        for j in range(i + 1, min(i + 20, len(lines))):
                            if lines[j].strip().startswith("#"):
                                break
                            if lines[j].strip():
                                content_lines.append(lines[j].strip())
                        section_content[section_name] = " ".join(content_lines)[:500]
                    break

    total_sections = len(SECTION_PATTERNS)
    found_count = len(sections_found)

    completeness_score = round((found_count / total_sections) * 10, 1)

    has_badges = bool(re.search(r"!\[.*\]\(.*badge.*\)", readme, re.IGNORECASE))
    has_code_blocks = len(re.findall(r"```", readme)) >= 2
    has_links = len(re.findall(r"\[.*?\]\(.*?\)", readme)) > 0
    has_images = bool(re.search(r"!\[.*?\]\(.*?\)", readme))
    has_table_of_contents = bool(re.search(r"(toc|table of contents|## contents)", readme, re.IGNORECASE))

    has_installation = "installation" in sections_found or "getting started" in sections_found
    has_usage = "usage" in sections_found
    has_license = "license" in sections_found

    quality_score = 0.0
    if has_installation:
        quality_score += 2.0
    if has_usage:
        quality_score += 2.0
    if has_license:
        quality_score += 1.0
    if has_code_blocks:
        quality_score += 1.5
    if has_badges:
        quality_score += 0.5
    if has_links:
        quality_score += 0.5
    if has_images:
        quality_score += 0.5
    if has_table_of_contents:
        quality_score += 0.5
    if len(readme) > 2000:
        quality_score += 1.0
    elif len(readme) > 500:
        quality_score += 0.5

    quality_score = round(min(10.0, quality_score), 1)

    missing_sections = [
        s for s in ["installation", "usage", "license", "contributing", "api"]
        if s not in sections_found
    ]

    return {
        "sections_found": sections_found,
        "section_content": section_content,
        "total_sections_found": found_count,
        "completeness_score": completeness_score,
        "quality_score": quality_score,
        "missing_sections": missing_sections,
        "has_badges": has_badges,
        "has_code_blocks": has_code_blocks,
        "has_links": has_links,
        "has_images": has_images,
        "has_table_of_contents": has_table_of_contents,
        "readme_length": len(readme),
    }


def _empty() -> dict:
    return {
        "sections_found": [],
        "section_content": {},
        "total_sections_found": 0,
        "completeness_score": 0,
        "quality_score": 0,
        "missing_sections": ["installation", "usage", "license", "contributing", "api"],
        "has_badges": False,
        "has_code_blocks": False,
        "has_links": False,
        "has_images": False,
        "has_table_of_contents": False,
        "readme_length": 0,
    }
