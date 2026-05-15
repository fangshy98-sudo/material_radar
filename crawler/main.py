from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import yaml

from . import feed, web, filter as flt, lark, summarize
from .feed import Item


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SEEN_FILE = DATA_DIR / "seen.json"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))


def save_seen(seen: set[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(
        json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def render_md(items: list[Item], today: str, digest: str | None) -> str:
    lines = [f"# Material Radar — {today}", "", f"_{len(items)} 条新内容_", ""]
    if digest:
        lines += ["## AI 摘要", "", digest, "", "---", ""]
    by_source: dict[str, list[Item]] = {}
    for it in items:
        by_source.setdefault(it.source, []).append(it)
    for src, group in by_source.items():
        lines.append(f"## {src}")
        lines.append("")
        for it in group:
            title = it.title or it.url
            lines.append(f"- [{title}]({it.url})")
            if it.summary:
                snippet = it.summary.replace("\n", " ").strip()
                if len(snippet) > 240:
                    snippet = snippet[:240] + "…"
                lines.append(f"  - {snippet}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    sources = load_yaml(ROOT / "sources.yml")
    keywords = load_yaml(ROOT / "keywords.yml")

    items: list[Item] = []
    items.extend(feed.fetch_all(sources.get("feeds", [])))
    items.extend(web.fetch_all(sources.get("pages", [])))

    items = flt.filter_items(
        items,
        include=keywords.get("include", []),
        exclude=keywords.get("exclude", []),
    )
    items = flt.dedupe(items)

    seen = load_seen()
    fresh = [it for it in items if (it.url or it.title) not in seen]
    for it in fresh:
        seen.add(it.url or it.title)

    today = date.today().isoformat()
    digest = summarize.summarize(fresh)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"{today}.md"
    out_path.write_text(render_md(fresh, today, digest), encoding="utf-8")
    save_seen(seen)

    if fresh:
        title = f"Material Radar — {today}"
        post_lines: list[list[dict]] = []
        if digest:
            post_lines.append([{"tag": "text", "text": "AI 摘要"}])
            for line in digest.split("\n"):
                line = line.strip()
                if line:
                    post_lines.append([{"tag": "text", "text": line}])
            post_lines.append([{"tag": "text", "text": "—— 原始列表 ——"}])
        post_lines.extend(lark.build_post_lines(fresh))
        lark.push_post(title, post_lines)

    print(f"wrote {len(fresh)} new items to {out_path}")


if __name__ == "__main__":
    main()
