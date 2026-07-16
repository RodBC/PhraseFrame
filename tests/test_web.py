from pathlib import Path
from unittest.mock import patch

from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from phraseframe.main import app


def test_home_page_contains_reader_and_science() -> None:
    with TestClient(app) as test_client:
        response = test_client.get("/")
    assert response.status_code == 200
    assert "Find your reading cadence" in response.text
    assert "THE EVIDENCE, WITHOUT THE HYPE" in response.text


def test_reader_forces_and_fits_a_single_line() -> None:
    with TestClient(app) as test_client:
        page = test_client.get("/").text
        styles = test_client.get("/static/styles.css").text
        script = test_client.get("/static/app.js").text
    assert "phrase-shell" in page
    assert "overflow-x: clip" in styles
    assert "grid-template-columns: 1fr" in styles
    assert "fitPhraseOnOneLine" in script
    assert "phraseAvailableWidth" in script
    assert "saveProgressNow" in script
    assert "snapshotBody" not in script


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
    assert "stop_frames" in payload
    assert set(payload["frames"][0]) == {
        "index",
        "text",
        "word_count",
        "duration_ms",
        "starts_at_ms",
        "boundary",
    }


def test_timeline_includes_stop_frames_when_configured() -> None:
    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/timeline",
            json={
                "text": " ".join(f"word{i}" for i in range(1, 41)),
                "wpm": 300,
                "stop_every_words": 50,
            },
        )
    payload = response.json()
    assert payload["stop_frames"]
    assert payload["frames"][-1]["index"] in payload["stop_frames"]


def test_timeline_validation_is_user_facing() -> None:
    with TestClient(app) as test_client:
        response = test_client.post("/api/timeline", json={"text": "   "})
    assert response.status_code == 422
    assert response.json()["detail"] == "Add some text before preparing the reader."


def test_upload_extracts_text_and_accepts_pdf() -> None:
    from phraseframe.adapters.pdf import build_sample_pdf

    with TestClient(app) as test_client:
        accepted = test_client.post(
            "/api/extract",
            files={"file": ("notes.txt", "Readable café text.", "text/plain")},
        )
        pdf = test_client.post(
            "/api/extract",
            files={"file": ("notes.pdf", build_sample_pdf(), "application/pdf")},
        )
    assert accepted.json()["text"] == "Readable café text."
    assert accepted.json()["format"] == "txt"
    assert "text" not in accepted.json()["chapters"][0]
    assert pdf.status_code == 200
    assert pdf.json()["format"] == "pdf"
    assert len(pdf.json()["chapters"]) == 2


def test_auth_documents_resume_and_chapter_flow(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "web.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "reader@example.com", "password": "secret-pass"},
        )
        token = register.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        uploaded = test_client.post(
            "/api/documents",
            headers=headers,
            files={"file": ("book.pdf", build_sample_pdf(), "application/pdf")},
        )
        document_id = uploaded.json()["document_id"]
        assert "text" not in uploaded.json()
        chapter = test_client.get(
            f"/api/documents/{document_id}/chapters/1",
            headers=headers,
        )
        saved = test_client.put(
            f"/api/documents/{document_id}/progress",
            headers=headers,
            json={"chapter_index": 1, "frame_index": 7, "wpm": 280, "target_words": 4},
        )
        resumed = test_client.get(f"/api/documents/{document_id}/resume", headers=headers)
        listed = test_client.get("/api/documents", headers=headers)

    assert uploaded.status_code == 200
    assert chapter.status_code == 200
    assert "Each section can be selected" in chapter.json()["text"]
    assert saved.status_code == 200
    assert resumed.status_code == 200
    payload = resumed.json()
    assert payload["progress"]["frame_index"] == 7
    assert payload["progress"]["chapter_index"] == 1
    assert "Each section can be selected" in payload["text"]
    assert listed.json()["documents"][0]["has_progress"] is True


def test_checkpoint_endpoint_creates_and_saves_answers(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "checkpoint.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "checkpoint@example.com", "password": "secret-pass"},
        )
        headers = {"Authorization": f"Bearer {register.json()['token']}"}
        uploaded = test_client.post(
            "/api/documents",
            headers=headers,
            files={"file": ("book.pdf", build_sample_pdf(), "application/pdf")},
        )
        document_id = uploaded.json()["document_id"]
        created = test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={"frame_index": 12, "snippet": "A focused passage about attention."},
        )
        checkpoint_id = created.json()["checkpoint_id"]
        saved = test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={
                "frame_index": 12,
                "snippet": "A focused passage about attention.",
                "checkpoint_id": checkpoint_id,
                "answers": ["Main idea", "Implication", "Connection"],
            },
        )

    assert created.status_code == 200
    assert len(created.json()["questions"]) == 3
    assert saved.status_code == 200
    assert saved.json()["saved"] is True


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
