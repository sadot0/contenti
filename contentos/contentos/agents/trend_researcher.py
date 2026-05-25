"""TrendResearcherAgent — темы и инфоповоды (крипто + Узбекистан).

На старте полуручной: ты подаёшь сырьё (новости/тренды текстом или через web-search MCP),
агент превращает его в список тем-кандидатов с обоснованием. Автоматический сбор источников —
фаза 2 (см. docs/03-roadmap.md).
"""

from __future__ import annotations

from contentos.agents.base import Agent


class TrendResearcherAgent(Agent):
    name = "trend_researcher"
    system_prompt = (
        "Ты — аналитик трендов в крипто и на рынке Узбекистана. Из сырых новостей/трендов "
        "формируешь темы для коротких видео под аудиторию UZ/Ташкент."
    )

    def run(self, raw_feed: str, positioning: str, n: int = 10) -> dict:
        prompt = f"""
СЫРЬЁ (новости/тренды):
{raw_feed}

ПОЗИЦИОНИРОВАНИЕ АВТОРА:
{positioning}

Предложи {n} тем для коротких видео. Верни JSON:
{{
  "topics": [
    {{"topic": "...", "why_now": "почему актуально", "angle": "угол", "rubric": "рубрика"}}
  ]
}}
"""
        return self._ask_json(prompt, temperature=0.7, max_tokens=1500)
