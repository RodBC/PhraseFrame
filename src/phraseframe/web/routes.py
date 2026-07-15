"""Thin HTTP routes for the local PhraseFrame application."""

from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask
from starlette.templating import Jinja2Templates

from phraseframe.adapters.text import TextDocumentExtractor
from phraseframe.adapters.video import PillowMoviePyRenderer
from phraseframe.core.models import ReadingSettings, Timeline
from phraseframe.services.reader import ReaderService

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
reader = ReaderService()
extractor = TextDocumentExtractor()
renderer = PillowMoviePyRenderer()


class ReadingRequest(BaseModel):
    text: str = Field(max_length=100_000)
    wpm: int = Field(default=300, ge=100, le=800)
    target_words: int = Field(default=4, ge=1, le=10)
    max_words: int = Field(default=6, ge=1, le=10)
    max_characters: int = Field(default=42, ge=10, le=100)
    preview_seconds: int | None = Field(default=None, ge=1, le=600)

    def settings(self) -> ReadingSettings:
        try:
            return ReadingSettings(
                wpm=self.wpm,
                target_words=self.target_words,
                max_words=self.max_words,
                max_characters=self.max_characters,
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error


def _timeline_payload(timeline: Timeline) -> dict[str, object]:
    return {
        "frames": [asdict(frame) for frame in timeline.frames],
        "word_count": timeline.word_count,
        "duration_ms": timeline.duration_ms,
        "wpm": timeline.wpm,
    }


def _prepare(payload: ReadingRequest) -> Timeline:
    try:
        timeline = reader.prepare(payload.text, payload.settings())
        return reader.limit_duration(timeline, payload.preview_seconds)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("/")
def index(request: Request) -> object:
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/api/timeline")
def create_timeline(payload: ReadingRequest) -> dict[str, object]:
    return _timeline_payload(_prepare(payload))


@router.post("/api/extract")
async def extract_text(file: Annotated[UploadFile, File()]) -> dict[str, str]:
    content = await file.read(extractor.max_bytes + 1)
    try:
        text = extractor.extract(content, file.filename or "upload.txt")
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return {"text": text}


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
