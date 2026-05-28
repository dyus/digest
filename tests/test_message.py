from digest.feeds import Item
from digest.message import format_item


def test_contains_title_and_url_no_summary():
    msg = format_item(Item(title="Encoding HLS", url="https://ex.com/a"))
    assert "Encoding HLS" in msg
    assert "https://ex.com/a" in msg
    # No summary cruft beyond title + url (two lines).
    assert msg.count("\n") == 1


def test_special_characters_passed_through_as_plain_text():
    # Sent with parse_mode=None, so markup chars are literal, not interpreted.
    title = "*bold* _under_ [x](http://evil) <b>html</b>"
    msg = format_item(Item(title=title, url="https://ex.com/a"))
    assert title in msg
    assert "https://ex.com/a" in msg
