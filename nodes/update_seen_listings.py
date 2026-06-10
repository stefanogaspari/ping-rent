"""Node 6 — Update Seen Listings.

Purpose:
    Merge newly-notified listing URLs into the seen set and atomically write
    the result back to disk.  Atomic write (tmp file → rename) prevents
    data loss if the process is interrupted mid-write.

Input:
    new_listings (list[dict]) — new listings from diff_listings (each has 'url').
    seen (set[str])           — current seen set from load_seen_listings.
    store_path (str)          — path to `outputs/seen_listings.json`.

Output:
    set[str] — updated seen set (in-memory and on-disk).

Raises:
    OSError: if the file cannot be written.
    ValueError: if a listing dict is missing the 'url' key.
"""

import json
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

DEFAULT_STORE = os.path.join("outputs", "seen_listings.json")


def update_seen_listings(
    new_listings: list,
    seen: set,
    store_path: str = DEFAULT_STORE,
) -> set:
    """Merge new listing URLs into `seen` and persist atomically.

    Args:
        new_listings: list of new listing dicts (each must have 'url' key).
        seen: current set of already-notified URLs.
        store_path: path to the JSON store.

    Returns:
        Updated set of seen URLs.

    Raises:
        ValueError: if any listing dict lacks a 'url' key.
        OSError: if writing the file fails.
    """
    for listing in new_listings:
        if "url" not in listing:
            raise ValueError(f"Listing dict missing 'url' key: {listing}")

    new_urls = {listing["url"] for listing in new_listings}
    updated = seen | new_urls

    if not new_urls:
        logger.info("No new URLs to persist — seen store unchanged.")
        return updated

    os.makedirs(os.path.dirname(os.path.abspath(store_path)), exist_ok=True)

    dir_name = os.path.dirname(os.path.abspath(store_path))
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(sorted(updated), fh, indent=2)
        os.replace(tmp_path, store_path)
    except OSError:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise

    logger.info(
        "Seen store updated: %d new URL(s) added, %d total. Written to %s.",
        len(new_urls),
        len(updated),
        store_path,
    )
    return updated
