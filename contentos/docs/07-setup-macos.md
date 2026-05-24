# 07 — Запуск на твоём Mac (M3 Pro, 36 ГБ, 24/7)

Подтверждённое железо: **MacBook Pro M3 Pro, 36 ГБ unified memory, включён 24/7.**
Это сильный сетап — хватает для локального LLM и быстрой транскрибации. Всё ниже — бесплатно.

## 1. Поставить Ollama + модель
```bash
# установить Ollama (https://ollama.com)
brew install ollama          # или скачать приложение
ollama serve                 # запустить сервер (в фоне)

# рабочая модель (быстрая, тянет 36 ГБ легко):
ollama pull qwen2.5:14b-instruct
# для редких тяжёлых задач можно:
ollama pull qwen2.5:32b-instruct      # q4 ~20 ГБ, влезает в 36 ГБ
# для частых лёгких задач:
ollama pull qwen2.5:7b-instruct
```
Рекомендация по умолчанию: **14B как рабочая**, 7B для высокочастотных задач, 32B — точечно.

## 2. Что тянет M3 Pro / 36 ГБ
- 7B — мгновенно. 14B — быстро. 32B (q4) — рабоче, чуть медленнее.
- **faster-whisper large-v3** на Metal — быстро (в отличие от облачного CPU). Значит узбекский
  звук расшифровывается качественно → транскрибацию делаем на твоём Маке, не в облаке.

## 3. Узбекский язык — тест перед стартом
Локальные модели слабы в узбекском. Перед продакшеном:
- прогнать одинаковый промпт на `qwen2.5:14b`, `qwen2.5:32b` (и при желании др.) на узбекском;
- выбрать лучшую; часть генерации, возможно, вести на русском с адаптацией на узбекский.
- Это эмпирический выбор на твоём железе (добавим команду `contentos test-uz`).

## 4. Транскрибация на Маке (качественно)
```bash
# в репозитории contenti:
pip install -r requirements.txt
python -m contenti transcribe data/mirzabek_vokhidov --model large-v3 --device auto
# на Apple Silicon faster-whisper использует ускорение; large-v3 идёт быстро
```

## 5. Автономный цикл через launchd (macOS «cron»)
Создать `~/Library/LaunchAgents/com.contentos.daily.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>Label</key><string>com.contentos.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string><string>-lc</string>
    <string>cd /ПУТЬ/contentos && /usr/bin/python3 -m contentos daily >> ~/contentos.log 2>&1</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
  <key>RunAtLoad</key><false/>
</dict></plist>
```
Активировать: `launchctl load ~/Library/LaunchAgents/com.contentos.daily.plist`
Теперь каждый день в 8:00 движок сам собирает тренды, генерит идеи и шлёт тебе (Telegram).

## 6. Уведомления (бесплатно)
Telegram-бот: создать через @BotFather, движок постит готовые идеи тебе в личку утром.
(Реализуем в фазе автономности — см. `docs/06-autonomy.md`.)

## Итог
- Инференс: **$0** (локально на M3 Pro).
- Транскрибация узбекского: **качественно** (large-v3 на Metal).
- Автономность: **launchd**, машина и так 24/7.
- Затраты: только электричество. Эффективность — за счёт промптов/скилов и человека в петле.
