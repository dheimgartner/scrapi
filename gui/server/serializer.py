from scrapi.pipeline.schemas import GraphEdge, GraphNode, PipelineGraph


def graph_dict_to_pipeline_graph(data: dict) -> PipelineGraph:
    nodes = [
        GraphNode(id=n["id"], type=n["type"], data=n.get("data", {}))
        for n in data.get("nodes", [])
    ]
    edges = [
        GraphEdge(id=e["id"], source=e["source"], target=e["target"])
        for e in data.get("edges", [])
    ]
    return PipelineGraph(nodes=nodes, edges=edges)


def pipeline_graph_to_toml(graph: PipelineGraph) -> str:
    """Serializes a single-orchestrator PipelineGraph to TOML.

    Produces output compatible with the existing example_config.toml format.
    Multi-orchestrator graphs are not supported; use the /api/graph/run endpoint
    directly for those.
    """
    nodes_by_id = {n.id: n for n in graph.nodes}

    orch_nodes = [n for n in graph.nodes if n.type == "orchestrator"]
    if len(orch_nodes) != 1:
        raise ValueError(
            f"TOML export requires exactly one orchestrator node, found {len(orch_nodes)}"
        )

    orch = orch_nodes[0]
    scraper_nodes = [
        nodes_by_id[e.source]
        for e in graph.edges
        if e.target == orch.id and nodes_by_id[e.source].type == "scraper"
    ]
    renderer_ids = [
        e.target
        for e in graph.edges
        if e.source == orch.id and nodes_by_id[e.target].type == "renderer"
    ]
    renderer_node = nodes_by_id[renderer_ids[0]] if renderer_ids else None

    lines: list[str] = []

    llm = orch.data.get("llm", {})
    lines += [
        "[llm]",
        f'provider = "{llm.get("provider", "openai")}"',
        "",
        "[llm.config]",
    ]
    for k, v in llm.get("config", {}).items():
        lines.append(f"{k} = {_toml_value(v)}")
    lines.append("")

    inf = orch.data.get("inference", {})
    search = inf.get("search", {})
    summary = inf.get("summary", {})
    lines += [
        "[inference.search]",
        f'system_prompt = {_toml_value(search.get("system_prompt", ""))}',
        f'task_prompt = {_toml_value(search.get("task_prompt", ""))}',
        "",
        "[inference.summary]",
        f'system_prompt = {_toml_value(summary.get("system_prompt", ""))}',
        f'task_prompt = {_toml_value(summary.get("task_prompt", ""))}',
        "",
    ]

    for sc in scraper_nodes:
        lines.append("[[scrapers]]")
        lines.append(f'provider = "{sc.data.get("provider", "")}"')
        fetch = sc.data.get("fetch", {})
        if fetch:
            lines.append("[scrapers.fetch]")
            for k, v in fetch.items():
                lines.append(f"{k} = {_toml_value(v)}")
        lines.append("")

    if renderer_node:
        lines.append("[renderer]")
        lines.append(f'provider = "{renderer_node.data.get("provider", "")}"')
        output_path = renderer_node.data.get("output_path", "")
        if output_path:
            lines.append(f'output_path = "{output_path}"')
        lines.append("")

    return "\n".join(lines)


def _toml_value(v: object) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_toml_value(i) for i in v) + "]"
    return '"' + str(v).replace("\\", "\\\\").replace('"', '\\"') + '"'
