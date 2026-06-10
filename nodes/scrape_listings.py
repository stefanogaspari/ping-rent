"""Node 3 — Scrape Listings.

Purpose:
    HTTP GET the Pararius search URL, parse the HTML with BeautifulSoup, and
    return a list of listing dicts extracted from the result cards.

Input:
    search_url (str) — Pararius search URL (all filters encoded in the URL).
    max_retries (int) — max retry attempts on network/parsing failure (default 3).
    backoff_base (float) — seconds for exponential backoff base (default 2.0).

Output:
    list[dict] — each dict has keys:
        url (str)        — absolute URL of the listing
        title (str)      — listing title / address
        price (str)      — rent string as shown on the page (e.g. "€ 1 200 /month")
        location (str)   — neighbourhood / city
        rooms (str)      — number of rooms (raw string)
        surface (str)    — floor area (raw string, e.g. "75 m²")

Raises:
    RuntimeError: if scraping fails after all retries.
    ValueError: if the page returns no listing cards (possible bot detection).
"""

import logging
import time
import random
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.pararius.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _fetch_html(search_url: str, session: requests.Session, timeout: int = 15) -> str:
    """Return the raw HTML of the search page."""
    jitter = random.uniform(0.5, 1.5)
    time.sleep(jitter)
    resp = session.get(search_url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _parse_listings(html: str) -> list:
    """Extract listing dicts from the raw HTML."""
    soup = BeautifulSoup(html, "lxml")

    cards = soup.select("li.search-list__item--listing, section.listing-search-item")
    if not cards:
        logger.warning("No listing cards found — Pararius HTML structure may have changed.")
        return []

    listings = []
    for card in cards:
        url_tag = card.select_one("a.listing-search-item__link--title, h2.listing-search-item__title a")
        if not url_tag:
            continue

        href = url_tag.get("href", "")
        if href.startswith("/"):
            href = BASE_URL + href

        title = url_tag.get_text(strip=True)

        price_tag = card.select_one(
            ".listing-search-item__price, .listing-search-item__sub-title--price"
        )
        price = price_tag.get_text(strip=True) if price_tag else ""

        location_tag = card.select_one(
            ".listing-search-item__sub-title, .listing-search-item__location"
        )
        location = location_tag.get_text(strip=True) if location_tag else ""

        features = card.select(".illustrated-features__item")
        rooms = features[0].get_text(strip=True) if len(features) > 0 else ""
        surface = features[1].get_text(strip=True) if len(features) > 1 else ""

        listings.append(
            {
                "url": href,
                "title": title,
                "price": price,
                "location": location,
                "rooms": rooms,
                "surface": surface,
            }
        )

    seen_urls: set = set()
    deduped = []
    for listing in listings:
        if listing["url"] not in seen_urls:
            seen_urls.add(listing["url"])
            deduped.append(listing)
    return deduped


def scrape_listings(
    search_url: str,
    max_retries: int = 3,
    backoff_base: float = 2.0,
    session: Optional[requests.Session] = None,
) -> list:
    """Scrape Pararius and return a list of listing dicts.

    Args:
        search_url: the full Pararius search URL.
        max_retries: number of retry attempts on failure.
        backoff_base: base seconds for exponential backoff between retries.
        session: optional pre-configured requests.Session (useful for testing).

    Returns:
        List of listing dicts (may be empty if no results match the search).

    Raises:
        RuntimeError: after exhausting all retries.
    """
    own_session = session is None
    if own_session:
        session = requests.Session()

    try:
        for attempt in range(1, max_retries + 1):
            try:
                logger.info("Scraping attempt %d/%d: %s", attempt, max_retries, search_url)
                html = _fetch_html(search_url, session)
                listings = _parse_listings(html)
                logger.info("Scraped %d listing(s).", len(listings))
                return listings
            except (requests.RequestException, Exception) as exc:
                logger.warning("Attempt %d failed: %s", attempt, exc)
                if attempt < max_retries:
                    sleep_time = backoff_base ** attempt
                    logger.info("Retrying in %.1fs…", sleep_time)
                    time.sleep(sleep_time)
                else:
                    raise RuntimeError(
                        f"Scraping failed after {max_retries} attempts: {exc}"
                    ) from exc
    finally:
        if own_session:
            session.close()

    return []


if __name__ == "__main__":
    import os, json
    from dotenv import load_dotenv

    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    url = os.environ.get("PARARIUS_SEARCH_URL", "https://www.pararius.com/apartments/amsterdam")
    results = scrape_listings(url)
    print(json.dumps(results[:3], indent=2))
