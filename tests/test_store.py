import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from phraseframe.adapters.pdf import build_sample_pdf
from phraseframe.db.store import LibraryStore


@pytest.fixture
def store(tmp_path: Path) -> LibraryStore:
    library = LibraryStore(db_path=tmp_path / "test.db", storage_path=tmp_path / "docs")
    library.init_schema()
    return library


def test_user_registration_and_authentication(store: LibraryStore) -> None:
    created = store.create_user("reader@example.com", "secret-pass")
    assert created.email == "reader@example.com"
    authenticated = store.authenticate("reader@example.com", "secret-pass")
    assert authenticated.id == created.id
    with pytest.raises(ValueError, match="incorrect"):
        store.authenticate("reader@example.com", "wrong-pass")


def test_document_upload_and_progress(store: LibraryStore) -> None:
    user = store.create_user("reader@example.com", "secret-pass")
    content = build_sample_pdf()
    document = store.save_document(user.id, "book.pdf", "Think", "pdf", content)
    listed = store.list_documents_with_progress(user.id)
    assert len(listed) == 1
    assert listed[0].title == "Think"
    assert listed[0].has_progress is False
    progress = store.save_progress(
        user.id,
        document.id,
        chapter_index=1,
        frame_index=42,
        wpm=280,
        target_words=4,
        stop_every_words=500,
    )
    assert progress.frame_index == 42
    assert progress.stop_every_words == 500
    resumed = store.get_progress(user.id, document.id)
    assert resumed is not None
    assert resumed.chapter_index == 1
    assert store.read_document_bytes(user.id, document.id) == content
    with_progress = store.list_documents_with_progress(user.id)
    assert with_progress[0].has_progress is True


def test_library_summary_and_due_queue_span_documents(store: LibraryStore) -> None:
    user = store.create_user("dashboard@example.com", "secret-pass")
    first = store.save_document(user.id, "one.txt", "One", "txt", b"One")
    second = store.save_document(user.id, "two.txt", "Two", "txt", b"Two")
    store.save_progress(
        user.id,
        first.id,
        chapter_index=0,
        frame_index=4,
        wpm=300,
        target_words=4,
    )
    checkpoint = store.save_checkpoint(
        user.id,
        second.id,
        frame_index=2,
        questions_json="[]",
    )
    store.save_checkpoint(
        user.id,
        second.id,
        frame_index=2,
        questions_json="[]",
        answers_json="[]",
        score=0.75,
        weak=True,
        checkpoint_id=checkpoint.id,
    )
    card = store.save_flashcards(
        user.id,
        second.id,
        checkpoint.id,
        [("Question", "Answer")],
    )[0]
    past = (datetime.now(tz=UTC) - timedelta(minutes=1)).isoformat()
    store.update_flashcard_due(user.id, second.id, card.id, due_at=past)

    summary = store.library_summary(user.id)
    queue = store.list_due_flashcards(user.id)

    assert summary.pending_flashcards == 1
    assert summary.average_comprehension == pytest.approx(0.75)
    assert summary.weak_stop_count == 1
    assert summary.last_read_at is not None
    assert len(queue) == 1
    assert queue[0].card.document_id == second.id
    assert queue[0].document_title == "Two"
    assert queue[0].source_frame_index == 2


def test_store_enables_wal_and_busy_timeout(store: LibraryStore) -> None:
    with sqlite3.connect(store.db_path) as connection:
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        busy_timeout = connection.execute("PRAGMA busy_timeout").fetchone()[0]
    assert journal_mode == "wal"
    assert busy_timeout >= 5000


def test_flashcard_schedule_columns_migrate_existing_database(tmp_path: Path) -> None:
    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE flashcards (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                checkpoint_id TEXT NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                due_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
    migrated = LibraryStore(db_path=db_path, storage_path=tmp_path / "docs")
    migrated.init_schema()
    with sqlite3.connect(db_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(flashcards)")}
    assert {"interval", "ease_factor", "repetitions"} <= columns
