import pytest
from nodes.diff_listings import diff_listings

LISTING_A = {"url": "https://pararius.com/a", "title": "Flat A"}
LISTING_B = {"url": "https://pararius.com/b", "title": "Flat B"}
LISTING_C = {"url": "https://pararius.com/c", "title": "Flat C"}


class TestDiffListings:
    def test_all_new(self):
        result = diff_listings([LISTING_A, LISTING_B], seen=set())
        assert result == [LISTING_A, LISTING_B]

    def test_all_seen(self):
        seen = {LISTING_A["url"], LISTING_B["url"]}
        result = diff_listings([LISTING_A, LISTING_B], seen=seen)
        assert result == []

    def test_partial_diff(self):
        seen = {LISTING_A["url"]}
        result = diff_listings([LISTING_A, LISTING_B, LISTING_C], seen=seen)
        assert result == [LISTING_B, LISTING_C]

    def test_empty_scraped(self):
        result = diff_listings([], seen={"https://pararius.com/a"})
        assert result == []

    def test_preserves_order(self):
        result = diff_listings([LISTING_C, LISTING_A, LISTING_B], seen=set())
        assert result == [LISTING_C, LISTING_A, LISTING_B]

    def test_missing_url_key_raises(self):
        with pytest.raises(ValueError, match="missing 'url' key"):
            diff_listings([{"title": "no url here"}], seen=set())
