import json
import pytest
from unittest.mock import MagicMock, patch
from nodes.scrape_listings_kamernet import scrape_listings_kamernet, _parse_listings


def _make_next_data(listings=None, top_listings=None):
    return {
        "props": {
            "pageProps": {
                "targetPageProps": {
                    "findListingsResponse": {
                        "listings": listings or [],
                        "topAdListings": top_listings or [],
                    }
                }
            }
        }
    }


def _make_html(listings=None, top_listings=None, extra_links=""):
    data = _make_next_data(listings=listings, top_listings=top_listings)
    all_items = (listings or []) + (top_listings or [])
    links_html = ""
    for item in all_items:
        lid = item["listingId"]
        city = item.get("citySlug", "rotterdam")
        street = item.get("streetSlug", "test-street")
        links_html += f'<a href="/en/for-rent/room-{city}/{street}/room-{lid}">Link</a>\n'
    links_html += extra_links
    return f"""<!DOCTYPE html>
<html>
<head>
<script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script>
</head>
<body>{links_html}</body>
</html>"""


LISTING_1 = {
    "listingId": 1001,
    "street": "Test Street",
    "streetSlug": "test-street",
    "city": "Rotterdam",
    "citySlug": "rotterdam",
    "totalRentalPrice": 1200,
    "surfaceArea": 50,
    "listingType": 1,
}

LISTING_2 = {
    "listingId": 1002,
    "street": "Canal Road",
    "streetSlug": "canal-road",
    "city": "Rotterdam",
    "citySlug": "rotterdam",
    "totalRentalPrice": 950,
    "surfaceArea": 35,
    "listingType": 1,
}


class TestParseListings:
    def test_parses_two_listings(self):
        html = _make_html(listings=[LISTING_1, LISTING_2])
        results = _parse_listings(html)
        assert len(results) == 2

    def test_correct_field_mapping(self):
        html = _make_html(listings=[LISTING_1])
        results = _parse_listings(html)
        r = results[0]
        assert r["url"] == "https://kamernet.nl/en/for-rent/room-rotterdam/test-street/room-1001"
        assert r["title"] == "Test Street, Rotterdam"
        assert r["price"] == "€1200 /month"
        assert r["location"] == "Rotterdam"
        assert r["surface"] == "50 m²"
        assert r["source"] == "Kamernet"

    def test_source_field_is_kamernet(self):
        html = _make_html(listings=[LISTING_1])
        results = _parse_listings(html)
        assert all(r["source"] == "Kamernet" for r in results)

    def test_deduplicates_across_listings_and_top_ads(self):
        # Same listing appears in both listings and topAdListings
        html = _make_html(listings=[LISTING_1], top_listings=[LISTING_1])
        results = _parse_listings(html)
        urls = [r["url"] for r in results]
        assert len(urls) == len(set(urls)), "Duplicate URLs should be removed"
        assert len(results) == 1

    def test_missing_next_data_returns_empty(self):
        html = "<html><body><p>No data</p></body></html>"
        results = _parse_listings(html)
        assert results == []

    def test_empty_listings_returns_empty(self):
        html = _make_html(listings=[], top_listings=[])
        results = _parse_listings(html)
        assert results == []

    def test_skips_items_without_url_in_html(self):
        # LISTING_1 has no corresponding anchor tag in the HTML
        data = _make_next_data(listings=[LISTING_1])
        html = f"""<html>
<head><script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script></head>
<body></body></html>"""
        results = _parse_listings(html)
        assert results == []

    def test_top_ad_listings_included(self):
        html = _make_html(listings=[], top_listings=[LISTING_2])
        results = _parse_listings(html)
        assert len(results) == 1
        assert results[0]["url"].endswith("room-1002")


class TestScrapeListingsKamernet:
    def _mock_session(self, html: str, status: int = 200):
        resp = MagicMock()
        resp.status_code = status
        resp.text = html
        resp.raise_for_status = MagicMock()
        session = MagicMock()
        session.get.return_value = resp
        session.__enter__ = MagicMock(return_value=session)
        session.__exit__ = MagicMock(return_value=False)
        return session

    def test_happy_path(self):
        html = _make_html(listings=[LISTING_1, LISTING_2])
        session = self._mock_session(html)
        with patch("nodes.scrape_listings_kamernet.time.sleep"):
            results = scrape_listings_kamernet("https://kamernet.nl/test", session=session)
        assert len(results) == 2

    def test_retries_on_failure_then_succeeds(self):
        html = _make_html(listings=[LISTING_1])
        resp_ok = MagicMock()
        resp_ok.text = html
        resp_ok.raise_for_status = MagicMock()

        session = MagicMock()
        session.get.side_effect = [IOError("timeout"), resp_ok]

        with patch("nodes.scrape_listings_kamernet.time.sleep"):
            results = scrape_listings_kamernet(
                "https://kamernet.nl/test", max_retries=3, backoff_base=0.01, session=session
            )
        assert len(results) == 1

    def test_raises_after_all_retries_exhausted(self):
        session = MagicMock()
        session.get.side_effect = IOError("always fails")

        with patch("nodes.scrape_listings_kamernet.time.sleep"):
            with pytest.raises(RuntimeError, match="Kamernet scraping failed"):
                scrape_listings_kamernet(
                    "https://kamernet.nl/test", max_retries=2, backoff_base=0.01, session=session
                )
