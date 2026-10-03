# scrapi

Fetch an information set from multiple sources and analyse it with an LLM. `scrapi` collects content from one or more scrapers, runs structured per-result inference, then produces a final summary.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:dheimgartner/scrapi.git
cd scrapi
uv sync
source .venv/bin/activate
```

## Configuration

`scrapi` is configured with a TOML file. The three top-level sections are `[llm]`, `[inference]`, and `[[scrapers]]`.

```toml
[llm]
provider = "openai"

[llm.config]
azure_endpoint = "https://<your-resource>.openai.azure.com/"
model = "gpt-4.1"

[inference.search]
system_prompt = "You are a financial research analyst."
task_prompt = "Extract the key facts and sentiment from this source relevant to the company's situation and outlook."

[inference.summary]
system_prompt = "You are a financial research analyst."
task_prompt = "Based on all sources, summarise the company's current situation and outlook. Cite your sources."

[[scrapers]]
provider = "yahoo"
[scrapers.fetch]
query = "Apple latest company news"
n = 5

[[scrapers]]
provider = "finance"
[scrapers.fetch]
query = ["AAPL"]
```

Multiple scrapers can be combined in a single run by adding more `[[scrapers]]` blocks.

**LLM providers**

| Provider | Config keys |
|---|---|
| `anthropic` | `model`, `api_key` |
| `openai` | `azure_endpoint`, `api_version`, `model`, `api_key` |
| `ollama` | `base_url`, `model` |

**Scraper providers**

| Provider | `fetch` keys | Description |
|---|---|---|
| `yahoo` | `query` (str), `n` (int) | Yahoo web search via DDGS + Selenium |
| `file` | `query` (list of paths/globs) | Local files; PDFs and common document formats |
| `finance` | `query` (list of ticker symbols) | Financial data via yfinance |
| `dummy` | `query` (str), `n` (int) | Synthetic results for testing |

**Environment variables**

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | API key for the `anthropic` provider (can also be set in `[llm.config]`) |
| `AZURE_OPENAI_API_KEY` | API key for the `openai` provider (can also be set in `[llm.config]`) |

## Usage

```python
import scrapi

config = scrapi.load_toml_config("config.toml")
orchestrator = scrapi.make_orchestrator(config)
result = orchestrator.run()

print(result.summary.result)
```

Build a config programmatically:

```python
from scrapi import parse_config, make_orchestrator

config = parse_config({
    "llm": {
        "provider": "openai",
        "config": {"azure_endpoint": "https://...", "model": "gpt-4.1"},
    },
    "inference": {
        "search": {
            "system_prompt": "You are a financial research analyst.",
            "task_prompt": "Extract the key facts and sentiment from this source relevant to the company's earnings outlook.",
        },
        "summary": {
            "system_prompt": "You are a financial research analyst.",
            "task_prompt": "Summarise the company's earnings situation and outlook. Cite your sources.",
        },
    },
    "scrapers": [
        {"provider": "yahoo", "fetch": {"query": "Apple latest company news", "n": 5}},
        {"provider": "finance", "fetch": {"query": ["AAPL"]}},
    ],
})

orchestrator = make_orchestrator(config)
result = orchestrator.run()
```

The returned `PipelineResult` contains individual result pairs (search result + inference result) and a final summary:

```python
for pair in result:
    print(pair.search.source)       # source URL / path / ticker
    print(pair.inference.result)    # per-source verdict

print(result.summary.result)       # final aggregated verdict
```

### Rendering

```python
from scrapi.renderer.markdown import MarkdownRenderer

renderer = MarkdownRenderer(result)
renderer.save("report.md")
```
