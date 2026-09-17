import shutil
import threading
from pathlib import Path

import pytest

from src.core.application.skill.services import SkillRegistryService
from src.core.domain.skill.entities import SkillMeta

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "skills"


@pytest.fixture
def skills_dir(tmp_path: Path) -> Path:
    shutil.copytree(FIXTURES, tmp_path / "skills")
    return tmp_path / "skills"


@pytest.fixture
def registry(skills_dir: Path) -> SkillRegistryService:
    reg = SkillRegistryService(skills_dir)
    reg.load()
    return reg


def test_valid_skill_loaded_with_files(registry: SkillRegistryService) -> None:
    skills = registry.list_skills()
    assert len(skills) == 1

    skill = skills[0]
    assert skill.name == "valid-skill"
    assert skill.caption == "Валидный скилл"
    assert "unit-тестов" in skill.description
    assert skill.has_files is True


@pytest.mark.parametrize(
    ("skill_dir", "warning_fragment"),
    [
        ("bad-name", "kebab-case"),
        ("empty-body", "пустым"),
        ("long-description", "1024"),
    ],
)
def test_invalid_skills_skipped_with_warning(
    skills_dir: Path,
    skill_dir: str,
    warning_fragment: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("WARNING", logger="src.infra.skill.filesystem_repo")

    registry = SkillRegistryService(skills_dir)
    registry.load()

    names = {skill.name for skill in registry.list_skills()}
    assert skill_dir not in names
    assert any(warning_fragment in record.message for record in caplog.records)


def test_directory_without_skill_file_is_skipped(
    registry: SkillRegistryService,
) -> None:
    names = {skill.name for skill in registry.list_skills()}
    assert "no-skill-file" not in names


def test_reload_updates_snapshot(skills_dir: Path) -> None:
    registry = SkillRegistryService(skills_dir)
    registry.load()
    assert len(registry.list_skills()) == 1

    new_skill_dir = skills_dir / "added-skill"
    new_skill_dir.mkdir()
    (new_skill_dir / "SKILL.md").write_text(
        """\
---
name: added-skill
description: Скилл, добавленный после первой загрузки.
caption: Новый скилл
---

Инструкции нового скила.
""",
        encoding="utf-8",
    )

    registry.reload()
    names = {skill.name for skill in registry.list_skills()}
    assert names == {"valid-skill", "added-skill"}


def test_search_by_name_and_caption(registry: SkillRegistryService) -> None:
    assert len(registry.search("valid")) == 1
    assert registry.search("valid")[0].name == "valid-skill"

    assert len(registry.search("Валидный")) == 1
    assert registry.search("ВАЛИДНЫЙ")[0].caption == "Валидный скилл"

    assert registry.search("missing") == ()
    assert registry.search(None) == registry.list_skills()
    assert registry.search("") == registry.list_skills()


def test_concurrent_read_during_reload(skills_dir: Path) -> None:
    registry = SkillRegistryService(skills_dir)
    registry.load()

    errors: list[Exception] = []
    seen_counts: set[int] = set()
    barrier = threading.Barrier(6)

    def reader() -> None:
        try:
            barrier.wait(timeout=5)
            for _ in range(200):
                skills = registry.list_skills()
                seen_counts.add(len(skills))
                for skill in skills:
                    assert isinstance(skill, SkillMeta)
        except Exception as exc:
            errors.append(exc)

    def reloader() -> None:
        try:
            barrier.wait(timeout=5)
            for i in range(50):
                skill_dir = skills_dir / f"temp-skill-{i}"
                skill_dir.mkdir(exist_ok=True)
                skill_path = skill_dir / "SKILL.md"
                skill_path.write_text(
                    f"""\
---
name: temp-skill-{i}
description: Временный скилл для concurrent-теста.
caption: Temp {i}
---

Тело временного скила.
""",
                    encoding="utf-8",
                )
                registry.reload()
                skill_path.unlink(missing_ok=True)
                skill_dir.rmdir()
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=reader) for _ in range(5)]
    threads.append(threading.Thread(target=reloader))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert not errors
    assert seen_counts <= {1, 2}
