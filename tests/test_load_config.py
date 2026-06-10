import os
import pytest
from unittest.mock import patch


class TestLoadConfig:
    def test_happy_path_single_recipient(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "PARARIUS_SEARCH_URL=https://www.pararius.com/apartments/amsterdam\n"
            "CALLMEBOT_TELEGRAM_USERNAME=@myusername\n"
            "POLL_INTERVAL_SECONDS=120\n"
            "NOTIFICATION_DELAY_SECONDS=3.5\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            from nodes.load_config import load_config
            cfg = load_config(env_path=str(env_file))

        assert cfg["search_url"] == "https://www.pararius.com/apartments/amsterdam"
        assert cfg["callmebot_recipients"] == ["@myusername"]
        assert cfg["poll_interval"] == 120
        assert cfg["notification_delay"] == 3.5

    def test_happy_path_multiple_recipients(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "PARARIUS_SEARCH_URL=https://www.pararius.com/apartments/amsterdam\n"
            "CALLMEBOT_TELEGRAM_USERNAME=@user1, @user2, @user3\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            from nodes.load_config import load_config
            cfg = load_config(env_path=str(env_file))

        assert cfg["callmebot_recipients"] == ["@user1", "@user2", "@user3"]

    def test_defaults(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "PARARIUS_SEARCH_URL=https://www.pararius.com/apartments/amsterdam\n"
            "CALLMEBOT_TELEGRAM_USERNAME=@myusername\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            from nodes.load_config import load_config
            cfg = load_config(env_path=str(env_file))

        assert cfg["poll_interval"] == 300
        assert cfg["notification_delay"] == 2.0

    def test_missing_required_key_raises(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "PARARIUS_SEARCH_URL=https://www.pararius.com/apartments/amsterdam\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            from nodes.load_config import load_config
            with pytest.raises(EnvironmentError, match="CALLMEBOT_TELEGRAM_USERNAME"):
                load_config(env_path=str(env_file))

    def test_empty_value_raises(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "PARARIUS_SEARCH_URL=\n"
            "CALLMEBOT_TELEGRAM_USERNAME=@myusername\n"
        )
        with patch.dict(os.environ, {}, clear=True):
            from nodes.load_config import load_config
            with pytest.raises(EnvironmentError, match="PARARIUS_SEARCH_URL"):
                load_config(env_path=str(env_file))
