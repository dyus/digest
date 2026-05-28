def format_item(item) -> str:
    """One plain-text message per link: title + URL, no summary."""
    title = (item.title or "").strip()
    if title:
        return f"{title}\n{item.url}"
    return item.url
