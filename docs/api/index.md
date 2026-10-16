# API Reference

Full docstring-driven reference for all public classes and functions.

## Module layout

| Module | Contents |
|---|---|
| `scrapi` | Top-level re-exports: `load_toml_config`, `parse_config`, `make_orchestrator` |
| [`scrapi.orchestrator`](orchestrator.md) | `Orchestrator` — wires scraping and inference |
| [`scrapi.factory`](factory.md) | `make_orchestrator` — builds an `Orchestrator` from config |
| [`scrapi.inference`](inference.md) | `Inference`, `SearchInference`, `SummaryInference` |
| [`scrapi.scraping`](scrapers.md) | `BaseScraper` + all provider implementations |
| [`scrapi.llm`](llm.md) | `BaseLLM` + all LLM provider implementations |
| [`scrapi.models`](models.md) | `RunResult`, `ResultPair`, `BaseSearchResult`, `BaseInferenceResult` and subtypes |
| [`scrapi.renderer`](renderer.md) | `BaseRenderer`, `MarkdownRenderer` |
| [`scrapi.config.schemas`](config.md) | `ScrapiConfig` and all config dataclasses |
