from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from phraseframe.main import app


def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_home_page_contains_reader_and_science() -> None:
    with TestClient(app) as test_client:
        response = test_client.get("/")
    assert response.status_code == 200
    assert "Find your reading cadence" in response.text
    assert "THE EVIDENCE, WITHOUT THE HYPE" in response.text


def test_timeline_endpoint_returns_shared_timing_contract() -> None:
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/timeline",
            json={"text": "A clear phrase, followed by another.", "wpm": 300},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["word_count"] == 6
    assert payload["duration_ms"] > 1200
    assert set(payload["frames"][0]) == {
        "index",
        "text",
        "word_count",
        "duration_ms",
        "starts_at_ms",
        "boundary",
    }


def test_timeline_validation_is_user_facing() -> None:
    with TestClient(app) as test_client:
        response = test_client.post("/api/timeline", json={"text": "   "})
    assert response.status_code == 422
    assert response.json()["detail"] == "Add some text before preparing the reader."


def test_upload_extracts_text_and_rejects_pdf() -> None:
    with TestClient(app) as test_client:
        accepted = test_client.post(
            "/api/extract",
            files={"file": ("notes.txt", "Readable café text.", "text/plain")},
        )
        rejected = test_client.post(
            "/api/extract",
            files={"file": ("notes.pdf", b"%PDF", "application/pdf")},
        )
    assert accepted.json() == {"text": "Readable café text."}
    assert rejected.status_code == 422
    assert "Only .txt" in rejected.json()["detail"]


def test_export_returns_and_cleans_generated_file(tmp_path: Path) -> None:
    output = tmp_path / "generated.mp4"
    rendered_path: Path | None = None

    def fake_render(_timeline: object, output_path: Path) -> Path:
        nonlocal rendered_path
        rendered_path = output_path
        output_path.write_bytes(b"fake mp4")
        output.write_bytes(output_path.read_bytes())
        return output_path

    with (
        patch("phraseframe.web.routes.renderer.render", side_effect=fake_render),
        TestClient(app) as test_client,
    ):
        response = test_client.post("/api/export", json={"text": "A tiny export test."})
    assert response.status_code == 200
    assert response.headers["content-type"] == "video/mp4"
    assert response.content == b"fake mp4"
    assert output.exists()
    assert rendered_path is not None
    assert not rendered_path.exists()


def test_invalid_settings_return_validation_error() -> None:
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/timeline",
            json={"text": "Words exist.", "target_words": 8, "max_words": 4},
        )
    assert response.status_code == 422
    assert "Chunk sizes" in response.json()["detail"]
