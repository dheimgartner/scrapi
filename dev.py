from scrapi.scraping.yahoo import YahooScraper
from scrapi.scraping.rss import RssScraper

# --- YahooScraper: free-text query ---
print("=== YahooScraper ===")
yahoo = YahooScraper()
results = yahoo.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:300])
    print("---")

# --- RssScraper: RSS feed URL ---
print("=== RssScraper ===")
rss = RssScraper()
results = rss.fetch_content(
    query="https://finance.yahoo.com/rss/2.0/headline?s=UBS&region=US&lang=en-US",
    n=3,
)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:300])
    print("---")
