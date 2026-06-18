from urllib.request import Request, urlopen
import json

URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=2000&idCompetition=17"

print("FIFA API diagnostic v7 — find 2026 season with count=2000")
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

def text_value(items):
    if isinstance(items, list) and items:
        return items[0].get("Description", "")
    return ""

seasons = {}

for m in results:
    season_id = m.get("IdSeason", "")
    season_name = text_value(m.get("SeasonName", []))
    date = m.get("Date", "")

    seasons.setdefault(
        season_id,
        {"name": season_name, "first": date, "last": date, "count": 0}
    )

    seasons[season_id]["count"] += 1

    if date < seasons[season_id]["first"]:
        seasons[season_id]["first"] = date

    if date > seasons[season_id]["last"]:
        seasons[season_id]["last"] = date

print("Found seasons:", len(seasons))

for sid, info in sorted(seasons.items(), key=lambda x: x[1]["first"]):
    line = (
        f"IdSeason={sid} | {info['name']} | "
        f"matches={info['count']} | first={info['first']} | last={info['last']}"
    )
    print(line)

print("\nCandidates containing 2026:")
for sid, info in seasons.items():
    if "2026" in info["name"] or "2026" in info["first"] or "2026" in info["last"]:
        print("FOUND:", sid, info)
