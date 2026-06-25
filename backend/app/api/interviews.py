import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.schemas.interview import InterviewSessionCreate, InterviewSessionUpdate, InterviewSessionResponse
from app.services import interview_service

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_session(
    data: InterviewSessionCreate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await interview_service.create_interview_session(db, current_user_id, data)


@router.get("/", response_model=list[InterviewSessionResponse])
async def list_interview_sessions(
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await interview_service.list_user_sessions(db, current_user_id)


@router.get("/{session_id}", response_model=InterviewSessionResponse)
async def get_interview_session(
    session_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await interview_service.get_session(db, session_id, current_user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return session


@router.put("/{session_id}", response_model=InterviewSessionResponse)
async def update_interview_session(
    session_id: uuid.UUID,
    data: InterviewSessionUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await interview_service.get_session(db, session_id, current_user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    return await interview_service.update_session(db, session, data)
