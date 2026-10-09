from fastapi import APIRouter

from scrapi.config.registry import LLM_REGISTRY, RENDERER_REGISTRY, SCRAPER_REGISTRY

router = APIRouter()


@router.get("/api/registry")
def get_registry() -> dict:
    return {
        "scrapers": list(SCRAPER_REGISTRY.keys()),
        "llms": list(LLM_REGISTRY.keys()),
        "renderers": list(RENDERER_REGISTRY.keys()),
    }
