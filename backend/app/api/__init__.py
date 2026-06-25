from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.interviews import router as interviews_router
from app.api.skill_gap import router as skill_gap_router

__all__ = [
    "auth_router", "users_router", "resumes_router",
    "jobs_router", "interviews_router", "skill_gap_router",
]
