import csv

print("FIFA parser started")

with open("worldcup2026_scores.csv", "r", encoding="utf-8") as f:
    rows = list(csv.reader(f))

print("Matches loaded:", len(rows)-1)
