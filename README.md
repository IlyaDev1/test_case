# LLM Skills

Тестовое задание: скил для протоколов встреч, парсер markdown-протокола, экспорт в Word и реестр скилов.

## Структура и слои

```
src/
  core/
    domain/       # сущности, правила валидации, доменные исключения
    application/  # use cases, сервисы приложения, Result
  infra/          # docx-экспорт, загрузчик скилов с диска, DI (dishka)
  presentation/   # FastAPI-роутеры, CLI
skills/           # артефакты скилов (SKILL.md, references/, routes/)
tests/
```

Слои повторяют подход `chatbot_to`: тонкие роутеры, use case + service + `Result`, без БД.

| Слой | Зачем |
|------|-------|
| **domain** | Чистые модели (`MeetingProtocol`, `SkillMeta`) и правила — без зависимостей от FastAPI, docx и файловой системы. |
| **application** | Оркестрация: `ParseProtocolUC`, `ExportProtocolToDocxUC`, `SkillRegistryService`. Возвращает `SuccessResult` / `FailResult`, не бросает HTTP-исключения. |
| **infra** | Конкретные адаптеры: `DocxProtocolExporterService`, `FilesystemSkillRepo`, wiring через dishka. |
| **presentation** | HTTP и CLI — только трансляция запроса в DTO и ответа в status code / файл. |

Зависимости направлены внутрь: `presentation → application → domain`, `infra` подключается снаружи через DI.

## Скил `meeting-minutes`

Артефакты: `skills/meeting-minutes/`.

- **`SKILL.md`** — YAML frontmatter (`name`, `caption`, `description`) + системный промпт. Поле `description` — узкий сигнал для классификатора; тело — инструкции модели.
- **`references/`** — справочные материалы, которые модель подтягивает по необходимости. Здесь `protocol_format.md` задаёт жёсткий контракт разделов и таблицы задач, чтобы парсер и Word-экспорт не «догадывались» о формате.
- **`routes/`** — сценарные подсказки для краевых случаев. `ambiguous_fields.md` описывает, как заполнять пропуски (`не указан` / `нет данных`).

Флаг `has_files` в API показывает, что у скила есть дополнительные файлы в `references/` или `routes/`.

Проверка классификатора: `eval_queries.md` (6 trigger / 4 no-trigger). Пример заметки → протокол: `examples/notes_input.md` → `examples/notes_to_protocol.md`.

## Установка

```bash
cd test_case
uv sync --group dev
uv run pre-commit install
```

Секреты (API-ключи и т.п.) храните в `.env` — файл в `.gitignore`, в репозиторий не коммитится.

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

Сервер по умолчанию: `http://127.0.0.1:8000`.

**Health check:**

```bash
curl http://127.0.0.1:8000/health
```

**Список скилов** (опциональный фильтр `q` по `name` и `caption`):

```bash
curl 'http://127.0.0.1:8000/skills'
curl 'http://127.0.0.1:8000/skills?q=протокол'
curl 'http://127.0.0.1:8000/skills?q=meeting'
```

**Экспорт протокола в Word** — тело JSON с полем `text` (markdown протокола):

```bash
curl -X POST http://127.0.0.1:8000/protocol/export \
  -H 'Content-Type: application/json' \
  -d "$(jq -n --rawfile t examples/notes_to_protocol.md '{text: $t}')" \
  -o protocol.docx
```

Без `jq` — передайте markdown вручную:

```bash
curl -X POST http://127.0.0.1:8000/protocol/export \
  -H 'Content-Type: application/json' \
  -d '{"text": "# Протокол встречи\n\n## Метаданные\n..."}' \
  -o protocol.docx
```

При ошибке парсинга — HTTP 422 с описанием. Успешный ответ — файл `.docx` (`Content-Disposition: attachment; filename="protocol.docx"`).

### CLI (экспорт протокола в Word)

```bash
uv run python -m src.presentation.cli.export_protocol \
  --in examples/notes_to_protocol.md \
  --out protocol.docx
```

При ошибке разбора markdown — сообщение в stderr и exit code `1`.
