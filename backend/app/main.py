from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.database import engine, Base
from app.api.routes import api_router
from app.core.storage import storage_service
import app.models # ensure all models are registered

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DataForge API",
    description="Intelligent Data Preparation & ML Readiness Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False
)

# CORS
origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Dataset-Id", "X-Version-Number", "X-Row-Count", "X-Column-Count"]
)

# Health Checks
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "DataForge Backend",
        "version": "1.0.0",
        "storage_backend": settings.STORAGE_BACKEND
    }

@app.get("/health/ready", status_code=status.HTTP_200_OK, tags=["Health"])
def readiness_check():
    db_ok = False
    storage_ok = False

    # Check DB
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    # Check Storage
    try:
        storage_ok = storage_service.is_ready()
    except Exception:
        storage_ok = False

    return {
        "status": "ready" if (db_ok and storage_ok) else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "storage": "connected" if storage_ok else "unreachable"
    }

# Include all API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
