import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class SkillGapAnalysisCreate(BaseModel):
    existing_skills: list[Any] = []
    missing_skills: list[Any] = []
    learning_recommendations: list[Any] = []
    radar_data: Optional[dict[str, Any]] = None


class SkillGapAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    existing_skills: list[Any] = []
    missing_skills: list[Any] = []
    learning_recommendations: list[Any] = []
    radar_data: Optional[dict[str, Any]] = None
    created_at: datetime
