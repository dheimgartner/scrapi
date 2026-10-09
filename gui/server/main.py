from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from gui.server.routes.pipeline import router as pipeline_router
from gui.server.routes.registry import router as registry_router

app = FastAPI(title="Scrapi GUI")

app.include_router(registry_router)
app.include_router(pipeline_router)

_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
