from urllib.request import Request, urlopen
import json
from pathlib import Path

FIFA_URL = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17"
)

BASE_DIR = Path(__file__).resolve().parent
DEBUG_DIR = BASE_DIR / "debug_v7"
DEBUG_DIR.mkdir(exist_ok=True)

TARGET_MATCHES = {
    81,
    86,
    87,
}

def fifa_match_id(match):
    return str(
        match.get("IdMatch")
        or match.get("Id")
        or match.get("MatchId")
        or match.get("MatchID")
        or ""
    )

def team_code(team):
    if not isinstance(team, dict):
        return ""
    return team.get("Abbreviation", "") or team.get("IdCountry", "")

def main():
    print("FIFA parser V7 DEBUG started")

    req = Request(
        FIFA_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Origin": "https://www.fifa.com",
            "Referer": "https://www.fifa.com/",
        },
    )

    with urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8", errors="ignore"))

    matches = data.get("Results", [])
    matches = sorted(matches, key=lambda m: m.get("Date", ""))

    print("Matches received:", len(matches))

    all_debug = []

    for index, match in enumerate(matches, start=1):
        if index not in TARGET_MATCHES:
            continue

        home = team_code(match.get("Home"))
        away = team_code(match.get("Away"))
        fifa_id = fifa_match_id(match)

        debug_item = {
            "CalculatedMatchNo": index,
            "FIFA_ID": fifa_id,
            "Home": home,
            "Away": away,
            "Date": match.get("Date", ""),
            "RawMatch": match,
        }

        all_debug.append(debug_item)

        out_file = DEBUG_DIR / f"debug_match_{index}_{home}_{away}.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(debug_item, f, ensure_ascii=False, indent=2)

        print("Written:", out_file.name)

    summary_file = DEBUG_DIR / "debug_extra_time_matches_81_86_87.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(all_debug, f, ensure_ascii=False, indent=2)

    print("Summary written:", summary_file)
    print("DEBUG completed")

if __name__ == "__main__":
    main()
