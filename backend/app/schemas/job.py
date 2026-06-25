import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobDescriptionCreate(BaseModel):
    title: str = Field(..., max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: str
    requirements: list[Any] = []
    keywords: list[Any] = []


class JobDescriptionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    requirements: Optional[list[Any]] = None
    keywords: Optional[list[Any]] = None


class JobDescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    company: Optional[str] = None
    description: str
    requirements: list[Any] = []
    keywords: list[Any] = []
    match_score: Optional[int] = None
    analysis: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ATSReportCreate(BaseModel):
    resume_id: Optional[uuid.UUID] = None
    job_description_id: Optional[uuid.UUID] = None


class ATSReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    job_description_id: Optional[uuid.UUID] = None
    overall_score: int
    section_scores: Optional[dict[str, Any]] = None
    missing_keywords: list[Any] = []
    formatting_issues: list[Any] = []
    suggestions: list[Any] = []
    raw_analysis: Optional[dict[str, Any]] = None
    created_at: datetime


class JobMatchRequest(BaseModel):
    resume_id: uuid.UUID
    job_description_id: uuid.UUID


class JobMatchResponse(BaseModel):
    match_score: int
    matching_keywords: list[str] = []
    missing_keywords: list[str] = []
    recommendations: list[str] = []
