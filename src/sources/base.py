from __future__ import annotations

import re
from abc import ABC, abstractmethod

import requests

from ..models import Listing

# A realistic desktop User-Agent. Portals reject obvious bot agents.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


class BaseSource(ABC):
    name: str

    @abstractmethod
    def fetch(self, url: str) -> list[Listing]:
        """Fetch a pre-filtered search URL and return the listings on it."""
        raise NotImplementedError

    def _get(self, url: str) -> str:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return resp.text


def parse_number(text: str | None) -> int | None:
    """'80.000 €' -> 80000, '1.250 m²' -> 1250, None-safe."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None
