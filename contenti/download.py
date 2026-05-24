"""Stage 1 — download an Instagram profile's videos.

Uses instaloader to enumerate posts and read metadata, then downloads the
video file straight from its CDN URL (which avoids fighting instaloader's
filename templating). A login session is optional for public profiles but
strongly recommended: anonymous access is heavily rate-limited by Instagram.
"""

from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

from contenti.store import Item, save_meta, write_manifest

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)


def _safe(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def _fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=120) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def download_profile(
    username: str,
    out_dir: str,
    limit: int | None = None,
    session_user: str | None = None,
    session_file: str | None = None,
    overwrite: bool = False,
) -> list[Item]:
    import instaloader

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    loader = instaloader.Instaloader(
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
    )

    if session_user:
        try:
            loader.load_session_from_file(session_user, session_file)
            print(f"[download] using session for @{session_user}")
        except FileNotFoundError:
            raise SystemExit(
                f"[download] no saved session for '{session_user}'. "
                f"Create one with:  instaloader -l {session_user}"
            )

    profile = instaloader.Profile.from_username(loader.context, username)
    print(f"[download] @{username}: {profile.mediacount} posts total, scanning for videos...")

    items: list[Item] = []
    for post in profile.get_posts():
        if not post.is_video:
            continue

        shortcode = post.shortcode
        item_dir = out / shortcode
        video_dest = item_dir / "video.mp4"

        if video_dest.exists() and not overwrite:
            print(f"[download] {shortcode}: already present, skipping")
        else:
            item_dir.mkdir(parents=True, exist_ok=True)
            video_url = _safe(lambda: post.video_url)
            if not video_url:
                print(f"[download] {shortcode}: no video URL (skipped)")
                continue
            print(f"[download] {shortcode}: fetching video...")
            try:
                _fetch(video_url, video_dest)
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"[download] {shortcode}: download failed ({exc})")
                continue

        caption = _safe(lambda: post.caption) or ""
        (item_dir / "caption.txt").write_text(caption, encoding="utf-8")

        item = Item(
            shortcode=shortcode,
            dir=str(item_dir),
            url=f"https://www.instagram.com/p/{shortcode}/",
            caption=caption,
            date=_safe(lambda: post.date_utc.isoformat()) or "",
            likes=_safe(lambda: post.likes),
            comments=_safe(lambda: post.comments),
            views=_safe(lambda: post.video_view_count),
            duration=_safe(lambda: post.video_duration),
            hashtags=_safe(lambda: list(post.caption_hashtags), []),
            mentions=_safe(lambda: list(post.caption_mentions), []),
            is_video=True,
        )
        save_meta(item)
        items.append(item)

        if limit and len(items) >= limit:
            print(f"[download] reached limit of {limit} videos")
            break

    write_manifest(out, username, items)
    print(f"[download] done: {len(items)} videos -> {out}")
    return items
