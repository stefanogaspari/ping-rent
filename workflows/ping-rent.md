# Workflow: ping-rent

## Purpose
Poll Pararius.com for new apartment listings matching configurable search criteria and notify the user via WhatsApp (CallMeBot) whenever a new listing appears.

## Workflow Type
**Deterministic** — fixed sequence, all function nodes, no LLM involved. Control flow is a polling loop.

## Ordered Steps

| # | Step name | What it does | Input | Output | Node type | Script |
|---|---|---|---|---|---|---|
| 1 | Load Config | Reads all environment variables from `.env`, validates required keys | `.env` file | Config dict | Function | `nodes/load_config.py` |
| 2 | Load Seen Listings | Reads seen-listings JSON; creates empty file if absent | `outputs/seen_listings.json` | Set of seen listing URLs | Function | `nodes/load_seen_listings.py` |
| 3 | Scrape Listings | HTTP GET on search URL, parse HTML, extract listing cards | Search URL + config | List of listing dicts `{ id, url, title, price, location, rooms, surface }` | Function | `nodes/scrape_listings.py` |
| 4 | Diff Listings | Set-difference between scraped URLs and seen set | Scraped listings + seen set | List of new (unseen) listings | Function | `nodes/diff_listings.py` |
| 5 | Send Notifications | Calls CallMeBot HTTP GET API once per new listing | New listings + phone + API key | Delivery status (logged) | Function | `nodes/send_notification.py` |
| 6 | Update Seen Listings | Merges new URLs into seen set, writes back atomically | New listings + seen set | Updated `outputs/seen_listings.json` | Function | `nodes/update_seen_listings.py` |

## Orchestrator
`orchestrator.py` — deterministic poll loop:
1. Run steps 1–6 in sequence
2. Sleep `POLL_INTERVAL_SECONDS`
3. Repeat indefinitely
4. On network/scraping failure: exponential backoff with max-retry cap, then continue

## Cold-Start Behaviour
On the **first run** (empty `seen_listings.json`): seed the seen set silently with all current listings — no notifications sent. Notifications begin from the second run onward to avoid first-run spam.

## External Dependencies

| Dependency | Purpose | `.env` key |
|---|---|---|
| Pararius.com | Listing source (scraped) | `PARARIUS_SEARCH_URL` |
| CallMeBot API | WhatsApp delivery | `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY` |
| `requests` | HTTP client | — |
| `beautifulsoup4` + `lxml` | HTML parsing | — |
| `python-dotenv` | `.env` loading | — |

**Optional fallback**: `playwright` — if Pararius serves JS-rendered content that `requests` cannot parse.

## Known Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Pararius bot detection / JS rendering | Realistic `User-Agent` + request jitter; fallback to `playwright` if needed |
| Pararius HTML structure changes | Assert ≥1 listing returned on a known search; fail loudly |
| CallMeBot rate limiting | `NOTIFICATION_DELAY_SECONDS` (default 2 s) between messages |
| Network failure | Exponential backoff with max-retry cap |
| Seen-listings file corruption | Atomic write (write to `.tmp`, rename); validate JSON on load |
