from __future__ import annotations

from .models import Listing


def passes(listing: Listing, filters: dict) -> bool:
    """Hard gate: drop rural land, over-budget, or too-small plots."""
    text = listing.haystack()

    if any(kw in text for kw in filters.get("exclude_keywords", [])):
        return False

    max_price = filters.get("max_price_eur")
    if max_price is not None and listing.price is not None and listing.price > max_price:
        return False

    min_area = filters.get("min_area_m2")
    if min_area is not None and listing.area_m2 is not None and listing.area_m2 < min_area:
        return False

    return True


def buildability_score(listing: Listing, filters: dict) -> int:
    """How many 'buildable' hints appear — a rough 'worth checking' signal."""
    text = listing.haystack()
    return sum(1 for kw in filters.get("buildability_keywords", []) if kw in text)
