"""CLI ContentOS.

Примеры (запускать у себя локально, где поднят Ollama):
    python -m contentos doctor
    python -m contentos idea "почему биткоин падает" --net instagram
"""

from __future__ import annotations

import argparse
import json

from contentos.llm.base import get_backend


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="contentos", description="Персональный AI-движок контента")
    p.add_argument("--llm", default="ollama", help="бэкенд: ollama | claude")
    p.add_argument("--model", default="qwen2.5:7b-instruct", help="имя модели Ollama")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="проверить окружение (Ollama доступен?)")

    i = sub.add_parser("idea", help="сгенерировать идею: бриф+сценарий+упаковку")
    i.add_argument("topic")
    i.add_argument("--net", default="instagram", help="instagram | tiktok | youtube")

    args = p.parse_args(argv)

    if args.cmd == "doctor":
        be = get_backend(args.llm, model=args.model) if args.llm == "ollama" else get_backend(args.llm)
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

        be = get_backend(args.llm, model=args.model) if args.llm == "ollama" else get_backend(args.llm)
        result = Orchestrator(be).make_idea(args.topic, network=args.net)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
