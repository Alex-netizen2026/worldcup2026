from urllib.request import Request, urlopen
import csv
import json

FIFA_URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17"

FIXTURES_FILE = "worldcup2026_fixtures.csv"
MANUAL_SCORES_FILE = "manual_scores.csv"


def text_value(items):
    if isinstance(items, list) and items:
        return items[0].get("Description", "")
    return ""


def team_code(team):
    if not isinstance(team, dict):
        return ""
    return team.get("Abbreviation", "") or team.get("IdCountry", "")


def get_score(match):
    home_score = match.get("HomeTeamScore")
    away_score = match.get("AwayTeamScore")

    if home_score is None or away_score is None:
        return ""

    return f"{home_score}-{away_score}"


def main():
    print("FIFA parser started")
    print("Source:", FIFA_URL)

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
    print("Matches received:", len(matches))

    fixtures_rows = []
    score_rows = []

    for match in matches:
        match_no = match.get("MatchNumber")
        if match_no is None:
            continue

        group_name = text_value(match.get("GroupName", []))
        group = group_name.replace("Group ", "").strip()

        home = team_code(match.get("Home"))
        away = team_code(match.get("Away"))

        stadium = match.get("Stadium") or {}
        stadium_name = text_value(stadium.get("Name", []))
        city = text_value(stadium.get("CityName", []))

        date_utc = match.get("Date", "")

        fixtures_rows.append({
            "MatchNo": match_no,
            "Group": group,
            "Home": home,
            "Away": away,
            "Date": date_utc,
            "City": city,
            "Stadium": stadium_name,
        })

        score = get_score(match)
        if score:
            score_rows.append({
                "MatchNo": match_no,
                "Score": score,
            })

    fixtures_rows = sorted(fixtures_rows, key=lambda x: int(x["MatchNo"]))
    score_rows = sorted(score_rows, key=lambda x: int(x["MatchNo"]))

    with open(FIXTURES_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["MatchNo", "Group", "Home", "Away", "Date", "City", "Stadium"]
        )
        writer.writeheader()
        writer.writerows(fixtures_rows)

    with open(MANUAL_SCORES_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["MatchNo", "Score"])
        writer.writeheader()
        writer.writerows(score_rows)

    print("Fixtures written:", len(fixtures_rows))
    print("Scores written:", len(score_rows))


if __name__ == "__main__":
    main()
