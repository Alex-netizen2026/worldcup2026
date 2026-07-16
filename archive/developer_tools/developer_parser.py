import json
import requests

FIFA_URL = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17"
)

KEYWORDS = [
    "score",
    "penalty",
    "penalties",
    "shoot",
    "extra",
    "aet",
    "winner",
    "period",
    "stage",
    "status",
    "result",
    "home",
    "away",
]


def collect_interesting_keys(obj, prefix=""):
    found = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            low = key.lower()

            if any(k in low for k in KEYWORDS):
                found.append((path, value))

            if isinstance(value, (dict, list)):
                found.extend(collect_interesting_keys(value, path))

    elif isinstance(obj, list):
        for i, item in enumerate(obj[:3]):
            found.extend(collect_interesting_keys(item, f"{prefix}[{i}]"))

    return found


def team_code(team):
    if isinstance(team, dict):
        return team.get("Abbreviation") or team.get("IdCountry") or ""
    return ""


def main():
    print("Developer FIFA parser started")
    print("This script reads FIFA JSON only. It does not write CSV files.")

    response = requests.get(
        FIFA_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Origin": "https://www.fifa.com",
            "Referer": "https://www.fifa.com/",
        },
        timeout=30,
    )

    print("HTTP status:", response.status_code)
    response.raise_for_status()

    data = response.json()
    matches = data.get("Results", [])

    print("Matches received:", len(matches))

    if not matches:
        print("No matches found")
        return

    matches = sorted(matches, key=lambda m: m.get("Date", ""))

    print("\n===== TOP-LEVEL MATCH KEYS =====")
    for key in sorted(matches[0].keys()):
        print(key)

    print("\n===== SCORE / PENALTY / EXTRA / WINNER RELATED FIELDS =====")

    checked = 0

    for idx, match in enumerate(matches, start=1):
        home = team_code(match.get("Home"))
        away = team_code(match.get("Away"))
        stage_text = json.dumps(match.get("StageName", ""), ensure_ascii=False)
        group_text = json.dumps(match.get("GroupName", ""), ensure_ascii=False)

        interesting = collect_interesting_keys(match)

        print("\n----------------------------------------")
        print("Excel chronological MatchNo:", idx)
        print("FIFA MatchNumber:", match.get("MatchNumber"))
        print("Date:", match.get("Date"))
        print("Teams:", home, "-", away)
        print("StageName:", stage_text)
        print("GroupName:", group_text)
        print("HomeTeamScore:", match.get("HomeTeamScore"))
        print("AwayTeamScore:", match.get("AwayTeamScore"))

        for path, value in interesting:
            if isinstance(value, (dict, list)):
                value_text = json.dumps(value, ensure_ascii=False)[:300]
            else:
                value_text = str(value)
            print(f"{path}: {value_text}")

        checked += 1
        if checked >= 12:
            break

    print("\n===== DIAGNOSTIC COMPLETE =====")
    print("If knockout matches are still scheduled, penalty/extra-time fields may be empty or absent.")
    print("Run this again after a playoff match goes to extra time or penalties.")


if __name__ == "__main__":
    main()
