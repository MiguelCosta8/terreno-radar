from __future__ import annotations

import os
import sys

# Windows consoles default to cp1252 and choke on emoji / PT characters in logs.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from . import telegram
from .config import load_config
from .filters import buildability_score, passes
from .sources import get_source
from .storage import load_seen, save_seen

DRY_RUN = os.environ.get("DRY_RUN") == "1"


def main() -> int:
    config = load_config()
    filters = config.get("filters", {})
    searches = config.get("searches", [])

    seen = load_seen()
    newly_seen: set[str] = set()
    alerts = 0

    for search in searches:
        url = search.get("url", "")
        if not url or url.startswith("PASTE_"):
            print(f"⏭  skipping '{search.get('name')}' — no URL set yet")
            continue

        source = get_source(search["source"])
        try:
            listings = source.fetch(url)
        except Exception as e:
            print(f"⚠️  fetch failed for {search.get('name')}: {e}")
            continue

        print(f"🔎 {search.get('name')}: {len(listings)} listings on page")

        for listing in listings:
            if listing.id in seen or listing.id in newly_seen:
                continue
            newly_seen.add(listing.id)

            if not passes(listing, filters):
                continue

            score = buildability_score(listing, filters)
            message = telegram.format_listing(listing, score)

            if DRY_RUN:
                print("\n--- would send ---\n" + message + "\n")
            else:
                telegram.send_message(message)
            alerts += 1

    save_seen(seen | newly_seen)
    print(f"✅ done — {len(newly_seen)} new listings seen, {alerts} alerts sent"
          f"{' (dry run)' if DRY_RUN else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
