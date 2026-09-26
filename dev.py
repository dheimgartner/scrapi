from scrapi.scraping.yahoo import YahooScraper
from scrapi.scraping.dummy import DummyScraper

# --- DummyScraper: no network, instant results ---
scraper = DummyScraper()
results = scraper.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content)
    print("---")

# --- YahooScraper: live web search ---
scraper = YahooScraper()
results = scraper.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:500])
    print("---")
