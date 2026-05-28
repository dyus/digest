from digest.state import load, save


def test_round_trip(tmp_path):
    path = tmp_path / "seen.json"
    urls = {"https://ex.com/a", "https://ex.com/b"}
    save(path, urls)
    assert load(path) == urls


def test_missing_file_returns_empty_set(tmp_path):
    assert load(tmp_path / "nope.json") == set()


def test_save_is_deterministic(tmp_path):
    p1, p2 = tmp_path / "1.json", tmp_path / "2.json"
    save(p1, {"https://ex.com/b", "https://ex.com/a", "https://ex.com/c"})
    save(p2, ["https://ex.com/c", "https://ex.com/a", "https://ex.com/b"])
    assert p1.read_bytes() == p2.read_bytes()


def test_invalid_urls_are_not_persisted(tmp_path):
    path = tmp_path / "seen.json"
    save(path, {
        "https://ex.com/ok",
        "https://user:pass@ex.com/secret",  # userinfo — must be rejected
        "ftp://ex.com/x",                    # non-http(s) — must be rejected
    })
    assert load(path) == {"https://ex.com/ok"}
