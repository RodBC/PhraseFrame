"""Comprehension checkpoint generation and persistence."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass

from phraseframe.db.store import CheckpointRecord, LibraryStore


@dataclass(frozen=True, slots=True)
class CheckpointQuestion:
    id: str
    text: str
    type: str


@dataclass(frozen=True, slots=True)
class CheckpointResult:
    checkpoint_id: str
    frame_index: int
    questions: tuple[CheckpointQuestion, ...]


class CheckpointService:
    """Generate template comprehension questions and store answers."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[CheckpointQuestion, ...]] = {}

    def create_checkpoint(
        self,
        store: LibraryStore,
        user_id: int,
        document_id: str,
        *,
        frame_index: int,
        snippet: str,
    ) -> CheckpointResult:
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
        answers: list[str],
    ) -> CheckpointRecord:
        checkpoint = store.get_checkpoint(user_id, document_id, checkpoint_id)
        return store.save_checkpoint(
            user_id,
            document_id,
            frame_index=checkpoint.frame_index,
            questions_json=checkpoint.questions_json,
            answers_json=json.dumps(answers),
            checkpoint_id=checkpoint_id,
        )

    def _questions_for_snippet(self, snippet: str) -> tuple[CheckpointQuestion, ...]:
        normalized = " ".join(snippet.split())
        if not normalized:
            normalized = "the passage you just read"
        cache_key = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key]

        if os.environ.get("PHRASEFRAME_LLM_API_KEY"):
            questions = self._llm_questions(normalized)
        else:
            questions = self._template_questions(normalized)

        self._cache[cache_key] = questions
        return questions

    def _template_questions(self, snippet: str) -> tuple[CheckpointQuestion, ...]:
        preview = snippet[:120].rstrip()
        if len(snippet) > 120:
            preview += "…"
        return (
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
        )

    def _llm_questions(self, snippet: str) -> tuple[CheckpointQuestion, ...]:
        # LLM integration deferred; fall back to templates until a provider is wired.
        return self._template_questions(snippet)
