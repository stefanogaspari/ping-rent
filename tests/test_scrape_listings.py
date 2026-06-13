import pytest
from unittest.mock import MagicMock, patch
from nodes.scrape_listings import scrape_listings, _parse_listings


SAMPLE_HTML = """
<html><body>
<ul>
  <li class="search-list__item--listing">
    <h2><a class="listing-search-item__link--title" href="/apartment/amsterdam/123">Nice flat</a></h2>
    <div class="listing-search-item__price">€ 1 200 /month</div>
    <div class="listing-search-item__sub-title">Centre, Amsterdam</div>
    <ul>
      <li class="illustrated-features__item">3 rooms</li>
      <li class="illustrated-features__item">75 m²</li>
    </ul>
  </li>
  <li class="search-list__item--listing">
    <h2><a class="listing-search-item__link--title" href="/apartment/amsterdam/456">Another flat</a></h2>
    <div class="listing-search-item__price">€ 900 /month</div>
    <div class="listing-search-item__sub-title">West, Amsterdam</div>
    <ul>
      <li class="illustrated-features__item">2 rooms</li>
      <li class="illustrated-features__item">50 m²</li>
    </ul>
  </li>
</ul>
</body></html>
"""

NO_CARDS_HTML = "<html><body><p>No results</p></body></html>"


class TestParseListings:
    def test_parses_two_listings(self):
        results = _parse_listings(SAMPLE_HTML)
        assert len(results) == 2
        assert results[0]["url"] == "https://www.pararius.com/apartment/amsterdam/123"
        assert results[0]["title"] == "Nice flat"
        assert results[0]["price"] == "€ 1 200 /month"
        assert results[0]["rooms"] == "3 rooms"
        assert results[0]["surface"] == "75 m²"

    def test_no_cards_returns_empty_list(self):
        results = _parse_listings(NO_CARDS_HTML)
        assert results == []

    def test_deduplicates_by_url(self):
        # Simulates the li + nested section both matching the same listing
        dup_html = """
        <html><body><ul>
          <li class="search-list__item--listing">
            <section class="listing-search-item">
              <a class="listing-search-item__link--title" href="/apartment/amsterdam/123">Flat A</a>
              <div class="listing-search-item__price">€ 1 000 /month</div>
            </section>
          </li>
        </ul></body></html>
        """
        results = _parse_listings(dup_html)
        urls = [r["url"] for r in results]
        assert len(urls) == len(set(urls)), "Duplicate URLs should be removed"


class TestScrapeListings:
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
        session = self._mock_session(SAMPLE_HTML)
        with patch("nodes.scrape_listings.time.sleep"):
            results = scrape_listings("https://pararius.com/test", session=session)
        assert len(results) == 2

    def test_retries_on_failure_then_succeeds(self):
        resp_ok = MagicMock()
        resp_ok.text = SAMPLE_HTML
        resp_ok.raise_for_status = MagicMock()

        session = MagicMock()
        session.get.side_effect = [
            IOError("timeout"),
            resp_ok,
        ]

        with patch("nodes.scrape_listings.time.sleep"):
            results = scrape_listings(
                "https://pararius.com/test", max_retries=3, backoff_base=0.01, session=session
            )
        assert len(results) == 2

    def test_raises_after_all_retries_exhausted(self):
        session = MagicMock()
        session.get.side_effect = IOError("always fails")

        with patch("nodes.scrape_listings.time.sleep"):
            with pytest.raises(RuntimeError, match="Scraping failed"):
                scrape_listings(
                    "https://pararius.com/test", max_retries=2, backoff_base=0.01, session=session
                )
