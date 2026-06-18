from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

FIFA_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures"

print("FIFA parser started")
print("Trying to access FIFA source:")
print(FIFA_URL)

try:
    req = Request(
        FIFA_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urlopen(req, timeout=30) as response:
        status = response.status
        content = response.read().decode("utf-8", errors="ignore")

    print("HTTP status:", status)
    print("Content length:", len(content))

    if "Portugal" in content or "World Cup" in content or "scores" in content:
        print("FIFA page content detected.")
    else:
        print("FIFA page downloaded, but expected keywords were not found.")

except HTTPError as e:
    print("HTTP error:", e.code)
    raise

except URLError as e:
    print("URL error:", e.reason)
    raise

except Exception as e:
    print("Unexpected error:", str(e))
    raise
