import os
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi.testclient import TestClient

from phraseframe.main import app


def test_home_page_contains_reader_and_science() -> None:
    with TestClient(app) as test_client:
        response = test_client.get("/")
    assert response.status_code == 200
    assert "Read with focus. Check what stuck. Keep it." in response.text
    assert "THE EVIDENCE, WITHOUT THE HYPE" in response.text
    assert "Revisar" not in response.text
    assert 'id="attention-loop"' in response.text
    assert 'id="demo-guide"' in response.text
    assert 'id="checkpoint-recall"' in response.text
    assert 'id="stop-every-words"' in response.text
    assert 'value="200"' in response.text


def test_health_endpoint() -> None:
    with TestClient(app) as test_client:
        response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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
    assert "refreshWeakStops" in script
    assert "gradeReviewCard" in script
    assert "manual-checkpoint-button" in page
    assert "weak-stops-panel" in page
    assert "saveProgressNow" in script
    assert "renderRecallMoment" in script
    assert "returnToSourcePassage" in script
    assert 'state.checkpointPhase === "results"' in script
    assert "snapshotBody" not in script
    assert "refreshLibrary()" not in script.split("async function saveProgressNow")[1].split("}")[0]


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
        chapter = test_client.get(
            f"/api/documents/{document_id}/chapters/1",
            headers=headers,
        )
        saved = test_client.put(
            f"/api/documents/{document_id}/progress",
            headers=headers,
            json={
                "chapter_index": 1,
                "frame_index": 7,
                "wpm": 280,
                "target_words": 4,
                "stop_every_words": 800,
            },
        )
        setting_only = test_client.put(
            f"/api/documents/{document_id}/progress",
            headers=headers,
            json={
                "chapter_index": 1,
                "frame_index": 7,
                "wpm": 260,
                "target_words": 5,
                "stop_every_words": 200,
            },
        )
        resumed = test_client.get(f"/api/documents/{document_id}/resume", headers=headers)
        listed = test_client.get("/api/documents", headers=headers)
        summary = test_client.get("/api/library/summary", headers=headers)

    assert uploaded.status_code == 200
    assert "Chapter One" in uploaded.json()["text"]
    assert chapter.status_code == 200
    assert "Each section can be selected" in chapter.json()["text"]
    assert saved.status_code == 200
    assert saved.json()["progress"]["stop_every_words"] == 800
    assert setting_only.status_code == 200
    assert resumed.status_code == 200
    payload = resumed.json()
    assert payload["progress"]["frame_index"] == 7
    assert payload["progress"]["chapter_index"] == 1
    assert payload["progress"]["wpm"] == 260
    assert payload["progress"]["target_words"] == 5
    assert payload["progress"]["stop_every_words"] == 200
    assert "Each section can be selected" in payload["text"]
    assert listed.json()["documents"][0]["has_progress"] is True
    assert summary.status_code == 200
    assert summary.json()["pending_flashcards"] == 0
    assert summary.json()["last_read_at"] is not None
    user = store.authenticate("reader@example.com", "secret-pass")
    assert store.read_chapters_meta(user.id, document_id) is not None


