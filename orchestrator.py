"""Orchestrator — ping-rent.

Traffic director for the ping-rent workflow.  Runs the deterministic poll loop:

    load_config → (one-time migration) → loop:
        for each source (Pararius, Kamernet):
            load_seen_listings → scrape → diff_listings
            → [cold-start seed OR send_notification] → update_seen_listings
        → sleep(poll_interval)

Business logic lives in the nodes.  This file is routing only.
"""

import logging
import os
import sys
import time

from nodes.load_config import load_config
from nodes.load_seen_listings import load_seen_listings
from nodes.scrape_listings import scrape_listings
from nodes.scrape_listings_kamernet import scrape_listings_kamernet
from nodes.diff_listings import diff_listings
from nodes.send_notification import send_notification
from nodes.update_seen_listings import update_seen_listings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("orchestrator")

SCRAPE_RETRIES = 3
SCRAPE_BACKOFF = 2.0

STORE_PARARIUS = os.path.join("outputs", "seen_listings_pararius.json")
STORE_KAMERNET = os.path.join("outputs", "seen_listings_kamernet.json")
STORE_LEGACY = os.path.join("outputs", "seen_listings.json")


def _migrate_legacy_store() -> None:
    """Rename the pre-Kamernet seen store to the Pararius-specific path.

    Runs once on startup. Safe to call repeatedly — no-ops if already migrated.
    """
    if os.path.exists(STORE_LEGACY) and not os.path.exists(STORE_PARARIUS):
        os.replace(STORE_LEGACY, STORE_PARARIUS)
        logger.info("Migrated %s → %s", STORE_LEGACY, STORE_PARARIUS)


def run_source(
    config: dict,
    source_name: str,
    search_url: str,
    store_path: str,
    scraper_fn,
    is_cold_start: bool,
) -> dict:
    """Execute one full poll sub-cycle for a single listing source.

    Args:
        config: validated config dict from load_config.
        source_name: human-readable source label (e.g. "Pararius", "Kamernet").
        search_url: the search URL to scrape.
        store_path: path to the per-source seen-listings JSON file.
        scraper_fn: callable with signature scraper_fn(search_url, max_retries, backoff_base).
        is_cold_start: True on the very first cycle (seed silently, no notify).

    Returns:
        dict with keys: new_count (int), notified (int), errors (int).
    """
    seen = load_seen_listings(store_path)

    try:
        scraped = scraper_fn(
            search_url,
            max_retries=SCRAPE_RETRIES,
            backoff_base=SCRAPE_BACKOFF,
        )
    except RuntimeError as exc:
        logger.error("[%s] Scraping failed — skipping source: %s", source_name, exc)
        return {"new_count": 0, "notified": 0, "errors": 1}

    new_listings = diff_listings(scraped, seen)

    if is_cold_start:
        if scraped:
            logger.info(
                "[%s] Cold start: seeding seen store with %d listing(s) — no notifications sent.",
                source_name,
                len(scraped),
            )
            update_seen_listings(scraped, seen, store_path)
        return {"new_count": 0, "notified": 0, "errors": 0}

    if not new_listings:
        logger.info("[%s] No new listings this cycle.", source_name)
        return {"new_count": 0, "notified": 0, "errors": 0}

    results = send_notification(
        new_listings,
        recipients=config["callmebot_recipients"],
        delay=config["notification_delay"],
    )

    update_seen_listings(new_listings, seen, store_path)

    notified = sum(1 for r in results if r["success"])
    errors = len(results) - notified
    return {"new_count": len(new_listings), "notified": notified, "errors": errors}


def main() -> None:
    logger.info("ping-rent starting up.")

    try:
        config = load_config()
    except EnvironmentError as exc:
        logger.critical("Configuration error: %s", exc)
        sys.exit(1)

    _migrate_legacy_store()

    sources = [
        {
            "name": "Pararius",
            "search_url": config["search_url"],
            "store_path": STORE_PARARIUS,
            "scraper_fn": scrape_listings,
        },
        {
            "name": "Kamernet",
            "search_url": config["kamernet_search_url"],
            "store_path": STORE_KAMERNET,
            "scraper_fn": scrape_listings_kamernet,
        },
    ]

    cycle = 0
    while True:
        cycle += 1
        is_cold_start = cycle == 1
        logger.info("=== Cycle %d %s===", cycle, "(cold start) " if is_cold_start else "")

        total = {"new_count": 0, "notified": 0, "errors": 0}
        for source in sources:
            stats = run_source(
                config,
                source_name=source["name"],
                search_url=source["search_url"],
                store_path=source["store_path"],
                scraper_fn=source["scraper_fn"],
                is_cold_start=is_cold_start,
            )
            for k in total:
                total[k] += stats[k]

        logger.info(
            "Cycle %d complete — new=%d notified=%d errors=%d",
            cycle,
            total["new_count"],
            total["notified"],
            total["errors"],
        )
        logger.info("Sleeping %ds until next cycle…", config["poll_interval"])
        time.sleep(config["poll_interval"])


if __name__ == "__main__":
    main()
