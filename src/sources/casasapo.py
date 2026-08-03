from __future__ import annotations

from bs4 import BeautifulSoup

from ..models import Listing
from .base import BaseSource, parse_number

# ---------------------------------------------------------------------------
# ⚠️  SELECTORS NEED VERIFICATION against the live Casa SAPO / SUPERCASA HTML.
# The structure below is a reasonable first pass. Run:
#     python scripts/debug_fetch.py <search-url>
# then send debug_page.html so the selectors can be mapped exactly.
# Everything downstream (dedupe, filter, Telegram) already works regardless.
# ---------------------------------------------------------------------------


class CasaSapoSource(BaseSource):
    name = "casasapo"

    def fetch(self, url: str) -> list[Listing]:
        html = self._get(url)
        soup = BeautifulSoup(html, "lxml")
        listings: list[Listing] = []

        # Each result card. Casa SAPO has historically used a "property" item card;
        # this selector is a best guess and likely needs adjusting.
        cards = soup.select("[class*='property'], article, .searchResultProperty")

        for card in cards:
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception:
                # Never let one malformed card kill the whole run.
                continue

        return listings

    def _parse_card(self, card) -> Listing | None:
        link = card.find("a", href=True)
        if not link:
            return None

        href = link["href"]
        if href.startswith("/"):
            href = "https://casa.sapo.pt" + href

        title = link.get_text(strip=True) or card.get("title", "") or "Terreno"

        # Price / area often live in labelled spans; grab the raw card text as a
        # fallback so filtering still has something to chew on.
        text = card.get_text(" ", strip=True)
        price = _extract_price(text)
        area = _extract_area(text)

        # A stable id: prefer the listing URL (unique per property).
        listing_id = f"{self.name}:{href}"

        return Listing(
            id=listing_id,
            source=self.name,
            title=title[:200],
            url=href,
            price=price,
            area_m2=area,
            location="",          # fill once real selectors are known
            description=text[:500],
        )


def _extract_price(text: str) -> int | None:
    # Look for a euro amount, e.g. "75.000 €"
    import re

    m = re.search(r"([\d\.\s]+)\s*€", text)
    return parse_number(m.group(1)) if m else None


def _extract_area(text: str) -> int | None:
    import re

    m = re.search(r"([\d\.\s]+)\s*m[²2]", text)
    return parse_number(m.group(1)) if m else None
