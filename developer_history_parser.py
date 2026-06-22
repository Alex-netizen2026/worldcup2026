import json
import requests

FIFA_URL = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=200&from=2022-11-20&to=2022-12-18&idCompetition=17"
)

TARGET_TEAMS = [
    ("CRO", "BRA"),  # Croatia - Brazil
    ("ARG", "FRA"),  # Argentina - France
    ("JPN", "CRO"),  # Japan - Croatia
    ("MAR", "ESP"),  # Morocco - Spain
    ("NED", "ARG"),  # Netherlands - Argentina
]


def team_code(team):
    if isinstance(team, dict):
        return team.get("Abbreviation") or team.get("IdCountry") or ""
    return ""


def is_target_match(home, away):
    for a, b in TARGET_TEAMS:
        if (home == a and away == b) or (home == b and away == a):
            return True
    return False


def print_short_match_info(match, home, away):
    print("\n========================================")
    print("TARGET MATCH FOUND")
    print("Date:", match.get("Date"))
    print("FIFA MatchNumber:", match.get("MatchNumber"))
    print("Teams:", home, "-", away)
    print("StageName:", json.dumps(match.get("StageName"), ensure_ascii=False))
    print("GroupName:", json.dumps(match.get("GroupName"), ensure_ascii=False))

    print("\n--- MAIN SCORE FIELDS ---")
    print("HomeTeamScore:", match.get("HomeTeamScore"))
    print("AwayTeamScore:", match.get("AwayTeamScore"))

    if isinstance(match.get("Home"), dict):
        print("Home.Score:", match["Home"].get("Score"))
    else:
        print("Home.Score:", None)

    if isinstance(match.get("Away"), dict):
        print("Away.Score:", match["Away"].get("Score"))
    else:
        print("Away.Score:", None)

    print("\n--- PENALTY / EXTRA / WINNER FIELDS ---")

    for key in sorted(match.keys()):
        low = key.lower()
        if (
            "penalty" in low
            or "extra" in low
            or "winner" in low
            or "result" in low
            or "period" in low
            or "status" in low
            or "aggregate" in low
        ):
            print(f"{key}: {match.get(key)}")


def main():
    print("Developer history parser started")
    print("World Cup 2022 knockout diagnostic only")
    print("This script does not write CSV files")

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

    found = 0

    for match in matches:
        home = team_code(match.get("Home"))
        away = team_code(match.get("Away"))

        if not is_target_match(home, away):
            continue

        found += 1
        print_short_match_info(match, home, away)

        if (home == "ARG" and away == "FRA") or (home == "FRA" and away == "ARG"):
            print("\n--- FULL JSON FOR ARGENTINA - FRANCE FINAL ---")
            print(json.dumps(match, indent=2, ensure_ascii=False))

    print("\n========================================")
    print("Target matches found:", found)
    print("Diagnostic complete")


if __name__ == "__main__":
    main()
