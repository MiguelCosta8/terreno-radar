from __future__ import annotations

import json
import re

from ..models import Listing
from .base import BaseSource

BASE = "https://www.imovirtual.com"

# Imovirtual is a Next.js app that embeds all listings as JSON in a
# <script id="__NEXT_DATA__"> tag — parsing that is far more robust than HTML.
_NEXT_RE = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


class ImovirtualSource(BaseSource):
    name = "imovirtual"

    def fetch(self, url: str) -> list[Listing]:
        return self.parse(self._get(url))

    def parse(self, html: str) -> list[Listing]:
        m = _NEXT_RE.search(html)
        if not m:
            return []
        try:
            data = json.loads(m.group(1))
            items = (
                data.get("props", {})
                .get("pageProps", {})
                .get("data", {})
                .get("searchAds", {})
                .get("items", [])
            )
        except (json.JSONDecodeError, AttributeError):
            return []

        listings: list[Listing] = []
        for item in items:
            try:
                listing = self._parse_item(item)
                if listing:
                    listings.append(listing)
            except Exception:
                continue
        return listings

    def _parse_item(self, item: dict) -> Listing | None:
        item_id = item.get("id")
        if item_id is None:
            return None

        href = item.get("href") or ""
        if href:
            url = f"{BASE}/" + href.replace("[lang]", "pt").lstrip("/")
        elif item.get("slug"):
            url = f"{BASE}/pt/ad/{item['slug']}"
        else:
            return None

        price = None
        total = item.get("totalPrice")
        if isinstance(total, dict) and not item.get("hidePrice"):
            price = total.get("value")

        area = item.get("areaInSquareMeters") or item.get("terrainAreaInSquareMeters")

        return Listing(
            id=f"{self.name}:{item_id}",
            source=self.name,
            title=item.get("title") or "Terreno",
            url=url,
            price=int(price) if price else None,
            area_m2=int(area) if area else None,
            location=_location(item.get("location")),
            description=item.get("shortDescription") or "",
        )


def _location(location) -> str:
    if not isinstance(location, dict):
        return ""
    addr = location.get("address") or {}
    parts = []
    for key in ("city", "province"):
        v = addr.get(key)
        if isinstance(v, dict):
            v = v.get("name")
        if v:
            parts.append(str(v))
    return ", ".join(parts)
