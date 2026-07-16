"""Thin HTTP routes for the local PhraseFrame application."""

from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask
from starlette.templating import Jinja2Templates

from phraseframe.adapters.documents import DocumentExtractionService
from phraseframe.adapters.video import PillowMoviePyRenderer
from phraseframe.auth.jwt import create_access_token
from phraseframe.core.models import ExtractedDocument, ReadingSettings, Timeline
from phraseframe.db.store import LibraryStore, User
from phraseframe.services.analytics import AnalyticsService
from phraseframe.services.checkpoints import CheckpointAnswer, CheckpointQuestion, CheckpointService
from phraseframe.services.library import LibraryService, metadata_payload
from phraseframe.services.reader import ReaderService
from phraseframe.services.review import ReviewService
from phraseframe.web.deps import get_current_user, get_store

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
reader = ReaderService()
extractor = DocumentExtractionService()
library = LibraryService(extractor)
checkpoints = CheckpointService(reader)
review = ReviewService()
analytics = AnalyticsService()
renderer = PillowMoviePyRenderer()


class ReadingRequest(BaseModel):
    text: str = Field(max_length=100_000)
    wpm: int = Field(default=300, ge=100, le=800)
    target_words: int = Field(default=4, ge=1, le=10)
    max_words: int = Field(default=6, ge=1, le=10)
    max_characters: int = Field(default=42, ge=10, le=100)
    preview_seconds: int | None = Field(default=None, ge=1, le=600)
    stop_every_words: int | None = Field(default=None, ge=50, le=5000)

    def settings(self) -> ReadingSettings:
        try:
            return ReadingSettings(
                wpm=self.wpm,
                target_words=self.target_words,
                max_words=self.max_words,
                max_characters=self.max_characters,
                stop_every_words=self.stop_every_words,
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error


class AuthRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class ProgressRequest(BaseModel):
    chapter_index: int = Field(default=0, ge=0)
    frame_index: int = Field(default=0, ge=0)
    wpm: int = Field(default=300, ge=100, le=800)
    target_words: int = Field(default=4, ge=1, le=10)
    stop_every_words: int | None = Field(default=None, ge=50, le=5000)


class CheckpointAnswerPayload(BaseModel):
    text: str = ""
    confidence: str = Field(default="unsure", pattern="^(sure|unsure|no_idea)$")


class CheckpointRequest(BaseModel):
    frame_index: int = Field(ge=0)
    chapter_index: int = Field(default=0, ge=0)
    checkpoint_id: str | None = None
    answers: list[CheckpointAnswerPayload] | None = None


class FlashcardReviewRequest(BaseModel):
    grade: str = Field(pattern="^(got_it|again)$")


class LearningEventRequest(BaseModel):
    event_type: str = Field(pattern="^(prepare|return_to_passage)$")
    document_id: str
    chapter_index: int = Field(default=0, ge=0)
    frame_index: int | None = Field(default=None, ge=0)
    wpm: int | None = Field(default=None, ge=100, le=800)


class CheckpointPreviewRequest(BaseModel):
    text: str = Field(max_length=100_000)
    frame_index: int = Field(ge=0)
    wpm: int = Field(default=300, ge=100, le=800)
    target_words: int = Field(default=4, ge=1, le=10)
    max_words: int = Field(default=6, ge=1, le=10)
    max_characters: int = Field(default=42, ge=10, le=100)
    answers: list[CheckpointAnswerPayload] | None = None
    questions: list[dict[str, str]] | None = None

    def settings(self) -> ReadingSettings:
        return ReadingSettings(
            wpm=self.wpm,
            target_words=self.target_words,
            max_words=self.max_words,
            max_characters=self.max_characters,
        )


def _timeline_payload(timeline: Timeline) -> dict[str, object]:
    return {
        "frames": [asdict(frame) for frame in timeline.frames],
        "word_count": timeline.word_count,
        "duration_ms": timeline.duration_ms,
        "wpm": timeline.wpm,
        "stop_frames": list(timeline.stop_frames),
    }


def _prepare(payload: ReadingRequest) -> Timeline:
    try:
        timeline = reader.prepare(payload.text, payload.settings())
        return reader.limit_duration(timeline, payload.preview_seconds)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


def _extract_upload(content: bytes, filename: str) -> ExtractedDocument:
    try:
        return extractor.extract(content, filename)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


def _reading_settings_from_progress(
    store: LibraryStore,
    user_id: int,
    document_id: str,
) -> ReadingSettings:
    progress = store.get_progress(user_id, document_id)
    if progress is None:
        return ReadingSettings()
    return ReadingSettings(
        wpm=progress.wpm,
        target_words=progress.target_words,
        stop_every_words=progress.stop_every_words,
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/")
def index(request: Request) -> object:
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/api/timeline")
def create_timeline(payload: ReadingRequest) -> dict[str, object]:
    return _timeline_payload(_prepare(payload))


@router.post("/api/extract")
async def extract_text(
    file: Annotated[UploadFile, File()],
    chapter_index: int = 0,
) -> dict[str, object]:
    content = await file.read(extractor.max_bytes + 1)
    document = _extract_upload(content, file.filename or "upload.txt")
    if chapter_index < 0 or chapter_index >= len(document.chapters):
        raise HTTPException(status_code=422, detail="Chapter index is out of range.")
    return metadata_payload(
        document,
        chapter_index=chapter_index,
        text=document.text_for_chapter(chapter_index),
    )


@router.post("/api/auth/register")
def register(
    payload: AuthRequest,
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        user = store.create_user(payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    token = create_access_token(user.id)
    return {"token": token, "email": user.email}


@router.post("/api/auth/login")
def login(
    payload: AuthRequest,
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        user = store.authenticate(payload.email, payload.password)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    token = create_access_token(user.id)
    return {"token": token, "email": user.email}


@router.get("/api/documents")
def list_documents(
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    entries = library.list_library(store, user.id)
    return {
        "documents": [
            {
                "id": entry.id,
                "title": entry.title,
                "filename": entry.filename,
                "format": entry.source_format,
                "created_at": entry.created_at,
                "has_progress": entry.has_progress,
                "comprehension_rate": entry.comprehension_rate,
                "progress_updated_at": entry.progress_updated_at,
            }
            for entry in entries
        ]
    }


@router.get("/api/library/summary")
def get_library_summary(
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    summary = asdict(store.library_summary(user.id))
    deep = analytics.deep_pace(store, user.id)
    summary["deep_pace_wpm"] = deep.wpm
    summary["deep_pace_message"] = deep.message
    return summary


@router.get("/api/analytics/summary")
def get_analytics_summary(
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    return analytics.aggregate_summary(store, user.id)


@router.post("/api/learning-events")
def record_learning_event(
    payload: LearningEventRequest,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        store.get_document(user.id, payload.document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    analytics.record(
        store,
        user.id,
        payload.event_type,
        document_id=payload.document_id,
        chapter_index=payload.chapter_index,
        frame_index=payload.frame_index,
        wpm=payload.wpm,
    )
    return {"recorded": True}


@router.post("/api/checkpoints/preview")
def preview_checkpoint(payload: CheckpointPreviewRequest) -> dict[str, object]:
    settings = payload.settings()
    if payload.answers is not None:
        if not payload.questions:
            raise HTTPException(status_code=422, detail="Questions are required to score answers.")
        question_objects = tuple(
            CheckpointQuestion(
                id=item["id"],
                text=item["text"],
                type=item.get("type", "literal"),
            )
            for item in payload.questions
        )
        feedback = checkpoints.preview_feedback(
            payload.text,
            frame_index=payload.frame_index,
            settings=settings,
            questions=question_objects,
            answers=[
                CheckpointAnswer(text=answer.text, confidence=answer.confidence)
                for answer in payload.answers
            ],
        )
        return {
            "checkpoint_id": feedback.checkpoint_id,
            "frame_index": feedback.frame_index,
            "score": feedback.score,
            "weak": feedback.weak,
            "feedback": feedback.feedback,
            "wpm_adjust": feedback.wpm_adjust,
            "flashcards_added": 0,
            "preview": True,
            "sign_in_hint": "Sign in to save cards, history, and resume.",
            "summary": feedback.summary,
            "gaps": [
                {
                    "question_id": gap.question_id,
                    "question_text": gap.question_text,
                    "reason": gap.reason,
                }
                for gap in feedback.gaps
            ],
        }

    result = checkpoints.preview_checkpoint(
        payload.text,
        frame_index=payload.frame_index,
        settings=settings,
    )
    return {
        "checkpoint_id": result.checkpoint_id,
        "frame_index": result.frame_index,
        "preview": True,
        "questions": [asdict(question) for question in result.questions],
    }


@router.post("/api/documents")
async def upload_document(
    file: Annotated[UploadFile, File()],
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    content = await file.read(extractor.max_bytes + 1)
    filename = file.filename or "upload.txt"
    try:
        result = library.upload(store, user.id, content, filename)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {
        "document_id": result.document_id,
        "title": result.title,
        "format": result.format,
        "chapter_index": 0,
        "chapters": [asdict(chapter) for chapter in result.chapters],
    }


@router.get("/api/documents/{document_id}/chapters/{chapter_index}")
def get_chapter(
    document_id: str,
    chapter_index: int,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        text = library.chapter_text(store, user.id, document_id, chapter_index)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"chapter_index": chapter_index, "text": text}


@router.get("/api/documents/{document_id}/resume")
def resume_document(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        result = library.resume(store, user.id, document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    payload: dict[str, object] = {
        "document_id": result.document_id,
        "title": result.title,
        "format": result.format,
        "chapter_index": result.chapter_index,
        "chapters": [asdict(chapter) for chapter in result.chapters],
        "text": result.text,
    }
    if result.progress is not None:
        payload["progress"] = asdict(result.progress)
    return payload


@router.put("/api/documents/{document_id}/progress")
def save_progress(
    document_id: str,
    payload: ProgressRequest,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        progress = library.save_progress(
            store,
            user.id,
            document_id,
            chapter_index=payload.chapter_index,
            frame_index=payload.frame_index,
            wpm=payload.wpm,
            target_words=payload.target_words,
            stop_every_words=payload.stop_every_words,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    if payload.frame_index > 0:
        analytics.record(
            store,
            user.id,
            AnalyticsService.EVENT_RESUME,
            document_id=document_id,
            chapter_index=payload.chapter_index,
            frame_index=payload.frame_index,
            wpm=payload.wpm,
        )
    return {"progress": asdict(progress)}


@router.get("/api/documents/{document_id}/checkpoints")
def list_checkpoints(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        history = checkpoints.list_history(store, user.id, document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"checkpoints": history}


@router.post("/api/documents/{document_id}/checkpoints")
def create_checkpoint(
    document_id: str,
    payload: CheckpointRequest,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        if payload.answers is not None:
            if not payload.checkpoint_id:
                raise HTTPException(
                    status_code=422,
                    detail="Checkpoint id is required to save answers.",
                )
            feedback = checkpoints.save_answers(
                store,
                user.id,
                document_id,
                checkpoint_id=payload.checkpoint_id,
                answers=[
                    CheckpointAnswer(text=answer.text, confidence=answer.confidence)
                    for answer in payload.answers
                ],
                chapter_text=library.chapter_text(
                    store,
                    user.id,
                    document_id,
                    payload.chapter_index,
                ),
                settings=_reading_settings_from_progress(store, user.id, document_id),
                review_service=review,
            )
            settings = _reading_settings_from_progress(store, user.id, document_id)
            analytics.record(
                store,
                user.id,
                AnalyticsService.EVENT_CHECKPOINT_SUBMIT,
                document_id=document_id,
                chapter_index=payload.chapter_index,
                frame_index=feedback.frame_index,
                wpm=settings.wpm,
                self_check_score=feedback.score,
            )
            if feedback.weak:
                analytics.record(
                    store,
                    user.id,
                    AnalyticsService.EVENT_WEAK_STOP_REPAIR,
                    document_id=document_id,
                    chapter_index=payload.chapter_index,
                    frame_index=feedback.frame_index,
                    wpm=settings.wpm,
                    self_check_score=feedback.score,
                )
            return {
                "checkpoint_id": feedback.checkpoint_id,
                "frame_index": feedback.frame_index,
                "score": feedback.score,
                "weak": feedback.weak,
                "feedback": feedback.feedback,
                "wpm_adjust": feedback.wpm_adjust,
                "flashcards_added": feedback.flashcards_added,
                "summary": feedback.summary,
                "gaps": [
                    {
                        "question_id": gap.question_id,
                        "question_text": gap.question_text,
                        "reason": gap.reason,
                    }
                    for gap in feedback.gaps
                ],
            }

        chapter_text = library.chapter_text(
            store,
            user.id,
            document_id,
            payload.chapter_index,
        )
        settings = _reading_settings_from_progress(store, user.id, document_id)
        result = checkpoints.create_checkpoint(
            store,
            user.id,
            document_id,
            frame_index=payload.frame_index,
            chapter_text=chapter_text,
            settings=settings,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "checkpoint_id": result.checkpoint_id,
        "frame_index": result.frame_index,
        "questions": [asdict(question) for question in result.questions],
    }


@router.get("/api/documents/{document_id}/flashcards")
def list_flashcards(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        cards = store.list_flashcards(user.id, document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "flashcards": [
            {
                "id": card.id,
                "checkpoint_id": card.checkpoint_id,
                "front": card.front,
                "back": card.back,
                "due_at": card.due_at,
                "interval": card.interval,
                "ease_factor": card.ease_factor,
                "repetitions": card.repetitions,
            }
            for card in cards
        ]
    }


@router.get("/api/review/queue")
def review_queue(
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    entries = store.list_due_flashcards(user.id)
    return {
        "flashcards": [
            {
                "id": entry.card.id,
                "document_id": entry.card.document_id,
                "document_title": entry.document_title,
                "checkpoint_id": entry.card.checkpoint_id,
                "frame_index": entry.source_frame_index,
                "front": entry.card.front,
                "back": entry.card.back,
                "due_at": entry.card.due_at,
                "interval": entry.card.interval,
                "ease_factor": entry.card.ease_factor,
                "repetitions": entry.card.repetitions,
            }
            for entry in entries
        ]
    }


@router.delete("/api/documents/{document_id}/flashcards/{flashcard_id}")
def delete_flashcard(
    document_id: str,
    flashcard_id: str,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        store.delete_flashcard(user.id, document_id, flashcard_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"deleted": True}


@router.post("/api/documents/{document_id}/flashcards/{flashcard_id}/review")
def review_flashcard(
    document_id: str,
    flashcard_id: str,
    payload: FlashcardReviewRequest,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        card = review.review_card(
            store,
            user.id,
            document_id,
            flashcard_id,
            payload.grade,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    analytics.record(
        store,
        user.id,
        AnalyticsService.EVENT_REVIEW_GRADE,
        document_id=document_id,
        card_grade=payload.grade,
        due_interval=card.interval,
    )
    return {
        "flashcard_id": card.id,
        "due_at": card.due_at,
        "grade": payload.grade,
        "interval": card.interval,
        "ease_factor": card.ease_factor,
        "repetitions": card.repetitions,
    }


@router.post("/api/export")
async def export_video(payload: ReadingRequest) -> FileResponse:
    timeline = _prepare(payload)
    with NamedTemporaryFile(prefix="phraseframe-", suffix=".mp4", delete=False) as temporary:
        output_path = Path(temporary.name)
    try:
        await run_in_threadpool(renderer.render, timeline, output_path)
    except Exception as error:
        output_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Video export failed: {error}") from error
    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename="phraseframe.mp4",
        background=BackgroundTask(output_path.unlink, missing_ok=True),
    )
