from scrapi.scraping.yahoo import YahooScraper
from scrapi.scraping.dummy import DummyScraper
from scrapi.scraping.file import FileScraper
from scrapi.config.loader import parse_config
from scrapi.factory import make_orchestrator

# --- DummyScraper: no network, instant results ---
scraper = DummyScraper()
results = scraper.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content)
    print("---")

# --- FileScraper: local files to markdown ---
scraper = FileScraper()
results = scraper.fetch_content(query=["path/to/paper1.pdf", "path/to/paper2.pdf"])

for result in results:
    print(result.source["path"])
    print(result.ai_content[:500])
    print("---")

# --- YahooScraper: live web search ---
scraper = YahooScraper()
results = scraper.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:500])
    print("---")

# --- Orchestrator: full pipeline via config + factory (requires ollama) ---
config = parse_config({
    "llm": {
        "provider": "ollama",
        "config": {"base_url": "http://10.89.0.7:11434/v1"},
    },
    "inference": {
        "search": {
            "system_prompt": "You are a helpful research analyst.",
            "task_prompt": "Summarize the key findings from the article.",
        },
        "summary": {
            "system_prompt": "You are a helpful research analyst.",
            "task_prompt": "Provide a concise final summary across all sources. Cite your sources.",
        },
    },
    "scrapers": [
        {
            "provider": "dummy",
            "config": {},
            "fetch": {"query": "Sergio Ermotti UBS", "n": 2},
        },
    ],
})

orchestrator = make_orchestrator(config)
pipeline_result = orchestrator.run()
print(pipeline_result.summary.result)

# --- MarkdownRenderer: render pipeline result to markdown ---
from scrapi.renderer.markdown import MarkdownRenderer

renderer = MarkdownRenderer(pipeline_result=pipeline_result)
print(renderer.render())
# renderer.save("report.md")
