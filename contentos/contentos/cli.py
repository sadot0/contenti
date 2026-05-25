"""CLI ContentOS.

Примеры (запускать у себя локально, где поднят Ollama):
    python3 -m contentos doctor
    python3 -m contentos idea "почему биткоин падает" --net instagram
    python3 -m contentos daily --net instagram --ideas 3

Глобальные флаги --llm / --model указываются ПОСЛЕ подкоманды, напр.:
    python3 -m contentos doctor --model qwen2.5:14b-instruct
"""

from __future__ import annotations

import argparse
import json

from contentos.llm.base import get_backend

DEFAULT_MODEL = "qwen2.5:14b-instruct"


def _common() -> argparse.ArgumentParser:
    """Общие флаги для всех подкоманд (работают после имени подкоманды)."""
    c = argparse.ArgumentParser(add_help=False)
    c.add_argument("--llm", default="ollama", help="бэкенд: ollama | claude")
    c.add_argument("--model", default=DEFAULT_MODEL, help="имя модели Ollama")
    return c


def _backend(args):
    if args.llm == "ollama":
        return get_backend("ollama", model=args.model)
    return get_backend(args.llm)


def main(argv: list[str] | None = None) -> int:
    common = _common()
    p = argparse.ArgumentParser(prog="contentos", description="Персональный AI-движок контента")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", parents=[common], help="проверить окружение (Ollama доступен?)")

    i = sub.add_parser("idea", parents=[common], help="идея: бриф+сценарий+упаковка")
    i.add_argument("topic")
    i.add_argument("--net", default="instagram", help="instagram | tiktok | youtube")

    d = sub.add_parser("daily", parents=[common], help="суточный цикл (для cron/launchd)")
    d.add_argument("--net", default="instagram", help="instagram | tiktok | youtube")
    d.add_argument("--ideas", type=int, default=3, help="сколько идей сгенерировать")

    args = p.parse_args(argv)

    if args.cmd == "doctor":
        be = _backend(args)
        ok = getattr(be, "health", lambda: None)()
        if ok is True:
            print(f"[ok] Ollama доступен, модель '{args.model}' найдена.")
        elif ok is False:
            print(f"[!] Ollama не отвечает или модель '{args.model}' не скачана.")
            print("    Запусти: ollama serve  &&  ollama pull", args.model)
        else:
            print(f"[i] Бэкенд '{args.llm}' не поддерживает health-check.")
        return 0

    if args.cmd == "idea":
        from contentos.orchestrator import Orchestrator

        result = Orchestrator(_backend(args)).make_idea(args.topic, network=args.net)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "daily":
        from contentos.daily import run_daily

        run_daily(_backend(args), network=args.net, n_ideas=args.ideas)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
