"""Суточный автономный цикл ContentOS.

Запускается по расписанию (launchd/cron) у тебя на Маке:
  собрать тренды (RSS) → предложить темы → сгенерировать идеи (бриф+сценарий+упаковка)
  → сохранить на диск → прислать сводку в Telegram.

Команда: `python -m contentos daily --net instagram --ideas 3`
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from contentos.agents import TrendResearcherAgent
from contentos.collectors import as_digest, fetch_feeds
from contentos.llm.base import LLMBackend
from contentos.notify import telegram_send
from contentos.orchestrator import KNOWLEDGE, Orchestrator, _read

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"


def _load_feeds() -> list[str]:
    for name in ("feeds.txt", "feeds.example.txt"):
        p = ROOT / "config" / name
        if p.exists():
            return [ln.strip() for ln in p.read_text().splitlines()
                    if ln.strip() and not ln.startswith("#")]
    return []


def run_daily(llm: LLMBackend, network: str = "instagram", n_ideas: int = 3) -> dict:
    today = datetime.date.today().isoformat()
    positioning = _read(KNOWLEDGE / "profile" / "positioning.md", "(позиционирование не задано)")

    # 1. собрать тренды
    feeds = _load_feeds()
    items = fetch_feeds(feeds) if feeds else []
    digest = as_digest(items) if items else "(ленты не настроены — заполни config/feeds.txt)"

    # 2. предложить темы
    topics_obj = TrendResearcherAgent(llm).run(digest, positioning, n=max(n_ideas * 2, 6))
    topics = [t.get("topic", "") for t in topics_obj.get("topics", []) if t.get("topic")]

    # сохранить тренды дня
    (KNOWLEDGE / "trends").mkdir(parents=True, exist_ok=True)
    (KNOWLEDGE / "trends" / f"{today}.md").write_text(
        f"# Тренды {today}\n\n## Сырьё (RSS)\n{digest}\n\n## Темы\n" +
        "\n".join(f"- {t}" for t in topics), encoding="utf-8"
    )

    # 3. сгенерировать идеи по top-N темам
    orch = Orchestrator(llm)
    ideas = []
    for topic in topics[:n_ideas]:
        try:
            ideas.append(orch.make_idea(topic, network=network))
        except Exception as exc:  # noqa: BLE001
            print(f"[daily] идея по теме '{topic}' не удалась: {exc}")

    # 4. сохранить
    out_dir = OUTPUT / today
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{network}.json").write_text(
        json.dumps(ideas, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 5. уведомить
    if ideas:
        msg = f"*ContentOS · {today} · {network}*\nГотово идей: {len(ideas)}\n\n"
        for i, idea in enumerate(ideas, 1):
            title = (idea.get("script", {}) or {}).get("title_working", idea.get("topic", "?"))
            score = (idea.get("virality", {}) or {}).get("score", "?")
            msg += f"{i}. {title} (потенциал: {score})\n"
        msg += f"\nПодробно: output/{today}/{network}.json"
        telegram_send(msg)

    print(f"[daily] {today}: тем={len(topics)}, идей={len(ideas)} → {out_dir}")
    return {"date": today, "network": network, "topics": topics, "ideas": ideas}
