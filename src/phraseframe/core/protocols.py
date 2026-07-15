"""Ports implemented by document and video adapters."""

from pathlib import Path
from typing import Protocol

from phraseframe.core.models import Timeline


class DocumentExtractor(Protocol):
    """Extract normalized source text from a supported document."""

    def extract(self, content: bytes, filename: str) -> str: ...


class VideoRenderer(Protocol):
    """Render a timeline into a playable media file."""

    def render(self, timeline: Timeline, output_path: Path) -> Path: ...
