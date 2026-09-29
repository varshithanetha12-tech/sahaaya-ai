import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.assessment import router as assessment_router
from app.api.cases import router as cases_router
from app.api.followups import router as followups_router
from app.api.resources import router as resources_router
from app.api.analytics import router as analytics_router
from app.api.admin import router as admin_router
from app.api.audit import router as audit_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Sahaaya AI – Real-Time Stress & Trauma Support",
    description=(
        "AI-assisted Real-Time Stress and Trauma Assessment Platform for national atrocity helplines, "
        "integrated grievance portals, chatbots, IVRS, and digital interfaces. "
        "Victim-centric AI decision-support and triage system."
    ),
    version="2.4.0"
)

# Production-safe CORS configuration
raw_origins = os.environ.get("CORS_ORIGINS", "*")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
if not origins:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Register API Routers
app.include_router(assessment_router)
app.include_router(cases_router)
app.include_router(followups_router)
app.include_router(resources_router)
app.include_router(analytics_router)
app.include_router(admin_router)
app.include_router(audit_router)
app.include_router(auth_router)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Sahaaya AI Platform API is online."}

@app.get("/manifest.json")
async def manifest_shortcut():
    manifest_file = os.path.join(static_dir, "manifest.json")
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file, media_type="application/manifest+json")
    return {"name": "Sahaaya AI"}

@app.get("/sw.js")
async def sw_shortcut():
    sw_file = os.path.join(static_dir, "sw.js")
    if os.path.exists(sw_file):
        return FileResponse(sw_file, media_type="application/javascript")
    return ""

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Sahaaya AI",
        "version": "2.4.0",
        "mode": "production" if os.environ.get("ENV", "development").lower() == "production" else "development"
    }
