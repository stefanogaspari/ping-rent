import json
import pytest
from nodes.update_seen_listings import update_seen_listings

LISTING_A = {"url": "https://pararius.com/a"}
LISTING_B = {"url": "https://pararius.com/b"}


class TestUpdateSeenListings:
    def test_writes_new_urls(self, tmp_path):
        store = tmp_path / "seen.json"
        result = update_seen_listings([LISTING_A], seen=set(), store_path=str(store))
        assert result == {"https://pararius.com/a"}
        data = json.loads(store.read_text())
        assert "https://pararius.com/a" in data

    def test_merges_with_existing_seen(self, tmp_path):
        store = tmp_path / "seen.json"
        existing = {"https://pararius.com/old"}
        result = update_seen_listings([LISTING_A], seen=existing, store_path=str(store))
        assert "https://pararius.com/old" in result
        assert "https://pararius.com/a" in result

    def test_no_new_listings_no_write(self, tmp_path):
        store = tmp_path / "seen.json"
        existing = {"https://pararius.com/a"}
        result = update_seen_listings([], seen=existing, store_path=str(store))
        assert result == existing
        assert not store.exists()

    def test_atomic_write_produces_valid_json(self, tmp_path):
        store = tmp_path / "seen.json"
        update_seen_listings([LISTING_A, LISTING_B], seen=set(), store_path=str(store))
        data = json.loads(store.read_text())
        assert isinstance(data, list)
        assert len(data) == 2

    def test_missing_url_key_raises(self, tmp_path):
        store = tmp_path / "seen.json"
        with pytest.raises(ValueError, match="missing 'url' key"):
            update_seen_listings([{"title": "no url"}], seen=set(), store_path=str(store))

    def test_creates_output_dir(self, tmp_path):
        store = tmp_path / "subdir" / "seen.json"
        update_seen_listings([LISTING_A], seen=set(), store_path=str(store))
        assert store.exists()
