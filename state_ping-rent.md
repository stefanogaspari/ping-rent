# WORKFLOW STATE

## Objective
Monitor **pararius.com** and **kamernet.nl** for new apartment listings matching configurable search criteria and send a Telegram notification via CallMeBot whenever a new listing is detected. Each source has its own configurable search URL and its own seen-listings JSON file to avoid duplicate alerts. Notifications are labeled with the source site ([Pararius] / [Kamernet]). Both sources are polled on the same interval in a single loop.

## Current Status
**Deployed (2026-06-15).** First live end-to-end run completed successfully. Legacy store migrated. Both sources scraped, seeded, and verified across two cycles (cold start + live). 54 tests passing. Deployment packaged: `requirements.txt` pinned to venv, `run.py` entrypoint verified, `README.md` written, `.env.example` complete.

## Data Schema
- **Seen listings store (Pararius)**: JSON file (`outputs/seen_listings_pararius.json`) — sorted list of Pararius URLs already notified
- **Seen listings store (Kamernet)**: JSON file (`outputs/seen_listings_kamernet.json`) — sorted list of Kamernet URLs already notified
- **Listing object**: `{ url, title, price, location, rooms, surface, source }` — `source` is `"Pararius"` or `"Kamernet"`, used to label notifications
- **Config** (`.env`): `PARARIUS_SEARCH_URL`, `KAMERNET_SEARCH_URL`, `CALLMEBOT_TELEGRAM_USERNAME`, `POLL_INTERVAL_SECONDS` (default 300), `NOTIFICATION_DELAY_SECONDS` (default 2)

## Tools Used
| Script | Purpose | Status |
|--------|---------|--------|
| `nodes/load_config.py` | Load & validate `.env` → config dict (both search URLs) | Done |
| `nodes/load_seen_listings.py` | Read per-source seen-listings JSON → set of seen URLs | Done |
| `nodes/scrape_listings.py` | HTTP GET Pararius search page → listings with `source: "Pararius"` | Done |
| `nodes/scrape_listings_kamernet.py` | HTTP GET Kamernet search page → listings with `source: "Kamernet"` via `__NEXT_DATA__` JSON | Done |
| `nodes/diff_listings.py` | Set-diff scraped vs seen → list of new listings | Done |
| `nodes/send_notification.py` | POST CallMeBot Telegram API once per new listing, labeled by source | Done |
| `nodes/update_seen_listings.py` | Atomic write of updated seen set to per-source JSON | Done |
| `orchestrator.py` | Poll loop: `run_source()` × 2 per cycle (Pararius + Kamernet), migration, sleeps, repeats | Done |
| `run.py` | Standalone entrypoint | Done |
| `tests/test_load_config.py` | 6 tests for load_config (incl. KAMERNET_SEARCH_URL) | Done |
| `tests/test_load_seen_listings.py` | 5 tests for load_seen_listings | Done |
| `tests/test_scrape_listings.py` | 6 tests for Pararius scraper | Done |
| `tests/test_scrape_listings_kamernet.py` | 11 tests for Kamernet scraper | Done |
| `tests/test_diff_listings.py` | 6 tests for diff_listings | Done |
| `tests/test_send_notification.py` | 11 tests for send_notification (incl. source labels) | Done |
| `tests/test_update_seen_listings.py` | 6 tests for update_seen_listings | Done |

## Re-Design Log

### 2026-06-15 — Add Kamernet.nl as second listing source

**What changed:**
- **Objective**: expanded from Pararius-only to Pararius + Kamernet.nl
- **Data Schema**: single `seen_listings.json` → two separate stores (`seen_listings_pararius.json`, `seen_listings_kamernet.json`)
- **Listing object**: added `source` field (`"Pararius"` / `"Kamernet"`) used to prefix notifications
- **Config**: added `KAMERNET_SEARCH_URL` to `.env` / `.env.example`
- **Notifications**: messages now labeled `[Pararius]` or `[Kamernet]` at the front

