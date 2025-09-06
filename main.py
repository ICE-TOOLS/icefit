from fastapi import FastAPI
from database import connect, close, db_instance
from routes.api import api_router

app = FastAPI(
    title="ICEFIT API",
    description="A comprehensive fitness and health tracking API",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_db_client():
    connect()
    app.mongodb = db_instance.db

@app.on_event("shutdown")
async def shutdown_db_client():
    close()

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "ICEFIT FastAPI backend is running!",
        "docs": "/docs",
        "api_health": "/api/health",
        "version": "1.0.0"
    }
