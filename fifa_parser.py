from urllib.request import Request, urlopen
import json

URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=20&idCompetition=17"

print("FIFA API diagnostic v5")
print("URL:", URL)

req = Request(
    URL,
    headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Origin": "https://www.fifa.com",
        "Referer": "https://www.fifa.com/",
    },
)

with urlopen(req, timeout=30) as response:
    data = json.loads(response.read().decode("utf-8", errors="ignore"))

results = data.get("Results", [])

print("Results count:", len(results))

if not results:
    print("No results found")
    raise SystemExit(0)

match = results[0]

print("\nTop-level keys:")
for key in match.keys():
    print("-", key)

print("\nFirst match JSON preview:")
print(json.dumps(match, indent=2, ensure_ascii=False)[:5000])
