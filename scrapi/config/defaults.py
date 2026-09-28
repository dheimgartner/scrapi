from scrapi.config.loader import parse_config

_config = {
    "llm": {
        "provider": "ollama",
        "config": {},
    },
    "inference": {
        "search": {
            "system_prompt": "You are a helpful research analyst.",
            "task_prompt": "Given the information, summarize the key findings relevant to the query.",
        },
        "summary": {
            "system_prompt": "You are a helpful research analyst.",
            "task_prompt": "Based on all sources, provide a concise final summary. Cite your sources.",
        },
    },
    "scrapers": [
        {
            "provider": "dummy",
            "config": {},
            "fetch": {
                "query": "example query",
                "n": 1,
            },
        },
    ],
}

DEFAULT_CONFIG = parse_config(_config)
