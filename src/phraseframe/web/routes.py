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
from phraseframe.services.checkpoints import CheckpointService
from phraseframe.services.library import LibraryService, metadata_payload
from phraseframe.services.reader import ReaderService
from phraseframe.web.deps import get_current_user, get_store

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
reader = ReaderService()
extractor = DocumentExtractionService()
library = LibraryService(extractor)
checkpoints = CheckpointService()
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


class CheckpointRequest(BaseModel):
    frame_index: int = Field(ge=0)
    snippet: str = Field(min_length=1, max_length=5000)
    checkpoint_id: str | None = None
    answers: list[str] | None = None


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
            }
            for entry in entries
        ]
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


@router.get("/api/documents/{document_id}")
def get_document(
    document_id: str,
    user: Annotated[User, Depends(get_current_user)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> dict[str, object]:
    try:
        stored, document, progress = library.document_meta(store, user.id, document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return metadata_payload(
        document,
        document_id=stored.id,
        progress=progress,
    )


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
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {"progress": asdict(progress)}


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
            record = checkpoints.save_answers(
                store,
                user.id,
                document_id,
                checkpoint_id=payload.checkpoint_id,
                answers=payload.answers,
            )
            return {
                "checkpoint_id": record.id,
                "frame_index": record.frame_index,
                "saved": True,
            }
        result = checkpoints.create_checkpoint(
            store,
            user.id,
            document_id,
            frame_index=payload.frame_index,
            snippet=payload.snippet,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return {
        "checkpoint_id": result.checkpoint_id,
        "frame_index": result.frame_index,
        "questions": [asdict(question) for question in result.questions],
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
