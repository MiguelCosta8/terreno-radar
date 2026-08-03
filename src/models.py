from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Listing:
    """A single land listing pulled from a portal."""

    id: str                       # stable, unique per portal (used for dedupe)
    source: str                   # e.g. "casasapo"
    title: str
    url: str
    price: int | None = None      # euros
    area_m2: int | None = None
    location: str = ""
    description: str = ""

    @property
    def price_per_m2(self) -> float | None:
        if self.price and self.area_m2:
            return round(self.price / self.area_m2, 1)
        return None

    def haystack(self) -> str:
        """All the text we keyword-match against, lowercased."""
        return " ".join([self.title, self.description, self.location]).lower()