def test_chapter_index_out_of_range_is_user_facing(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "bounds.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "bounds@example.com", "password": "secret-pass"},
        )
        headers = {"Authorization": f"Bearer {register.json()['token']}"}
        uploaded = test_client.post(
            "/api/documents",
            headers=headers,
            files={"file": ("notes.txt", b"Only one chapter.", "text/plain")},
        )
        response = test_client.get(
            f"/api/documents/{uploaded.json()['document_id']}/chapters/99",
            headers=headers,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chapter index is out of range."


def test_upload_writes_chapter_cache(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "cache.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "cache@example.com", "password": "secret-pass"},
        )
        headers = {"Authorization": f"Bearer {register.json()['token']}"}
        uploaded = test_client.post(
            "/api/documents",
            headers=headers,
            files={"file": ("book.pdf", build_sample_pdf(), "application/pdf")},
        )
        document_id = uploaded.json()["document_id"]

    user = store.authenticate("cache@example.com", "secret-pass")
    meta = store.read_chapters_meta(user.id, document_id)
    text = store.read_chapter_text(user.id, document_id, 0)
    assert meta is not None
    assert len(meta) == 2
    assert text is not None
    assert "PhraseFrame" in text


def test_checkpoint_endpoint_creates_scores_and_flashcards(
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
            json={"frame_index": 12, "chapter_index": 0},
        )
        checkpoint_id = created.json()["checkpoint_id"]
        saved = test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={
                "frame_index": 12,
                "chapter_index": 0,
                "checkpoint_id": checkpoint_id,
                "answers": [
                    {"text": "", "confidence": "no_idea"},
                    {"text": "Maybe", "confidence": "unsure"},
                    {"text": "Earlier ideas", "confidence": "unsure"},
                ],
            },
        )
        history = test_client.get(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
        )
        flashcards = test_client.get(
            f"/api/documents/{document_id}/flashcards",
            headers=headers,
        )
        review_queue = test_client.get("/api/review/queue", headers=headers)
        summary = test_client.get("/api/library/summary", headers=headers)

    assert created.status_code == 200
    assert len(created.json()["questions"]) == 3
    assert saved.status_code == 200
    saved_payload = saved.json()
    assert saved_payload["weak"] is True
    assert saved_payload["score"] < 0.67
    assert saved_payload["feedback"]
    assert saved_payload["flashcards_added"] >= 1
    assert history.status_code == 200
    assert len(history.json()["checkpoints"]) == 1
    assert flashcards.status_code == 200
    assert len(flashcards.json()["flashcards"]) >= 1
    assert review_queue.status_code == 200
    assert review_queue.json()["flashcards"][0]["frame_index"] == 12
    assert summary.json()["weak_stop_count"] == 1


def test_checkpoint_answer_requires_checkpoint_id(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "checkpoint-id.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "missing-id@example.com", "password": "secret-pass"},
        )
        headers = {"Authorization": f"Bearer {register.json()['token']}"}
        uploaded = test_client.post(
            "/api/documents",
            headers=headers,
            files={"file": ("book.pdf", build_sample_pdf(), "application/pdf")},
        )
        document_id = uploaded.json()["document_id"]
        response = test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={
                "frame_index": 3,
                "chapter_index": 0,
                "answers": [{"text": "Answer", "confidence": "sure"}],
            },
        )

    assert response.status_code == 422


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


