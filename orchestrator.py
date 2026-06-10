"""Orchestrator — ping-rent.

Traffic director for the ping-rent workflow.  Runs the deterministic poll loop:

    load_config → loop:
        load_seen_listings → scrape_listings → diff_listings
        → [cold-start seed OR send_notification] → update_seen_listings
        → sleep(poll_interval)

Business logic lives in the nodes.  This file is routing only.
"""

import logging
import sys
import time

from nodes.load_config import load_config
from nodes.load_seen_listings import load_seen_listings
from nodes.scrape_listings import scrape_listings
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


def run_once(config: dict, is_cold_start: bool) -> dict:
    """Execute one full poll cycle.

    Args:
        config: validated config dict from load_config.
        is_cold_start: True on the very first cycle (seed silently, no notify).

    Returns:
        dict with keys: new_count (int), notified (int), errors (int).
    """
    seen = load_seen_listings()

    try:
        scraped = scrape_listings(
            config["search_url"],
            max_retries=SCRAPE_RETRIES,
            backoff_base=SCRAPE_BACKOFF,
        )
    except RuntimeError as exc:
        logger.error("Scraping failed — skipping this cycle: %s", exc)
        return {"new_count": 0, "notified": 0, "errors": 1}

    new_listings = diff_listings(scraped, seen)

    if is_cold_start:
        if new_listings or scraped:
            logger.info(
                "Cold start: seeding seen store with %d listing(s) — no notifications sent.",
                len(scraped),
            )
            update_seen_listings(scraped, seen)
        return {"new_count": 0, "notified": 0, "errors": 0}

    if not new_listings:
        logger.info("No new listings this cycle.")
        return {"new_count": 0, "notified": 0, "errors": 0}

    results = send_notification(
        new_listings,
        recipients=config["callmebot_recipients"],
        delay=config["notification_delay"],
    )

    update_seen_listings(new_listings, seen)

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

    cycle = 0
    while True:
        cycle += 1
        is_cold_start = cycle == 1
        logger.info("=== Cycle %d %s===", cycle, "(cold start) " if is_cold_start else "")

        stats = run_once(config, is_cold_start=is_cold_start)
        logger.info(
            "Cycle %d complete — new=%d notified=%d errors=%d",
            cycle,
            stats["new_count"],
            stats["notified"],
            stats["errors"],
        )

        logger.info("Sleeping %ds until next cycle…", config["poll_interval"])
        time.sleep(config["poll_interval"])


if __name__ == "__main__":
    main()
