"""Уведомления в Telegram (бесплатно).

Создай бота через @BotFather, получи token и свой chat_id, положи в settings.yaml или env:
    CONTENTOS_TG_TOKEN, CONTENTOS_TG_CHAT
Движок будет присылать тебе готовые идеи (напр. каждое утро после `contentos daily`).
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request


def send(text: str, token: str | None = None, chat_id: str | None = None) -> bool:
    token = token or os.environ.get("CONTENTOS_TG_TOKEN")
    chat_id = chat_id or os.environ.get("CONTENTOS_TG_CHAT")
    if not token or not chat_id:
        print("[telegram] не задан токен/chat_id — пропускаю уведомление")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode(
        {"chat_id": chat_id, "text": text[:4000], "parse_mode": "Markdown"}
    ).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as r:
            return json.loads(r.read()).get("ok", False)
    except Exception as exc:  # noqa: BLE001
        print(f"[telegram] ошибка отправки: {exc}")
        return False
