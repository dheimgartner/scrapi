# Inference

scrapi provides three inference classes:

- `Inference` — generic single-shot structured LLM call; bring your own Pydantic schema
- `SearchInference` — wraps `Inference` with the built-in `SearchSchema`
- `SummaryInference` — wraps `Inference` with the built-in `SummarySchema`

The `Orchestrator` uses `SearchInference` and `SummaryInference` internally, but `Inference` can be used standalone against any scraper output.

## Inference

::: scrapi.inference.inference.Inference

## SearchInference

::: scrapi.inference.search.SearchInference

## SummaryInference

::: scrapi.inference.summary.SummaryInference

## Output schemas

::: scrapi.inference.schemas.SearchSchema

::: scrapi.inference.schemas.SummarySchema
