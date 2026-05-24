"""Опциональный Claude/Anthropic-бэкенд.

Не используется по умолчанию (нужен платный ANTHROPIC_API_KEY). Оставлен как пример
сменности бэкендов: при желании подключается одной настройкой в config.
"""

from __future__ import annotations

import os

from contentos.llm.base import LLMBackend, LLMResponse


class ClaudeBackend(LLMBackend):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.model = model

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        import anthropic

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY не задан. По умолчанию используй Ollama (бесплатно)."
            )
        client = anthropic.Anthropic()
        kw = {"system": system} if system else {}
        resp = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
            **kw,
        )
        text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
        return LLMResponse(text=text.strip(), model=self.model)
