"""Template flashcards from weak comprehension checkpoints."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from phraseframe.db.store import FlashcardRecord, LibraryStore
from phraseframe.services.checkpoints import CheckpointAnswer, CheckpointQuestion


@dataclass(frozen=True, slots=True)
class ReviewSchedule:
    due_at: str
    interval: int
    ease_factor: float
    repetitions: int


class ReviewService:
    """Generate flashcards and schedule later review."""

    def create_from_weak_checkpoint(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        checkpoint_id: str,
        questions: tuple[CheckpointQuestion, ...],
        answers: list[CheckpointAnswer],
        summary: str | None = None,
    ) -> int:
        cards: list[tuple[str, str]] = []
        for question, answer in zip(questions, answers, strict=False):
            if not answer.text.strip():
                continue
            preview = question.text[:100].rstrip()
            if len(question.text) > 100:
                preview += "…"
            cards.append((preview, answer.text.strip()))
            if len(cards) >= (3 if summary else 4):
                break

        if summary and len(cards) < 4:
            cards.append(("Passage summary", summary))

        if not cards:
            return 0

        created = store.save_flashcards(user_id, document_id, checkpoint_id, cards[:4])
        return len(created)

    def grade_card(
        self,
        grade: str,
        card: FlashcardRecord,
        *,
        now: datetime | None = None,
    ) -> ReviewSchedule:
        reviewed_at = now or datetime.now(tz=UTC)
        if grade == "again":
            interval = 1
            repetitions = 0
            ease_factor = max(1.3, card.ease_factor - 0.2)
        elif grade == "got_it":
            repetitions = card.repetitions + 1
            ease_factor = card.ease_factor
            if repetitions == 1:
                interval = 1
            elif repetitions == 2:
                interval = 6
            else:
                interval = max(1, round(card.interval * ease_factor))
        else:
            raise ValueError("Grade must be 'got_it' or 'again'.")
        return ReviewSchedule(
            due_at=(reviewed_at + timedelta(days=interval)).isoformat(),
            interval=interval,
            ease_factor=round(ease_factor, 2),
            repetitions=repetitions,
        )

    def review_card(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        flashcard_id: str,
        grade: str,
    ) -> FlashcardRecord:
        card = next(
            (
                candidate
                for candidate in store.list_flashcards(user_id, document_id)
                if candidate.id == flashcard_id
            ),
            None,
        )
        if card is None:
            raise ValueError("Flashcard not found.")
        schedule = self.grade_card(grade, card)
        return store.update_flashcard_due(
            user_id,
            document_id,
            flashcard_id,
            due_at=schedule.due_at,
            interval=schedule.interval,
            ease_factor=schedule.ease_factor,
            repetitions=schedule.repetitions,
        )
