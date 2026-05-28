from digest.feeds import Item
from digest.select import normalize_url, select


def _item(url, title="Video encoding", source=None):
    return Item(title=title, url=url, published=None, source=source)


def test_selects_only_unseen():
    # Covers AE2: 3 items, 1 unseen -> returns exactly that one.
    items = [_item("https://ex.com/a"), _item("https://ex.com/b"), _item("https://ex.com/c")]
    seen = {normalize_url("https://ex.com/a"), normalize_url("https://ex.com/b")}
    assert [i.url for i in select(items, seen)] == ["https://ex.com/c"]


def test_all_seen_returns_empty():
    # Covers AE1.
    items = [_item("https://ex.com/a"), _item("https://ex.com/b")]
    seen = {normalize_url(i.url) for i in items}
    assert select(items, seen) == []


def test_within_run_duplicate_returned_once():
    # Covers AE4.
    items = [_item("https://ex.com/a"), _item("https://ex.com/a")]
    assert len(select(items, set())) == 1


def test_cross_source_duplicate_returned_once():
    items = [_item("https://ex.com/a", source="Mux"), _item("https://ex.com/a", source="Cloudflare")]
    assert len(select(items, set())) == 1


def test_distinct_non_tracking_params_stay_distinct():
    # Under-collapse guard: ?p=1 vs ?p=2 are different articles.
    items = [_item("https://ex.com/?p=1"), _item("https://ex.com/?p=2")]
    assert len(select(items, set())) == 2


def test_tracking_params_and_trailing_slash_collapse():
    assert normalize_url("https://ex.com/a/?utm_source=x") == normalize_url("https://ex.com/a")
    items = [_item("https://ex.com/a?utm_source=x"), _item("https://ex.com/a/")]
    assert len(select(items, set())) == 1


def test_keyword_filter_per_source():
    kw = {"Cloudflare": ("video", "codec")}
    on_topic = _item("https://ex.com/x", title="New codec support", source="Cloudflare")
    off_topic = _item("https://ex.com/y", title="Quarterly earnings", source="Cloudflare")
    result = select([on_topic, off_topic], set(), kw)
    assert [i.url for i in result] == ["https://ex.com/x"]
