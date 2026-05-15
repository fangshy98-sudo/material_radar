from __future__ import annotations

import os
from typing import Iterable

import requests

from .feed import Item


API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
API_URL = "https://api.anthropic.com/v1/messages"

PROMPT = """你是一名电子烟雾化材料分析师。下面是本期抓取到的多条资讯。请按"材料类别(网片 / 棉芯 / 陶瓷 / 塑料 / 硅胶 / 其他)"分组,每条用一句话提炼:
- 涉及什么材料,有什么性能或工艺变化
- 是否是潜在的"降本增效替代"线索(✅ 表示是 / ❌ 表示否)
- 附原链接

要求:输出 markdown,无多余解释,无前言后语。

资讯列表:
{items}
"""


def summarize(items: Iterable[Item]) -> str | None:
    if not API_KEY:
        return None
    items = list(items)
    if not items:
        return None
    bullets = "\n".join(
        f"- [{it.source}] {it.title} — {it.summary[:300]} ({it.url})"
        for it in items
    )
    body = {
        "model": MODEL,
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": PROMPT.format(items=bullets)}],
    }
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
    except Exception as e:
        print(f"[summarize] failed: {e}")
        return None
