"""Comprehension checkpoint generation and persistence."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Protocol

from phraseframe.core.models import ReadingSettings
from phraseframe.db.store import LibraryStore
from phraseframe.services.reader import ReaderService


@dataclass(frozen=True, slots=True)
class CheckpointQuestion:
    id: str
    text: str
    type: str


@dataclass(frozen=True, slots=True)
class CheckpointAnswer:
    text: str
    confidence: str


@dataclass(frozen=True, slots=True)
class CheckpointResult:
    checkpoint_id: str
    frame_index: int
    questions: tuple[CheckpointQuestion, ...]


@dataclass(frozen=True, slots=True)
class CheckpointGap:
    question_id: str
    question_text: str
    reason: str


@dataclass(frozen=True, slots=True)
class CheckpointFeedback:
    checkpoint_id: str
    frame_index: int
    score: float
    weak: bool
    feedback: str
    wpm_adjust: int
    flashcards_added: int
    summary: str | None = None
    gaps: tuple[CheckpointGap, ...] = ()


class WeakCheckpointReview(Protocol):
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
    ) -> int: ...


class CheckpointService:
    """Generate template comprehension questions and store answers."""

    def __init__(self, reader: ReaderService | None = None) -> None:
        self._reader = reader or ReaderService()
        self._cache: dict[str, tuple[CheckpointQuestion, ...]] = {}

    def create_checkpoint(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        frame_index: int,
        chapter_text: str,
        settings: ReadingSettings,
    ) -> CheckpointResult:
        snippet = self._snippet_for_frame(
            store,
            user_id,
            document_id,
            frame_index=frame_index,
            chapter_text=chapter_text,
            settings=settings,
        )
        questions = self._questions_for_snippet(snippet)
        record = store.save_checkpoint(
            user_id,
            document_id,
            frame_index=frame_index,
            questions_json=json.dumps([asdict(question) for question in questions]),
        )
        return CheckpointResult(
            checkpoint_id=record.id,
            frame_index=frame_index,
            questions=questions,
        )

    def save_answers(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        checkpoint_id: str,
        answers: list[CheckpointAnswer],
        chapter_text: str,
        settings: ReadingSettings,
        review_service: WeakCheckpointReview | None = None,
    ) -> CheckpointFeedback:
        checkpoint = store.get_checkpoint(user_id, document_id, checkpoint_id)
        questions = tuple(
            CheckpointQuestion(**item) for item in json.loads(checkpoint.questions_json)
        )
        score, weak, feedback, wpm_adjust = self._score_answers(questions, answers)
        summary: str | None = None
        gaps: tuple[CheckpointGap, ...] = ()
        if weak:
            gaps = self._gaps_from_answers(questions, answers)
            snippet = self._snippet_for_frame(
                store,
                user_id,
                document_id,
                frame_index=checkpoint.frame_index,
                chapter_text=chapter_text,
                settings=settings,
            )
            summary = self._extractive_summary(snippet)
        record = store.save_checkpoint(
            user_id,
            document_id,
            frame_index=checkpoint.frame_index,
            questions_json=checkpoint.questions_json,
            answers_json=json.dumps([asdict(answer) for answer in answers]),
            confidence_json=json.dumps([answer.confidence for answer in answers]),
            score=score,
            weak=weak,
            checkpoint_id=checkpoint_id,
        )
        flashcards_added = 0
        if weak and review_service is not None:
            flashcards_added = review_service.create_from_weak_checkpoint(
                store,
                user_id,
                document_id,
                checkpoint_id=record.id,
                questions=questions,
                answers=answers,
                summary=summary,
            )
        return CheckpointFeedback(
            checkpoint_id=record.id,
            frame_index=record.frame_index,
            score=score,
            weak=weak,
            feedback=feedback,
            wpm_adjust=wpm_adjust,
            flashcards_added=flashcards_added,
            summary=summary,
            gaps=gaps,
        )

    def list_history(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
    ) -> list[dict[str, object]]:
        return [
            {
                "checkpoint_id": record.id,
                "frame_index": record.frame_index,
                "score": record.score,
                "weak": record.weak,
                "answered": record.answers_json is not None,
                "created_at": record.created_at,
            }
            for record in store.list_checkpoints(user_id, document_id)
            if record.score is not None
        ]

    def preview_checkpoint(
        self,
        chapter_text: str,
        *,
        frame_index: int,
        settings: ReadingSettings,
    ) -> CheckpointResult:
        snippet = self._snippet_from_text(
            chapter_text,
            frame_index=frame_index,
            settings=settings,
        )
        questions = self._questions_for_snippet(snippet)
        return CheckpointResult(
            checkpoint_id="preview",
            frame_index=frame_index,
            questions=questions,
        )

    def preview_feedback(
        self,
        chapter_text: str,
        *,
        frame_index: int,
        settings: ReadingSettings,
        questions: tuple[CheckpointQuestion, ...],
        answers: list[CheckpointAnswer],
    ) -> CheckpointFeedback:
        score, weak, feedback, wpm_adjust = self._score_answers(questions, answers)
        summary: str | None = None
        gaps: tuple[CheckpointGap, ...] = ()
        if weak:
            gaps = self._gaps_from_answers(questions, answers)
            snippet = self._snippet_from_text(
                chapter_text,
                frame_index=frame_index,
                settings=settings,
            )
            summary = self._extractive_summary(snippet)
        return CheckpointFeedback(
            checkpoint_id="preview",
            frame_index=frame_index,
            score=score,
            weak=weak,
            feedback=feedback,
            wpm_adjust=wpm_adjust,
            flashcards_added=0,
            summary=summary,
            gaps=gaps,
        )

    def _snippet_from_text(
        self,
        chapter_text: str,
        *,
        frame_index: int,
        settings: ReadingSettings,
        start_frame: int | None = None,
    ) -> str:
        timeline = self._reader.prepare(chapter_text, settings)
        start_index = start_frame if start_frame is not None else max(0, frame_index - 20)
        end_index = min(frame_index + 1, len(timeline.frames))
        if start_index >= end_index:
            return chapter_text[:500]
        return " ".join(frame.text for frame in timeline.frames[start_index:end_index])

    def _snippet_for_frame(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        frame_index: int,
        chapter_text: str,
        settings: ReadingSettings,
    ) -> str:
        timeline = self._reader.prepare(chapter_text, settings)
        start_frame = store.last_checkpoint_frame(user_id, document_id, frame_index)
        start_index = (start_frame + 1) if start_frame is not None else 0
        end_index = min(frame_index + 1, len(timeline.frames))
        if start_index >= end_index:
            return chapter_text[:500]
        return " ".join(frame.text for frame in timeline.frames[start_index:end_index])

    def _questions_for_snippet(self, snippet: str) -> tuple[CheckpointQuestion, ...]:
        normalized = " ".join(snippet.split())
        if not normalized:
            normalized = "the passage you just read"
        cache_key = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        questions = self._template_questions(normalized)
        self._cache[cache_key] = questions
        return questions

    def _template_questions(self, snippet: str) -> tuple[CheckpointQuestion, ...]:
        preview = snippet[:120].rstrip()
        if len(snippet) > 120:
            preview += "…"
        questions = [
            CheckpointQuestion(
                id="literal",
                text=f"What specific point does this passage make about “{preview}”?",
                type="literal",
            ),
            CheckpointQuestion(
                id="inferential",
                text="What might this passage imply beyond what is directly stated?",
                type="inferential",
            ),
            CheckpointQuestion(
                id="connection",
                text="How does this connect to what you read earlier in this chapter?",
                type="connection",
            ),
        ]
        word_count = len(snippet.split())
        if word_count < 6:
            return tuple(questions[:2])
        if word_count >= 120:
            questions.append(
                CheckpointQuestion(
                    id="key_detail",
                    text="Which supporting detail is most important to the passage's main point?",
                    type="literal",
                )
            )
        if word_count >= 240:
            questions.append(
                CheckpointQuestion(
                    id="application",
                    text="How could you apply or test the passage's main idea?",
                    type="application",
                )
            )
        return tuple(questions)

    def _score_answers(
        self,
        questions: tuple[CheckpointQuestion, ...],
        answers: list[CheckpointAnswer],
    ) -> tuple[float, bool, str, int]:
        if not answers:
            return 0.0, True, "Answer at least one question before continuing.", -30

        weighted_score = 0.0
        total_weight = 0.0
        weak = False
        for index, question in enumerate(questions):
            answer = (
                answers[index]
                if index < len(answers)
                else CheckpointAnswer(text="", confidence="no_idea")
            )
            text = answer.text.strip()
            confidence = answer.confidence
            weight = 2.0 if question.type == "literal" else 1.0
            total_weight += weight
            if not text or confidence == "no_idea":
                answer_score = 0.0
                weak = True
            elif confidence == "unsure":
                answer_score = 0.5
            elif question.type == "literal" and len(text) < 10:
                answer_score = 0.5
                weak = True
            else:
                answer_score = 1.0
            weighted_score += answer_score * weight

        score = weighted_score / total_weight if total_weight else 0.0
        if score < 0.67:
            weak = True

        if weak:
            feedback = (
                "Some answers look uncertain. Consider slowing down or re-reading "
                "the last few phrases before continuing."
            )
            wpm_adjust = -30
        elif score >= 0.9:
            feedback = "Strong recall on this passage. Your current pace looks sustainable."
            wpm_adjust = 0
        else:
            feedback = "Decent recall. Keep checking whether each phrase connects to the last."
            wpm_adjust = 0

        return round(score, 2), weak, feedback, wpm_adjust

    def _extractive_summary(self, snippet: str) -> str:
        normalized = " ".join(snippet.split())
        if not normalized:
            return "Review the passage you just read."
        sentences = [
            part.strip() for part in re.findall(r"[^.!?]+[.!?]?", normalized) if part.strip()
        ]
        if not sentences:
            return self._cap_summary(normalized)
        return self._cap_summary(" ".join(sentences[:3]))

    @staticmethod
    def _cap_summary(summary: str, limit: int = 400) -> str:
        if len(summary) <= limit:
            return summary
        shortened = summary[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:")
        return f"{shortened}…"

    def _gaps_from_answers(
        self,
        questions: tuple[CheckpointQuestion, ...],
        answers: list[CheckpointAnswer],
    ) -> tuple[CheckpointGap, ...]:
        gaps: list[CheckpointGap] = []
        for question, answer in zip(questions, answers, strict=False):
            text = answer.text.strip()
            if not text:
                gaps.append(
                    CheckpointGap(
                        question_id=question.id,
                        question_text=question.text,
                        reason="empty_answer",
                    )
                )
            elif answer.confidence == "no_idea":
                gaps.append(
                    CheckpointGap(
                        question_id=question.id,
                        question_text=question.text,
                        reason="no_idea",
                    )
                )
            elif answer.confidence == "unsure":
                gaps.append(
                    CheckpointGap(
                        question_id=question.id,
                        question_text=question.text,
                        reason="unsure",
                    )
                )
        return tuple(gaps)
