"""Базовый класс агента.

Агент = роль + системный промпт + метод run(). Все агенты вызывают сменный LLM-бэкенд.
Контекст (позиционирование, правила соцсети, паттерны виральности) подаётся снаружи —
из knowledge base и workspace.
"""

from __future__ import annotations

from contentos.llm.base import LLMBackend


class Agent:
    name: str = "agent"
    system_prompt: str = "Ты помощник."

    def __init__(self, llm: LLMBackend):
        self.llm = llm

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _ask(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1500) -> str:
        return self.llm.complete(
            prompt, system=self.system_prompt, temperature=temperature, max_tokens=max_tokens
        ).text

    def _ask_json(self, prompt: str, **kw) -> dict:
        return self.llm.complete_json(prompt, system=self.system_prompt, **kw)
