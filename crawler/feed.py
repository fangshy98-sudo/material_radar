from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import feedparser


@dataclass
class Item:
    source: str
    title: str
    url: str
    summary: str
    published: str


def fetch_feed(name: str, url: str) -> list[Item]:
    parsed = feedparser.parse(url)
    items: list[Item] = []
    for entry in parsed.entries:
        items.append(
            Item(
                source=name,
                title=getattr(entry, "title", "").strip(),
                url=getattr(entry, "link", "").strip(),
                summary=getattr(entry, "summary", "").strip(),
                published=getattr(entry, "published", "") or getattr(entry, "updated", ""),
            )
        )
    return items


def fetch_all(feeds: Iterable[dict]) -> list[Item]:
    out: list[Item] = []
    for f in feeds:
        try:
            out.extend(fetch_feed(f["name"], f["url"]))
        except Exception as e:
            print(f"[feed] {f.get('name')} failed: {e}")
    return out
