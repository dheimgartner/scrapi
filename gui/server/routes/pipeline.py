from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel

from gui.server.serializer import graph_dict_to_pipeline_graph, pipeline_graph_to_toml
from scrapi.config.registry import LLM_REGISTRY, RENDERER_REGISTRY, SCRAPER_REGISTRY
from scrapi.pipeline.executor import PipelineExecutor, _topological_sort

router = APIRouter()


class GraphRequest(BaseModel):
    nodes: list[dict]
    edges: list[dict]


def _graph_payload(req: GraphRequest) -> dict:
    return {"nodes": req.nodes, "edges": req.edges}


def _validate(req: GraphRequest) -> list[str]:
    errors: list[str] = []

    for node in req.nodes:
        t = node.get("type")
        data = node.get("data", {})
        if t == "scraper":
            p = data.get("provider", "")
            if p not in SCRAPER_REGISTRY:
                errors.append(f"Unknown scraper provider: '{p}'")
        elif t == "orchestrator":
            p = data.get("llm", {}).get("provider", "")
            if p not in LLM_REGISTRY:
                errors.append(f"Unknown LLM provider: '{p}'")
        elif t == "renderer":
            p = data.get("provider", "")
            if p not in RENDERER_REGISTRY:
                errors.append(f"Unknown renderer provider: '{p}'")

    try:
        graph = graph_dict_to_pipeline_graph(_graph_payload(req))
        _topological_sort(graph.nodes, graph.edges)
    except ValueError as e:
        errors.append(str(e))

    return errors


@router.post("/api/graph/validate")
def validate(req: GraphRequest) -> dict:
    errors = _validate(req)
    return {"valid": len(errors) == 0, "errors": errors}


@router.post("/api/graph/export", response_class=PlainTextResponse)
def export_toml(req: GraphRequest) -> str:
    try:
        graph = graph_dict_to_pipeline_graph(_graph_payload(req))
        return pipeline_graph_to_toml(graph)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


async def _run_stream(req: GraphRequest) -> AsyncIterator[str]:
    yield _sse({"status": "starting", "message": "Parsing graph..."})

    try:
        graph = graph_dict_to_pipeline_graph(_graph_payload(req))
    except Exception as e:
        yield _sse({"status": "error", "message": str(e)})
        return

    yield _sse({"status": "running", "message": "Executing pipeline..."})

    loop = asyncio.get_event_loop()
    try:
        run_result = await loop.run_in_executor(None, PipelineExecutor().execute, graph)
    except Exception as e:
        yield _sse({"status": "error", "message": str(e)})
        return

    yield _sse({"status": "done", "message": run_result.summary.result})


@router.post("/api/graph/run")
async def run(req: GraphRequest) -> StreamingResponse:
    return StreamingResponse(_run_stream(req), media_type="text/event-stream")
