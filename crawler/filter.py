from __future__ import annotations

from typing import Iterable

from .feed import Item


def _match_any(text: str, needles: Iterable[str]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def filter_items(
    items: Iterable[Item],
    include: list[str],
    exclude: list[str],
) -> list[Item]:
    kept: list[Item] = []
    for it in items:
        blob = f"{it.title}\n{it.summary}"
        if exclude and _match_any(blob, exclude):
            continue
        if include and not _match_any(blob, include):
            continue
        kept.append(it)
    return kept


def dedupe(items: Iterable[Item]) -> list[Item]:
    seen: set[str] = set()
    out: list[Item] = []
    for it in items:
        key = it.url or it.title
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
