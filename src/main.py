from __future__ import annotations

import os
import sys
import time

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


def _load_dotenv() -> None:
    """Load TELEGRAM_* from a local .env file (no dependency).

    On GitHub the vars already come from secrets, so setdefault won't override.
    """
    from pathlib import Path

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())


def main() -> int:
    _load_dotenv()
    config = load_config()
    filters = config.get("filters", {})
    searches = config.get("searches", [])

    seen = load_seen()
    first_run = len(seen) == 0          # empty state = we've never run before
    newly_seen: set[str] = set()
    matched: list[tuple] = []           # (listing, score) that pass the filters
    alerts = 0

    for i, search in enumerate(searches):
        if i > 0:
            time.sleep(3)               # be polite — small pause between towns
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

            if passes(listing, filters):
                matched.append((listing, buildability_score(listing, filters)))

    # ---- Decide what to send -------------------------------------------------
    if first_run:
        # Don't flood on the very first run — just start tracking, send a summary.
        summary = (
            f"🌱 <b>Terreno Radar</b> is live — now tracking "
            f"{len(matched)} matching terrenos in your areas.\n"
            f"From now on you'll only get a ping when a <b>new</b> one appears."
        )
        if DRY_RUN:
            print("\n--- would send (first-run summary) ---\n" + summary + "\n")
        elif matched:
            telegram.send_message(summary)
        print(f"🚀 first run: recorded {len(newly_seen)} listings "
              f"({len(matched)} matched filters) — no individual alerts")
    else:
        for listing, score in matched:
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
