from scrapi.scraping.yahoo import YahooScraper
from scrapi.scraping.yfinance import YFinanceScraper

# --- YahooScraper: free-text query ---
print("=== YahooScraper ===")
yahoo = YahooScraper()
results = yahoo.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:300])
    print("---")

# --- YFinanceScraper: ticker-based news ---
print("=== YFinanceScraper ===")
yf = YFinanceScraper()
results = yf.fetch_content(query="UBS", n=2)

for result in results:
    print(result.source["title"])
    print(result.source["url"])
    print(result.ai_content[:300])
    print("---")