**Affected workflow areas:**
- **Added**: `nodes/scrape_listings_kamernet.py` — new scraper for kamernet.nl HTML structure
- **Added**: `tests/test_scrape_listings_kamernet.py` — unit tests for Kamernet scraper
- **Modified**: `nodes/load_config.py` — added `KAMERNET_SEARCH_URL` validation
- **Modified**: `nodes/send_notification.py` — prepended `[{source}]` label to notification text
- **Modified**: `orchestrator.py` — `run_source()` helper, migration of legacy store, two-source loop
- **Modified**: `.env.example` — added `KAMERNET_SEARCH_URL` placeholder
- **Kept**: `nodes/diff_listings.py`, `nodes/scrape_listings.py`, `nodes/load_seen_listings.py`, `nodes/update_seen_listings.py`

**Rationale:** User wants broader coverage across two rental platforms in a single running workflow.

---

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
- **Kamernet scraping strategy**: `__NEXT_DATA__` JSON extraction instead of CSS selectors — Kamernet is Next.js server-rendered; all listing data is embedded in a single JSON payload, more stable than CSS selectors. URLs reconstructed from anchor tags via regex to handle all listing types (room, apartment, studio).
- **Legacy store migration**: On startup the orchestrator renames `outputs/seen_listings.json` → `outputs/seen_listings_pararius.json` if the new path is absent, preserving the seeded Rotterdam state.
- **`topAdListings` null handling**: Kamernet returns `topAdListings: null` (not absent) for some search URLs; use `or []` rather than `get(..., [])` to handle both cases.

## Known Issues
- Pararius may block automated scraping (rate limiting, CAPTCHAs, JS rendering). `curl_cffi` (Chrome 124 impersonation) + `BeautifulSoup` used; `playwright` fallback documented in workflow if needed. Windows 403 blocking resolved by the `curl-cffi` switch.
- Pararius HTML structure changes will break the CSS selectors in `scrape_listings.py`; the node logs a warning and returns an empty list rather than crashing.
- Kamernet `__NEXT_DATA__` path (`props.pageProps.targetPageProps.findListingsResponse`) may change with site updates; the node logs a warning and returns an empty list rather than crashing.
- Kamernet listings do not expose a room count in the JSON; the `rooms` field is always an empty string.
- CallMeBot Telegram rate limiting mitigated by `NOTIFICATION_DELAY_SECONDS` (default 2s) between messages.

## Next Steps
1. Start continuous polling: `venv/bin/python run.py` (local) or deploy to VPS/Docker/cron (see README)

## Latest Code Snapshot
```
nodes/
  load_config.py               — load_config(env_path) → dict (PARARIUS + KAMERNET search URLs)
  load_seen_listings.py        — load_seen_listings(store_path) → set
  scrape_listings.py           — scrape_listings(search_url, ..., session) → list[dict] (Pararius, curl_cffi)
  scrape_listings_kamernet.py  — scrape_listings_kamernet(search_url, ..., session) → list[dict]
                                  Extracts __NEXT_DATA__ JSON; URL map from anchor tags
  diff_listings.py             — diff_listings(scraped, seen) → list[dict]
  send_notification.py         — send_notification(new_listings, ...) → list[dict]; [Source] label
  update_seen_listings.py      — update_seen_listings(new_listings, seen, store_path) → set
orchestrator.py                — run_source(config, source_name, search_url, store_path, scraper_fn, is_cold_start)
                                  main(): load_config → _migrate_legacy_store → loop over sources
run.py                         — standalone entrypoint (calls orchestrator.main())
requirements.txt               — all deps pinned (runtime + dev); curl-cffi replaces requests
.env                           — KAMERNET_SEARCH_URL set to properties-rotterdam search with filters
.env.example                   — variable template with both search URL placeholders
outputs/seen_listings_pararius.json  — 80 URLs (migrated from seen_listings.json + live seeded 2026-06-15)
outputs/seen_listings_kamernet.json  — 17 URLs (seeded live 2026-06-15)
tests/                         — 54 tests, all passing
```
