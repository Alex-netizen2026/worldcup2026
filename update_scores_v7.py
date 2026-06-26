from pathlib import Path
from datetime import datetime, timezone
import csv
import re

MANUAL_FILE = Path("manual_scores_v7.csv")
SCORES_FILE = Path("worldcup2026_scores_v7.csv")
HISTORY_FILE = Path("worldcup2026_history_v7.csv")
LOG_FILE = Path("update_log_v7.csv")

FIELDS = [
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


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def valid_score(score):
    score = str(score).strip()
    return score == "" or bool(re.fullmatch(r"\d+-\d+", score))


def read_csv_by_fifa_id(path):
    data = {}

    if not path.exists():
        return data

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            fifa_id = str(row.get("FIFA_ID", "")).strip()
            score = str(row.get("Score", "")).strip()

            if not fifa_id:
                continue

            if not valid_score(score):
                continue

            clean_row = {}
            for field in FIELDS:
                clean_row[field] = str(row.get(field, "")).strip()

            data[fifa_id] = clean_row

    return data


def write_csv(path, data):
    rows = list(data.values())

    rows.sort(
        key=lambda r: int(r["MatchNo"])
        if str(r.get("MatchNo", "")).isdigit()
        else 9999
    )

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path, fieldnames, row):
    file_exists = path.exists() and path.stat().st_size > 0

    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def main():
    print("===================================")
    print(" FIFA World Cup 2026 - Update V7")
    print("===================================")

    now = utc_now()

    current_scores = read_csv_by_fifa_id(SCORES_FILE)
    new_scores = read_csv_by_fifa_id(MANUAL_FILE)

    updated = 0
    skipped = 0

    for fifa_id, new_row in new_scores.items():
        old_row = current_scores.get(fifa_id)

        if old_row is None:
            current_scores[fifa_id] = new_row
            updated += 1

            append_csv(
                HISTORY_FILE,
                ["DateTimeUTC", "FIFA_ID", "MatchNo", "Home", "Away", "OldScore", "NewScore", "Action"],
                {
                    "DateTimeUTC": now,
                    "FIFA_ID": fifa_id,
                    "MatchNo": new_row.get("MatchNo", ""),
                    "Home": new_row.get("Home", ""),
                    "Away": new_row.get("Away", ""),
                    "OldScore": "",
                    "NewScore": new_row.get("Score", ""),
                    "Action": "INSERT",
                },
            )

        else:
            old_score = old_row.get("Score", "")
            new_score = new_row.get("Score", "")

            if old_score != new_score:
                current_scores[fifa_id] = new_row
                updated += 1

                append_csv(
                    HISTORY_FILE,
                    ["DateTimeUTC", "FIFA_ID", "MatchNo", "Home", "Away", "OldScore", "NewScore", "Action"],
                    {
                        "DateTimeUTC": now,
                        "FIFA_ID": fifa_id,
                        "MatchNo": new_row.get("MatchNo", ""),
                        "Home": new_row.get("Home", ""),
                        "Away": new_row.get("Away", ""),
                        "OldScore": old_score,
                        "NewScore": new_score,
                        "Action": "UPDATE",
                    },
                )
            else:
                skipped += 1

    write_csv(SCORES_FILE, current_scores)

    status = "SUCCESS" if updated > 0 else "NO_NEW_DATA"

    append_csv(
        LOG_FILE,
        ["DateTimeUTC", "Status", "UpdatedMatches", "SkippedMatches"],
        {
            "DateTimeUTC": now,
            "Status": status,
            "UpdatedMatches": updated,
            "SkippedMatches": skipped,
        },
    )

    print(f"{status}: updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    main()
