"""PositioningAgent — позиционирование бренда автора."""

from __future__ import annotations

from contentos.agents.base import Agent


class PositioningAgent(Agent):
    name = "positioning"
    system_prompt = (
        "Ты — бренд-стратег. Определяешь позиционирование автора: кто он, для кого, "
        "чем отличается от конкурентов, какие рубрики и tone of voice. Рынок — UZ/Ташкент."
    )

    def run(self, author_analysis: str, inspirations_summary: str, market_notes: str = "") -> dict:
        prompt = f"""
АНАЛИЗ КОНТЕНТА АВТОРА:
{author_analysis}

ВДОХНОВИТЕЛИ (выжимка):
{inspirations_summary}

РЫНОК UZ/ТАШКЕНТ:
{market_notes or '(заполнить позже трендами)'}

Сформулируй позиционирование. Верни JSON:
{{
  "one_liner": "кто автор в одной фразе",
  "audience": "для кого (узко)",
  "differentiation": "чем отличается от вдохновителей",
  "tone_of_voice": "как говорит",
  "rubrics": ["3-6 контент-рубрик"],
  "do": ["что делать"],
  "dont": ["чего избегать"]
}}
"""
        return self._ask_json(prompt, temperature=0.5, max_tokens=1200)
