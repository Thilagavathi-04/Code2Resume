import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.skill_gap import SkillGapAnalysisCreate, SkillGapAnalysisResponse
from app.services import skill_gap_service

router = APIRouter(prefix="/skill-gap", tags=["skill-gap"])


@router.post("/", response_model=SkillGapAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_gap_analysis(
    data: SkillGapAnalysisCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await skill_gap_service.create_skill_gap_analysis(db, current_user_id, data)


@router.get("/", response_model=list[SkillGapAnalysisResponse])
async def list_skill_gap_analyses(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await skill_gap_service.get_user_analyses(db, current_user_id)
