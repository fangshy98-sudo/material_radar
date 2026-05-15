from __future__ import annotations

from typing import Iterable

import requests
import trafilatura

from .feed import Item


UA = "Mozilla/5.0 (compatible; MaterialRadar/0.1)"
TIMEOUT = 20


def fetch_page(name: str, url: str) -> Item | None:
    resp = requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT)
    resp.raise_for_status()
    extracted = trafilatura.extract(
        resp.text,
        url=url,
        include_comments=False,
        favor_recall=True,
    ) or ""
    title = ""
    meta = trafilatura.extract_metadata(resp.text)
    if meta and meta.title:
        title = meta.title.strip()
    return Item(
        source=name,
        title=title or url,
        url=url,
        summary=extracted[:600],
        published=(meta.date if meta and meta.date else ""),
    )


def fetch_all(pages: Iterable[dict]) -> list[Item]:
    out: list[Item] = []
    for p in pages:
        try:
            item = fetch_page(p["name"], p["url"])
            if item:
                out.append(item)
        except Exception as e:
            print(f"[web] {p.get('name')} failed: {e}")
    return out
