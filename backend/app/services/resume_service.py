import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Resume, Experience, Education, Skill, Certification, Project
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ExperienceCreate, EducationCreate,
    SkillCreate, CertificationCreate, ProjectCreate,
)


async def create_resume(db: AsyncSession, user_id: uuid.UUID, resume_data: ResumeCreate) -> Resume:
    resume = Resume(user_id=user_id, **resume_data.model_dump())
    db.add(resume)
    await db.flush()
    await db.refresh(resume)
    return resume


async def get_resume(db: AsyncSession, resume_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Resume]:
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id, Resume.is_deleted == False)
    )
    return result.scalar_one_or_none()


async def list_user_resumes(db: AsyncSession, user_id: uuid.UUID) -> list[Resume]:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id, Resume.is_deleted == False).order_by(Resume.created_at.desc())
    )
    return list(result.scalars().all())


async def update_resume(db: AsyncSession, resume: Resume, resume_data: ResumeUpdate) -> Resume:
    update_data = resume_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)
    await db.flush()
    await db.refresh(resume)
    return resume


async def delete_resume(db: AsyncSession, resume: Resume) -> Resume:
    resume.is_deleted = True
    await db.flush()
    await db.refresh(resume)
    return resume


async def add_experience(db: AsyncSession, resume_id: uuid.UUID, data: ExperienceCreate) -> Experience:
    exp = Experience(resume_id=resume_id, **data.model_dump())
    db.add(exp)
    await db.flush()
    await db.refresh(exp)
    return exp


async def add_education(db: AsyncSession, resume_id: uuid.UUID, data: EducationCreate) -> Education:
    edu = Education(resume_id=resume_id, **data.model_dump())
    db.add(edu)
    await db.flush()
    await db.refresh(edu)
    return edu


async def add_skill(db: AsyncSession, resume_id: uuid.UUID, data: SkillCreate) -> Skill:
    skill = Skill(resume_id=resume_id, **data.model_dump())
    db.add(skill)
    await db.flush()
    await db.refresh(skill)
    return skill


async def add_certification(db: AsyncSession, resume_id: uuid.UUID, data: CertificationCreate) -> Certification:
    cert = Certification(resume_id=resume_id, **data.model_dump())
    db.add(cert)
    await db.flush()
    await db.refresh(cert)
    return cert


async def add_project(db: AsyncSession, resume_id: uuid.UUID, data: ProjectCreate) -> Project:
    proj = Project(resume_id=resume_id, **data.model_dump())
    db.add(proj)
    await db.flush()
    await db.refresh(proj)
    return proj
