import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ExperienceCreate(BaseModel):
    company: str = Field(..., max_length=255)
    position: str = Field(..., max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    highlights: list[Any] = []
    order_index: int = 0


class ExperienceUpdate(BaseModel):
    company: Optional[str] = Field(None, max_length=255)
    position: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    highlights: Optional[list[Any]] = None
    order_index: Optional[int] = None


class ExperienceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool
    description: Optional[str] = None
    highlights: list[Any] = []
    order_index: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class EducationCreate(BaseModel):
    institution: str = Field(..., max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = Field(None, max_length=20)
    highlights: list[Any] = []
    order_index: int = 0


class EducationUpdate(BaseModel):
    institution: Optional[str] = Field(None, max_length=255)
    degree: Optional[str] = Field(None, max_length=255)
    field_of_study: Optional[str] = Field(None, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = Field(None, max_length=20)
    highlights: Optional[list[Any]] = None
    order_index: Optional[int] = None


class EducationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    highlights: list[Any] = []
    order_index: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class SkillCreate(BaseModel):
    name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    proficiency: Optional[str] = Field(None, max_length=50)
    years_experience: Optional[int] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    proficiency: Optional[str] = Field(None, max_length=50)
    years_experience: Optional[int] = None


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    name: str
    category: Optional[str] = None
    proficiency: Optional[str] = None
    years_experience: Optional[int] = None
    created_at: datetime


class CertificationCreate(BaseModel):
    name: str = Field(..., max_length=255)
    issuer: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)


class CertificationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    issuer: Optional[str] = Field(None, max_length=255)
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = Field(None, max_length=255)
    credential_url: Optional[str] = Field(None, max_length=500)


class CertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[str] = None
    created_at: datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    technologies: list[Any] = []
    highlights: list[Any] = []
    github_url: Optional[str] = Field(None, max_length=500)
    live_url: Optional[str] = Field(None, max_length=500)
    order_index: int = 0


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    technologies: Optional[list[Any]] = None
    highlights: Optional[list[Any]] = None
    github_url: Optional[str] = Field(None, max_length=500)
    live_url: Optional[str] = Field(None, max_length=500)
    order_index: Optional[int] = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    name: str
    description: Optional[str] = None
    technologies: list[Any] = []
    highlights: list[Any] = []
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    order_index: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class GeneratedResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    filename: str
    file_path: str
    file_size: Optional[int] = None
    format: str
    content_hash: Optional[str] = None
    created_at: datetime


class ResumeCreate(BaseModel):
    title: str = Field("Untitled Resume", max_length=255)
    template: str = Field("modern", max_length=50)
    summary: Optional[str] = None
    target_role: Optional[str] = Field(None, max_length=255)
    content: Optional[dict[str, Any]] = None


class ResumeUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    template: Optional[str] = Field(None, max_length=50)
    summary: Optional[str] = None
    target_role: Optional[str] = Field(None, max_length=255)
    content: Optional[dict[str, Any]] = None
    ats_score: Optional[int] = None


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    template: str
    summary: Optional[str] = None
    target_role: Optional[str] = None
    content: Optional[dict[str, Any]] = None
    ats_score: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    experiences: list[ExperienceResponse] = []
    educations: list[EducationResponse] = []
    skills: list[SkillResponse] = []
    certifications: list[CertificationResponse] = []
    projects: list[ProjectResponse] = []
    generated_files: list[GeneratedResumeResponse] = []


class ResumeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    template: str
    summary: Optional[str] = None
    target_role: Optional[str] = None
    ats_score: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
