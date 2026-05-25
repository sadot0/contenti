#!/usr/bin/env bash
# Обёртка для автозапуска ContentOS под launchd.
# launchd даёт минимальный PATH, поэтому задаём окружение явно.
set -euo pipefail

# Полный PATH (чтобы нашлись python3.12 и ollama из Homebrew)
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

# Опциональные секреты (Telegram): создай ~/.contentos.env по образцу deploy/contentos.env.example
[ -f "$HOME/.contentos.env" ] && source "$HOME/.contentos.env"

CO_DIR="${CONTENTOS_DIR:-$HOME/contenti/contentos}"
MODEL="${CONTENTOS_MODEL:-qwen2.5:14b-instruct}"
NET="${CONTENTOS_NET:-instagram}"
IDEAS="${CONTENTOS_IDEAS:-3}"

PY="$(command -v python3.12 || command -v python3.13 || command -v python3)"

echo "===== $(date '+%Y-%m-%d %H:%M:%S') ContentOS daily ($PY, $MODEL, $NET, ideas=$IDEAS) ====="
cd "$CO_DIR"
exec "$PY" -m contentos daily --net "$NET" --ideas "$IDEAS" --model "$MODEL"
