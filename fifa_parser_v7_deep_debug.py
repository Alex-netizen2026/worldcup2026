from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "deep_debug_v7"
OUT_DIR.mkdir(exist_ok=True)

MATCHES = {
    81: "400021525",  # BEL-SEN
    86: "400021515",  # AUS-EGY
    87: "400021521",  # ARG-CPV
}

URLS = [
    "https://api.fifa.com/api/v3/calendar/matches/{id}?language=en",
    "https://api.fifa.com/api/v3/matches/{id}?language=en",
    "https://api.fifa.com/api/v3/match/{id}?language=en",
    "https://api.fifa.com/api/v3/live/football/{id}?language=en",
    "https://api.fifa.com/api/v3/timelines/{id}?language=en",
    "https://api.fifa.com/api/v3/matches/{id}/timeline?language=en",
    "https://api.fifa.com/api/v3/matches/{id}/events?language=en",
    "https://api.fifa.com/api/v3/matches/{id}/statistics?language=en",
]

def get_json(url):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Origin": "https://www.fifa.com",
            "Referer": "https://www.fifa.com/",
        },
    )

    try:
        with urlopen(req, timeout=30) as response:
            text = response.read().decode("utf-8", errors="ignore")
            return response.status, text
    except HTTPError as e:
        return e.code, ""
    except URLError as e:
        return "URL_ERROR", str(e)

def main():
    report = []

    for match_no, fifa_id in MATCHES.items():
        for template in URLS:
            url = template.format(id=fifa_id)
            status, text = get_json(url)

            item = {
                "MatchNo": match_no,
                "FIFA_ID": fifa_id,
                "URL": url,
                "Status": status,
                "Length": len(text) if text else 0,
            }

            if status == 200 and text:
                try:
                    data = json.loads(text)
                    item["TopKeys"] = list(data.keys()) if isinstance(data, dict) else "LIST"

                    out_file = OUT_DIR / f"match_{match_no}_{fifa_id}_{len(report)}.json"
                    with out_file.open("w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

                    item["Saved"] = out_file.name
                except Exception as e:
                    item["JsonError"] = str(e)

            report.append(item)
            print(match_no, fifa_id, status, url)

    with (OUT_DIR / "deep_debug_report.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Deep debug completed.")

if __name__ == "__main__":
    main()
