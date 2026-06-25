import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.job import (
    JobDescriptionCreate, JobDescriptionResponse,
    ATSReportCreate, ATSReportResponse,
    JobMatchRequest, JobMatchResponse,
)
from app.services import job_service, ats_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_description(
    data: JobDescriptionCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.create_job_description(db, current_user_id, data)


@router.get("/", response_model=list[JobDescriptionResponse])
async def list_job_descriptions(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await job_service.get_user_job_descriptions(db, current_user_id)


@router.get("/{job_id}", response_model=JobDescriptionResponse)
async def get_job_description(
    job_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    jd = await job_service.get_job_description(db, job_id, current_user_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    return jd


@router.post("/analyze", response_model=JobMatchResponse)
async def analyze_job_match(
    data: JobMatchRequest,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await job_service.match_job_to_resume(db, data.resume_id, data.job_description_id, current_user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/ats", response_model=ATSReportResponse, status_code=status.HTTP_201_CREATED)
async def create_ats_report(
    data: ATSReportCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.resume_id and data.job_description_id:
        analysis = await ats_service.analyze_resume_ats(db, data.resume_id, data.job_description_id, current_user_id)
        if "error" in analysis:
            raise HTTPException(status_code=400, detail=analysis["error"])
    else:
        analysis = {
            "overall_score": 0,
            "section_scores": {},
            "missing_keywords": [],
            "formatting_issues": [],
            "suggestions": ["Please provide both a resume and job description for analysis"],
        }
    try:
        return await ats_service.create_ats_report(db, current_user_id, data, analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save ATS report: {str(e)}")


@router.get("/ats/reports", response_model=list[ATSReportResponse])
async def list_ats_reports(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ats_service.get_user_ats_reports(db, current_user_id)


@router.delete("/{job_id}", response_model=JobDescriptionResponse)
async def delete_job_description(
    job_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    jd = await job_service.get_job_description(db, job_id, current_user_id)
    if not jd:
        raise HTTPException(status_code=404, detail="Job description not found")
    jd.is_deleted = True
    await db.flush()
    await db.refresh(jd)
    return jd
