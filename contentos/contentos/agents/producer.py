"""ProducerAgent — из темы + соцсети собирает бриф ролика."""

from __future__ import annotations

from contentos.agents.base import Agent


class ProducerAgent(Agent):
    name = "producer"
    system_prompt = (
        "Ты — продюсер коротких видео. Из темы делаешь чёткий бриф: угол подачи, цель, "
        "целевую эмоцию, формат, длину. Думаешь о виральности и об аудитории UZ/Ташкент."
    )

    def run(self, topic: str, positioning: str, net_rules: dict, virality_patterns: str = "") -> dict:
        prompt = f"""
ТЕМА: {topic}

ПОЗИЦИОНИРОВАНИЕ АВТОРА:
{positioning}

ПРАВИЛА СОЦСЕТИ:
{net_rules}

ПАТТЕРНЫ ВИРАЛЬНОСТИ (что заходит):
{virality_patterns or '(пока нет — используй здравый смысл и правила соцсети)'}

Собери бриф. Верни JSON:
{{
  "angle": "под каким углом подаём (неочевидный, цепляющий)",
  "goal": "охват | вовлечение | сохранения | подписки",
  "emotion": "целевая эмоция зрителя",
  "format": "квиз | история | разбор | POV | предмет-в-кадре | расследование",
  "target_seconds": <число>,
  "rubric": "к какой рубрике автора относится",
  "why_viral": "почему может зайти у аудитории UZ"
}}
"""
        return self._ask_json(prompt, temperature=0.7, max_tokens=900)
