# LLM Skills

Тестовое задание: скил для протоколов встреч, парсер markdown-протокола и экспорт в Word.

## Структура

```
src/
  core/           # domain + application (use cases, ports)
  infra/          # парсер, docx-экспорт, загрузчик скилов
  presentation/   # FastAPI, CLI
skills/           # артефакты скилов (SKILL.md, references, routes)
tests/
```

Слои повторяют подход `chatbot_to`: тонкие роутеры, use case + port + Result, без DI-контейнера и БД.

## Скил `meeting-minutes`

Артефакты: `skills/meeting-minutes/`. `description` в frontmatter — узкий сигнал для классификатора; тело `SKILL.md` — системный промпт.

- `references/protocol_format.md` — жёсткий контракт разделов и таблицы задач (чтобы парсер/Word не гадали).
- `routes/ambiguous_fields.md` — сценарии пропусков и неоднозначностей (`не указан` / `нет данных`).

Проверка классификатора: `eval_queries.md` (6 trigger / 4 no-trigger). Пример заметки → протокол: `examples/notes_input.md` → `examples/notes_to_protocol.md`.

## Установка

```bash
cd test/llm_skills
uv sync --group dev
uv run pre-commit install
```

Git-корень репозитория — `test/` (не `llm_skills/`). `pre-commit install` из `llm_skills/` ставит хук с конфигом `llm_skills/.pre-commit-config.yaml`.

## Запуск

### Тесты

```bash
uv run pytest
```

### Линтеры и формат

```bash
uv run ruff check .
uv run black .
uv run mypy src
```

### Pre-commit (все хуки вручную)

```bash
uv run pre-commit run --all-files
```

На `git commit` автоматически: ruff → black → mypy → unit tests.

### API

```bash
uv run uvicorn src.presentation.fastapi.app:create_app --factory --reload
```

### CLI (экспорт протокола в Word)

```bash
uv run python -m src.presentation.cli.export_protocol --in examples/notes_to_protocol.md --out protocol.docx
```
