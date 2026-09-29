from fastapi import APIRouter
from app.api.routes.auth import router as auth_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.profiling import router as profiling_router
from app.api.routes.schemas import router as schemas_router
from app.api.routes.transformations import router as transformations_router
from app.api.routes.validation import router as validation_router
from app.api.routes.versions import router as versions_router
from app.api.routes.ml_readiness import router as ml_readiness_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.export import router as export_router
from app.api.routes.visualizations import router as visualizations_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(datasets_router)
api_router.include_router(profiling_router)
api_router.include_router(schemas_router)
api_router.include_router(transformations_router)
api_router.include_router(validation_router)
api_router.include_router(versions_router)
api_router.include_router(ml_readiness_router)
api_router.include_router(jobs_router)
api_router.include_router(export_router)
api_router.include_router(visualizations_router)
