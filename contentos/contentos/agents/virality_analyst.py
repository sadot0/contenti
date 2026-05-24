"""ViralityAnalystAgent — паттерны виральности и оценка готового сценария."""

from __future__ import annotations

from contentos.agents.base import Agent


class ViralityAnalystAgent(Agent):
    name = "virality_analyst"
    system_prompt = (
        "Ты — аналитик виральности коротких видео. Делаешь выводы на основе данных "
        "(метрики автора и вдохновителей), а не общих советов. Честно называешь риски."
    )

    def derive_patterns(self, metrics_table: str, network: str) -> str:
        """Из таблицы метрик вывести паттерны 'что заходит' для конкретной соцсети."""
        prompt = f"""
Данные роликов (соцсеть {network}): метрики + темы + форматы.
{metrics_table}

Выведи паттерны: что коррелирует с высоким охватом и высоким ER? Какие форматы/хуки/темы
работают, какие нет? Дай конкретные, проверяемые наблюдения (markdown, по пунктам).
"""
        return self._ask(prompt, temperature=0.4, max_tokens=1200)

    def score(self, script: dict, patterns: str) -> dict:
        """Оценить потенциал готового сценария."""
        prompt = f"""
СЦЕНАРИЙ:
{script}

ИЗВЕСТНЫЕ ПАТТЕРНЫ ВИРАЛЬНОСТИ:
{patterns}

Оцени. Верни JSON:
{{
  "score": <0-100>,
  "strengths": ["..."],
  "risks": ["..."],
  "fixes": ["конкретные правки, чтобы поднять потенциал"]
}}
"""
        return self._ask_json(prompt, temperature=0.4, max_tokens=900)
