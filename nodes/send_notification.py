"""Node 5 — Send Notification.

Purpose:
    Send one Telegram message per new listing to every configured recipient
    via the CallMeBot Telegram API. For CallMeBot Telegram the API key equals
    the recipient's @username, so no separate key is needed.

Input:
    new_listings (list[dict]) — new listings from diff_listings.
    recipients (list[str])    — Telegram @usernames registered with CallMeBot.
    delay (float)             — seconds to sleep between messages (default 2.0).
    session                   — optional requests.Session (for testing / mocking).

Output:
    list[dict] — delivery results, one per (listing × recipient):
        { url (str), recipient (str), success (bool), status_code (int | None), error (str | None) }

Raises:
    Nothing — all per-message errors are captured in the result list and logged.

Notes:
    CallMeBot Telegram API endpoint:
        https://api.callmebot.com/text.php?user=@<USERNAME>&text=<TEXT>&apikey=@<USERNAME>
    Setup: search @CallMeBot_txtbot on Telegram, start it, send /start.
"""

import logging
import time
import urllib.parse
from typing import Optional

import requests

logger = logging.getLogger(__name__)

CALLMEBOT_ENDPOINT = "https://api.callmebot.com/text.php"


def _build_message(listing: dict) -> str:
    """Format a listing dict into a human-readable Telegram message."""
    source = listing.get("source", "")
    label = f"[{source}] " if source else ""
    parts = [f"🏠 {label}New listing!"]
    if listing.get("title"):
        parts.append(f"📍 {listing['title']}")
    if listing.get("location"):
        parts.append(f"🏙️ {listing['location']}")
    if listing.get("price"):
        parts.append(f"💶 {listing['price']}")
    if listing.get("rooms"):
        parts.append(f"🛏️ {listing['rooms']}")
    if listing.get("surface"):
        parts.append(f"📐 {listing['surface']}")
    parts.append(f"🔗 {listing.get('url', '')}")
    return "\n".join(parts)


def send_notification(
    new_listings: list,
    recipients: list,
    delay: float = 2.0,
    session: Optional[requests.Session] = None,
) -> list:
    """Send one Telegram notification per new listing to every recipient.

    Args:
        new_listings: list of new listing dicts.
        recipients: list of Telegram @usernames (API key is the username itself).
        delay: seconds to sleep between successive messages.
        session: optional requests.Session (pass a Mock in tests).

    Returns:
        List of result dicts with keys: url, recipient, success, status_code, error.
    """
    if not new_listings or not recipients:
        logger.info("No new listings or no recipients — nothing to notify.")
        return []

    own_session = session is None
    if own_session:
        session = requests.Session()

    results = []
    deliveries = [(listing, recipient) for listing in new_listings for recipient in recipients]

    try:
        for i, (listing, recipient) in enumerate(deliveries):
            url = listing.get("url", "")
            message = _build_message(listing)
            params = {
                "user": recipient,
                "text": message,
                "apikey": recipient,
            }
            try:
                resp = session.get(
                    CALLMEBOT_ENDPOINT,
                    params=params,
                    timeout=10,
                )
                resp.raise_for_status()
                logger.info(
                    "Notification sent to %s for listing: %s (HTTP %d)",
                    recipient, url, resp.status_code,
                )
                results.append(
                    {"url": url, "recipient": recipient, "success": True, "status_code": resp.status_code, "error": None}
                )
            except requests.RequestException as exc:
                status = exc.response.status_code if hasattr(exc, "response") and exc.response else None
                logger.error("Failed to notify %s for listing %s: %s", recipient, url, exc)
                results.append(
                    {"url": url, "recipient": recipient, "success": False, "status_code": status, "error": str(exc)}
                )

            if i < len(deliveries) - 1:
                time.sleep(delay)
    finally:
        if own_session:
            session.close()

    successes = sum(1 for r in results if r["success"])
    logger.info("Notifications: %d/%d delivered.", successes, len(results))
    return results
