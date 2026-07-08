from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import csv
import json
import re
from pathlib import Path

FIFA_URL = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=200&from=2026-06-01&to=2026-07-31&idCompetition=17"
)

BASE_DIR = Path(__file__).resolve().parent

FIXTURES_FILE = BASE_DIR / "worldcup2026_fixtures_v7.csv"
SCORES_FILE = BASE_DIR / "worldcup2026_scores_v7.csv"
LEGACY_SCORES_FILE = BASE_DIR / "manual_scores_v7.csv"

FIXTURE_FIELDS = [
    "MatchNo", "FIFA_ID", "Group", "Home", "Away",
    "UTCDateTime", "Country", "City", "Stadium",
]

SCORE_FIELDS = [
    "MatchNo", "FIFA_ID", "Home", "Away", "Status", "Score",
    "HomeGoals", "AwayGoals",
    "ResultType", "MatchTime", "DecidedBy",
    "Home90", "Away90", "HomeExtra", "AwayExtra",
    "HomePen", "AwayPen",
    "Winner", "Loser",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Origin": "https://www.fifa.com",
    "Referer": "https://www.fifa.com/",
}


def http_json(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", errors="ignore"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return None


def text_value(items):
    if isinstance(items, list) and items:
        return items[0].get("Description", "")
    return ""


def team_code(team):
    if not isinstance(team, dict):
        return ""
    return team.get("Abbreviation", "") or team.get("IdCountry", "")


def team_id(team):
    if not isinstance(team, dict):
        return ""
    return str(team.get("IdTeam") or "")


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


def to_int_or_blank(v):
    if v is None or v == "":
        return ""
    try:
        return int(v)
    except Exception:
        return ""


def match_minutes(match_time):
    if not match_time:
        return 0
    m = re.search(r"\d+", str(match_time))
    return int(m.group(0)) if m else 0


def get_live_match(fifa_id):
    return http_json(f"https://api.fifa.com/api/v3/live/football/{fifa_id}?language=en")


def get_timeline(fifa_id):
    return http_json(f"https://api.fifa.com/api/v3/timelines/{fifa_id}?language=en")


def timeline_regular_score(timeline):
    if not isinstance(timeline, dict):
        return "", ""

    events = timeline.get("Event", [])
    home90, away90 = "", ""

    for ev in events:
        period = ev.get("Period")
        if period in (3, 5):  # first half / second half
            hg = ev.get("HomeGoals")
            ag = ev.get("AwayGoals")
            if hg is not None and ag is not None:
                home90 = hg
                away90 = ag

    return to_int_or_blank(home90), to_int_or_blank(away90)


def decide_by(result_type, match_time, home_pen, away_pen):
    if home_pen not in ("", None) or away_pen not in ("", None):
        return "PENALTY"

    try:
        rt = int(result_type)
    except Exception:
        rt = 0

    if rt == 2:
        return "PENALTY"
    if rt == 3:
        return "EXTRA"

    if match_minutes(match_time) > 120:
        return "EXTRA"

    return "REGULAR"


def calculate_period_scores(home_total, away_total, home90, away90, decided_by):
    home_extra, away_extra = "", ""

    if decided_by == "REGULAR":
        return home_total, away_total, "—", "—"

    if home90 == "" or away90 == "":
        if decided_by == "PENALTY":
            return home_total, away_total, 0, 0
        return "", "", "", ""

    home_extra = int(home_total) - int(home90)
    away_extra = int(away_total) - int(away90)

    if decided_by == "PENALTY" and home_extra == 0 and away_extra == 0:
        return home90, away90, 0, 0

    return home90, away90, home_extra, away_extra


def get_winner_loser(live, home_code, away_code, home_id, away_id):
    winner_id = str(live.get("Winner") or "") if isinstance(live, dict) else ""

    if winner_id and winner_id == home_id:
        return home_code, away_code
    if winner_id and winner_id == away_id:
        return away_code, home_code

    return "", ""


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("FIFA parser V7 started")
    print("Output directory:", BASE_DIR)

    data = http_json(FIFA_URL)
    if not data:
        raise RuntimeError("Could not download FIFA calendar API")

    matches = data.get("Results", [])
    matches = sorted(matches, key=lambda m: m.get("Date", ""))

    print("Matches received:", len(matches))

    fixtures = []
    scores = []

    for index, match in enumerate(matches, start=1):
        match_no = index
        fifa_id = fifa_match_id(match)

        group_name = text_value(match.get("GroupName", []))
        group = group_name.replace("Group ", "").strip()

        home_obj = match.get("Home") or {}
        away_obj = match.get("Away") or {}

        home = team_code(home_obj)
        away = team_code(away_obj)
        home_id = team_id(home_obj)
        away_id = team_id(away_obj)

        stadium = match.get("Stadium") or {}
        stadium_name = text_value(stadium.get("Name", []))
        city = text_value(stadium.get("CityName", []))
        country = text_value(stadium.get("CountryName", []))

        utc_datetime = match.get("Date", "")

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

        if not fifa_id:
            continue

        live = get_live_match(fifa_id) or {}
        timeline = get_timeline(fifa_id) or {}

        home_total = to_int_or_blank(
            (live.get("HomeTeam") or {}).get("Score")
            if isinstance(live.get("HomeTeam"), dict)
            else match.get("HomeTeamScore")
        )
        away_total = to_int_or_blank(
            (live.get("AwayTeam") or {}).get("Score")
            if isinstance(live.get("AwayTeam"), dict)
            else match.get("AwayTeamScore")
        )

        if home_total == "":
            home_total = to_int_or_blank(match.get("HomeTeamScore"))
        if away_total == "":
            away_total = to_int_or_blank(match.get("AwayTeamScore"))

        if home_total == "" or away_total == "":
            continue

        result_type = live.get("ResultType", match.get("ResultType", ""))
        match_time = live.get("MatchTime", match.get("MatchTime", ""))

        home_pen = to_int_or_blank(live.get("HomeTeamPenaltyScore"))
        away_pen = to_int_or_blank(live.get("AwayTeamPenaltyScore"))

        decided_by = decide_by(result_type, match_time, home_pen, away_pen)

        home90, away90 = timeline_regular_score(timeline)
        home90, away90, home_extra, away_extra = calculate_period_scores(
            home_total, away_total, home90, away90, decided_by
        )

        winner, loser = get_winner_loser(live, home, away, home_id, away_id)

        scores.append({
            "MatchNo": match_no,
            "FIFA_ID": fifa_id,
            "Home": home,
            "Away": away,
            "Status": match_status(match),
            "Score": score_text(home_total, away_total),
            "HomeGoals": home_total,
            "AwayGoals": away_total,
            "ResultType": result_type,
            "MatchTime": match_time,
            "DecidedBy": decided_by,
            "Home90": home90,
            "Away90": away90,
            "HomeExtra": home_extra,
            "AwayExtra": away_extra,
            "HomePen": home_pen,
            "AwayPen": away_pen,
            "Winner": winner,
            "Loser": loser,
        })

    write_csv(FIXTURES_FILE, FIXTURE_FIELDS, fixtures)
    write_csv(SCORES_FILE, SCORE_FIELDS, scores)
    write_csv(LEGACY_SCORES_FILE, SCORE_FIELDS, scores)

    print("Fixtures written:", len(fixtures))
    print("Scores written:", len(scores))
    print("Parser V7 completed")


if __name__ == "__main__":
    main()