def test_production_startup_provisions_secret(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.main import _configure_production_secret

    monkeypatch.setenv("PHRASEFRAME_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.delenv("PHRASEFRAME_SECRET_KEY", raising=False)
    _configure_production_secret()
    assert os.environ["PHRASEFRAME_SECRET_KEY"]
    assert (tmp_path / ".secret_key").read_text().strip() == os.environ["PHRASEFRAME_SECRET_KEY"]

    monkeypatch.delenv("PHRASEFRAME_SECRET_KEY", raising=False)
    _configure_production_secret()
    assert os.environ["PHRASEFRAME_SECRET_KEY"] == (tmp_path / ".secret_key").read_text().strip()


def test_production_startup_respects_explicit_secret(monkeypatch: MonkeyPatch) -> None:
    from phraseframe.main import _configure_production_secret

    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("PHRASEFRAME_SECRET_KEY", "render-dashboard-secret")
    _configure_production_secret()
    assert os.environ["PHRASEFRAME_SECRET_KEY"] == "render-dashboard-secret"


def test_flashcard_review_reschedules_due_date(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "review-flash.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "flash@example.com", "password": "secret-pass"},
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
            json={"frame_index": 8, "chapter_index": 0},
        )
        checkpoint_id = created.json()["checkpoint_id"]
        test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={
                "frame_index": 8,
                "chapter_index": 0,
                "checkpoint_id": checkpoint_id,
                "answers": [
                    {"text": "", "confidence": "no_idea"},
                    {"text": "Maybe", "confidence": "unsure"},
                    {"text": "Earlier ideas", "confidence": "unsure"},
                ],
            },
        )
        cards = test_client.get(
            f"/api/documents/{document_id}/flashcards",
            headers=headers,
        ).json()["flashcards"]
        reviewed = test_client.post(
            f"/api/documents/{document_id}/flashcards/{cards[0]['id']}/review",
            headers=headers,
            json={"grade": "got_it"},
        )

    assert reviewed.status_code == 200
    assert reviewed.json()["grade"] == "got_it"
    assert reviewed.json()["due_at"] > cards[0]["due_at"]
    assert reviewed.json()["interval"] == 1
    assert reviewed.json()["repetitions"] == 1


def test_weak_checkpoint_returns_summary_and_gaps(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from phraseframe.adapters.pdf import build_sample_pdf
    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "summary.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "summary@example.com", "password": "secret-pass"},
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
            json={"frame_index": 10, "chapter_index": 0},
        )
        checkpoint_id = created.json()["checkpoint_id"]
        saved = test_client.post(
            f"/api/documents/{document_id}/checkpoints",
            headers=headers,
            json={
                "frame_index": 10,
                "chapter_index": 0,
                "checkpoint_id": checkpoint_id,
                "answers": [
                    {"text": "", "confidence": "no_idea"},
                    {"text": "Maybe", "confidence": "unsure"},
                    {"text": "Earlier ideas", "confidence": "unsure"},
                ],
            },
        )

    payload = saved.json()
    assert payload["weak"] is True
    assert payload["summary"]
    assert payload["gaps"]
    assert any(gap["reason"] == "empty_answer" for gap in payload["gaps"])
    assert all(gap["question_text"] for gap in payload["gaps"])


def test_review_queue_returns_due_cards_with_document_identity(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    from datetime import UTC, datetime, timedelta

    from phraseframe.db.store import LibraryStore

    store = LibraryStore(db_path=tmp_path / "queue.db", storage_path=tmp_path / "docs")
    store.init_schema()
    monkeypatch.setattr("phraseframe.main.LibraryStore.from_env", lambda: store)

    with TestClient(app) as test_client:
        register = test_client.post(
            "/api/auth/register",
            json={"email": "queue@example.com", "password": "secret-pass"},
        )
        headers = {"Authorization": f"Bearer {register.json()['token']}"}
        user = store.authenticate("queue@example.com", "secret-pass")
        document = store.save_document(user.id, "notes.txt", "Queue Notes", "txt", b"Notes")
        checkpoint = store.save_checkpoint(
            user.id,
            document.id,
            frame_index=1,
            questions_json="[]",
        )
        card = store.save_flashcards(
            user.id,
            document.id,
            checkpoint.id,
            [("Front", "Back")],
        )[0]
        store.update_flashcard_due(
            user.id,
            document.id,
            card.id,
            due_at=(datetime.now(tz=UTC) - timedelta(minutes=1)).isoformat(),
        )
        response = test_client.get("/api/review/queue", headers=headers)

    assert response.status_code == 200
    queued = response.json()["flashcards"]
    assert len(queued) == 1
    assert queued[0]["document_id"] == document.id
    assert queued[0]["document_title"] == "Queue Notes"
    assert queued[0]["frame_index"] == 1


def test_guest_checkpoint_preview_is_stateless() -> None:
    text = "Attention is limited. Reading needs focus and honest recall checks at stop points."
    with TestClient(app) as test_client:
        create = test_client.post(
            "/api/checkpoints/preview",
            json={"text": text, "frame_index": 2, "wpm": 300, "target_words": 4},
        )
        assert create.status_code == 200
        questions = create.json()["questions"]
        submit = test_client.post(
            "/api/checkpoints/preview",
            json={
                "text": text,
                "frame_index": 2,
                "wpm": 300,
                "target_words": 4,
                "questions": questions,
                "answers": [{"text": "Focus matters for comprehension.", "confidence": "sure"}],
            },
        )
    payload = submit.json()
    assert payload["preview"] is True
    assert "score" in payload
    assert payload["flashcards_added"] == 0
    assert "sign_in_hint" in payload


def test_analytics_summary_requires_auth() -> None:
    with TestClient(app) as test_client:
        denied = test_client.get("/api/analytics/summary")
        assert denied.status_code == 401
        register = test_client.post(
            "/api/auth/register",
            json={"email": "metrics-analytics@example.com", "password": "secret-pass"},
        )
        assert register.status_code == 200, register.text
        token = register.json()["token"]
        response = test_client.get(
            "/api/analytics/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    payload = response.json()
    assert "deep_pace_message" in payload
    assert "wpm_band_scores" in payload
