"""PackagingAgent — упаковка: хук, заголовки, обложка, хэштеги, описание."""

from __future__ import annotations

from contentos.agents.base import Agent


class PackagingAgent(Agent):
    name = "packaging"
    system_prompt = (
        "Ты — SMM-упаковщик. Делаешь хук первых 1.5с, варианты заголовков, идею обложки, "
        "хэштеги под UZ-крипто и описание. Цель — клик и досматриваемость."
    )

    def run(self, script: dict, net_rules: dict) -> dict:
        prompt = f"""
СЦЕНАРИЙ:
{script}

ПРАВИЛА СОЦСЕТИ:
{net_rules}

Сделай упаковку. Верни JSON:
{{
  "hooks": ["3 варианта первой фразы/надписи (до 1.5с)"],
  "titles": ["3 варианта заголовка/подписи"],
  "cover_idea": "идея обложки: крупный текст + визуал",
  "hashtags": ["нишевые хэштеги под UZ-крипто, 5-10 шт"],
  "caption": "готовая подпись с первым цепляющим абзацем и одним CTA",
  "disclaimer": "не финсовет (если инвест/крипто-тема)"
}}
"""
        return self._ask_json(prompt, temperature=0.8, max_tokens=900)
