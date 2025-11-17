"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from .core.config import settings
from .core.database import connect_to_mongo, close_mongo_connection, connect_to_redis, close_redis_connection
from .api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Dark Web Monitoring Platform...")

    # Connect to databases
    await connect_to_mongo()
    connect_to_redis()

    # Create indexes
    from .core.database import db
    if db.db is not None:
        # Text index for search
        await db.db.threats.create_index([("title", "text"), ("content", "text")])
        # Index for queries
        await db.db.threats.create_index("discovered_at")
        await db.db.threats.create_index("severity")
        await db.db.threats.create_index("threat_type")
        await db.db.threats.create_index("source")
        logger.info("Database indexes created")

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_mongo_connection()
    close_redis_connection()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Dark Web Monitoring and Intelligence Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from .core.database import db

    health_status = {
        "status": "healthy",
        "mongodb": "connected" if db.db else "disconnected",
        "redis": "connected" if db.redis else "disconnected",
    }

    # Check database connections
    try:
        if db.db:
            await db.db.command("ping")
        if db.redis:
            db.redis.ping()
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)

    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
