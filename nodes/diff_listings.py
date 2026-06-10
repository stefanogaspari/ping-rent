"""Node 4 — Diff Listings.

Purpose:
    Compare scraped listings against the set of already-seen URLs and return
    only the listings that have not been notified yet.

Input:
    scraped (list[dict]) — listings returned by scrape_listings (each has a 'url' key).
    seen (set[str])      — set of URLs already in the seen-listings store.

Output:
    list[dict] — subset of `scraped` whose 'url' is NOT in `seen`.
                 Preserves original order (newest-first as Pararius returns them).

Raises:
    ValueError: if a listing dict is missing the 'url' key.
"""

import logging

logger = logging.getLogger(__name__)


def diff_listings(scraped: list, seen: set) -> list:
    """Return listings from `scraped` that are not in `seen`.

    Args:
        scraped: list of listing dicts, each must contain a 'url' key.
        seen: set of URL strings already notified.

    Returns:
        Ordered list of new (unseen) listing dicts.

    Raises:
        ValueError: if any listing dict lacks a 'url' key.
    """
    new_listings = []
    for listing in scraped:
        if "url" not in listing:
            raise ValueError(f"Listing dict missing 'url' key: {listing}")
        if listing["url"] not in seen:
            new_listings.append(listing)

    logger.info(
        "Diff: %d scraped, %d seen → %d new listing(s).",
        len(scraped),
        len(seen),
        len(new_listings),
    )
    return new_listings
