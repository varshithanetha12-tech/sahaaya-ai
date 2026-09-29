import os
from fastapi import FastAPI
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
    title="Sahaaya AI",
    description=(
        "AI-assisted Real-Time Stress and Trauma Assessment Platform for national atrocity helplines, "
        "integrated grievance portals, chatbots, IVRS, and digital interfaces. "
        "Victim-centric AI decision-support and triage system."
    ),
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
