from scrapi.scraping.yahoo import YahooScraper

scraper = YahooScraper()
results = scraper.fetch_content(query="Sergio Ermotti UBS", n=2)

for result in results:
    print(result.source["url"])
    print(result.ai_content[:500])
    print("---")
