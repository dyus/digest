from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    name: str
    feed_url: str
    keywords: tuple[str, ...] | None = None


# Cloudflare's blog RSS is a general feed; keep only video-engineering-relevant posts.
CLOUDFLARE_KEYWORDS = (
    "stream",
    "video",
    "codec",
    "hls",
    "dash",
    "transcode",
    "encode",
    "webrtc",
    "media",
)

SOURCES: list[Source] = [
    Source("Mux", "https://www.mux.com/blog/rss.xml"),
    Source("Bitmovin", "https://bitmovin.com/blog/feed/"),
    Source("Cloudflare", "https://blog.cloudflare.com/rss/", CLOUDFLARE_KEYWORDS),
    Source("The Broadcast Knowledge", "https://thebroadcastknowledge.com/feed/"),
]
