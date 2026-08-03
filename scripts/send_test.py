"""Send a test message to confirm your Telegram bot + chat id work.

Usage:
    python scripts/send_test.py <BOT_TOKEN> <CHAT_ID>
"""

import sys

import requests


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python scripts/send_test.py <BOT_TOKEN> <CHAT_ID>")
        return 1

    token, chat_id = sys.argv[1], sys.argv[2]
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": "✅ <b>Terreno Radar</b> is connected! You'll get land alerts here.",
            "parse_mode": "HTML",
        },
        timeout=20,
    )
    if resp.ok:
        print("Sent! Check your Telegram group.")
        return 0

    print(f"Failed (HTTP {resp.status_code}): {resp.text}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
