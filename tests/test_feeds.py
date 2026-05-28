from digest.feeds import fetch_source, parse_content


def test_parse_basic_preserves_order_and_fields(basic_feed):
    items = parse_content(basic_feed, source="Test")
    assert [i.url for i in items] == ["https://ex.com/a", "https://ex.com/b", "https://ex.com/c"]
    assert items[0].title == "Encoding HLS at scale"
    assert items[0].source == "Test"
    assert items[0].published is not None


def test_missing_date_item_still_produced(basic_feed):
    # Covers AE3: an entry with no published date is usable, not dropped.
    items = parse_content(basic_feed)
    no_date = next(i for i in items if i.url == "https://ex.com/b")
    assert no_date.title == "No date here"
    assert no_date.published is None


def test_empty_feed_yields_no_items(empty_feed):
    assert parse_content(empty_feed) == []


def test_malformed_feed_yields_no_items_without_raising():
    assert parse_content("this is not xml at all") == []


def test_fetch_source_uses_injected_http_get(basic_feed):
    src = type("S", (), {"feed_url": "https://ex.com/feed", "name": "Mux"})()
    items = fetch_source(src, http_get=lambda url: basic_feed.encode())
    assert [i.url for i in items] == ["https://ex.com/a", "https://ex.com/b", "https://ex.com/c"]
    assert items[0].source == "Mux"
