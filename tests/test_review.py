"""Unit tests for weak-checkpoint flashcard generation."""

from pathlib import Path

import pytest

from phraseframe.db.store import LibraryStore
from phraseframe.services.checkpoints import CheckpointAnswer, CheckpointQuestion
from phraseframe.services.review import ReviewService


@pytest.fixture
def store(tmp_path: Path) -> LibraryStore:
    library = LibraryStore(db_path=tmp_path / "review.db", storage_path=tmp_path / "docs")
    library.init_schema()
    return library


def test_create_from_weak_checkpoint_uses_only_answered_questions(store: LibraryStore) -> None:
    user = store.create_user("review@example.com", "secret-pass")
    document = store.save_document(user.id, "notes.txt", "Notes", "txt", b"Sample text.")
    checkpoint = store.save_checkpoint(
        user.id,
        document.id,
        frame_index=5,
        questions_json="[]",
    )
    service = ReviewService()
    questions = (
        CheckpointQuestion(
            id="literal",
            text="What specific point does this passage make?",
            type="literal",
        ),
        CheckpointQuestion(
            id="inferential",
            text="What might this passage imply?",
            type="inferential",
        ),
        CheckpointQuestion(
            id="connection",
            text="How does this connect to earlier ideas?",
            type="connection",
        ),
    )
    answers = [
        CheckpointAnswer(text="Attention is limited.", confidence="unsure"),
        CheckpointAnswer(text="Focus matters for comprehension.", confidence="sure"),
        CheckpointAnswer(text="", confidence="no_idea"),
    ]

    created = service.create_from_weak_checkpoint(
        store,
        user.id,
        document.id,
        checkpoint_id=checkpoint.id,
        questions=questions,
        answers=answers,
    )

    assert created == 2
    cards = store.list_flashcards(user.id, document.id)
    assert len(cards) == 2
    assert cards[0].front
    assert cards[0].back == "Attention is limited."
    assert len({card.back for card in cards}) == 2


def test_new_cards_are_due_immediately_and_checkpoint_generation_is_idempotent(
    store: LibraryStore,
) -> None:
    user = store.create_user("immediate@example.com", "secret-pass")
    document = store.save_document(user.id, "notes.txt", "Notes", "txt", b"Sample text.")
    checkpoint = store.save_checkpoint(
        user.id,
        document.id,
        frame_index=7,
        questions_json="[]",
    )
    questions = (CheckpointQuestion(id="literal", text="What happened?", type="literal"),)
    answers = [CheckpointAnswer(text="Attention narrowed.", confidence="unsure")]
    service = ReviewService()

    first = service.create_from_weak_checkpoint(
        store,
        user.id,
        document.id,
        checkpoint_id=checkpoint.id,
        questions=questions,
        answers=answers,
    )
    repeated = service.create_from_weak_checkpoint(
        store,
        user.id,
        document.id,
        checkpoint_id=checkpoint.id,
        questions=questions,
        answers=answers,
    )

    assert first == 1
    assert repeated == 0
    assert len(store.list_flashcards(user.id, document.id)) == 1
    due = store.list_due_flashcards(user.id)
    assert len(due) == 1
    assert due[0].source_frame_index == 7


def test_create_from_weak_checkpoint_returns_zero_without_answers(store: LibraryStore) -> None:
    user = store.create_user("empty@example.com", "secret-pass")
    document = store.save_document(user.id, "notes.txt", "Notes", "txt", b"Sample text.")
    checkpoint = store.save_checkpoint(
        user.id,
        document.id,
        frame_index=2,
        questions_json="[]",
    )
    service = ReviewService()
    questions = (CheckpointQuestion(id="literal", text="What happened?", type="literal"),)

    created = service.create_from_weak_checkpoint(
        store,
        user.id,
        document.id,
        checkpoint_id=checkpoint.id,
        questions=questions,
        answers=[CheckpointAnswer(text="", confidence="no_idea")],
    )

    assert created == 0
    assert store.list_flashcards(user.id, document.id) == []


def test_summary_is_added_as_at_most_fourth_card(store: LibraryStore) -> None:
    user = store.create_user("summary@example.com", "secret-pass")
    document = store.save_document(user.id, "notes.txt", "Notes", "txt", b"Sample text.")
    checkpoint = store.save_checkpoint(
        user.id,
        document.id,
        frame_index=3,
        questions_json="[]",
    )
    questions = tuple(
        CheckpointQuestion(id=str(index), text=f"Question {index}", type="inferential")
        for index in range(5)
    )
    answers = [CheckpointAnswer(text=f"Answer {index}", confidence="unsure") for index in range(5)]

    created = ReviewService().create_from_weak_checkpoint(
        store,
        user.id,
        document.id,
        checkpoint_id=checkpoint.id,
        questions=questions,
        answers=answers,
        summary="The passage has one central claim.",
    )

    cards = store.list_flashcards(user.id, document.id)
    assert created == 4
    assert [card.back for card in cards[:3]] == ["Answer 0", "Answer 1", "Answer 2"]
    assert cards[3].front == "Passage summary"
    assert cards[3].back == "The passage has one central claim."


def test_sm2_progression_and_again_reset(store: LibraryStore) -> None:
    user = store.create_user("schedule@example.com", "secret-pass")
    document = store.save_document(user.id, "notes.txt", "Notes", "txt", b"Sample text.")
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
    service = ReviewService()

    first = service.review_card(store, user.id, document.id, card.id, "got_it")
    second = service.review_card(store, user.id, document.id, card.id, "got_it")
    third = service.review_card(store, user.id, document.id, card.id, "got_it")
    reset = service.review_card(store, user.id, document.id, card.id, "again")

    assert (first.interval, first.repetitions) == (1, 1)
    assert (second.interval, second.repetitions) == (6, 2)
    assert (third.interval, third.repetitions) == (15, 3)
    assert (reset.interval, reset.repetitions) == (1, 0)
    assert reset.ease_factor == pytest.approx(2.3)
