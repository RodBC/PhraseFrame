"""Text cleanup and punctuation-aware phrase segmentation."""

import re

from phraseframe.core.models import PhraseChunk, ReadingSettings

_WORD_RE = re.compile(r"[\w]+(?:[’'-][\w]+)*", re.UNICODE)
_SENTENCE_END_RE = re.compile(r"""[.!?]["'’”)]*$""")
_CLAUSE_END_RE = re.compile(r"""[,;:—]["'’”)]*$""")


def normalize_text(text: str) -> str:
    """Normalize newlines and spaces while preserving paragraph boundaries."""

    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    paragraphs = []
    for paragraph in re.split(r"\n\s*\n", text):
        compact = re.sub(r"[ \t\n]+", " ", paragraph).strip()
        if compact:
            paragraphs.append(compact)
    return "\n\n".join(paragraphs)


def count_words(text: str) -> int:
    """Count human-readable words consistently across the application."""

    return len(_WORD_RE.findall(text))


def _boundary_for(token: str) -> str:
    if _SENTENCE_END_RE.search(token):
        return "sentence"
    if _CLAUSE_END_RE.search(token):
        return "clause"
    return "none"


def chunk_text(text: str, settings: ReadingSettings) -> tuple[PhraseChunk, ...]:
    """Split text into short phrases without crossing strong boundaries."""

    normalized = normalize_text(text)
    if not normalized:
        return ()

    chunks: list[PhraseChunk] = []
    paragraphs = normalized.split("\n\n")
    for paragraph_index, paragraph in enumerate(paragraphs):
        current: list[str] = []
        current_words = 0

        def flush(boundary: str = "none") -> None:
            nonlocal current, current_words
            if current:
                chunks.append(PhraseChunk(" ".join(current), current_words, boundary))
                current = []
                current_words = 0

        for token in paragraph.split():
            token_words = max(1, count_words(token))
            projected_text = " ".join((*current, token))
            would_overflow = bool(current) and (
                current_words + token_words > settings.max_words
                or len(projected_text) > settings.max_characters
            )
            if would_overflow:
                flush()

            current.append(token)
            current_words += token_words
            boundary = _boundary_for(token)

            if boundary == "sentence":
                flush("sentence")
            elif boundary == "clause" and current_words >= 2:
                flush("clause")
            elif current_words >= settings.target_words:
                flush()

        paragraph_boundary = "paragraph" if paragraph_index < len(paragraphs) - 1 else "none"
        if current:
            flush(paragraph_boundary)
        elif paragraph_boundary == "paragraph" and chunks:
            previous = chunks[-1]
            chunks[-1] = PhraseChunk(previous.text, previous.word_count, "paragraph")

    return tuple(chunks)
