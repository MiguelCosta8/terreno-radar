from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEEN_PATH = ROOT / "seen.json"


def load_seen(path: Path = SEEN_PATH) -> set[str]:
    if path.exists():
        try:
            return set(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            return set()
    return set()


def save_seen(seen: set[str], path: Path = SEEN_PATH) -> None:
    # Cap the file so it can't grow forever; keep the most recent ~5000 ids.
    trimmed = sorted(seen)[-5000:]
    path.write_text(json.dumps(trimmed, ensure_ascii=False, indent=0), encoding="utf-8")
