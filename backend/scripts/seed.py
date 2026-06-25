import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import async_session_factory, init_db
from app.services.user_service import create_user, get_user_by_username
from app.services.resume_service import (
    create_resume, add_experience, add_education, add_skill, add_project,
)
from app.services.ats_service import analyze_resume_ats, create_ats_report
from app.schemas.user import UserCreate
from app.schemas.resume import (
    ResumeCreate, ExperienceCreate, EducationCreate, SkillCreate, ProjectCreate,
)
from app.schemas.job import ATSReportCreate


async def seed():
    await init_db()
    async with async_session_factory() as db:
        existing = await get_user_by_username(db, "demo_user")
        if existing:
            print(f"Demo user already exists (id={existing.id})")
            return

        user_data = UserCreate(
            username="demo_user",
            email="demo@code2resume.com",
            password="demo123456",
            github_url="https://github.com/demo_user",
        )
        from app.api.auth import get_password_hash
        hashed = get_password_hash(user_data.password)
        user = await create_user(db, user_data, hashed)
        print(f"Created user: {user.username} (id={user.id})")

        resume_data = ResumeCreate(
            title="Full Stack Developer Resume",
            template="modern",
            summary="Experienced full-stack developer with 5+ years building web applications.",
            target_role="Senior Full Stack Developer",
        )
        resume = await create_resume(db, user.id, resume_data)
        print(f"Created resume: {resume.title} (id={resume.id})")

        await add_experience(db, resume.id, ExperienceCreate(
            company="TechCorp",
            position="Senior Developer",
            start_date="2021-01",
            end_date="2024-01",
            description="Led development of microservices architecture",
            highlights=["Reduced API latency by 40%", "Mentored 3 junior developers"],
        ))
        await add_experience(db, resume.id, ExperienceCreate(
            company="StartupXYZ",
            position="Full Stack Developer",
            start_date="2019-06",
            end_date="2021-01",
            description="Built customer-facing web application",
            highlights=["Shipped MVP in 3 months", "Served 10K+ daily users"],
        ))

        await add_education(db, resume.id, EducationCreate(
            institution="State University",
            degree="B.S.",
            field_of_study="Computer Science",
            start_date="2015-09",
            end_date="2019-05",
            gpa="3.8",
        ))

        for skill_name in ["Python", "JavaScript", "React", "PostgreSQL", "Docker", "AWS", "Git"]:
            await add_skill(db, resume.id, SkillCreate(
                name=skill_name,
                category="technical" if skill_name in ["Python", "JavaScript", "React"] else "tools",
                proficiency="advanced",
                years_experience=4,
            ))

        await add_project(db, resume.id, ProjectCreate(
            name="E-Commerce Platform",
            description="Full-stack e-commerce application with payment processing",
            technologies=["React", "Node.js", "PostgreSQL", "Stripe"],
            highlights=["Handled $1M+ in transactions", "99.9% uptime"],
            github_url="https://github.com/demo_user/ecommerce",
        ))

        analysis = await analyze_resume_ats({}, ["python", "react", "docker"])
        report = await create_ats_report(db, user.id, ATSReportCreate(resume_id=resume.id), analysis)
        print(f"Created ATS report (score={report.overall_score})")

        await db.commit()
        print("Seed completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
