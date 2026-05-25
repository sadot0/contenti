"""ScriptwriterAgent — пишет сценарий по 7-блочной структуре.

Блоки: захват → удержание → завлечение → объяснение → вдохновение → действие → заключение.
Подробности — в docs/04-virality-framework.md.
"""

from __future__ import annotations

from contentos.agents.base import Agent

BLOCKS = [
    ("hook", "Захват", "за 1–1.5 сек дать причину не листать: вопрос / шок-факт / предмет в кадре"),
    ("retention", "Удержание", "пообещать ценность или интригу"),
    ("engagement", "Завлечение", "втянуть зрителя: вопрос к нему, ставка, «угадай до конца»"),
    ("explanation", "Объяснение", "суть по шагам: история/разбор/пример, просто"),
    ("inspiration", "Вдохновение", "что это меняет для зрителя, смысл, эмоция"),
    ("action", "Действие", "ровно один чёткий CTA"),
    ("conclusion", "Заключение", "кольцевая фраза-петля назад к хуку"),
]


class ScriptwriterAgent(Agent):
    name = "scriptwriter"
    system_prompt = (
        "Ты — сценарист коротких видео для соцсетей. Пишешь живо, просто, под голос автора. "
        "Аудитория — Узбекистан/Ташкент, язык ру/уз, локальные примеры. "
        "Строго соблюдаешь 7-блочную структуру. Один ролик — одна мысль. CTA ровно один."
    )

    def run(self, brief: dict, voice: str, net_rules: dict) -> dict:
        """brief — от ProducerAgent; voice — tone of voice автора; net_rules — правила соцсети."""
        blocks_spec = "\n".join(f"{i+1}. {ru} ({k}): {desc}" for i, (k, ru, desc) in enumerate(BLOCKS))
        prompt = f"""
Напиши сценарий короткого видео.

ТЕМА/БРИФ:
{brief}

ГОЛОС АВТОРА (tone of voice):
{voice}

ПРАВИЛА СОЦСЕТИ:
{net_rules}

Используй СТРОГО эти 7 блоков:
{blocks_spec}

Верни JSON:
{{
  "title_working": "рабочее название",
  "target_seconds": <число>,
  "blocks": {{
    "hook": {{"text": "...", "shot": "ремарка по съёмке", "seconds": "0-2с"}},
    "retention": {{...}}, "engagement": {{...}}, "explanation": {{...}},
    "inspiration": {{...}}, "action": {{...}}, "conclusion": {{...}}
  }},
  "on_screen_text": ["ключевые надписи на экране"],
  "one_idea": "одна мысль ролика в одной фразе"
}}
"""
        return self._ask_json(prompt, temperature=0.8, max_tokens=1800)
