"""Базовый workspace соцсети.

Каждая соцсеть — независимый модуль со своими правилами (длина, хук, сигналы алгоритма,
формат упаковки). Workspaces НЕ обмениваются логикой между собой — общая только база знаний
об авторе и рынке. Это требование архитектуры (см. docs/01-architecture.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Workspace:
    network: str
    length_sweetspot: str
    primary_signal: str          # главный сигнал алгоритма
    hook_style: str
    packaging_notes: str
    extra_rules: list = field(default_factory=list)

    def rules(self) -> dict:
        return {
            "network": self.network,
            "length_sweetspot": self.length_sweetspot,
            "primary_signal": self.primary_signal,
            "hook_style": self.hook_style,
            "packaging_notes": self.packaging_notes,
            "extra_rules": self.extra_rules,
        }
