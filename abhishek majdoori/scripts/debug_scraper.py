"""Debug the scraper to understand why the smoke test HTML fails."""
import sys
sys.path.insert(0, "src")

from handshake_watcher.scraper.projects import parse_projects, _find_project_cards
from bs4 import BeautifulSoup

html = "<html><body><ul><li data-id='p1'><h3>Test Project</h3><a href='/projects/1'>L</a></li></ul></body></html>"

soup = BeautifulSoup(html, "lxml")
print("HTML parsed OK")
print("Body:", soup.body)

cards = _find_project_cards(soup)
print(f"Cards found: {len(cards)}")
for c in cards:
    print("  Card:", c)

results = parse_projects(html)
print(f"Results: {len(results)}")
for r in results:
    print("  Result:", r)
