from __future__ import annotations

import re

from bs4 import BeautifulSoup

from ..models import Listing
from .base import BaseSource, parse_number

BASE = "https://www.olx.pt"


class OlxSource(BaseSource):
    """Parser for OLX terrenos search pages.

    OLX is messier than the other portals:
      - it mixes rentals into the same category (dropped via exclude_keywords),
      - it cross-posts Imovirtual ads (skipped here — external hrefs),
      - card area (m²) is usually absent (left as None).
    """

    name = "olx"

    def fetch(self, url: str) -> list[Listing]:
        return self.parse(self._get(url))

    def parse(self, html: str) -> list[Listing]:
        soup = BeautifulSoup(html, "lxml")
        listings: list[Listing] = []
        for card in soup.select('[data-testid="l-card"]'):
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception:
                continue
        return listings

    def _parse_card(self, card) -> Listing | None:
        anchor = card.select_one("a[href]")
        if not anchor:
            return None

        href = anchor["href"]
        if href.startswith("/"):
            href = BASE + href
        if "olx.pt" not in href:      # skip cross-posted Imovirtual/other ads
            return None
        href = href.split("?")[0]     # drop tracking query for a stable id

        title_el = card.select_one('[data-testid="ad-title"]') or card.find(["h4", "h6"])
        title = title_el.get_text(strip=True) if title_el else "Terreno"

        price_el = card.select_one('[data-testid="ad-price"]')
        price = parse_number(price_el.get_text(strip=True)) if price_el else None

        loc_el = card.select_one('[data-testid="location-date"]')
        location = loc_el.get_text(strip=True).split(" - ")[0].strip() if loc_el else ""

        area = None
        m = re.search(r"([\d\.\s]+)\s*m[²2]", card.get_text(" ", strip=True))
        if m:
            area = parse_number(m.group(1))

        return Listing(
            id=f"{self.name}:{href}",
            source=self.name,
            title=title,
            url=href,
            price=price,
            area_m2=area,
            location=location,
            description=title,        # OLX cards carry no separate description
        )
