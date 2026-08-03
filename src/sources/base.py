from __future__ import annotations

import re
import time
from abc import ABC, abstractmethod

import requests

from ..models import Listing

# Look like a real browser. Portals reject obvious bot agents.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    "Referer": "https://casa.sapo.pt/",
}


class BaseSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, url: str) -> list[Listing]:
        """Fetch a pre-filtered search URL and return the listings on it."""
        raise NotImplementedError

    def _get(self, url: str, *, retries: int = 3, backoff: float = 3.0) -> str:
        """GET with retry/backoff on rate limits (429) and server errors."""
        last: requests.Response | None = None
        for attempt in range(retries):
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 429 or resp.status_code >= 500:
                last = resp
                time.sleep(backoff * (attempt + 1))   # 3s, 6s, 9s
                continue
            resp.raise_for_status()
            return resp.text
        # Retries exhausted — raise the last error (usually the 429).
        assert last is not None
        last.raise_for_status()
        return ""  # unreachable


def parse_number(text: str | None) -> int | None:
    """'80.000 €' -> 80000, '1.250 m²' -> 1250, None-safe."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None
