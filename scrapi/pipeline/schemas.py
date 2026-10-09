from dataclasses import dataclass, field
from typing import Literal


@dataclass
class GraphNode:
    id: str
    type: Literal["scraper", "orchestrator", "renderer"]
    data: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    id: str
    source: str
    target: str


@dataclass
class PipelineGraph:
    nodes: list[GraphNode]
    edges: list[GraphEdge]
