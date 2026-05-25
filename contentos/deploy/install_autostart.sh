#!/usr/bin/env bash
# Установить автозапуск ContentOS каждое утро (macOS launchd).
# Использование:  bash contentos/deploy/install_autostart.sh [час]
#   час — час запуска 0..23 (по умолчанию 8). Пример: bash .../install_autostart.sh 9
set -euo pipefail

HOUR="${1:-8}"
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$DEPLOY_DIR/run_daily.sh"
chmod +x "$RUNNER"

LABEL="com.contentos.daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$HOME/contentos.log</string>
  <key>StandardErrorPath</key><string>$HOME/contentos.log</string>
  <key>RunAtLoad</key><false/>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "✅ Автозапуск установлен: $PLIST"
echo "   Каждый день в $HOUR:00 движок соберёт тренды и сгенерит идеи."
echo "   Лог:        $HOME/contentos.log"
echo "   Результаты: $HOME/contenti/contentos/output/<дата>/"
echo ""
echo "Проверить разово прямо сейчас:  bash $RUNNER"
echo "Снять автозапуск:               launchctl unload $PLIST"
