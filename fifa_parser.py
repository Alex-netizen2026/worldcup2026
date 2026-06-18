from urllib.request import Request, urlopen
import re

FIFA_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"

print("FIFA parser diagnostic v2")
print("URL:", FIFA_URL)

req = Request(
    FIFA_URL,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urlopen(req, timeout=30) as response:
    content = response.read().decode("utf-8", errors="ignore")

print("Content length:", len(content))
print("First 1000 chars:")
print(content[:1000])

print("\nFound script src:")
for m in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content):
    print(m)

print("\nFound href:")
for m in re.findall(r'href=["\']([^"\']+)["\']', content):
    if "fifa" in m.lower() or "api" in m.lower() or "worldcup" in m.lower():
        print(m)

print("\nSearch tokens:")
for token in ["__NEXT_DATA__", "api", "matches", "fixtures", "scores", "tournament"]:
    print(token, "=", token in content)
