from urllib.request import Request, urlopen
import csv
import json
from pathlib import Path

FIFA_URL = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17"
)

BASE_DIR = Path(__file__).resolve().parent

FIXTURES_FILE = BASE_DIR / "worldcup2026_fixtures_v7.csv"
SCORES_FILE = BASE_DIR / "manual_scores_v7.csv"


FIXTURE_FIELDS = [
    "MatchNo",
    "FIFA_ID",
    "Group",
    "Home",
    "Away",
    "UTCDateTime",
    "Country",
    "City",
    "Stadium",
]

SCORE_FIELDS = [
    "MatchNo",
    "FIFA_ID",
    "Home",
    "Away",
    "Status",
    "Score",
    "HomeGoals",
    "AwayGoals",
    "Home90",
    "Away90",
    "HomeExtra",
    "AwayExtra",
    "HomePen",
    "AwayPen",
]


def text_value(items):
    if isinstance(items, list) and items:
        return items[0].get("Description", "")
    return ""


def team_code(team):
    if not isinstance(team, dict):
        return ""
    return team.get("Abbreviation", "") or team.get("IdCountry", "")


def fifa_match_id(match):
    return str(
        match.get("IdMatch")
        or match.get("Id")
        or match.get("MatchId")
        or match.get("MatchID")
        or ""
    )


def match_status(match):
    return str(
        match.get("MatchStatus")
        or match.get("Status")
        or match.get("MatchTimeStatus")
        or ""
    )


def score_text(home_goals, away_goals):
    if home_goals is None or away_goals is None:
        return ""
    return f"{home_goals}-{away_goals}"


def safe_score(match, *keys):
    for key in keys:
        value = match.get(key)
        if value is not None:
            return value
    return ""


def main():
    print("FIFA parser V7 started")
    print("Output directory:", BASE_DIR)

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

    matches = sorted(matches, key=lambda m: m.get("Date", ""))

    fixtures = []
    scores = []

    missing_fifa_id = 0

    for index, match in enumerate(matches, start=1):
        match_no = index
        fifa_id = fifa_match_id(match)

        if not fifa_id:
            missing_fifa_id += 1

        group_name = text_value(match.get("GroupName", []))
        group = group_name.replace("Group ", "").strip()

        home = team_code(match.get("Home"))
        away = team_code(match.get("Away"))

        stadium = match.get("Stadium") or {}
        stadium_name = text_value(stadium.get("Name", []))
        city = text_value(stadium.get("CityName", []))
        country = text_value(stadium.get("CountryName", []))

        utc_datetime = match.get("Date", "")

        home_goals = match.get("HomeTeamScore")
        away_goals = match.get("AwayTeamScore")
        score = score_text(home_goals, away_goals)

        fixtures.append({
            "MatchNo": match_no,
            "FIFA_ID": fifa_id,
            "Group": group,
            "Home": home,
            "Away": away,
            "UTCDateTime": utc_datetime,
            "Country": country,
            "City": city,
            "Stadium": stadium_name,
        })

        if score:
            scores.append({
                "MatchNo": match_no,
                "FIFA_ID": fifa_id,
                "Home": home,
                "Away": away,
                "Status": match_status(match),
                "Score": score,
                "HomeGoals": home_goals,
                "AwayGoals": away_goals,
                "Home90": safe_score(match, "HomeTeamScore90", "HomeScore90", "HomeTeamRegularTimeScore"),
                "Away90": safe_score(match, "AwayTeamScore90", "AwayScore90", "AwayTeamRegularTimeScore"),
                "HomeExtra": safe_score(match, "HomeTeamExtraTimeScore", "HomeExtraTimeScore"),
                "AwayExtra": safe_score(match, "AwayTeamExtraTimeScore", "AwayExtraTimeScore"),
                "HomePen": safe_score(match, "HomeTeamPenaltyScore", "HomePenaltyScore"),
                "AwayPen": safe_score(match, "AwayTeamPenaltyScore", "AwayPenaltyScore"),
            })

    with FIXTURES_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIXTURE_FIELDS)
        writer.writeheader()
        writer.writerows(fixtures)

    with SCORES_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCORE_FIELDS)
        writer.writeheader()
        writer.writerows(scores)

    print("Fixtures written:", len(fixtures))
    print("Scores written:", len(scores))
    print("Missing FIFA_ID:", missing_fifa_id)


if __name__ == "__main__":
    main()
