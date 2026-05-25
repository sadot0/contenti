"""Оркестратор — собирает агентов в пайплайн под конкретную соцсеть.

Пайплайн идеи: тема → producer → scriptwriter → packaging → virality_analyst.
Позиционирование и паттерны виральности подаются контекстом.
"""

from __future__ import annotations

from pathlib import Path

from contentos.agents import (
    PackagingAgent,
    ProducerAgent,
    ScriptwriterAgent,
    ViralityAnalystAgent,
)
from contentos.llm.base import LLMBackend
from contentos.workspaces import get_workspace

KNOWLEDGE = Path(__file__).resolve().parent.parent / "knowledge"


def _read(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


class Orchestrator:
    def __init__(self, llm: LLMBackend):
        self.llm = llm
        self.producer = ProducerAgent(llm)
        self.scriptwriter = ScriptwriterAgent(llm)
        self.packaging = PackagingAgent(llm)
        self.virality = ViralityAnalystAgent(llm)

    def make_idea(self, topic: str, network: str = "instagram") -> dict:
        ws = get_workspace(network)
        rules = ws.rules()

        positioning = _read(KNOWLEDGE / "profile" / "positioning.md", "(позиционирование не задано)")
        voice = _read(KNOWLEDGE / "profile" / "tone_of_voice.md", positioning)
        patterns = _read(KNOWLEDGE / network / "virality-patterns.md", "")

        brief = self.producer.run(topic, positioning, rules, patterns)
        script = self.scriptwriter.run(brief, voice, rules)
        pack = self.packaging.run(script, rules)
        score = self.virality.score(script, patterns)

        return {
            "topic": topic,
            "network": network,
            "brief": brief,
            "script": script,
            "packaging": pack,
            "virality": score,
        }
