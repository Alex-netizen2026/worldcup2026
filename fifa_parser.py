from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json

URLS = [
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=100&idCompetition=17",
    "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500",
    "https://api.fifa.com/api/v3/competitions/17",
    "https://api.fifa.com/api/v3/competitions/17/matches",
    "https://fdh-api.fifa.com/v1/calendar/matches?language=en&count=500",
    "https://fdh-api.fifa.com/v1/competitions/17/matches",
    "https://cxm-api.fifa.com/fifaplusweb/api/sections/competitionSeasonSummary/",
    "https://cxm-api.fifa.com/fifaplusweb/api/data/competitionSeasonSummaryData/",
]

print("FIFA API diagnostic v4")

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
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            raw = response.read()

        text = raw.decode("utf-8", errors="ignore")

        print("HTTP:", status)
        print("Content-Type:", content_type)
        print("Length:", len(text))
        print("Preview:", text[:500].replace("\n", " "))

        try:
            data = json.loads(text)
            print("JSON: yes")
            if isinstance(data, dict):
                print("Top keys:", list(data.keys())[:20])
            elif isinstance(data, list):
                print("List length:", len(data))
        except Exception:
            print("JSON: no")

    except HTTPError as e:
        print("HTTP error:", e.code)

    except URLError as e:
        print("URL error:", e.reason)

    except Exception as e:
        print("Unexpected error:", str(e))
