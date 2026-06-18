from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

URLS = [
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=200&from=2026-06-01&to=2026-07-31",
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17",
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=200&dateFrom=2026-06-01&dateTo=2026-07-31&idCompetition=17",
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=200&startDate=2026-06-01&endDate=2026-07-31&idCompetition=17",
]

print("FIFA API diagnostic v8 — date filters 2026")

for url in URLS:
    print("\n---")
    print("URL:", url)

    try:
        req = Request(
            url,
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

        for m in results[:10]:
            season = m.get("SeasonName", [])
            season_name = season[0].get("Description", "") if season else ""
            print(
                "MatchNumber=", m.get("MatchNumber"),
                "| Date=", m.get("Date"),
                "| Season=", season_name,
                "| Home=", (m.get("Home") or {}).get("Abbreviation"),
                "| Away=", (m.get("Away") or {}).get("Abbreviation"),
                "| Score=", m.get("HomeTeamScore"), "-", m.get("AwayTeamScore")
            )

    except HTTPError as e:
        print("HTTP error:", e.code)

    except Exception as e:
        print("Error:", str(e))
