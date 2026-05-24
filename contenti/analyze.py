"""Stage 3 — understand each video and analyze the account with an LLM.

For every video we ask the model to distil the "essence" (topic, hook,
key points). Those per-video digests plus engagement stats are then fed into
a single account-level analysis that produces a Markdown report.

Requires ANTHROPIC_API_KEY in the environment.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from contenti.store import Item, load_items, load_transcript

DEFAULT_MODEL = os.environ.get("CONTENTI_MODEL", "claude-sonnet-4-6")
_MAX_TRANSCRIPT_CHARS = 6000

_ESSENCE_PROMPT = """\
You analyze short-form social video. Below is one Instagram video from the \
account @{username}: its caption and (when available) an auto-transcript of \
the spoken audio.

Return ONLY a JSON object with these keys (write the string values in {lang}):
  "topic":      short topic label (3-6 words)
  "summary":    2-3 sentence summary of what the video is actually about
  "hook":       the opening hook / how it grabs attention
  "format":     content format (e.g. talking head, listicle, tutorial, story)
  "key_points": array of 2-5 concrete takeaways
  "cta":        the call to action, or "" if none

CAPTION:
{caption}

TRANSCRIPT:
{transcript}
"""

_ACCOUNT_PROMPT = """\
You are a senior social-media strategist. Analyze the Instagram account \
@{username} based on the per-video digests and engagement stats below \
({n} videos).

Write a thorough analysis in {lang} as Markdown. Use these sections:
1. Резюме аккаунта (ниша, позиционирование, о чём канал в одном абзаце)
2. Контент-рубрики (повторяющиеся темы/форматы, с примерами)
3. Приёмы и хуки (как удерживают внимание)
4. Тональность и стиль подачи
5. Целевая аудитория
6. Вовлечённость (выводы из просмотров/лайков/комментов: что заходит лучше)
7. Сильные стороны
8. Слабые места и риски
9. Рекомендации по росту (конкретные, действенные)
10. 5 идей для новых роликов в этом стиле

Be specific and reference real patterns from the data. Do not invent numbers.

DATA (JSON):
{data}
"""


def _client():
    import anthropic

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("[analyze] ANTHROPIC_API_KEY is not set in the environment")
    return anthropic.Anthropic()


def _complete(client, model: str, prompt: str, max_tokens: int) -> str:
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}


def _essence(client, model: str, item: Item, username: str, lang: str) -> dict:
    transcript = load_transcript(item.dir)[:_MAX_TRANSCRIPT_CHARS] or "(no transcript)"
    prompt = _ESSENCE_PROMPT.format(
        username=username,
        lang=lang,
        caption=(item.caption or "(no caption)")[:2000],
        transcript=transcript,
    )
    return _parse_json(_complete(client, model, prompt, max_tokens=900))


def analyze_account(
    data_dir: str,
    username: str | None = None,
    model: str = DEFAULT_MODEL,
    lang: str = "Russian",
    max_videos: int | None = None,
    out_file: str | None = None,
) -> str:
    items = load_items(data_dir)
    if not items:
        raise SystemExit(f"[analyze] no items found in {data_dir}")

    username = username or Path(data_dir).name
    if max_videos:
        items = items[:max_videos]

    client = _client()
    print(f"[analyze] model={model}; distilling {len(items)} videos...")

    digests = []
    for i, item in enumerate(items, 1):
        print(f"[analyze] ({i}/{len(items)}) {item.shortcode}")
        essence = _essence(client, model, item, username, lang)
        digests.append(
            {
                "shortcode": item.shortcode,
                "url": item.url,
                "date": item.date,
                "views": item.views,
                "likes": item.likes,
                "comments": item.comments,
                "hashtags": item.hashtags[:15],
                **essence,
            }
        )

    print("[analyze] writing account-level analysis...")
    account_prompt = _ACCOUNT_PROMPT.format(
        username=username,
        n=len(digests),
        lang=lang,
        data=json.dumps(digests, ensure_ascii=False, indent=2),
    )
    body = _complete(client, model, account_prompt, max_tokens=4000)

    report = _render(username, digests, body)
    out_path = Path(out_file) if out_file else Path(data_dir) / "report.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"[analyze] report written -> {out_path}")
    return report


def _render(username: str, digests: list[dict], body: str) -> str:
    lines = [f"# Анализ аккаунта @{username}", "", body, "", "---", "", "## Разбор роликов", ""]
    for d in digests:
        lines.append(f"### [{d.get('topic') or d['shortcode']}]({d['url']})")
        stats = []
        if d.get("views") is not None:
            stats.append(f"{d['views']} просмотров")
        if d.get("likes") is not None:
            stats.append(f"{d['likes']} лайков")
        if d.get("comments") is not None:
            stats.append(f"{d['comments']} комм.")
        if d.get("date"):
            stats.append(d["date"][:10])
        if stats:
            lines.append("_" + " · ".join(stats) + "_")
        if d.get("summary"):
            lines.append("")
            lines.append(d["summary"])
        if d.get("hook"):
            lines.append(f"- **Хук:** {d['hook']}")
        if d.get("format"):
            lines.append(f"- **Формат:** {d['format']}")
        for kp in d.get("key_points", []) or []:
            lines.append(f"- {kp}")
        if d.get("cta"):
            lines.append(f"- **CTA:** {d['cta']}")
        lines.append("")
    return "\n".join(lines)
