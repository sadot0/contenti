"""Сменный интерфейс LLM-бэкенда.

Продукт не привязан к одному провайдеру. По умолчанию — локальный Ollama (бесплатно).
Можно подключить другой бэкенд, реализовав этот интерфейс.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    model: str
    raw: dict | None = None


class LLMBackend(ABC):
    """Базовый интерфейс. Любой бэкенд обязан уметь `complete`."""

    @abstractmethod
    def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        ...

    def complete_json(self, prompt: str, system: str | None = None, **kw) -> dict:
        """Удобный помощник: просит модель вернуть JSON и парсит его."""
        import json
        import re

        guard = (
            "\n\nВерни ТОЛЬКО валидный JSON-объект без markdown-обёртки и комментариев."
        )
        resp = self.complete(prompt + guard, system=system, **kw)
        text = re.sub(r"^```(?:json)?|```$", "", resp.text.strip(), flags=re.MULTILINE).strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return {}
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return {}


def get_backend(name: str = "ollama", **kw) -> LLMBackend:
    """Фабрика бэкендов по имени из конфига."""
    name = (name or "ollama").lower()
    if name == "ollama":
        from contentos.llm.ollama_backend import OllamaBackend

        return OllamaBackend(**kw)
    if name in ("claude", "anthropic"):
        from contentos.llm.claude_backend import ClaudeBackend

        return ClaudeBackend(**kw)
    raise ValueError(f"Неизвестный LLM-бэкенд: {name}")
