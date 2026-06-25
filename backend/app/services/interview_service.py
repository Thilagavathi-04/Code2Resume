import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import InterviewSession
from app.schemas.interview import InterviewSessionCreate, InterviewSessionUpdate


async def create_interview_session(
    db: AsyncSession, user_id: uuid.UUID, data: InterviewSessionCreate
) -> InterviewSession:
    session = InterviewSession(user_id=user_id, **data.model_dump())
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID) -> Optional[InterviewSession]:
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
            InterviewSession.is_deleted == False,
        )
    )
    return result.scalar_one_or_none()


async def list_user_sessions(db: AsyncSession, user_id: uuid.UUID) -> list[InterviewSession]:
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.user_id == user_id, InterviewSession.is_deleted == False
        ).order_by(InterviewSession.created_at.desc())
    )
    return list(result.scalars().all())


async def update_session(
    db: AsyncSession, session: InterviewSession, data: InterviewSessionUpdate
) -> InterviewSession:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    await db.flush()
    await db.refresh(session)
    return session
