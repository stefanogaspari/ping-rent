"""Node 1 — Load Config.

Purpose:
    Read all required environment variables from `.env` and return a validated
    config dict that every downstream node can consume.

Input:
    `.env` file in the project root (loaded via python-dotenv).

Output:
    dict with keys:
        search_url (str)               — Pararius search URL with all filters encoded
        kamernet_search_url (str)      — Kamernet search URL with all filters encoded
        callmebot_recipients (list)    — list of Telegram @usernames (API key = username)
        poll_interval (int)            — seconds between scrape cycles (default 300)
        notification_delay (float)     — seconds between Telegram messages (default 2)

Raises:
    EnvironmentError: if any required key is missing or empty.
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ("PARARIUS_SEARCH_URL", "KAMERNET_SEARCH_URL", "CALLMEBOT_TELEGRAM_USERNAME")


def load_config(env_path: str = ".env") -> dict:
    """Load and validate configuration from `.env`.

    Args:
        env_path: path to the .env file (default ".env" — relative to cwd).

    Returns:
        Validated config dict.

    Raises:
        EnvironmentError: if a required variable is missing or empty.
    """
    load_dotenv(dotenv_path=env_path, override=False)

    missing = [k for k in REQUIRED_KEYS if not os.environ.get(k, "").strip()]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )

    raw_recipients = os.environ["CALLMEBOT_TELEGRAM_USERNAME"].strip()
    recipients = [u.strip() for u in raw_recipients.split(",") if u.strip()]

    config = {
        "search_url": os.environ["PARARIUS_SEARCH_URL"].strip(),
        "kamernet_search_url": os.environ["KAMERNET_SEARCH_URL"].strip(),
        "callmebot_recipients": recipients,
        "poll_interval": int(os.environ.get("POLL_INTERVAL_SECONDS", "300")),
        "notification_delay": float(os.environ.get("NOTIFICATION_DELAY_SECONDS", "2")),
    }

    logger.info(
        "Config loaded — pararius_url=%s kamernet_url=%s poll_interval=%ds recipients=%d",
        config["search_url"],
        config["kamernet_search_url"],
        config["poll_interval"],
        len(config["callmebot_recipients"]),
    )
    return config


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import json
    cfg = load_config()
    print(json.dumps(cfg, indent=2))
