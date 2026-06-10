# ping-rent

Polls [Pararius.com](https://www.pararius.com) for new apartment listings matching your search criteria and sends a Telegram notification via [CallMeBot](https://www.callmebot.com/blog/free-telegram-messages-api/) whenever a new listing appears.

---

## How it works

1. **Load config** — reads `.env`
2. **Load seen listings** — reads `outputs/seen_listings.json` (created on first run)
3. **Scrape Pararius** — HTTP GET on your search URL, parse listing cards
4. **Diff** — identify listings not yet seen
5. **Notify** — send one Telegram message per new listing via CallMeBot
6. **Update store** — write new URLs back to `outputs/seen_listings.json`
7. **Sleep** — wait `POLL_INTERVAL_SECONDS`, then repeat

**Cold-start behaviour:** the very first cycle seeds the seen store silently — no notifications are sent. Notifications begin from the second cycle onward, avoiding first-run spam.

---

## Requirements

- Python 3.9+
- A [CallMeBot Telegram](https://www.callmebot.com/blog/free-telegram-messages-api/) account (free)
  - Start a chat with `@CallMeBot_txtbot` on Telegram and send `/start`

---

## Setup

### 1. Install dependencies

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```bat
:: Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the values:

| Variable | Required | Description |
|---|---|---|
| `PARARIUS_SEARCH_URL` | Yes | Full Pararius search URL with all filters (city, max rent, min rooms, etc.) |
| `CALLMEBOT_TELEGRAM_USERNAME` | Yes | Your Telegram `@username` (or comma-separated list for multiple recipients) |
| `POLL_INTERVAL_SECONDS` | No | How often to check for new listings, in seconds. Default: `300` (5 min) |
| `NOTIFICATION_DELAY_SECONDS` | No | Delay between successive Telegram messages. Default: `2` |

**Example `.env`:**
```
PARARIUS_SEARCH_URL=https://www.pararius.com/apartments/rotterdam/0-1500/2-bedrooms
CALLMEBOT_TELEGRAM_USERNAME=@johndoe
POLL_INTERVAL_SECONDS=300
NOTIFICATION_DELAY_SECONDS=2
```

---

## Run

```bash
# macOS / Linux
source venv/bin/activate
python run.py
```

```bat
:: Windows
venv\Scripts\activate
python run.py
```

The workflow runs indefinitely. Press `Ctrl-C` to stop.

---

## Expected output

- **Console logs** — one line per cycle showing new listing count, notifications sent, and any errors
- **`outputs/seen_listings.json`** — running list of all URLs that have already been notified (grows over time; safe to delete to reset the seen store)

---

## Running as a background process

### macOS — launchd

Create `~/Library/LaunchAgents/com.ping-rent.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>          <string>com.ping-rent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/ping-rent/venv/bin/python</string>
    <string>/path/to/ping-rent/run.py</string>
  </array>
  <key>WorkingDirectory</key> <string>/path/to/ping-rent</string>
  <key>RunAtLoad</key>        <true/>
  <key>KeepAlive</key>        <true/>
  <key>StandardOutPath</key>  <string>/tmp/ping-rent.log</string>
  <key>StandardErrorPath</key><string>/tmp/ping-rent.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.ping-rent.plist
```

### Linux / VPS — systemd

Create `/etc/systemd/system/ping-rent.service`:

```ini
[Unit]
Description=ping-rent Pararius monitor

[Service]
WorkingDirectory=/path/to/ping-rent
ExecStart=/path/to/ping-rent/venv/bin/python run.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now ping-rent
```

---

## Portability notes

- **Python version**: developed and tested on Python 3.14; any Python 3.9+ should work.
- **OS**: macOS and Linux tested. Windows supported via the `venv\Scripts\activate` path.
- **No database**: state is stored in `outputs/seen_listings.json` — a plain JSON file. Back it up if you care about not re-notifying old listings after a machine migration.
- **Pararius scraping**: uses `requests` + `BeautifulSoup`. A `playwright` fallback is documented in `workflows/ping-rent.md` if Pararius starts serving JS-rendered pages. First requests to Pararius may occasionally return 403; the workflow retries automatically (3 attempts, exponential backoff).

---

## Running tests

```bash
source venv/bin/activate   # or venv\Scripts\activate on Windows
python -m pytest tests/ -v
```

39 unit tests, all passing. No network calls made during tests.
