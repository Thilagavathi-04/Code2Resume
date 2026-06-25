import uuid
import re
import math
from collections import Counter
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import ATSReport, Resume, JobDescription
from app.schemas.job import ATSReportCreate

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "shall", "can", "need",
    "dare", "ought", "used", "this", "that", "these", "those", "i", "me",
    "my", "we", "our", "you", "your", "he", "him", "his", "she", "her",
    "it", "its", "they", "them", "their", "what", "which", "who", "whom",
    "where", "when", "why", "how", "all", "each", "every", "both", "few",
    "more", "most", "other", "some", "such", "no", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because", "if", "then",
    "else", "while", "about", "up", "out", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "again",
    "further", "once", "here", "there", "also", "over", "any", "well",
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#\.]', ' ', text)
    tokens = text.split()
    return [t for t in tokens if len(t) > 1 and t not in STOP_WORDS]


def extract_bigrams(tokens: list[str]) -> list[str]:
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]


def compute_tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {word: count / total for word, count in counts.items()}


def compute_idf(documents: list[list[str]]) -> dict[str, float]:
    n_docs = len(documents) or 1
    doc_freq = Counter()
    for doc in documents:
        unique = set(doc)
        for token in unique:
            doc_freq[token] += 1
    return {word: math.log((n_docs + 1) / (freq + 1)) + 1 for word, freq in doc_freq.items()}


def compute_tfidf(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = compute_tf(tokens)
    return {word: tf_val * idf.get(word, 1.0) for word, tf_val in tf.items()}


def extract_keywords_from_text(text: str) -> list[str]:
    tokens = tokenize(text)
    bigrams = extract_bigrams(tokens)
    all_terms = tokens + bigrams
    tf = compute_tf(all_terms)
    sorted_terms = sorted(tf.items(), key=lambda x: x[1], reverse=True)
    seen = set()
    keywords = []
    for term, _ in sorted_terms:
        if term not in seen:
            seen.add(term)
            keywords.append(term)
    return keywords[:50]


def analyze_text_match(resume_text: str, job_text: str) -> dict:
    resume_tokens = tokenize(resume_text)
    job_tokens = tokenize(job_text)

    resume_bigrams = extract_bigrams(resume_tokens)
    job_bigrams = extract_bigrams(job_tokens)

    resume_all = resume_tokens + resume_bigrams
    job_all = job_tokens + job_bigrams

    idf = compute_idf([resume_all, job_all])

    resume_tfidf = compute_tfidf(resume_all, idf)
    job_tfidf = compute_tfidf(job_all, idf)

    job_keywords = set(job_all)
    resume_keyword_set = set(resume_all)

    matched = []
    missing = []
    for kw in sorted(job_keywords, key=lambda x: job_tfidf.get(x, 0), reverse=True):
        if kw in resume_keyword_set:
            matched.append(kw)
        else:
            missing.append(kw)

    job_set_lower = {k.lower() for k in job_keywords}
    resume_set_lower = {k.lower() for k in resume_keyword_set}
    matched_lower = job_set_lower & resume_set_lower
    missing_lower = job_set_lower - resume_set_lower

    keyword_score = (len(matched_lower) / max(len(job_set_lower), 1)) * 100

    resume_len = len(resume_text.split())
    length_score = 0
    if resume_len < 50:
        length_score = 20
    elif resume_len < 150:
        length_score = 50
    elif resume_len <= 600:
        length_score = 100
    elif resume_len <= 1000:
        length_score = 80
    else:
        length_score = 60

    has_contact = bool(re.search(r'\b[\w.-]+@[\w.-]+\.\w+\b', resume_text))
    has_phone = bool(re.search(r'[\+]?[\d\-\(\)\s]{7,}', resume_text))
    has_education = bool(re.search(r'\b(education|degree|bachelor|master|phd|university|college|b\.?s\.?|m\.?s\.?)\b', resume_text, re.I))
    has_experience = bool(re.search(r'\b(experience|worked|employment|position|role|company|intern)\b', resume_text, re.I))
    has_projects = bool(re.search(r'\b(project|built|developed|created|implemented|designed)\b', resume_text, re.I))
    has_skills = bool(re.search(r'\b(skills|technologies|proficient|expertise|competenc)\b', resume_text, re.I))

    section_checks = [
        ("Contact Information", has_contact),
        ("Phone Number", has_phone),
        ("Education Section", has_education),
        ("Work Experience", has_experience),
        ("Projects Section", has_projects),
        ("Skills Section", has_skills),
    ]
    sections_passed = sum(1 for _, p in section_checks if p)
    section_score = (sections_passed / len(section_checks)) * 100

    formatting_issues = []
    if resume_len < 100:
        formatting_issues.append({"issue": "Resume is too short — aim for at least 200 words", "severity": "high"})
    if resume_len > 1500:
        formatting_issues.append({"issue": "Resume is very long — consider trimming to under 800 words", "severity": "medium"})
    if not has_contact:
        formatting_issues.append({"issue": "Missing contact information (email)", "severity": "high"})
    if not has_education:
        formatting_issues.append({"issue": "No education section detected", "severity": "medium"})
    if not has_experience:
        formatting_issues.append({"issue": "No work experience section detected", "severity": "medium"})
    if not has_projects:
        formatting_issues.append({"issue": "No projects section detected — add relevant projects", "severity": "low"})
    if not has_skills:
        formatting_issues.append({"issue": "No skills section detected", "severity": "medium"})

    bullets = len(re.findall(r'\\item|\\begin\{itemize\}|•|\- \w', resume_text))
    if resume_len > 100 and bullets < 3:
        formatting_issues.append({"issue": "Very few bullet points — use action verbs and bullet format", "severity": "medium"})

    numbers_in_resume = len(re.findall(r'\b\d+\b', resume_text))
    if resume_len > 100 and numbers_in_resume < 3:
        formatting_issues.append({"issue": "Add quantifiable achievements (numbers, percentages, metrics)", "severity": "medium"})

    overall_score = int(keyword_score * 0.45 + section_score * 0.30 + length_score * 0.25)
    overall_score = max(5, min(98, overall_score))

    suggestions = []
    top_missing = [m for m in missing_lower if len(m) > 2][:8]
    if top_missing:
        suggestions.append(f"Add these keywords to your resume: {', '.join(top_missing[:5])}")
    if not has_projects:
        suggestions.append("Include a Projects section with 2-4 relevant projects")
    if numbers_in_resume < 3:
        suggestions.append("Quantify achievements — use numbers, percentages, and metrics")
    if bullets < 3 and resume_len > 100:
        suggestions.append("Use bullet points with action verbs (Built, Developed, Implemented)")
    if not has_experience:
        suggestions.append("Add work experience or internship details")
    if resume_len < 150:
        suggestions.append("Expand your resume with more details about your experience and skills")
    if keyword_score < 40:
        suggestions.append("Tailor your resume keywords to match the job description more closely")

    return {
        "overall_score": overall_score,
        "section_scores": {
            "keywords": int(keyword_score),
            "formatting": int(section_score),
            "experience": int(100 if has_experience else 30),
            "education": int(100 if has_education else 40),
        },
        "keywords_found": len(matched_lower),
        "total_keywords": len(job_set_lower),
        "missing_keywords": top_missing,
        "matching_keywords": sorted(list(matched_lower))[:20],
        "formatting_issues": formatting_issues,
        "suggestions": suggestions,
        "health_check": [
            {"label": label, "passed": passed}
            for label, passed in section_checks
        ],
    }


async def analyze_resume_ats(
    db: AsyncSession,
    resume_id: uuid.UUID,
    job_description_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict:
    resume_result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id, Resume.is_deleted == False)
    )
    resume = resume_result.scalar_one_or_none()
    if not resume:
        return {"error": "Resume not found"}

    jd_result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_description_id,
            JobDescription.user_id == user_id,
            JobDescription.is_deleted == False,
        )
    )
    jd = jd_result.scalar_one_or_none()
    if not jd:
        return {"error": "Job description not found"}

    resume_text = _resume_to_text(resume)
    job_text = f"{jd.title or ''} {jd.description or ''} {' '.join(jd.keywords or [])}"

    return analyze_text_match(resume_text, job_text)


