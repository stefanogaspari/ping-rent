"""Node 3b — Scrape Listings (Kamernet).

Purpose:
    HTTP GET the Kamernet search URL, extract listing data from the embedded
    __NEXT_DATA__ JSON (Next.js), and return a list of listing dicts.
    The page is server-side rendered and embeds all listing data in a single
    JSON payload — no CSS selector fragility.

Input:
    search_url (str)    — Kamernet search URL (all filters encoded in the URL).
    max_retries (int)   — max retry attempts on network/parsing failure (default 3).
    backoff_base (float)— seconds for exponential backoff base (default 2.0).
    session             — optional curl_cffi.requests.Session (for testing / mocking).

Output:
    list[dict] — each dict has keys:
        url (str)        — absolute URL of the listing
        title (str)      — street address and city
        price (str)      — rent string (e.g. "€1200 /month")
        location (str)   — city
        rooms (str)      — empty string (Kamernet JSON does not expose room count)
        surface (str)    — floor area (e.g. "50 m²")
        source (str)     — always "Kamernet"

Raises:
    RuntimeError: if scraping fails after all retries.
"""

import json
import logging
import re
import time
import random
from typing import Optional

from curl_cffi.requests import Session
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://kamernet.nl"
NEXT_DATA_RE = re.compile(
    r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', re.DOTALL
)
LISTING_ID_RE = re.compile(r'/en/for-rent/[^/]+/[^/]+/[^-]+-(\d+)$')


def _fetch_html(search_url: str, session, timeout: int = 15) -> str:
    """Return the raw HTML of the Kamernet search page."""
    jitter = random.uniform(0.5, 1.5)
    time.sleep(jitter)
    resp = session.get(search_url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _build_url_map(soup: BeautifulSoup) -> dict:
    """Build a listingId (int) → absolute URL (str) map from anchor tags."""
    url_map = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        m = LISTING_ID_RE.search(href)
        if m:
            listing_id = int(m.group(1))
            url_map[listing_id] = BASE_URL + href
    return url_map


def _parse_listings(html: str) -> list:
    """Extract listing dicts from the Kamernet search page HTML.

    Combines entries from the main listings array and the top-ad listings array
    embedded in __NEXT_DATA__. Deduplicates by URL. Skips items whose URL
    cannot be resolved from the page's anchor tags.

    Args:
        html: raw HTML of the Kamernet search results page.

    Returns:
        List of listing dicts, deduplicated by URL.
    """
    soup = BeautifulSoup(html, "lxml")
    url_map = _build_url_map(soup)

    match = NEXT_DATA_RE.search(html)
    if not match:
        logger.warning("__NEXT_DATA__ not found in Kamernet HTML — page structure may have changed.")
        return []

    try:
        data = json.loads(match.group(1))
        response = (
            data["props"]["pageProps"]["targetPageProps"]["findListingsResponse"]
        )
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        logger.warning("Failed to navigate Kamernet __NEXT_DATA__ structure: %s", exc)
        return []

    all_items = (response.get("listings") or []) + (response.get("topAdListings") or [])

    if not all_items:
        logger.warning("No listing items found in Kamernet __NEXT_DATA__.")
        return []

    seen_urls: set = set()
    listings = []

    for item in all_items:
        listing_id = item.get("listingId")
        url = url_map.get(listing_id)
        if not url:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        street = item.get("street", "")
        city = item.get("city", "")
        title = f"{street}, {city}".strip(", ")
        price_val = item.get("totalRentalPrice")
        price = f"€{price_val} /month" if price_val is not None else ""
        surface_val = item.get("surfaceArea")
        surface = f"{surface_val} m²" if surface_val is not None else ""

        listings.append({
            "url": url,
            "title": title,
            "price": price,
            "location": city,
            "rooms": "",
            "surface": surface,
            "source": "Kamernet",
        })

    return listings


def scrape_listings_kamernet(
    search_url: str,
    max_retries: int = 3,
    backoff_base: float = 2.0,
    session: Optional[Session] = None,
) -> list:
    """Scrape Kamernet and return a list of listing dicts.

    Args:
        search_url: the full Kamernet search URL.
        max_retries: number of retry attempts on failure.
        backoff_base: base seconds for exponential backoff between retries.
        session: optional pre-configured Session (useful for testing).

    Returns:
        List of listing dicts (may be empty if no results match the search).

    Raises:
        RuntimeError: after exhausting all retries.
    """
    own_session = session is None
    if own_session:
        session = Session(impersonate="chrome124")

    try:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Kamernet scrape attempt %d/%d: %s", attempt, max_retries, search_url)
                html = _fetch_html(search_url, session)
                listings = _parse_listings(html)
                logger.info("Scraped %d Kamernet listing(s).", len(listings))
                return listings
            except Exception as exc:
                logger.warning("Kamernet attempt %d failed: %s", attempt, exc)
                if attempt < max_retries:
                    sleep_time = backoff_base ** attempt
                    logger.info("Retrying in %.1fs…", sleep_time)
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(
                        f"Kamernet scraping failed after {max_retries} attempts: {exc}"
                    ) from exc
    finally:
        if own_session:
            session.close()

    return []


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    url = os.environ.get("KAMERNET_SEARCH_URL", "https://kamernet.nl/en/for-rent/rooms-rotterdam")
    results = scrape_listings_kamernet(url)
    import json as _json
    print(_json.dumps(results[:3], indent=2))
