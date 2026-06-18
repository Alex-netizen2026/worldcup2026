import csv
import os
import requests
from datetime import datetime

API_URL = "https://api.fifa.com/api/v3/calendar/matches"
PARAMS = {
    "language": "en",
    "count": 200,
    "from": "2026-06-01",
    "to": "2026-07-31",
    "idCompetition": 17,
}

FIXTURES_FILE = "worldcup2026_fixtures.csv"
MANUAL_SCORES_FILE = "manual_scores.csv"


def get_matches():
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict):
        return data.get("Results") or data.get("results") or data.get("Matches") or []

    return data


def value(obj, *keys):
    for key in keys:
        if isinstance(obj, dict) and key in obj and obj[key] not in (None, ""):
            return obj[key]
    return ""


def nested_name(obj):
    if isinstance(obj, dict):
        return (
            obj.get("Name")
            or obj.get("name")
            or obj.get("Description")
            or obj.get("description")
            or obj.get("ShortName")
            or obj.get("shortName")
            or ""
        )
    return obj or ""


def parse_match(match):
    home = value(match, "Home", "HomeTeam", "homeTeam")
    away = value(match, "Away", "AwayTeam", "awayTeam")

    stadium = value(match, "Stadium", "stadium")
    city = value(match, "City", "city")
    stage = value(match, "Stage", "stage")
    group = value(match, "Group", "group")

    utc_date = value(match, "Date", "date", "MatchDate", "matchDate")

    return {
        "match_id": value(match, "IdMatch", "idMatch", "Id", "id"),
        "match_number": value(match, "MatchNumber", "matchNumber"),
        "stage": nested_name(stage),
        "group": nested_name(group),
        "utc_datetime": utc_date,
        "home_team": nested_name(home),
        "away_team": nested_name(away),
        "city": nested_name(city),
        "stadium": nested_name(stadium),
        "home_score": "",
        "away_score": "",
        "status": value(match, "MatchStatus", "matchStatus", "Status", "status"),
    }


def write_fixtures(rows):
    fieldnames = [
        "match_id",
        "match_number",
        "stage",
        "group",
        "utc_datetime",
        "home_team",
        "away_team",
        "city",
        "stadium",
        "status",
    ]

    with open(FIXTURES_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def read_existing_manual_scores():
    if not os.path.exists(MANUAL_SCORES_FILE):
        return {}

    existing = {}
    with open(MANUAL_SCORES_FILE, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            match_id = row.get("match_id", "")
            if match_id:
                existing[match_id] = row
    return existing


def write_manual_scores(rows):
    existing = read_existing_manual_scores()

    fieldnames = [
        "match_id",
        "match_number",
        "stage",
        "group",
        "utc_datetime",
        "home_team",
        "away_team",
        "home_score",
        "away_score",
        "pen_home",
        "pen_away",
        "status",
    ]

    with open(MANUAL_SCORES_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            old = existing.get(row["match_id"], {})

            writer.writerow({
                "match_id": row.get("match_id", ""),
                "match_number": row.get("match_number", ""),
                "stage": row.get("stage", ""),
                "group": row.get("group", ""),
                "utc_datetime": row.get("utc_datetime", ""),
                "home_team": row.get("home_team", ""),
                "away_team": row.get("away_team", ""),
                "home_score": old.get("home_score", ""),
                "away_score": old.get("away_score", ""),
                "pen_home": old.get("pen_home", ""),
                "pen_away": old.get("pen_away", ""),
                "status": row.get("status", ""),
            })


def main():
    matches = get_matches()
    rows = [parse_match(m) for m in matches]

    rows = sorted(rows, key=lambda x: int(x["match_number"]) if str(x["match_number"]).isdigit() else 9999)

    write_fixtures(rows)
    write_manual_scores(rows)

    print(f"OK: {len(rows)} matches saved")
    print(f"Created/updated: {FIXTURES_FILE}")
    print(f"Created/updated: {MANUAL_SCORES_FILE}")


if __name__ == "__main__":
    main()
