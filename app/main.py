from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
import os

app = FastAPI(title="LBM Arena API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Ensure database tables exist on startup"""
    try:
        # Create tables if they don't exist (safe operation)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables verified on startup")
    except Exception as e:
        print(f"⚠️  Database table creation failed on startup: {e}")

# Update CORS for production deployment
allowed_origins = [
    "http://localhost:3000",
    "https://jonaspetersen.com", 
    "https://lbm-arena-frontend.onrender.com",
    # Add your custom domain here if you have one
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "LBM Arena API", 
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "database": "connected" if settings.database_url else "not configured",
        "redis": "connected" if settings.redis_url else "not configured",
        "openai": "configured" if settings.openai_api_key else "not configured",
        "anthropic": "configured" if settings.anthropic_api_key else "not configured"
    }
