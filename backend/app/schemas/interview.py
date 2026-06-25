import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewSessionCreate(BaseModel):
    title: str = Field(..., max_length=255)
    session_type: str = Field("technical", max_length=50)
    difficulty: Optional[str] = Field("medium", max_length=20)


class InterviewSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    session_type: Optional[str] = Field(None, max_length=50)
    questions: Optional[list[Any]] = None
    completed_count: Optional[int] = None
    total_count: Optional[int] = None
    difficulty: Optional[str] = Field(None, max_length=20)


class InterviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    session_type: str
    questions: list[Any] = []
    completed_count: int
    total_count: int
    difficulty: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
