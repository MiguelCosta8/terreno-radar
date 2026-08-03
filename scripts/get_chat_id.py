"""Print the Telegram chat id(s) your bot can see.

Usage:
    1. Add your bot to the group and send any message there.
    2. python scripts/get_chat_id.py <BOT_TOKEN>
"""

import sys

import requests


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/get_chat_id.py <BOT_TOKEN>")
        return 1

    token = sys.argv[1]
    resp = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("result"):
        print("No updates found. Send a message in the group (with the bot added), then re-run.")
        return 0

    seen = {}
    for update in data["result"]:
        chat = (update.get("message") or update.get("channel_post") or {}).get("chat")
        if chat:
            seen[chat["id"]] = chat.get("title") or chat.get("username") or chat.get("type")

    print("Chat id(s) your bot can see:")
    for chat_id, name in seen.items():
        print(f"  {chat_id}   ({name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
