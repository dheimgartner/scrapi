# scrapi

**Fetch an information set from multiple sources and analyse it with an LLM.**

`scrapi` orchestrates a three-stage pipeline:

1. **Scrape** — collect content from one or more sources (web, files, financial data, SQL)
2. **Search inference** — run a structured LLM extraction on each individual result
3. **Summary inference** — aggregate all results into a final cross-source summary

```python
import scrapi

config = scrapi.load_toml_config("config.toml")
orchestrator = scrapi.make_orchestrator(config)
result = orchestrator.run()

print(result.summary.result)
```

## Key concepts

| Concept | Description |
|---|---|
| `Orchestrator` | Wires scrapers, inference, and renderer into a single `run()` call |
| `ScrapiConfig` | TOML-based configuration parsed into typed dataclasses |
| `BaseScraper` | Abstract interface all scrapers implement — yields `BaseSearchResult` objects |
| `Inference` | Single-shot structured LLM call; `SearchInference` and `SummaryInference` wrap it |
| `RunResult` | Iterable container holding `ResultPair` objects and the final summary |

## Navigation

- **[Quick Start](quickstart.md)** — install and run your first pipeline in minutes
- **[Configuration](configuration.md)** — complete TOML reference with all providers and options
- **[API Reference](api/index.md)** — full docstring-driven reference for every public class and function
