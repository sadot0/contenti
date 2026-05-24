"""RSS-сборщик трендов/новостей (интернет-доступ движка).

Использует только стандартную библиотеку (urllib + xml), без внешних зависимостей.
Подбери ленты под нишу: крипто + узбекские источники. Примеры лент — в config/feeds.example.txt.
"""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

_UA = "Mozilla/5.0 (compatible; ContentOS/0.1; +local)"


@dataclass
class FeedItem:
    title: str
    link: str
    published: str
    summary: str
    source: str


def _text(el, *tags) -> str:
    for t in tags:
        found = el.find(t)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def fetch_feed(url: str, limit: int = 15) -> list[FeedItem]:
    """Скачать одну RSS/Atom-ленту. Возвращает список FeedItem."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    root = ET.fromstring(raw)

    items: list[FeedItem] = []
    # RSS 2.0: channel/item ; Atom: feed/entry
    channel = root.find("channel")
    source = _text(channel, "title") if channel is not None else _text(root, "{http://www.w3.org/2005/Atom}title")
    entries = (channel.findall("item") if channel is not None
               else root.findall("{http://www.w3.org/2005/Atom}entry"))

    for e in entries[:limit]:
        if channel is not None:  # RSS
            items.append(FeedItem(
                title=_text(e, "title"),
                link=_text(e, "link"),
                published=_text(e, "pubDate", "{http://purl.org/dc/elements/1.1/}date"),
                summary=_text(e, "description"),
                source=source,
            ))
        else:  # Atom
            ns = "{http://www.w3.org/2005/Atom}"
            link_el = e.find(f"{ns}link")
            items.append(FeedItem(
                title=_text(e, f"{ns}title"),
                link=link_el.get("href") if link_el is not None else "",
                published=_text(e, f"{ns}updated", f"{ns}published"),
                summary=_text(e, f"{ns}summary", f"{ns}content"),
                source=source,
            ))
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
