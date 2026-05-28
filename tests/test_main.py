import pytest

from digest.config import Source
from digest.feeds import Item
from digest.main import run
from digest.select import normalize_url
from digest.state import load


class FakePublisher:
    def __init__(self, fail_on_index=None):
        self.sent = []
        self._fail_on = fail_on_index

    def send(self, text):
        if self._fail_on is not None and len(self.sent) == self._fail_on:
            raise RuntimeError("send failed")
        self.sent.append(text)


def _fetcher(items_by_source, failing=()):
    def fetch_fn(source):
        if source.name in failing:
            raise RuntimeError("fetch failed")
        return items_by_source.get(source.name, [])

    return fetch_fn


def test_sends_only_new_item_and_persists(tmp_path):
    # Covers F1 / AE2.
    state = tmp_path / "seen.json"
    src = Source("Mux", "u")
    items = [
        Item("A", "https://ex.com/a", source="Mux"),
        Item("B", "https://ex.com/b", source="Mux"),
    ]
    # Pre-seed 'a' as already seen.
    from digest.state import save

    save(state, {normalize_url("https://ex.com/a")})

    pub = FakePublisher()
    summary = run([src], pub, state, _fetcher({"Mux": items}))

    assert summary["sent"] == 1
    assert pub.sent == ["B\nhttps://ex.com/b"]
    assert normalize_url("https://ex.com/b") in load(state)


def test_all_seen_sends_nothing_and_leaves_state(tmp_path):
    # Covers AE1.
    state = tmp_path / "seen.json"
    src = Source("Mux", "u")
    items = [Item("A", "https://ex.com/a", source="Mux")]
    from digest.state import save

    save(state, {normalize_url("https://ex.com/a")})
    before = state.read_bytes()

    pub = FakePublisher()
    summary = run([src], pub, state, _fetcher({"Mux": items}))

    assert summary["sent"] == 0
    assert pub.sent == []
    assert state.read_bytes() == before


def test_second_run_sends_nothing(tmp_path):
    state = tmp_path / "seen.json"
    src = Source("Mux", "u")
    items = [Item("A", "https://ex.com/a", source="Mux")]
    fetch = _fetcher({"Mux": items})

    run([src], FakePublisher(), state, fetch)
    pub2 = FakePublisher()
    run([src], pub2, state, fetch)

    assert pub2.sent == []


def test_partial_send_persists_only_sent(tmp_path):
    # Atomicity: publisher raises on the 3rd item -> items 1-2 saved, 3-5 not.
    state = tmp_path / "seen.json"
    src = Source("Mux", "u")
    items = [Item(f"T{i}", f"https://ex.com/{i}", source="Mux") for i in range(5)]
    pub = FakePublisher(fail_on_index=2)

    with pytest.raises(RuntimeError):
        run([src], pub, state, _fetcher({"Mux": items}))

    seen = load(state)
    assert normalize_url("https://ex.com/0") in seen
    assert normalize_url("https://ex.com/1") in seen
    assert normalize_url("https://ex.com/2") not in seen
    assert normalize_url("https://ex.com/3") not in seen


def test_cross_source_duplicate_posted_once(tmp_path):
    state = tmp_path / "seen.json"
    sources = [Source("Mux", "u1"), Source("Cloudflare", "u2", ("video",))]
    items = {
        "Mux": [Item("Video thing", "https://ex.com/a", source="Mux")],
        "Cloudflare": [Item("Video thing", "https://ex.com/a", source="Cloudflare")],
    }
    pub = FakePublisher()
    run(sources, pub, state, _fetcher(items))
    assert len(pub.sent) == 1


def test_one_failing_source_does_not_abort_run(tmp_path):
    state = tmp_path / "seen.json"
    sources = [Source("Mux", "u1"), Source("Bitmovin", "u2")]
    items = {"Bitmovin": [Item("B", "https://ex.com/b", source="Bitmovin")]}
    pub = FakePublisher()
    summary = run(sources, pub, state, _fetcher(items, failing=("Mux",)))
    assert summary["sent"] == 1
    assert pub.sent == ["B\nhttps://ex.com/b"]


def test_seed_only_records_state_without_sending(tmp_path):
    state = tmp_path / "seen.json"
    src = Source("Mux", "u")
    items = [Item("A", "https://ex.com/a", source="Mux")]
    summary = run([src], None, state, _fetcher({"Mux": items}), seed_only=True)
    assert summary["sent"] == 0
    assert normalize_url("https://ex.com/a") in load(state)
