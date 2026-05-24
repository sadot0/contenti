#!/usr/bin/env bash
# ContentOS — установка на macOS (M-серия). Запусти из корня репозитория:
#   bash contentos/setup_mac.sh
# Скрипт идемпотентный: можно запускать повторно.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CO="$ROOT/contentos"
MODEL="${CONTENTOS_MODEL:-qwen2.5:14b-instruct}"

echo "==> ContentOS setup (root: $ROOT, model: $MODEL)"

# 1. Python-зависимости (для ingestion/транскрибации). Само ядро contentos — на stdlib.
if [ -f "$ROOT/requirements.txt" ]; then
  echo "==> pip install зависимостей ingestion (instaloader, faster-whisper)..."
  python3 -m pip install -r "$ROOT/requirements.txt" || echo "[!] pip частично не прошёл — проверь Python3/pip"
fi

# 2. Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "==> Ollama не найден. Поставь его:"
  echo "    brew install ollama    (или скачай с https://ollama.com)"
  echo "    затем запусти этот скрипт снова."
  exit 1
fi

echo "==> запускаю ollama serve (в фоне, если ещё не запущен)..."
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  (ollama serve >/tmp/ollama.log 2>&1 &) ; sleep 3
fi

echo "==> тяну модель $MODEL (один раз, может занять время)..."
ollama pull "$MODEL"

# 3. Конфиги из шаблонов (не перезаписываем существующие)
[ -f "$CO/config/settings.yaml" ] || cp "$CO/config/settings.example.yaml" "$CO/config/settings.yaml"
[ -f "$CO/config/feeds.txt" ]     || cp "$CO/config/feeds.example.txt"     "$CO/config/feeds.txt"
echo "==> конфиги: $CO/config/settings.yaml и feeds.txt (поправь ленты под себя)"

# 4. Проверка ядра
echo "==> проверка движка (doctor)..."
( cd "$CO" && python3 -m contentos doctor --model "$MODEL" ) || true

echo ""
echo "================ ГОТОВО ================"
echo "Проверь генерацию идеи:"
echo "  cd $CO && python3 -m contentos idea \"почему биткоин падает\" --net instagram --model $MODEL"
echo ""
echo "Суточный цикл вручную:"
echo "  cd $CO && python3 -m contentos daily --net instagram --ideas 3 --model $MODEL"
echo ""
echo "Автозапуск каждое утро — см. contentos/docs/07-setup-macos.md (launchd)."
echo "Уведомления в Telegram — задай CONTENTOS_TG_TOKEN и CONTENTOS_TG_CHAT."
