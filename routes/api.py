from fastapi import APIRouter
from routes.auth.auth import router as auth_router

# Create main API router
api_router = APIRouter()

# Include auth routes with v1 prefix
api_router.include_router(
    auth_router,
    prefix="/v1/auth",
    tags=["Authentication"]
)

# Health check endpoint for the API
@api_router.get("/health")
async def api_health_check():
    return {
        "status": "healthy",
        "message": "ICEFIT API is running",
        "version": "1.0.0"
    }