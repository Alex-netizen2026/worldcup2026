from pathlib import Path
from datetime import datetime, timezone
import csv
import re

SCORES_FILE = Path("worldcup2026_scores.csv")
MANUAL_FILE = Path("manual_scores.csv")
HISTORY_FILE = Path("worldcup2026_history.csv")
LOG_FILE = Path("update_log.csv")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def valid_score(score: str) -> bool:
    return bool(re.fullmatch(r"\d+-\d+", score.strip()))


def read_scores(path: Path) -> dict:
    data = {}

    if not path.exists():
        return data

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            match_no = str(row.get("MatchNo", "")).strip()
            score = str(row.get("Score", "")).strip()

            if match_no.isdigit() and valid_score(score):
                data[match_no] = score

    return data


def write_scores(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["MatchNo", "Score"])
        writer.writeheader()

        for match_no in sorted(data, key=lambda x: int(x)):
            writer.writerow({
                "MatchNo": match_no,
                "Score": data[match_no],
            })


def append_csv(path: Path, fieldnames: list, row: dict) -> None:
    file_exists = path.exists() and path.stat().st_size > 0

    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(row)


def main() -> None:
    now = utc_now()

    current_scores = read_scores(SCORES_FILE)
    manual_scores = read_scores(MANUAL_FILE)

    updated = 0

    for match_no, new_score in manual_scores.items():
        old_score = current_scores.get(match_no, "")

        if old_score != new_score:
            current_scores[match_no] = new_score
            updated += 1

            append_csv(
                HISTORY_FILE,
                ["DateTimeUTC", "MatchNo", "OldScore", "NewScore"],
                {
                    "DateTimeUTC": now,
                    "MatchNo": match_no,
                    "OldScore": old_score if old_score else "blank",
                    "NewScore": new_score,
                },
            )

    write_scores(SCORES_FILE, current_scores)

    status = "SUCCESS" if updated > 0 else "NO_NEW_DATA"

    append_csv(
        LOG_FILE,
        ["DateTimeUTC", "Status", "UpdatedMatches"],
        {
            "DateTimeUTC": now,
            "Status": status,
            "UpdatedMatches": updated,
        },
    )

    print(f"{status}: updated matches = {updated}")


if __name__ == "__main__":
    main()
