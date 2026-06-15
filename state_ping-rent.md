# WORKFLOW STATE

## Objective
Monitor pararius.com for new apartment listings matching configurable search criteria (city, max rent, min rooms, etc.) and send a Telegram notification via CallMeBot whenever a new listing is detected. Seen listings are tracked in a local JSON file to avoid duplicate alerts.

## Current Status
**Deployed.** All 6 nodes implemented, orchestrator written, 39 unit tests passing (39/39). Cold-start cycle executed successfully — 30 listings seeded in `outputs/seen_listings.json`. Standalone entrypoint `run.py` created, `requirements.txt` fully pinned, `.env.example` updated, `README.md` written. Workflow runs without the agent via `python run.py`.

**Latest change (2026-06-13):** Replaced `requests` with `curl-cffi` in `scrape_listings.py` to fix Windows bot detection (Pararius blocked Python `requests` on Windows due to TLS fingerprint mismatch). `curl_cffi` impersonates Chrome 124's TLS handshake cross-platform.

## Data Schema
- **Seen listings store**: JSON file (`outputs/seen_listings.json`) — sorted list of listing URLs already notified
- **Listing object** (scraped from Pararius): `{ url, title, price, location, rooms, surface }`
- **Config** (`.env`): `PARARIUS_SEARCH_URL`, `CALLMEBOT_TELEGRAM_USERNAME`, `CALLMEBOT_APIKEY`, `POLL_INTERVAL_SECONDS` (default 300), `NOTIFICATION_DELAY_SECONDS` (default 2)

## Tools Used
| Script | Purpose |
|--------|---------|
| `nodes/load_config.py` | Load & validate `.env` → config dict |
| `nodes/load_seen_listings.py` | Read `outputs/seen_listings.json` → set of seen URLs |
| `nodes/scrape_listings.py` | HTTP GET Pararius search page → list of listing dicts (deduplicated by URL) |
| `nodes/diff_listings.py` | Set-diff scraped vs seen → list of new listings |
| `nodes/send_notification.py` | POST CallMeBot Telegram API once per new listing |
| `nodes/update_seen_listings.py` | Atomic write of updated seen set to JSON |
| `orchestrator.py` | Poll loop: runs steps 1–6, sleeps, repeats |
| `tests/test_load_config.py` | 4 tests for load_config |
| `tests/test_load_seen_listings.py` | 5 tests for load_seen_listings |
| `tests/test_scrape_listings.py` | 6 tests for scrape_listings (parser + HTTP layer + dedup) |
| `tests/test_diff_listings.py` | 6 tests for diff_listings |
| `tests/test_send_notification.py` | 8 tests for send_notification |
| `tests/test_update_seen_listings.py` | 6 tests for update_seen_listings |

## Decisions Taken
- **Notification delivery**: CallMeBot Telegram (`@CallMeBot_txtbot`) — switched from WhatsApp (CallMeBot WhatsApp activation unreliable for UAE numbers). Telegram API key is the Telegram `@username` itself; no separate numeric key needed.
- **Pararius scraping**: Poll the search URL on a configurable interval; compare scraped listing IDs against the seen-listings JSON file.
- **State storage**: Local JSON file (`outputs/seen_listings.json`) — simple, no DB dependency.
- **Deployment**: Designed to run on both local machine (cron / launchd) and a VPS (cron). Docker-friendly for VPS.
- **Error handling**: Retry with exponential backoff (base 2s, 3 attempts) on network/scraping failures; cycle skipped on exhaustion rather than hard crash.
- **Workflow type**: Deterministic (no LLM involved).
- **Language**: Python 3.x with pip/venv.
- **Cold-start behaviour**: First cycle seeds the seen store silently — no notifications sent. Avoids first-run spam.
- **Atomic write**: `tempfile.mkstemp` + `os.replace` for seen store — prevents data loss on crash mid-write.
- **Session injection**: All HTTP-touching nodes accept an optional `session` parameter, enabling clean mocking in tests without patching globals.
- **Scraper deduplication**: `_parse_listings` deduplicates by URL before returning — Pararius HTML contains both `li.search-list__item--listing` and a nested `section.listing-search-item` per card, causing each listing to match the CSS selector twice.
- **HTTP client**: switched from `requests` to `curl-cffi` (`Session(impersonate="chrome124")`) — resolves Windows-specific TLS fingerprint bot detection by Pararius.

## Known Issues
- Pararius may block automated scraping (rate limiting, CAPTCHAs, JS rendering). `curl_cffi` (Chrome 124 impersonation) + `BeautifulSoup` used; `playwright` fallback documented in workflow if needed. Windows 403 blocking resolved by the `curl-cffi` switch.
- Pararius HTML structure changes will break the CSS selectors in `scrape_listings.py`; the node logs a warning and returns an empty list rather than crashing.
- CallMeBot Telegram rate limiting mitigated by `NOTIFICATION_DELAY_SECONDS` (default 2s) between messages.

## Next Steps
1. Set up as a background process via launchd (macOS), systemd (Linux), or Docker — instructions in README.md
2. Optionally extend: Docker packaging, cron-based scheduling, or a Telegram command to pause/resume alerts

## Latest Code Snapshot
```
nodes/
  load_config.py          — load_config(env_path) → dict (uses CALLMEBOT_TELEGRAM_USERNAME)
  load_seen_listings.py   — load_seen_listings(store_path) → set
  scrape_listings.py      — scrape_listings(search_url, ..., session) → list[dict] (URL-deduplicated)
                            Uses curl_cffi.requests.Session(impersonate="chrome124") for HTTP
  diff_listings.py        — diff_listings(scraped, seen) → list[dict]
  send_notification.py    — send_notification(new_listings, user, api_key, ...) → list[dict]
  update_seen_listings.py — update_seen_listings(new_listings, seen, store_path) → set
orchestrator.py           — main() poll loop; run_once(config, is_cold_start) → stats dict
run.py                    — standalone entrypoint (calls orchestrator.main())
requirements.txt          — all deps pinned (runtime + dev); curl-cffi replaces requests
.env.example              — variable template with descriptive placeholders
README.md                 — setup, run, background-process, portability docs
outputs/seen_listings.json — 30 URLs seeded (Rotterdam search, 2026-06-10)
tests/                    — 39 tests, all passing
```
