# ping-rent

Monitor **Pararius.com** and **Kamernet.nl** for new apartment listings and receive instant Telegram notifications via CallMeBot whenever a new listing appears.

---

## How it works

The workflow polls both rental platforms on a configurable interval. On the first cycle it silently seeds the seen-listings store (no notifications sent). From cycle 2 onward, any listing not previously seen triggers a Telegram message labeled `[Pararius]` or `[Kamernet]`.

---

## Quick start

### 1. Install dependencies

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `PARARIUS_SEARCH_URL` | Yes | Pararius search URL with your filters (city, max rent, rooms, etc.) |
| `KAMERNET_SEARCH_URL` | Yes | Kamernet search URL with your filters |
| `CALLMEBOT_TELEGRAM_USERNAME` | Yes | Telegram `@username`(s), comma-separated for multiple recipients |
| `POLL_INTERVAL_SECONDS` | No | How often to check both sites (default: `300` = 5 minutes) |
| `NOTIFICATION_DELAY_SECONDS` | No | Delay between successive Telegram messages (default: `2`) |

**Telegram setup (one-time per recipient):** Each recipient must open Telegram, search for `@CallMeBot_txtbot`, and send `/start`.

### 3. Run

```bash
# macOS / Linux
python run.py

# Windows
python run.py
```

Press `Ctrl-C` to stop.

---

## Expected output

| File | Description |
|---|---|
| `outputs/seen_listings_pararius.json` | Sorted list of Pararius URLs already notified — prevents duplicate alerts |
| `outputs/seen_listings_kamernet.json` | Sorted list of Kamernet URLs already notified |

On each cycle the orchestrator logs progress to stdout:

```
2026-06-15 10:00:00  INFO      orchestrator — === Cycle 2 ===
2026-06-15 10:00:03  INFO      orchestrator — [Pararius] No new listings this cycle.
2026-06-15 10:00:07  INFO      orchestrator — [Kamernet] No new listings this cycle.
2026-06-15 10:00:07  INFO      orchestrator — Cycle 2 complete — new=0 notified=0 errors=0
2026-06-15 10:00:07  INFO      orchestrator — Sleeping 300s until next cycle…
```

---

## Run tests

```bash
pytest tests/ -v
```

54 tests — all passing.

---

## Portability notes

- **Python**: requires Python 3.9+
- **HTTP client**: `curl-cffi` with Chrome 124 TLS impersonation — handles bot detection on both sites without Playwright
- **No browser required**: fully headless, no Selenium/Playwright dependency
- **Windows**: works; `curl-cffi` resolves TLS fingerprinting issues that block the standard `requests` library
- **VPS / cron**: designed to run continuously as a background process; wrap with `nohup` or a systemd service, or schedule with cron (see below)

### Running as a background process (macOS / Linux)

```bash
nohup python run.py > ping-rent.log 2>&1 &
```

### Running as a cron job (every 5 minutes, no internal sleep)

If you prefer cron over the built-in poll loop, set `POLL_INTERVAL_SECONDS=0` and add to crontab:

```
*/5 * * * * cd /path/to/ping-rent && venv/bin/python run.py
```

### Docker (optional)

A minimal Dockerfile is straightforward since there are no system dependencies beyond Python 3.9+:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

Build and run:

```bash
docker build -t ping-rent .
docker run --env-file .env ping-rent
```
