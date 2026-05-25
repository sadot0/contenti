# ContentOS

Персональный AI-движок личного бренда: «штат» AI-агентов, который изучает тебя, твоих
вдохновителей, рынок и тренды, и помогает производить виральный контент под каждую соцсеть
отдельно (Instagram / TikTok / YouTube).

> **Сначала прочитай [`START_HERE.md`](./START_HERE.md)** — там вся картина, ограничения и
> что нужно от тебя.

## Статус
Фаза 0 (фундамент): заложены план, архитектура, каркас кода и анализ. Рантайм — локальный
Ollama (бесплатно). Запуск агентов — у тебя на машине (в облаке Ollama нет).

## Быстрый старт (локально, у тебя)
```bash
# 1. Поставь Ollama и модель
ollama serve
ollama pull qwen2.5:7b-instruct      # или своя модель из `ollama list`

# 2. Проверь окружение
python -m contentos doctor --model qwen2.5:7b-instruct

# 3. Сгенерируй идею (бриф + сценарий по 7 блокам + упаковку)
python -m contentos idea "почему биткоин упал" --net instagram
```

## Структура
- `docs/` — план, архитектура, роли агентов, дорожная карта, фреймворк виральности, ограничения.
- `contentos/llm/` — сменный LLM-бэкенд (Ollama по умолчанию, Claude опционально).
- `contentos/agents/` — AI-агенты: positioning, trend_researcher, producer, scriptwriter,
  packaging, virality_analyst.
- `contentos/workspaces/` — независимые пространства соцсетей (свои правила у каждой).
- `contentos/orchestrator.py` — пайплайн идеи под соцсеть.
- `knowledge/` — база знаний: profile (ты), inspirations (вдохновители), market, trends.

## Данные
Ingestion (скачивание + транскрибация) делает модуль `contenti` (в корне репозитория).
Сырьё и отчёты лежат в `data/<account>/` (вне git — в .gitignore).
