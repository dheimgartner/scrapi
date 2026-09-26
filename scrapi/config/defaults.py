from scrapi.config.loader import parse_config

_system_prompt = "You are a helpful research analyst."

_task_prompt = "Given the information, summarize the key findings relevant to the query."

_summary_prompt = "Based on all sources, provide a concise final summary. Cite your sources."

_query = "example query"

_config = {
    "scraper": {
        "provider": "dummy",
        "config": {},
    },
    "inference": {
        "provider": "ollama",
        "config": {},
    },
    "orchestrator": {
        "config": {
            "system_prompt": _system_prompt,
            "task_prompt": _task_prompt,
            "summary_prompt": _summary_prompt,
            "query": _query,
            "n": 1,
        },
    },
}

DEFAULT_CONFIG = parse_config(_config)
