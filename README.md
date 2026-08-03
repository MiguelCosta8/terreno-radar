# 🌱 Terreno Radar

Monitors Portuguese property portals for **buildable land plots (terrenos urbanos)** around
**Vila Nova de Famalicão, Guimarães, and Santo Tirso**, and pings a **Telegram** chat when a
new one worth checking appears. Runs for free on **GitHub Actions**.

Target defaults: max **€80.000**, land you could build a house on.

---

## How it works

```
 GitHub Actions (every 15 min)
        │
        ▼
  fetch each search URL ─► parse listings ─► drop already-seen ─► filter (buildable, price, size) ─► Telegram alert
                                                     │
                                                seen.json  (committed back to the repo = persistent memory)
```

You give each portal a **pre-filtered search URL** (you set location + price on the portal's own
website, copy the resulting URL). The script polls those URLs — that's far more robust than
reverse-engineering each portal's query format, and it keeps location/price logic in the portal's hands.

---

## One-time setup

### 1. Create a Telegram bot (2 minutes)
1. In Telegram, open a chat with **@BotFather**.
2. Send `/newbot`, follow the prompts, and copy the **bot token** it gives you
   (looks like `123456789:AAE...`).
3. Create a group (or channel), and **add your bot to it**.
4. Send any message in the group (e.g. "hi").
5. Get your **chat id**: run `python scripts/get_chat_id.py <YOUR_BOT_TOKEN>` — it prints the chat id
   (a negative number for groups, e.g. `-1001234567890`).

### 2. Configure your searches
Edit [`config.yaml`](config.yaml):
- Adjust `max_price_eur` / `min_area_m2` if you want.
- For each portal, go to the portal's website, filter for **terrenos** in your municipalities under
  €80k, then **copy the URL from your browser** into the `url:` field.

### 3. Run it locally first (recommended)
```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# mac/linux: source .venv/bin/activate
pip install -r requirements.txt

# put your token + chat id in a .env file (copy .env.example)
python -m src.main          # sends real alerts
DRY_RUN=1 python -m src.main # prints instead of sending
```

### 4. Deploy to GitHub Actions (free, always-on)
1. Create a **public** GitHub repo (public = unlimited free Actions minutes) and push this folder.
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**, add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. That's it — [`.github/workflows/monitor.yml`](.github/workflows/monitor.yml) runs every 15 minutes.
   Trigger a manual test run from the **Actions** tab → *Terreno Radar* → *Run workflow*.

---

## Tuning the scraper

I could not verify each portal's live HTML, so the parser in `src/sources/` is a first pass.
To lock it in, run the debug helper and send me the output:

```bash
python scripts/debug_fetch.py <your-search-url>   # saves debug_page.html
```

Then I map the real selectors exactly.

## Legal / etiquette
This is a personal monitoring tool. Keep the schedule modest (15+ min), don't hammer the portals,
and respect their Terms of Service. Some portals (esp. Idealista) actively block datacenter IPs —
if a portal blocks the GitHub runner, run that source from home instead (a Raspberry Pi or your PC on
a cron), or add a proxy for that source only.
