# scrapi

Scrape the web and analyse the results with an LLM. Built for conflict-of-interest checks: given a search query, `scrapi` fetches pages, runs per-result inference, then produces a final summary verdict.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd <repo>
uv sync
source .venv/bin/activate
```

## Configuration

`scrapi` is configured with a YAML file. The three top-level keys are `scraper`, `inference`, and `orchestrator`.

```yaml
# config.yaml
scraper:
  provider: yahoo
  config: {}

inference:
  provider: openai
  config:
    azure_endpoint: https://<your-resource>.openai.azure.com/
    api_version: "2024-12-01-preview"
    model: gpt-4.1

orchestrator:
  config:
    system_prompt: |
      You are a legal analyst investigating whether a candidate is independent
      from the party it would oversee.
    task_prompt: |
      Given the information, evaluate whether the candidate is independent.
    summary_prompt: |
      Based on all context, give a final verdict on whether the candidate
      should receive the mandate. Cite your sources.
    query: "Sergio Ermotti AND UBS"
    n: 5
```

**Providers**

| Key | Providers |
|---|---|
| `scraper` | `yahoo` |
| `inference` | `openai` (Azure OpenAI) |

**Environment variables**

| Variable | Purpose |
|---|---|
| `AZURE_OPENAI_API_KEY` | API key for Azure OpenAI (used by the `openai` provider) |

## Usage

```python
import scrapi

config = scrapi.load_yaml_config("config.yaml")
orchestrator = scrapi.make_orchestrator(config)
report = orchestrator.run()

print(report.summary.result)
```

Build a config programmatically instead of from a file:

```python
from scrapi import parse_config, make_orchestrator

config = parse_config({
    "scraper": {"provider": "yahoo", "config": {}},
    "inference": {
        "provider": "openai",
        "config": {"azure_endpoint": "https://...", "model": "gpt-4.1"},
    },
    "orchestrator": {
        "config": {
            "system_prompt": "...",
            "task_prompt": "...",
            "summary_prompt": "...",
            "query": "Sergio Ermotti AND UBS",
            "n": 5,
        }
    },
})

orchestrator = make_orchestrator(config)
report = orchestrator.run()
```

The returned `Report` contains individual result pairs (search result + inference result) and a final summary:

```python
for pair in report:
    print(pair.search.source)        # source URL / metadata
    print(pair.inference.result)     # per-article verdict

print(report.summary.result)        # final aggregated verdict
```
