from scrapi.config.loader import parse_config

_system_prompt = """
You are a legal analyst at FINMA investigating whether or not a candidate is suitable to get a mandate.
A suitable candidate should be independent from the party it oversees.
"""

_task_prompt = "Given the information, evaluate whether or not the candidate is independent from the party."

_summary_prompt = """
Based on the context information, give a final verdict whether or not the candidate should get the mandate.
Make sure the source of your arguments is clearly stated.
"""

_query = "Sergio Ermotti AND UBS"

_config = {
    "scraper": {
        "provider": "yahoo",
        "config": {},
    },
    "inference": {
        "provider": "openai",
        "config": {},
    },
    "orchestrator": {
        "config": {
            "system_prompt": _system_prompt,
            "task_prompt": _task_prompt,
            "summary_prompt": _summary_prompt,
            "query": _query,
            "n": 1,
            "save": False,
        },
    },
}

DEFAULT_CONFIG = parse_config(_config)
