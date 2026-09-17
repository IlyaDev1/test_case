# LLM Skills

Скилы для LLM-ассистента: протокол встречи из заметок, экспорт в Word, реестр скилов.

## Где смотреть

- `skills/meeting-minutes/` — скил (`SKILL.md`, `references/`, `routes/`)
- `eval_queries.md` — 6 trigger / 4 no-trigger запроса для классификатора
- `examples/` — заметки → протокол (`notes_input.md` → `notes_to_protocol.md`)
- `src/` — API, парсер, docx, реестр скилов
- `tests/` — pytest

## Установка

```bash
uv sync --group dev
cp .env.example .env   # затем DEEPSEEK_API_KEY
```

`.env` подхватывается при старте.

## Запуск

```bash
uv run pytest
uv run python -m src.presentation.fastapi.app
```

Сервер: `http://127.0.0.1:8000`.

**Скилы**

```bash
curl 'http://127.0.0.1:8000/skills'
curl 'http://127.0.0.1:8000/skills?q=протокол'
```

**Экспорт markdown-протокола в Word**

```bash
curl -X POST http://127.0.0.1:8000/protocol/export \
  -H 'Content-Type: application/json' \
  -d "$(jq -n --rawfile t examples/notes_to_protocol.md '{text: $t}')" \
  -o protocol.docx
```

**Заметки → протокол → Word** (нужен `DEEPSEEK_API_KEY`)

```bash
curl -X POST http://127.0.0.1:8000/protocol/generate \
  -H 'Content-Type: application/json' \
  -d '{"notes": "12.03 созвон: решили не переносить релиз, Павел чинит 401 до 15.03"}' \
  -o protocol.docx
```
