# scrapi

**Turn any information set into a structured LLM analysis — in a single config file.**

Point `scrapi` at your sources (web, documents, databases, financial data), describe what you want the LLM to extract and summarise, and get back a typed, auditable result. No glue code. No prompt plumbing. Just configure and run.

```python
import scrapi

config = scrapi.load_toml_config("config.toml")
result = scrapi.make_orchestrator(config).run()

print(result.summary.result)
```

---

## What can you build with it?

### Financial research reports

Combine live web search with market data to produce a structured company brief on demand. Each source is analysed individually, then all findings are aggregated into a single cross-source summary — complete with citations. The result can be rendered as a Markdown report and saved automatically.

### Customer feedback analysis

Your customer survey responses sit in a database table. Point the SQL scraper at them, define what you want extracted (sentiment, topic, urgency), and let the LLM run structured inference over every row. Aggregate the individual results into an overall summary without writing a single line of prompt-management code.

### AI-assisted decision support

Define a Pydantic schema that captures not just the decision outcome but also a mandatory explanation field. Feed the decision-relevant information set through `scrapi`, and each result is tagged with a structured rationale — traceable, auditable, and ready to feed into a downstream approval workflow.

---

## How it works

`scrapi` runs a three-stage pipeline:

1. **Scrape** — collect content from one or more sources (web, files, financial data, SQL)
2. **Search inference** — run a structured LLM extraction on each individual result
3. **Summary inference** — aggregate all results into a final cross-source summary

| Concept | Description |
|---|---|
| `Orchestrator` | Wires scrapers, inference, and renderer into a single `run()` call |
| `ScrapiConfig` | TOML-based configuration parsed into typed dataclasses |
| `BaseScraper` | Abstract interface all scrapers implement — yields `BaseSearchResult` objects |
| `Inference` | Single-shot structured LLM call; `SearchInference` and `SummaryInference` wrap it |
| `RunResult` | Iterable container holding `ResultPair` objects and the final summary |
