"""Command-line interface for the contenti pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from contenti import __version__


def _default_out(username: str) -> str:
    return str(Path("data") / username)


def _add_download_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--limit", type=int, default=None, help="max number of videos")
    p.add_argument("--login", dest="session_user", default=None,
                   help="Instagram username whose saved session to use")
    p.add_argument("--session-file", default=None, help="path to instaloader session file")


def _add_transcribe_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--model", default="small",
                   help="whisper model size: tiny|base|small|medium|large-v3")
    p.add_argument("--lang", default=None, help="force language code (e.g. ru); default=auto")
    p.add_argument("--device", default="auto", help="auto|cpu|cuda")
    p.add_argument("--compute-type", default="default",
                   help="faster-whisper compute type, e.g. int8|float16|default")


def _add_analyze_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--llm-model", default=None, help="Anthropic model id (default: env or sonnet)")
    p.add_argument("--report-lang", default="Russian", help="language for the report")
    p.add_argument("--max-videos", type=int, default=None, help="cap videos sent to the LLM")
    p.add_argument("--report", default=None, help="report output path (default: <data>/report.md)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="contenti",
        description="Download, transcribe and analyze an Instagram account's videos.",
    )
    parser.add_argument("--version", action="version", version=f"contenti {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    d = sub.add_parser("download", help="download videos from a profile")
    d.add_argument("username")
    d.add_argument("--out", default=None, help="output dir (default: data/<username>)")
    _add_download_args(d)
    d.add_argument("--overwrite", action="store_true", help="re-download existing videos")

    t = sub.add_parser("transcribe", help="transcribe downloaded videos")
    t.add_argument("data_dir", help="directory produced by 'download'")
    _add_transcribe_args(t)
    t.add_argument("--overwrite", action="store_true", help="re-transcribe existing")

    a = sub.add_parser("analyze", help="analyze the account with an LLM")
    a.add_argument("data_dir", help="directory produced by 'download'")
    a.add_argument("--username", default=None)
    _add_analyze_args(a)

    r = sub.add_parser("run", help="full pipeline: download -> transcribe -> analyze")
    r.add_argument("username")
    r.add_argument("--out", default=None, help="output dir (default: data/<username>)")
    _add_download_args(r)
    _add_transcribe_args(r)
    _add_analyze_args(r)
    r.add_argument("--overwrite", action="store_true",
                   help="re-download and re-transcribe existing items")

    args = parser.parse_args(argv)

    if args.command == "download":
        from contenti.download import download_profile

        out = args.out or _default_out(args.username)
        download_profile(args.username, out, limit=args.limit,
                         session_user=args.session_user, session_file=args.session_file,
                         overwrite=args.overwrite)
        return 0

    if args.command == "transcribe":
        from contenti.transcribe import transcribe_dir

        transcribe_dir(args.data_dir, model_size=args.model, language=args.lang,
                       device=args.device, compute_type=args.compute_type,
                       overwrite=args.overwrite)
        return 0

    if args.command == "analyze":
        from contenti.analyze import DEFAULT_MODEL, analyze_account

        analyze_account(args.data_dir, username=args.username,
                        model=args.llm_model or DEFAULT_MODEL, lang=args.report_lang,
                        max_videos=args.max_videos, out_file=args.report)
        return 0

    if args.command == "run":
        from contenti.analyze import DEFAULT_MODEL, analyze_account
        from contenti.download import download_profile
        from contenti.transcribe import transcribe_dir

        out = args.out or _default_out(args.username)
        download_profile(args.username, out, limit=args.limit,
                         session_user=args.session_user, session_file=args.session_file,
                         overwrite=args.overwrite)
        transcribe_dir(out, model_size=args.model, language=args.lang,
                       device=args.device, compute_type=args.compute_type,
                       overwrite=args.overwrite)
        analyze_account(out, username=args.username,
                        model=args.llm_model or DEFAULT_MODEL, lang=args.report_lang,
                        max_videos=args.max_videos, out_file=args.report)
        return 0

    return 1
