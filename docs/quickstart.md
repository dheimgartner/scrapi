# Quick Start

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone git@github.com:dheimgartner/scrapi.git
cd scrapi
uv sync
source .venv/bin/activate
```

## Your first run

### 1. Write a config file

Create `config.toml`:

```toml
[llm]
provider = "openai"

[llm.config]
azure_endpoint = "https://<your-resource>.openai.azure.com/"
model = "gpt-4.1"

[inference.search]
system_prompt = "You are a financial research analyst."
task_prompt = "Extract the key facts and sentiment from this source relevant to the company's situation."

[inference.summary]
system_prompt = "You are a financial research analyst."
task_prompt = "Summarise the company's current situation and outlook. Cite your sources."

[[scrapers]]
provider = "yahoo"
[scrapers.scrape]
query = "Apple latest company news"
n = 5

[[scrapers]]
provider = "finance"
[scrapers.scrape]
query = ["AAPL"]

[renderer]
provider = "markdown"
report_path = "~/report.md"
```

### 2. Set environment variables

```bash
export AZURE_OPENAI_API_KEY="..."
# or for Anthropic:
export ANTHROPIC_API_KEY="..."
```

### 3. Run

```python
import scrapi

config = scrapi.load_toml_config("config.toml")
orchestrator = scrapi.make_orchestrator(config)
result = orchestrator.run()

print(result.summary.result)
```

The rendered Markdown report is saved to `~/report.md`.

---

## Iterating over results

```python
for pair in result:
    print(pair.search.source)       # source URL / path / ticker
    print(pair.inference.result)    # per-source LLM verdict
```

## Programmatic config

No TOML file required — build the config dict directly:

```python
from scrapi import parse_config, make_orchestrator

config = parse_config({
    "llm": {
        "provider": "anthropic",
        "config": {"model": "claude-opus-4-7"},
    },
    "inference": {
        "search": {
            "system_prompt": "You are a research analyst.",
            "task_prompt": "Extract the key facts from this source.",
        },
        "summary": {
            "system_prompt": "You are a research analyst.",
            "task_prompt": "Summarise all sources. Cite them.",
        },
    },
    "scrapers": [
        {"provider": "yahoo", "scrape": {"query": "Apple Q1 2025 earnings", "n": 3}},
    ],
})

orchestrator = make_orchestrator(config)
result = orchestrator.run()
```

## Standalone Inference

Use `Inference` directly without the orchestrator:

```python
from pydantic import BaseModel, Field
from scrapi.scraping.dummy import DummyScraper
from scrapi.inference import Inference

class RiskSchema(BaseModel):
    summary: str = Field(description="One-sentence summary.")
    risk: str = Field(description="Key risk identified in the source.")

scraper = DummyScraper()
results = scraper.scrape(query="Apple earnings", n=3)

inference = Inference(
    llm=llm,
    system_prompt="You are a risk analyst.",
    task_prompt="Identify the main risk.",
    schema=RiskSchema,
)

for result in results:
    ir = inference.run(result)
    print(ir.structured_output.risk)
```

## Manual rendering

```python
from scrapi.renderer.markdown import MarkdownRenderer

renderer = MarkdownRenderer(report_path="report.md")
renderer.render(result)
renderer.save()
```

`render()` returns the document as a string and caches it internally. `save()` writes the cache to `report_path`.
