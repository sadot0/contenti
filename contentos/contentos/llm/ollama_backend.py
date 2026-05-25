"""Локальный Ollama-бэкенд (рантайм по умолчанию).

Работает на твоей машине: запусти `ollama serve` и скачай модель, напр.:
    ollama pull qwen2.5:7b-instruct
Никаких платных API. Используется только стандартная библиотека (urllib) — без лишних зависимостей.
"""

from __future__ import annotations

import json
import urllib.request

from contentos.llm.base import LLMBackend, LLMResponse


class OllamaBackend(LLMBackend):
    def __init__(
        self,
        model: str = "qwen2.5:7b-instruct",
        host: str = "http://localhost:11434",
        timeout: int = 300,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout = timeout

    def complete(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1500,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if system:
            payload["system"] = system

        req = urllib.request.Request(
            f"{self.host}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())
        return LLMResponse(text=data.get("response", "").strip(), model=self.model, raw=data)

    def health(self) -> bool:
        """Проверить, что Ollama поднят и модель доступна."""
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=10) as resp:
                tags = json.loads(resp.read())
            names = {m.get("name", "") for m in tags.get("models", [])}
            return any(self.model.split(":")[0] in n for n in names)
        except Exception:
            return False
