import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import SkillGapAnalysis
from app.schemas.skill_gap import SkillGapAnalysisCreate


async def create_skill_gap_analysis(
    db: AsyncSession, user_id: uuid.UUID, data: SkillGapAnalysisCreate
) -> SkillGapAnalysis:
    analysis = SkillGapAnalysis(user_id=user_id, **data.model_dump())
    db.add(analysis)
    await db.flush()
    await db.refresh(analysis)
    return analysis


async def get_user_analyses(db: AsyncSession, user_id: uuid.UUID) -> list[SkillGapAnalysis]:
    result = await db.execute(
        select(SkillGapAnalysis).where(SkillGapAnalysis.user_id == user_id).order_by(SkillGapAnalysis.created_at.desc())
    )
    return list(result.scalars().all())
