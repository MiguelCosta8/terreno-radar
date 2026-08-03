"""Download a search URL to debug_page.html so the HTML can be inspected.

Usage:
    python scripts/debug_fetch.py "<search-url>"
"""

import sys

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python scripts/debug_fetch.py "<search-url>"')
        return 1

    url = sys.argv[1]
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print(f"HTTP {resp.status_code}, {len(resp.text):,} chars")
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("Saved -> debug_page.html")

    if resp.status_code != 200 or "captcha" in resp.text.lower():
        print("⚠️  Looks like the portal may be blocking automated requests "
              "(non-200 or a captcha page). See README → Legal / etiquette.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
