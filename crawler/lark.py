from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from typing import Iterable

import requests

from .feed import Item


WEBHOOK_URL = os.environ.get("LARK_WEBHOOK_URL", "")
WEBHOOK_SECRET = os.environ.get("LARK_WEBHOOK_SECRET", "")


def _sign(timestamp: int, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    h = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256)
    return base64.b64encode(h.digest()).decode("utf-8")


def build_post_lines(items: Iterable[Item]) -> list[list[dict]]:
    out: list[list[dict]] = []
    items = list(items)
    out.append([{"tag": "text", "text": f"本期共 {len(items)} 条新内容"}])
    for it in items:
        out.append(
            [
                {"tag": "text", "text": f"【{it.source}】"},
                {"tag": "a", "text": it.title or it.url, "href": it.url},
            ]
        )
        if it.summary:
            snippet = it.summary.replace("\n", " ").strip()
            if len(snippet) > 160:
                snippet = snippet[:160] + "…"
            out.append([{"tag": "text", "text": "  " + snippet}])
    return out


def push_post(title: str, content_lines: list[list[dict]]) -> None:
    if not WEBHOOK_URL:
        print("[lark] LARK_WEBHOOK_URL not set, skipping push")
        return
    payload: dict = {
        "msg_type": "post",
        "content": {"post": {"zh_cn": {"title": title, "content": content_lines}}},
    }
    if WEBHOOK_SECRET:
        ts = int(time.time())
        payload["timestamp"] = str(ts)
        payload["sign"] = _sign(ts, WEBHOOK_SECRET)
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=20)
    resp.raise_for_status()
    body = resp.json()
    if body.get("code", 0) != 0:
        print(f"[lark] push failed: {body}")
    else:
        print("[lark] pushed")
