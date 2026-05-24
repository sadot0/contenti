"""RSS/Atom-сборщик трендов (интернет-доступ движка).

Парсер написан на чистом Python (regex + html), БЕЗ модуля xml/expat — чтобы работать на
любой машине, включая сборки Python со сломанным pyexpat (частая болячка Homebrew на macOS).
Подбери ленты под нишу (крипто + узбекские источники) в config/feeds.txt.
"""

from __future__ import annotations

import html
import re
import urllib.request
from dataclasses import dataclass

_UA = "Mozilla/5.0 (compatible; ContentOS/0.1; +local)"

_ITEM_RE = re.compile(r"<(item|entry)\b[^>]*>(.*?)</\1>", re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class FeedItem:
    title: str
    link: str
    published: str
    summary: str
    source: str


def _field(block: str, *tags: str) -> str:
    """Вытащить содержимое первого встретившегося тега из блока."""
    for tag in tags:
        m = re.search(rf"<{tag}\b[^>]*>(.*?)</{tag}>", block, re.DOTALL | re.IGNORECASE)
        if m:
            return _clean(m.group(1))
    return ""


def _link(block: str) -> str:
    """RSS: <link>url</link>; Atom: <link href="url"/>."""
    m = re.search(r"<link\b[^>]*>(.*?)</link>", block, re.DOTALL | re.IGNORECASE)
    if m and m.group(1).strip():
        return _clean(m.group(1))
    m = re.search(r'<link\b[^>]*href=["\']([^"\']+)["\']', block, re.IGNORECASE)
    return _clean(m.group(1)) if m else ""


def _clean(s: str) -> str:
    s = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", s, flags=re.DOTALL)
    s = _TAG_RE.sub("", s)              # снять вложенный HTML
    return html.unescape(s).strip()


def _source_title(text: str) -> str:
    # заголовок ленты = первый <title> до первого <item>/<entry>
    head = re.split(r"<(?:item|entry)\b", text, maxsplit=1, flags=re.IGNORECASE)[0]
    m = re.search(r"<title\b[^>]*>(.*?)</title>", head, re.DOTALL | re.IGNORECASE)
    return _clean(m.group(1)) if m else ""


def fetch_feed(url: str, limit: int = 15) -> list[FeedItem]:
    """Скачать одну RSS/Atom-ленту. Возвращает список FeedItem. Парсинг без xml/expat."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")

    source = _source_title(text)
    items: list[FeedItem] = []
    for m in _ITEM_RE.finditer(text):
        block = m.group(2)
        items.append(FeedItem(
            title=_field(block, "title"),
            link=_link(block),
            published=_field(block, "pubDate", "published", "updated", "dc:date"),
            summary=_field(block, "description", "summary", "content"),
            source=source,
        ))
        if len(items) >= limit:
            break
    return items


def fetch_feeds(urls: list[str], limit_per: int = 15) -> list[FeedItem]:
    """Скачать несколько лент, пропуская упавшие."""
    out: list[FeedItem] = []
    for u in urls:
        try:
            out.extend(fetch_feed(u, limit=limit_per))
        except Exception as exc:  # noqa: BLE001
            print(f"[rss] не удалось загрузить {u}: {exc}")
    return out


def as_digest(items: list[FeedItem], max_items: int = 40) -> str:
    """Свести в текстовый дайджест для подачи в LLM."""
    lines = []
    for it in items[:max_items]:
        s = (it.summary or "")[:200].replace("\n", " ")
        lines.append(f"- [{it.source}] {it.title} — {s} ({it.link})")
    return "\n".join(lines)
