from __future__ import annotations

import os

import requests

from .models import Listing

API = "https://api.telegram.org"


def send_message(text: str, *, token: str | None = None, chat_id: str | None = None) -> None:
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = chat_id or os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        f"{API}/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
        timeout=20,
    )
    resp.raise_for_status()


def format_listing(listing: Listing, score: int) -> str:
    price = f"{listing.price:,} €".replace(",", ".") if listing.price else "price n/a"
    area = f"{listing.area_m2} m²" if listing.area_m2 else "area n/a"
    ppm = f" · {listing.price_per_m2} €/m²" if listing.price_per_m2 else ""
    hints = "🏗️ buildable hints: " + ("✅" * score if score else "—")

    return (
        f"🌱 <b>New terreno</b> · {listing.source}\n"
        f"<b>{listing.title}</b>\n"
        f"📍 {listing.location or 'location n/a'}\n"
        f"💶 {price}   📐 {area}{ppm}\n"
        f"{hints}\n"
        f'<a href="{listing.url}">Open listing →</a>'
    )
