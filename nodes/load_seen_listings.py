"""Node 2 — Load Seen Listings.

Purpose:
    Read the persisted set of already-notified listing URLs from JSON.
    If the file is absent or empty, return an empty set (cold-start).

Input:
    store_path (str) — path to `outputs/seen_listings.json`

Output:
    set[str] — set of listing URLs that have already been notified.

Raises:
    ValueError: if the file exists but contains invalid JSON or an unexpected type.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

DEFAULT_STORE = os.path.join("outputs", "seen_listings.json")


def load_seen_listings(store_path: str = DEFAULT_STORE) -> set:
    """Load the seen-listings set from disk.

    Args:
        store_path: path to the JSON store file.

    Returns:
        set of URL strings that have already been notified.

    Raises:
        ValueError: if the file contains corrupt or unexpected data.
    """
    if not os.path.exists(store_path):
        logger.info("Seen-listings store not found at %s — starting fresh.", store_path)
        return set()

    try:
        with open(store_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Seen-listings file at {store_path!r} contains invalid JSON: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            f"Seen-listings file must contain a JSON array, got {type(data).__name__}."
        )

    seen = set(data)
    logger.info("Loaded %d seen listing(s) from %s.", len(seen), store_path)
    return seen


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(load_seen_listings())
