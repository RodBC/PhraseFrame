from pathlib import Path

import pytest

from phraseframe.db.store import LibraryStore
from phraseframe.services.analytics import DEEP_PACE_MIN_SAMPLES, AnalyticsService


@pytest.fixture
def store(tmp_path: Path) -> LibraryStore:
    library = LibraryStore(db_path=tmp_path / "test.db", storage_path=tmp_path / "docs")
    library.init_schema()
    return library


def test_learning_events_store_no_text(store: LibraryStore) -> None:
    user = store.create_user("reader@example.com", "secret-pass")
    document = store.save_document(user.id, "book.txt", "Book", "txt", b"Sample text")
    store.record_learning_event(
        user.id,
        "checkpoint_submit",
        document_id=document.id,
        frame_index=3,
        wpm=300,
        self_check_score=0.72,
    )
    with store._connect() as connection:
        row = connection.execute(
            "SELECT event_type, wpm, self_check_score FROM learning_events WHERE user_id = ?",
            (user.id,),
        ).fetchone()
        columns = {
            item[1] for item in connection.execute("PRAGMA table_info(learning_events)").fetchall()
        }
    assert row is not None
    assert row["event_type"] == "checkpoint_submit"
    assert row["wpm"] == 300
    assert row["self_check_score"] == pytest.approx(0.72)
    assert "front" not in columns
    assert "answer_text" not in columns


def test_deep_pace_requires_minimum_samples(store: LibraryStore) -> None:
    user = store.create_user("pace@example.com", "secret-pass")
    document = store.save_document(user.id, "one.txt", "One", "txt", b"One")
    store.save_progress(
        user.id,
        document.id,
        chapter_index=0,
        frame_index=1,
        wpm=300,
        target_words=4,
    )
    checkpoint = store.save_checkpoint(user.id, document.id, frame_index=1, questions_json="[]")
    store.save_checkpoint(
        user.id,
        document.id,
        frame_index=1,
        questions_json="[]",
        answers_json="[]",
        score=0.8,
        weak=False,
        checkpoint_id=checkpoint.id,
    )
    service = AnalyticsService()
    result = service.deep_pace(store, user.id)
    assert result.wpm is None
    assert result.sample_count < DEEP_PACE_MIN_SAMPLES
    assert "Not enough checks yet" in result.message


def test_deep_pace_picks_highest_qualifying_band(store: LibraryStore) -> None:
    user = store.create_user("pace2@example.com", "secret-pass")
    document = store.save_document(user.id, "two.txt", "Two", "txt", b"Two")
    store.save_progress(
        user.id,
        document.id,
        chapter_index=0,
        frame_index=1,
        wpm=280,
        target_words=4,
    )
    for index in range(DEEP_PACE_MIN_SAMPLES):
        checkpoint = store.save_checkpoint(
            user.id,
            document.id,
            frame_index=index,
            questions_json="[]",
        )
        store.save_checkpoint(
            user.id,
            document.id,
            frame_index=index,
            questions_json="[]",
            answers_json="[]",
            score=0.75,
            weak=False,
            checkpoint_id=checkpoint.id,
        )
    service = AnalyticsService()
    result = service.deep_pace(store, user.id)
    assert result.wpm == 280
    assert result.sample_count >= DEEP_PACE_MIN_SAMPLES


def test_aggregate_summary_exposes_rates(store: LibraryStore) -> None:
    user = store.create_user("agg@example.com", "secret-pass")
    document = store.save_document(user.id, "three.txt", "Three", "txt", b"Three")
    store.record_learning_event(
        user.id,
        "review_grade",
        document_id=document.id,
        card_grade="again",
        due_interval=1,
    )
    store.record_learning_event(
        user.id,
        "review_grade",
        document_id=document.id,
        card_grade="got_it",
        due_interval=3,
    )
    summary = AnalyticsService().aggregate_summary(store, user.id)
    assert summary["again_rate"] == pytest.approx(0.5)
    assert "deep_pace_message" in summary
