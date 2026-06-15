import pytest
import requests
from unittest.mock import MagicMock, patch
from nodes.send_notification import send_notification, _build_message


LISTING = {
    "url": "https://pararius.com/a",
    "title": "Nice flat",
    "price": "€ 1 200 /month",
    "location": "Centre, Amsterdam",
    "rooms": "3 rooms",
    "surface": "75 m²",
}

LISTING_B = {**LISTING, "url": "https://pararius.com/b"}


def _make_session(status=200, raise_exc=None):
    resp = MagicMock()
    resp.status_code = status
    if raise_exc:
        resp.raise_for_status.side_effect = raise_exc
    else:
        resp.raise_for_status = MagicMock()
    session = MagicMock()
    if raise_exc and not isinstance(raise_exc, requests.HTTPError):
        session.get.side_effect = raise_exc
    else:
        session.get.return_value = resp
    return session


class TestBuildMessage:
    def test_includes_url(self):
        msg = _build_message(LISTING)
        assert "https://pararius.com/a" in msg

    def test_includes_price(self):
        msg = _build_message(LISTING)
        assert "€ 1 200 /month" in msg

    def test_empty_listing_graceful(self):
        msg = _build_message({})
        assert "New listing" in msg

    def test_pararius_source_label(self):
        msg = _build_message({**LISTING, "source": "Pararius"})
        assert "[Pararius]" in msg

    def test_kamernet_source_label(self):
        msg = _build_message({**LISTING, "source": "Kamernet"})
        assert "[Kamernet]" in msg

    def test_no_source_no_label(self):
        msg = _build_message(LISTING)
        assert "[" not in msg.split("\n")[0]  # no label bracket in the first line


class TestSendNotification:
    def test_empty_listings_returns_empty(self):
        result = send_notification([], recipients=["@testuser"])
        assert result == []

    def test_empty_recipients_returns_empty(self):
        result = send_notification([LISTING], recipients=[])
        assert result == []

    def test_successful_delivery_single_recipient(self):
        session = _make_session(status=200)
        with patch("nodes.send_notification.time.sleep"):
            results = send_notification([LISTING], recipients=["@testuser"], session=session)
        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["recipient"] == "@testuser"
        assert results[0]["status_code"] == 200

    def test_multiple_recipients_all_notified(self):
        session = _make_session(status=200)
        with patch("nodes.send_notification.time.sleep"):
            results = send_notification([LISTING], recipients=["@user1", "@user2"], session=session)
        assert len(results) == 2
        assert {r["recipient"] for r in results} == {"@user1", "@user2"}
        assert all(r["success"] for r in results)

    def test_multiple_listings_multiple_recipients(self):
        session = _make_session(status=200)
        with patch("nodes.send_notification.time.sleep"):
            results = send_notification(
                [LISTING, LISTING_B], recipients=["@user1", "@user2"], session=session
            )
        assert len(results) == 4  # 2 listings × 2 recipients

    def test_network_error_captured(self):
        session = _make_session(raise_exc=requests.RequestException("conn refused"))
        with patch("nodes.send_notification.time.sleep"):
            results = send_notification([LISTING], recipients=["@testuser"], session=session)
        assert len(results) == 1
        assert results[0]["success"] is False
        assert "conn refused" in results[0]["error"]

    def test_delay_between_messages(self):
        session = _make_session(status=200)
        with patch("nodes.send_notification.time.sleep") as mock_sleep:
            send_notification([LISTING, LISTING_B], recipients=["@testuser"], delay=1.5, session=session)
        mock_sleep.assert_called_once_with(1.5)

    def test_no_delay_after_last_message(self):
        session = _make_session(status=200)
        with patch("nodes.send_notification.time.sleep") as mock_sleep:
            send_notification([LISTING], recipients=["@testuser"], delay=1.5, session=session)
        mock_sleep.assert_not_called()
