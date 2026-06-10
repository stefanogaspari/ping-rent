import json
import pytest
from nodes.load_seen_listings import load_seen_listings


class TestLoadSeenListings:
    def test_missing_file_returns_empty_set(self, tmp_path):
        result = load_seen_listings(store_path=str(tmp_path / "missing.json"))
        assert result == set()

    def test_empty_array_returns_empty_set(self, tmp_path):
        p = tmp_path / "seen.json"
        p.write_text("[]")
        assert load_seen_listings(str(p)) == set()

    def test_loads_urls(self, tmp_path):
        urls = ["https://pararius.com/a", "https://pararius.com/b"]
        p = tmp_path / "seen.json"
        p.write_text(json.dumps(urls))
        result = load_seen_listings(str(p))
        assert result == set(urls)

    def test_invalid_json_raises(self, tmp_path):
        p = tmp_path / "seen.json"
        p.write_text("not json{{{")
        with pytest.raises(ValueError, match="invalid JSON"):
            load_seen_listings(str(p))

    def test_non_array_json_raises(self, tmp_path):
        p = tmp_path / "seen.json"
        p.write_text(json.dumps({"url": "x"}))
        with pytest.raises(ValueError, match="JSON array"):
            load_seen_listings(str(p))
