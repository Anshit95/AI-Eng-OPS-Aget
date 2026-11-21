from pathlib import Path

from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
import backend.app.models  # ensure models are discovered
from backend.app.rag.retriever import index_all_documents

# Import API Routers
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.services import router as services_router
from backend.app.api.v1.incidents import router as incidents_router
from backend.app.api.v1.investigations import router as investigations_router
from backend.app.api.v1.logs_metrics import router as logs_metrics_router
from backend.app.api.v1.deployments import router as deployments_router
from backend.app.api.v1.security import router as security_router
from backend.app.api.v1.actions import router as actions_router
from backend.app.api.v1.ml_models import router as ml_router
from backend.app.api.v1.knowledge import router as knowledge_router
from backend.app.api.v1.agent import router as agent_router
from backend.app.api.v1.evaluation import router as evaluation_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ops_agent")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Initializing operational database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = index_all_documents(db)
        if count > 0:
            logger.info(f"Indexed {count} RAG document chunks on startup.")
    except Exception as e:
        logger.warning(f"RAG startup indexing note: {e}")
    finally:
        db.close()
    logger.info(f"AI Engineering Operations Agent backend started in {settings.ENVIRONMENT} mode.")
    yield
    # Shutdown logic
    logger.info("Shutting down AI Engineering Operations Agent backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise AI Operations Agent with AI Security Engineering & Security Intelligence",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Safe Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal operational error occurred. Details have been logged for forensic audit."}
    )

# Root Health Endpoints
@app.get("/health", tags=["Health"])
def root_health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_docs": "/docs"
    }

# Register Versioned API v1 Routers
api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=f"{api_v1}/auth", tags=["Authentication & RBAC"])
app.include_router(health_router, prefix=f"{api_v1}/health", tags=["Health & Readiness"])
app.include_router(dashboard_router, prefix=f"{api_v1}/dashboard", tags=["Dashboard & Operations"])
app.include_router(services_router, prefix=f"{api_v1}/services", tags=["Services & Infrastructure"])
app.include_router(incidents_router, prefix=f"{api_v1}/incidents", tags=["Incidents & Timelines"])
app.include_router(investigations_router, prefix=f"{api_v1}/investigations", tags=["AI Investigations"])
app.include_router(logs_metrics_router, prefix=f"{api_v1}/observability", tags=["Telemetry & Logs"])
app.include_router(deployments_router, prefix=f"{api_v1}/deployments", tags=["Deployments & Git"])
app.include_router(security_router, prefix=f"{api_v1}/security", tags=["Security Intelligence & IAM"])
app.include_router(actions_router, prefix=f"{api_v1}/actions", tags=["Remediation & Approval Queue"])
app.include_router(ml_router, prefix=f"{api_v1}/ml", tags=["Machine Learning Pipelines"])
app.include_router(knowledge_router, prefix=f"{api_v1}/knowledge", tags=["RAG Knowledge Base"])
app.include_router(agent_router, prefix=f"{api_v1}/agent", tags=["Google ADK Agent Orchestration"])
app.include_router(evaluation_router, prefix=f"{api_v1}/evaluation", tags=["Benchmark & Evaluation Runs"])

# ============================================================
# FRONTEND SERVING - React + Vite on the same Render domain
# ============================================================

FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if FRONTEND_DIST.is_dir():

    # Serve compiled frontend assets
    assets_dir = FRONTEND_DIST / "assets"

    if assets_dir.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=str(assets_dir)),
            name="frontend-assets"
        )

    # Main dashboard homepage
    @app.get("/", include_in_schema=False)
    async def serve_frontend():
        return FileResponse(str(FRONTEND_DIST / "index.html"))

    # React SPA routing and static file fallback
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_routes(full_path: str):

        # Keep unknown API requests as API 404s
        if full_path == "api" or full_path.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )

        # Serve an existing frontend file
        requested_file = (FRONTEND_DIST / full_path).resolve()

        if (
            requested_file.is_file()
            and requested_file.is_relative_to(FRONTEND_DIST.resolve())
        ):
            return FileResponse(str(requested_file))

        # Otherwise return React homepage for client-side routing
        return FileResponse(str(FRONTEND_DIST / "index.html"))

