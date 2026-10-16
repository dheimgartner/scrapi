# Factory

`make_orchestrator` is the recommended way to build a fully-wired `Orchestrator` from a `ScrapiConfig`. It looks up each provider in the appropriate registry, validates constructor arguments, and instantiates all components.

::: scrapi.factory.make_orchestrator
