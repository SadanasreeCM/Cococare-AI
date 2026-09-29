import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routes import health, detection, history, statistics, chat, auth, farm, phase2_routes, phase3_routes, weather

# Initialize Database tables on application startup
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production Coconut Tree Disease Detection & Management API powered by Roboflow object detection & SQLite.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cococare.streamlit.app",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "*"  # Fallback if needed, but origins are explicitly listed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads directory
os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOADS_DIR), name="uploads")

# Include API Routers
app.include_router(health.router)
app.include_router(detection.router)
app.include_router(history.router)
app.include_router(statistics.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(farm.router)
app.include_router(phase2_routes.router)
app.include_router(phase3_routes.router)
app.include_router(weather.router)





@app.get("/health")
def simple_health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "service": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "status": "online",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
