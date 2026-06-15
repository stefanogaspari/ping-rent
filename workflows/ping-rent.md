# Workflow: ping-rent

## Purpose
Poll Pararius.com and Kamernet.nl for new apartment listings matching configurable search criteria and notify the user via Telegram (CallMeBot) whenever a new listing appears. Notifications are labeled with the source site.

## Workflow Type
**Deterministic** — fixed sequence, all function nodes, no LLM involved. Control flow is a polling loop running both sources per cycle.

## Ordered Steps

The poll loop runs one full sub-cycle per source (Pararius, then Kamernet) on every iteration.

| # | Step name | What it does | Input | Output | Node type | Script |
|---|---|---|---|---|---|---|
| 1 | Load Config | Reads all environment variables from `.env`, validates required keys including both search URLs | `.env` file | Config dict | Function | `nodes/load_config.py` |
| 2a | Load Seen Listings (Pararius) | Reads `outputs/seen_listings_pararius.json`; returns empty set if absent | `outputs/seen_listings_pararius.json` | Set of seen Pararius URLs | Function | `nodes/load_seen_listings.py` |
| 3a | Scrape Pararius | HTTP GET on Pararius search URL, parse HTML, extract listing cards with `source: "Pararius"` | Pararius search URL + config | `list[dict]` with `{ url, title, price, location, rooms, surface, source }` | Function | `nodes/scrape_listings.py` |
| 4a | Diff (Pararius) | Set-difference between scraped Pararius URLs and seen set | Scraped listings + seen set | List of new (unseen) Pararius listings | Function | `nodes/diff_listings.py` |
| 5a | Send Notifications (Pararius) | Calls CallMeBot once per new Pararius listing; message prefixed `[Pararius]` | New listings + recipients | Delivery results | Function | `nodes/send_notification.py` |
| 6a | Update Seen (Pararius) | Merges new Pararius URLs into seen set, writes atomically | New listings + seen set | Updated `outputs/seen_listings_pararius.json` | Function | `nodes/update_seen_listings.py` |
| 2b | Load Seen Listings (Kamernet) | Reads `outputs/seen_listings_kamernet.json`; returns empty set if absent | `outputs/seen_listings_kamernet.json` | Set of seen Kamernet URLs | Function | `nodes/load_seen_listings.py` |
| 3b | Scrape Kamernet | HTTP GET on Kamernet search URL, parse HTML, extract listing cards with `source: "Kamernet"` | Kamernet search URL + config | `list[dict]` with `{ url, title, price, location, rooms, surface, source }` | Function | `nodes/scrape_listings_kamernet.py` |
| 4b | Diff (Kamernet) | Set-difference between scraped Kamernet URLs and seen set | Scraped listings + seen set | List of new (unseen) Kamernet listings | Function | `nodes/diff_listings.py` |
| 5b | Send Notifications (Kamernet) | Calls CallMeBot once per new Kamernet listing; message prefixed `[Kamernet]` | New listings + recipients | Delivery results | Function | `nodes/send_notification.py` |
| 6b | Update Seen (Kamernet) | Merges new Kamernet URLs into seen set, writes atomically | New listings + seen set | Updated `outputs/seen_listings_kamernet.json` | Function | `nodes/update_seen_listings.py` |

## Orchestrator
`orchestrator.py` — deterministic poll loop:
1. Load config once at startup
2. One-time migration on startup: if `outputs/seen_listings.json` exists and `outputs/seen_listings_pararius.json` does not, rename to preserve seeded state
3. Each cycle: call `run_source()` for Pararius, then `run_source()` for Kamernet
4. `run_source(config, source_name, search_url, store_path, scraper_fn, is_cold_start)` — encapsulates steps 2–6 for one source
5. Sleep `POLL_INTERVAL_SECONDS`
6. Repeat indefinitely
7. On network/scraping failure per source: exponential backoff with max-retry cap, then continue to next source

## Cold-Start Behaviour
On the **first cycle** (`cycle == 1`): both sources seed their seen stores silently — no notifications sent. Notifications begin from cycle 2 onward to avoid first-run spam.

## External Dependencies

| Dependency | Purpose | `.env` key |
|---|---|---|
| Pararius.com | Listing source (scraped) | `PARARIUS_SEARCH_URL` |
| Kamernet.nl | Listing source (scraped) | `KAMERNET_SEARCH_URL` |
| CallMeBot Telegram API | Notification delivery | `CALLMEBOT_TELEGRAM_USERNAME` |
| `curl-cffi` | HTTP client with Chrome 124 TLS impersonation | — |
| `beautifulsoup4` + `lxml` | HTML parsing | — |
| `python-dotenv` | `.env` loading | — |

**Optional fallback**: `playwright` — if either site serves JS-rendered content that `curl-cffi` + BeautifulSoup cannot parse.

## Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Kamernet HTML structure unknown until fetch | CSS selectors derived from live HTML during `/develop` |
| Kamernet may use JS rendering | If BeautifulSoup returns no cards, add `playwright` fallback |
| Bot detection (either site) | `curl_cffi` Chrome 124 TLS impersonation applied to both scrapers from the start |
| Pararius HTML structure changes | Assert ≥1 listing returned on a known search; log warning and return empty list |
| CallMeBot rate limiting | `NOTIFICATION_DELAY_SECONDS` (default 2s) between messages |
| Network failure | Exponential backoff (base 2s, 3 attempts) per source; cycle continues after exhaustion |
| Seen-listings file corruption | Atomic write (write to `.tmp`, rename); validate JSON on load |
| Old `seen_listings.json` after migration | One-time rename to `seen_listings_pararius.json` on startup if new path absent |
