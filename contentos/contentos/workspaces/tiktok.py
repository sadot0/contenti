"""TikTok workspace (сейчас не ведётся — заготовка под запуск)."""

from contentos.workspaces.base import Workspace

TIKTOK = Workspace(
    network="tiktok",
    length_sweetspot="15–34 секунды",
    primary_signal="watch time + процент завершений + rewatch",
    hook_style="резкий паттерн-брейк в первый кадр; динамика и темп выше, чем в Reels",
    packaging_notes=(
        "Трендовые звуки и форматы важнее хэштегов; текст-крючок на экране сразу; "
        "локальные UZ-тренды и звуки отслеживать отдельно."
    ),
    extra_rules=[
        "Темп быстрее, монтаж плотнее.",
        "Использовать актуальные звуки/тренды.",
        "Тестировать дуэты/стич под нишу.",
        "Один ролик — одна мысль; CTA один.",
    ],
)
