"""On-disk layout helpers shared by all pipeline stages.

Layout:
    <data_dir>/                  e.g. data/kirills_finance
        manifest.json            index of all items
        <shortcode>/
            video.mp4            downloaded media
            caption.txt          original caption
            meta.json            structured metadata (see Item)
            transcript.txt       added by the transcribe stage
        report.md                added by the analyze stage
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

VIDEO_EXTS = (".mp4", ".mov", ".mkv", ".webm")


@dataclass
class Item:
    shortcode: str
    dir: str
    url: str = ""
    caption: str = ""
    date: str = ""
    likes: Optional[int] = None
    comments: Optional[int] = None
    views: Optional[int] = None
    duration: Optional[float] = None
    hashtags: list = field(default_factory=list)
    mentions: list = field(default_factory=list)
    is_video: bool = True
    language: str = ""


def meta_path(item_dir) -> Path:
    return Path(item_dir) / "meta.json"


def transcript_path(item_dir) -> Path:
    return Path(item_dir) / "transcript.txt"


def save_meta(item: Item) -> None:
    p = meta_path(item.dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(asdict(item), ensure_ascii=False, indent=2), encoding="utf-8")


def load_meta(item_dir) -> Item:
    data = json.loads(meta_path(item_dir).read_text(encoding="utf-8"))
    item = Item(**data)
    item.dir = str(item_dir)  # trust the on-disk location over the stored path
    return item


def find_video(item_dir) -> Optional[Path]:
    for p in sorted(Path(item_dir).iterdir()):
        if p.suffix.lower() in VIDEO_EXTS:
            return p
    return None


def load_transcript(item_dir) -> str:
    p = transcript_path(item_dir)
    return p.read_text(encoding="utf-8").strip() if p.exists() else ""


def load_items(data_dir) -> list[Item]:
    data = Path(data_dir)
    if not data.exists():
        return []
    items = []
    for d in sorted(p for p in data.iterdir() if p.is_dir()):
        if meta_path(d).exists():
            items.append(load_meta(d))
    return items


def write_manifest(data_dir, username: str, items: list[Item]) -> None:
    manifest = {
        "username": username,
        "count": len(items),
        "items": [
            {
                "shortcode": i.shortcode,
                "url": i.url,
                "date": i.date,
                "views": i.views,
                "likes": i.likes,
                "comments": i.comments,
            }
            for i in items
        ],
    }
    (Path(data_dir) / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
