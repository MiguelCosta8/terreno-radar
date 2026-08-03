from __future__ import annotations

from bs4 import BeautifulSoup

from ..models import Listing
from .base import BaseSource, parse_number

BASE = "https://casa.sapo.pt"


class CasaSapoSource(BaseSource):
    """Parser for Casa SAPO search-result pages.

    Card structure (verified against a live terrenos search):
        div.property-info-content
          a.property-info[href]
            div.property-type          -> "Terreno T1"
            div.property-location       -> "Vila Nova de Famalicão e Calendário, ..."
            div.property-features
              div.property-features-text -> "1 446m²"
            div.property-price
              div.property-price-value   -> "750.000 €"
          div.property-description       -> long free text (buildability hints live here)
    """

    name = "casasapo"

    def fetch(self, url: str) -> list[Listing]:
        return self.parse(self._get(url))

    def parse(self, html: str) -> list[Listing]:
        soup = BeautifulSoup(html, "lxml")
        listings: list[Listing] = []
        for card in soup.select("div.property-info-content"):
            try:
                listing = self._parse_card(card)
                if listing:
                    listings.append(listing)
            except Exception:
                # One malformed card must never kill the whole run.
                continue
        return listings

    def _parse_card(self, card) -> Listing | None:
        anchor = card.select_one("a.property-info[href]")
        if not anchor:
            return None

        href = anchor["href"]
        if href.startswith("/"):
            href = BASE + href

        title = _text(card.select_one(".property-type")) or "Terreno"
        location = _text(card.select_one(".property-location"))
        price = parse_number(_text(card.select_one(".property-price-value")))
        area = parse_number(_area_text(card))
        description = _text(card.select_one(".property-description"))

        return Listing(
            id=f"{self.name}:{href}",   # href carries a unique listing UUID
            source=self.name,
            title=title,
            url=href,
            price=price,
            area_m2=area,
            location=location,
            description=description,
        )


def _text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


def _area_text(card) -> str:
    """Pick the feature entry that holds the m² area."""
    for el in card.select(".property-features-text"):
        t = el.get_text(" ", strip=True)
        if "m" in t.lower() and any(ch.isdigit() for ch in t):
            return t
    return ""
