"""
FastAPI Backend Application Entrypoint - Phase 5 Complete
Serves Reconciliation Engine, AI Controller Agent, RAG Knowledge Engine, Health Endpoints,
Exportable Reports, and Dashboard SPA.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Load environment variables from .env
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from backend.api.routes import router as api_router
from backend.api.ai_routes import ai_router
from backend.api.agent_routes import agent_router
from backend.api.report_routes import report_router
from backend.api.health_routes import health_router
from backend.api.settings_routes import settings_router

app = FastAPI(
    title="AI Finance Controller - Production Platform API",
    description="Automated reconciliation platform with Policy RAG, Controlled Agent Tools, and Evaluation Engine.",
    version="5.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router)
app.include_router(api_router)
app.include_router(ai_router)
app.include_router(agent_router)
app.include_router(report_router)
app.include_router(settings_router)

class SafeStaticFiles(StaticFiles):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1000})
            return
        if scope["type"] != "http":
            return
        await super().__call__(scope, receive, send)

# Mount Dashboard static files
dashboard_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/", SafeStaticFiles(directory=dashboard_dir, html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