def _resume_to_text(resume) -> str:
    parts = []
    if resume.title:
        parts.append(resume.title)
    if resume.summary:
        parts.append(resume.summary)
    if resume.target_role:
        parts.append(resume.target_role)
    content = resume.content or {}
    if isinstance(content, dict):
        personal = content.get("personal", {})
        if isinstance(personal, dict):
            for v in personal.values():
                if v:
                    parts.append(str(v))
    for exp in (resume.experiences or []):
        parts.append(f"{getattr(exp, 'position', '')} {getattr(exp, 'company', '')} {getattr(exp, 'description', '')}")
        for h in (getattr(exp, 'highlights', None) or []):
            parts.append(str(h))
    for edu in (resume.educations or []):
        parts.append(f"{getattr(edu, 'degree', '')} {getattr(edu, 'field_of_study', '')} {getattr(edu, 'institution', '')}")
    for skill in (resume.skills or []):
        parts.append(f"{getattr(skill, 'name', '')} {getattr(skill, 'category', '')}")
    for cert in (resume.certifications or []):
        parts.append(f"{getattr(cert, 'name', '')} {getattr(cert, 'issuer', '')}")
    for proj in (resume.projects or []):
        parts.append(f"{getattr(proj, 'name', '')} {getattr(proj, 'description', '')}")
        techs = getattr(proj, 'technologies', None) or []
        if isinstance(techs, list):
            parts.append(" ".join(str(t) for t in techs))
    return " ".join(parts)


async def create_ats_report(
    db: AsyncSession, user_id: uuid.UUID, report_data: ATSReportCreate, analysis: dict
) -> ATSReport:
    report = ATSReport(
        user_id=user_id,
        resume_id=report_data.resume_id,
        job_description_id=report_data.job_description_id,
        overall_score=analysis["overall_score"],
        section_scores=analysis.get("section_scores"),
        missing_keywords=analysis.get("missing_keywords", []),
        formatting_issues=analysis.get("formatting_issues", []),
        suggestions=analysis.get("suggestions", []),
        raw_analysis=analysis,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)
    return report


async def get_user_ats_reports(db: AsyncSession, user_id: uuid.UUID) -> list[ATSReport]:
    result = await db.execute(
        select(ATSReport).where(ATSReport.user_id == user_id).order_by(ATSReport.created_at.desc())
    )
    return list(result.scalars().all())
