from urllib.request import Request, urlopen
import re

BASE_URL = "https://www.fifa.com"
JS_URL = "https://www.fifa.com/static/js/main.d9a5be55.js"

print("FIFA parser diagnostic v3")
print("JS URL:", JS_URL)

req = Request(JS_URL, headers={"User-Agent": "Mozilla/5.0"})

with urlopen(req, timeout=30) as response:
    js = response.read().decode("utf-8", errors="ignore")

print("JS length:", len(js))

keywords = [
    "cxm-api",
    "api.fifa.com",
    "matches",
    "fixtures",
    "scores",
    "competitions",
    "tournament",
    "fifaplusweb",
]

print("\nKeyword search:")
for k in keywords:
    print(k, "=", k in js)

print("\nCandidate API fragments:")
patterns = [
    r"https?://[^\"']+",
    r"/fifaplusweb/api[^\"']+",
    r"/api/[^\"']+",
    r"[A-Za-z0-9_/-]*(matches|fixtures|scores|competitions|tournament)[A-Za-z0-9_/?=&.-]*",
]

found = set()

for pattern in patterns:
    for m in re.findall(pattern, js):
        if isinstance(m, tuple):
            continue

for m in re.findall(r"https?://[^\"'\\\s]+", js):
    if any(x in m.lower() for x in ["api", "fifa", "match", "fixture", "score", "tournament"]):
        found.add(m[:300])

for m in re.findall(r"[/A-Za-z0-9_.-]*(?:matches|fixtures|scores|competitions|tournament)[/A-Za-z0-9_?=&:.,-]*", js, flags=re.I):
    found.add(m[:300])

for item in sorted(found):
    print(item)

print("\nFirst 1500 chars:")
print(js[:1500])
