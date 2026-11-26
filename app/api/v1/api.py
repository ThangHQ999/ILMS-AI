from fastapi import APIRouter

api_v1_router = APIRouter()

tutor_router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])
# tutor_router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])
# tutor_router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])
# tutor_router = APIRouter(prefix="/tutor", tags=["AI Socratic Tutor"])

api_v1_router.include_router(tutor_router)
