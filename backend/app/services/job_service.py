import uuid
import re
import math
from collections import Counter
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import JobDescription, Resume
from app.schemas.job import JobDescriptionCreate
from app.services.ats_service import analyze_text_match, _resume_to_text


async def create_job_description(db: AsyncSession, user_id: uuid.UUID, data: JobDescriptionCreate) -> JobDescription:
    jd = JobDescription(user_id=user_id, **data.model_dump())
    db.add(jd)
    await db.flush()
    await db.refresh(jd)
    return jd


async def get_job_description(db: AsyncSession, job_id: uuid.UUID, user_id: uuid.UUID) -> Optional[JobDescription]:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id, JobDescription.user_id == user_id, JobDescription.is_deleted == False
        )
    )
    return result.scalar_one_or_none()


async def get_user_job_descriptions(db: AsyncSession, user_id: uuid.UUID) -> list[JobDescription]:
    result = await db.execute(
        select(JobDescription).where(
            JobDescription.user_id == user_id, JobDescription.is_deleted == False
        ).order_by(JobDescription.created_at.desc())
    )
    return list(result.scalars().all())


async def match_job_to_resume(db: AsyncSession, resume_id: uuid.UUID, job_id: uuid.UUID, user_id: uuid.UUID) -> dict:
    resume_result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id, Resume.is_deleted == False)
    )
    resume = resume_result.scalar_one_or_none()
    if not resume:
        return {"error": "Resume not found"}

    jd_result = await db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id, JobDescription.user_id == user_id, JobDescription.is_deleted == False
        )
    )
    jd = jd_result.scalar_one_or_none()
    if not jd:
        return {"error": "Job description not found"}

    resume_text = _resume_to_text(resume)
    job_text = f"{jd.title or ''} {jd.description or ''} {' '.join(jd.keywords or [])}"

    analysis = analyze_text_match(resume_text, job_text)

    missing_list = analysis.get("missing_keywords", [])
    matched_list = analysis.get("matching_keywords", [])

    recommendations = []
    if analysis["overall_score"] < 50:
        recommendations.append("Your resume needs significant tailoring for this position")
    if len(missing_list) > 3:
        recommendations.append(f"Add these key skills: {', '.join(missing_list[:5])}")
    recommendations.append("Quantify your achievements with specific metrics and numbers")
    recommendations.append("Use keywords from the job description naturally in your resume")
    if analysis["section_scores"].get("experience", 0) < 60:
        recommendations.append("Expand your work experience with relevant details")
    if analysis["section_scores"].get("keywords", 0) < 50:
        recommendations.append("Include more technical keywords matching the job requirements")

    return {
        "match_score": analysis["overall_score"],
        "matching_keywords": matched_list[:15],
        "missing_keywords": missing_list[:10],
        "recommendations": recommendations,
        "breakdown": [
            {"category": "Keyword Match", "score": analysis["section_scores"]["keywords"]},
            {"category": "Section Coverage", "score": analysis["section_scores"]["formatting"]},
            {"category": "Experience", "score": analysis["section_scores"]["experience"]},
            {"category": "Education", "score": analysis["section_scores"]["education"]},
        ],
        "required_skills": matched_list + missing_list,
        "your_skills": matched_list,
    }
