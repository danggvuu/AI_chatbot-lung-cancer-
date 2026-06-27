import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from .routes import chat, sources, health
import yaml

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo 1 lần duy nhất khi server bắt đầu
    from rag_engine.chat_service import ChatService
    app.state.chat_service = ChatService()
    yield
    # Cleanup khi server tắt
    if hasattr(app.state, "chat_service"):
        qdrant_store = getattr(app.state.chat_service.retriever, "qdrant", None)
        if qdrant_store and hasattr(qdrant_store, "client"):
            qdrant_store.client.close()

def create_app() -> FastAPI:
    app = FastAPI(title="LungCare AI API", version="2.0.0", lifespan=lifespan)

    # Load config
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            settings = yaml.safe_load(f)
            cors_origins = settings.get("server", {}).get("cors_origins", ["*"])
    except Exception:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat.router, prefix="/api")
    app.include_router(sources.router, prefix="/api")
    app.include_router(health.router, prefix="/api")

    # Serve React frontend build if available
    FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    if os.path.isdir(FRONTEND_DIST):
        app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

        @app.get("/")
        async def index():
            return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

        @app.get("/favicon.svg")
        async def favicon():
            return FileResponse(os.path.join(FRONTEND_DIST, "favicon.svg"))

        @app.get("/icons.svg")
        async def icons():
            return FileResponse(os.path.join(FRONTEND_DIST, "icons.svg"))

    # Mount static for R plots
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")), name="static")

    return app
