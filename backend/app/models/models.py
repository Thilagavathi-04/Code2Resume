import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, ForeignKey, Index, Integer
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    github_url = Column(String(500), nullable=True)
    github_token = Column(String(500), nullable=True)
    linkedin_id = Column(String(255), nullable=True)
    leetcode_id = Column(String(255), nullable=True)
    mobile_number = Column(String(50), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    resumes = relationship("Resume", back_populates="user", lazy="selectin")
    job_descriptions = relationship("JobDescription", back_populates="user", lazy="selectin")
    ats_reports = relationship("ATSReport", back_populates="user", lazy="selectin")
    interview_sessions = relationship("InterviewSession", back_populates="user", lazy="selectin")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="Untitled Resume")
    template = Column(String(50), nullable=False, default="modern")
    summary = Column(Text, nullable=True)
    target_role = Column(String(255), nullable=True)
    content = Column(JSONB, nullable=True)
    ats_score = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="resumes")
    experiences = relationship("Experience", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")
    generated_files = relationship("GeneratedResume", back_populates="resume", lazy="selectin", cascade="all, delete-orphan")


class Experience(Base):
    __tablename__ = "experiences"
    __table_args__ = (Index("ix_experiences_resume_id", "resume_id"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    highlights = Column(JSONB, nullable=True, default=list)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    resume = relationship("Resume", back_populates="experiences")


class Education(Base):
    __tablename__ = "educations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    institution = Column(String(255), nullable=False)
    degree = Column(String(255), nullable=True)
    field_of_study = Column(String(255), nullable=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    gpa = Column(String(20), nullable=True)
    highlights = Column(JSONB, nullable=True, default=list)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    resume = relationship("Resume", back_populates="educations")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    proficiency = Column(String(50), nullable=True)
    years_experience = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    resume = relationship("Resume", back_populates="skills")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    expiry_date = Column(String(50), nullable=True)
    credential_id = Column(String(255), nullable=True)
    credential_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    resume = relationship("Resume", back_populates="certifications")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSONB, nullable=True, default=list)
    highlights = Column(JSONB, nullable=True, default=list)
    github_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    resume = relationship("Resume", back_populates="projects")


class GeneratedResume(Base):
    __tablename__ = "generated_resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    format = Column(String(20), nullable=False, default="pdf")
    content_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    resume = relationship("Resume", back_populates="generated_files")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(JSONB, nullable=True, default=list)
    keywords = Column(JSONB, nullable=True, default=list)
    match_score = Column(Integer, nullable=True)
    analysis = Column(JSONB, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="job_descriptions")
    ats_reports = relationship("ATSReport", back_populates="job_description", lazy="selectin")


class ATSReport(Base):
    __tablename__ = "ats_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    job_description_id = Column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=True)
    overall_score = Column(Integer, nullable=False, default=0)
    section_scores = Column(JSONB, nullable=True)
    missing_keywords = Column(JSONB, nullable=True, default=list)
    formatting_issues = Column(JSONB, nullable=True, default=list)
    suggestions = Column(JSONB, nullable=True, default=list)
    raw_analysis = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="ats_reports")
    job_description = relationship("JobDescription", back_populates="ats_reports")


class SkillGapAnalysis(Base):
    __tablename__ = "skill_gap_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    existing_skills = Column(JSONB, nullable=True, default=list)
    missing_skills = Column(JSONB, nullable=True, default=list)
    learning_recommendations = Column(JSONB, nullable=True, default=list)
    radar_data = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    session_type = Column(String(50), nullable=False, default="technical")
    questions = Column(JSONB, nullable=True, default=list)
    completed_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    difficulty = Column(String(20), nullable=True, default="medium")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="interview_sessions")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
