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

`scrapi` is configured with a TOML file. The required top-level sections are `[llm]`, `[inference]`, and `[[scrapers]]`. The `[renderer]` section is optional.

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

[renderer]
provider = "markdown"
output_path = "~/report.md"
```

Multiple scrapers can be combined in a single run by adding more `[[scrapers]]` blocks. When `[renderer]` is present, `orchestrator.run()` automatically renders and saves the report to `output_path`.

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
| `sql` | `query` (str), `rows_as_results` (bool) | SQL query via SQLAlchemy; result set rendered as a Markdown table |
| `dummy` | `query` (str), `n` (int) | Synthetic results for testing |

**Renderer providers**

| Provider | Description |
|---|---|
| `markdown` | Markdown report with a search results table and summary |

**Environment variables**

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | API key for the `anthropic` provider (can also be set in `[llm.config]`) |
| `AZURE_OPENAI_API_KEY` | API key for the `openai` provider (can also be set in `[llm.config]`) |

The `sql` scraper supports `${VAR}` placeholders anywhere in the connection string. They are resolved from the environment at instantiation time and URL-encoded automatically, so passwords containing special characters work without manual escaping:

```toml
[[scrapers]]
provider = "sql"
[scrapers.config]
connection_string = "mssql+pymssql://user:${DB_PASSWORD}@host:1433/mydb"
[scrapers.fetch]
query = "SELECT * FROM schema.table"
rows_as_results = false
```

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
    "renderer": {"provider": "markdown", "output_path": "~/report.md"},
})

orchestrator = make_orchestrator(config)
result = orchestrator.run()
```

The returned `RunResult` contains individual result pairs (search result + inference result) and a final summary:

```python
for pair in result:
    print(pair.search.source)       # source URL / path / ticker
    print(pair.inference.result)    # per-source verdict

print(result.summary.result)       # final aggregated verdict
```

### Inference without the orchestrator

`Inference` can be used standalone against any scraper output:

```python
from pydantic import BaseModel, Field
from scrapi.scraping.dummy import DummyScraper
from scrapi.inference import Inference

class RiskSchema(BaseModel):
    summary: str = Field(description="One-sentence summary of the result.")
    risk: str = Field(description="Key risk identified in the source.")

scraper = DummyScraper()
results = scraper.fetch_content(query="Apple earnings", n=3)

inference = Inference(llm=llm, system_prompt="You are a risk analyst.", task_prompt="Identify the main risk.", schema=RiskSchema)

for result in results:
    ir = inference.run(result)
    print(ir.structured_output.risk)
```

### Rendering

When a `[renderer]` section is present in the config, the report is rendered and saved automatically at the end of `orchestrator.run()`. To render manually:

```python
from scrapi.renderer.markdown import MarkdownRenderer

renderer = MarkdownRenderer(output_path="report.md")
renderer.render(result)
renderer.save()
```

`render()` returns the document as a string and caches it; `save()` writes the cache to `output_path`.
