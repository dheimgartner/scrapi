# Configuration

`scrapi` is configured with a TOML file. The required top-level sections are `[llm]`, `[inference]`, and `[[scrapers]]`. The `[renderer]` section is optional.

## Full example

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

---

## `[llm]`

| Key | Type | Description |
|---|---|---|
| `provider` | string | LLM backend to use. One of `anthropic`, `openai`, `ollama`. |

### `[llm.config]` — provider-specific keys

=== "anthropic"

    | Key | Type | Default | Description |
    |---|---|---|---|
    | `model` | string | — | Model identifier, e.g. `claude-opus-4-7` |
    | `api_key` | string | `$ANTHROPIC_API_KEY` | API key (can also be set via env var) |

=== "openai (Azure)"

    | Key | Type | Default | Description |
    |---|---|---|---|
    | `azure_endpoint` | string | — | Azure OpenAI endpoint URL |
    | `model` | string | — | Deployment name, e.g. `gpt-4.1` |
    | `api_version` | string | — | Azure API version, e.g. `2024-12-01-preview` |
    | `api_key` | string | `$AZURE_OPENAI_API_KEY` | API key (can also be set via env var) |

=== "ollama"

    | Key | Type | Default | Description |
    |---|---|---|---|
    | `base_url` | string | `http://localhost:11434` | Ollama server URL |
    | `model` | string | — | Model name, e.g. `llama3.2` |

---

## `[inference]`

Inference is split into two stages. Both are required.

### `[inference.search]`

Applied per-result to each individual search result.

| Key | Type | Description |
|---|---|---|
| `system_prompt` | string | System-level instruction for the LLM |
| `task_prompt` | string | Per-result extraction instruction |

### `[inference.summary]`

Applied once across all collected search inference results.

| Key | Type | Description |
|---|---|---|
| `system_prompt` | string | System-level instruction for the LLM |
| `task_prompt` | string | Cross-source summary instruction |

---

## `[[scrapers]]`

Each `[[scrapers]]` block defines one scraper. Multiple blocks can be combined in a single run.

| Key | Type | Description |
|---|---|---|
| `provider` | string | Scraper backend. One of `yahoo`, `file`, `finance`, `sql`, `dummy`. |

### `[scrapers.config]` — provider-specific constructor args

Some scrapers require a `[scrapers.config]` section (e.g. `sql` for the connection string).

### `[scrapers.scrape]` — arguments forwarded to `scraper.scrape()`

=== "yahoo"

    | Key | Type | Description |
    |---|---|---|
    | `query` | string | Search query string |
    | `n` | int | Number of results to fetch |

=== "file"

    | Key | Type | Description |
    |---|---|---|
    | `query` | list[str] | File paths or glob patterns. PDFs are converted via PyMuPDF4LLM; other formats via MarkItDown. |

=== "finance"

    | Key | Type | Description |
    |---|---|---|
    | `query` | list[str] | List of ticker symbols, e.g. `["AAPL", "MSFT"]` |

=== "sql"

    | Key | Type | Description |
    |---|---|---|
    | `query` | string | SQL query to execute |
    | `rows_as_results` | bool | If `true`, each row becomes a separate `SQLSearchResult`; if `false`, the entire result set is one result rendered as a Markdown table |

    The `sql` scraper requires a `[scrapers.config]` section:

    ```toml
    [[scrapers]]
    provider = "sql"
    [scrapers.config]
    connection_string = "mssql+pymssql://user:${DB_PASSWORD}@host:1433/mydb"
    [scrapers.scrape]
    query = "SELECT * FROM schema.table"
    rows_as_results = false
    ```

    `${VAR}` placeholders in the connection string are resolved from environment variables at instantiation time and URL-encoded automatically.

=== "dummy"

    | Key | Type | Description |
    |---|---|---|
    | `query` | string | Synthetic query label (used in result metadata) |
    | `n` | int | Number of synthetic results to generate |

---

## `[renderer]`

Optional. When present, `orchestrator.run()` automatically renders and saves the report.

| Key | Type | Description |
|---|---|---|
| `provider` | string | Renderer backend. Currently only `markdown`. |
| `report_path` | string | Path where the rendered report is saved. Supports `~` expansion. |
| `result_md_path` | string | Optional path to save a separate Markdown file containing just the per-result `result_md` fields. |

---

## Environment variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | API key for the `anthropic` provider |
| `AZURE_OPENAI_API_KEY` | API key for the `openai` provider |
| Any `${VAR}` used in `connection_string` | Resolved at SQL scraper instantiation time |
