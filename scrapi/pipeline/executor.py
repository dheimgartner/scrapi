from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
from typing import Any

from scrapi.config.registry import LLM_REGISTRY, RENDERER_REGISTRY, SCRAPER_REGISTRY
from scrapi.config.schemas import (
    InferenceConfig,
    LLMConfig,
    RendererConfig,
    ScraperConfig,
    ScrapiConfig,
    SearchInferenceConfig,
    SummaryInferenceConfig,
)
from scrapi.factory import _base_factory
from scrapi.inference.search import SearchInference
from scrapi.inference.summary import SummaryInference
from scrapi.models.run_result import RunResult
from scrapi.models.search_result import SuccessfulSearch, WebSearchResult
from scrapi.orchestrator import Orchestrator
from scrapi.pipeline.schemas import GraphEdge, GraphNode, PipelineGraph
from scrapi.scraping.base import BaseScraper


class SyntheticScraper(BaseScraper):
    """Wraps an upstream orchestrator's summary as a single search result.

    Enables chaining: the output text of one Orchestrator stage becomes the
    scraped input to the next without changing the Orchestrator interface.
    """

    def __init__(self, content: str, source_id: str) -> None:
        self._content = content
        self._source_id = source_id

    def _fetch_content(self, **_kwargs: Any) -> list[WebSearchResult]:
        return [
            WebSearchResult(
                scraper_repr=repr(SyntheticScraper),
                status=SuccessfulSearch(status=200),
                fetched_at=datetime.now(),
                source={"synthetic_from": self._source_id},
                raw_content=self._content,
                ai_content=self._content,
            )
        ]

    @staticmethod
    def convert_to_ai_content(raw_content: Any) -> str:
        return raw_content


def _topological_sort(nodes: list[GraphNode], edges: list[GraphEdge]) -> list[str]:
    in_degree: dict[str, int] = {n.id: 0 for n in nodes}
    adj: dict[str, list[str]] = defaultdict(list)

    for e in edges:
        adj[e.source].append(e.target)
        in_degree[e.target] += 1

    queue: deque[str] = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        nid = queue.popleft()
        order.append(nid)
        for neighbor in adj[nid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(nodes):
        raise ValueError("Pipeline graph contains a cycle")

    return order


class PipelineExecutor:
    """Executes a PipelineGraph by traversing the DAG in topological order.

    Scraper nodes are data sources, orchestrator nodes are processing stages,
    and renderer nodes are sinks. Upstream orchestrator summaries are injected
    into downstream stages via SyntheticScraper, enabling chaining without
    modifying the Orchestrator interface.
    """

    def execute(self, graph: PipelineGraph) -> RunResult:
        nodes_by_id = {n.id: n for n in graph.nodes}

        outgoing: dict[str, list[str]] = defaultdict(list)
        incoming: dict[str, list[str]] = defaultdict(list)
        for edge in graph.edges:
            outgoing[edge.source].append(edge.target)
            incoming[edge.target].append(edge.source)

        order = _topological_sort(graph.nodes, graph.edges)
        results: dict[str, RunResult] = {}

        for node_id in order:
            node = nodes_by_id[node_id]
            if node.type in ("scraper", "renderer"):
                continue

            scrapers: list[tuple[BaseScraper, dict]] = []
            for up_id in incoming[node_id]:
                up = nodes_by_id[up_id]
                if up.type == "scraper":
                    sc_cfg = ScraperConfig(
                        provider=up.data["provider"],
                        fetch=up.data.get("fetch", {}),
                        config=up.data.get("config", {}),
                    )
                    scrapers.append(
                        (_base_factory(SCRAPER_REGISTRY[sc_cfg.provider], sc_cfg), sc_cfg.fetch)
                    )
                elif up.type == "orchestrator":
                    scrapers.append(
                        (SyntheticScraper(content=results[up_id].summary.result, source_id=up_id), {})
                    )

            renderer_cfg: RendererConfig | None = None
            for down_id in outgoing[node_id]:
                dn = nodes_by_id[down_id]
                if dn.type == "renderer":
                    renderer_cfg = RendererConfig(
                        provider=dn.data["provider"],
                        output_path=dn.data.get("output_path") or None,
                    )

            orch_data = node.data
            llm_cfg = LLMConfig(
                provider=orch_data["llm"]["provider"],
                config=orch_data["llm"].get("config", {}),
            )
            inf_cfg = InferenceConfig(
                search=SearchInferenceConfig(
                    system_prompt=orch_data["inference"]["search"]["system_prompt"],
                    task_prompt=orch_data["inference"]["search"]["task_prompt"],
                ),
                summary=SummaryInferenceConfig(
                    system_prompt=orch_data["inference"]["summary"]["system_prompt"],
                    task_prompt=orch_data["inference"]["summary"]["task_prompt"],
                ),
            )

            llm = _base_factory(LLM_REGISTRY[llm_cfg.provider], llm_cfg)
            search_inference = SearchInference(
                llm=llm.llm,
                system_prompt=inf_cfg.search.system_prompt,
                task_prompt=inf_cfg.search.task_prompt,
            )
            summary_inference = SummaryInference(
                llm=llm.llm,
                system_prompt=inf_cfg.summary.system_prompt,
                task_prompt=inf_cfg.summary.task_prompt,
            )

            renderer = None
            if renderer_cfg is not None:
                renderer_cls = RENDERER_REGISTRY[renderer_cfg.provider]
                renderer = renderer_cls(output_path=renderer_cfg.output_path)

            results[node_id] = Orchestrator(
                scrapers=scrapers,
                search_inference=search_inference,
                summary_inference=summary_inference,
                renderer=renderer,
            ).run()

        orch_order = [nid for nid in order if nodes_by_id[nid].type == "orchestrator"]
        if not orch_order:
            raise ValueError("Graph contains no orchestrator nodes")
        return results[orch_order[-1]]
