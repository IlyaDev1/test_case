from fastapi.testclient import TestClient

from src.presentation.fastapi.app import create_app


def test_list_all_skills() -> None:
    client = TestClient(create_app())

    response = client.get("/skills")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    meeting = next(skill for skill in data if skill["name"] == "meeting-minutes")
    assert meeting["caption"] == "Протокол встречи"
    assert "протокол" in meeting["description"].lower()
    assert meeting["has_files"] is True


def test_search_skills_by_caption() -> None:
    client = TestClient(create_app())

    response = client.get("/skills", params={"q": "протокол"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "meeting-minutes"
    assert data[0]["caption"] == "Протокол встречи"


def test_search_skills_by_name() -> None:
    client = TestClient(create_app())

    response = client.get("/skills", params={"q": "meeting"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "meeting-minutes"
