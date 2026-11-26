from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.db.lifespan import db_lifespan
from app.core.config import Settings
from app.api.v1.endpoints.router import api_v1_router

settings = Settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API cho hệ thống hướng dẫn học tập Socratic",
    version=settings.APP_VERSION,
    lifespan=db_lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.include_router(api_v1_router, prefix="/api/v1")

# Endpoint Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME, "version": settings.APP_VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)