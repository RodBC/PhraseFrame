import pytest

from phraseframe.adapters.text import TextDocumentExtractor


def test_extracts_utf8_with_bom() -> None:
    adapter = TextDocumentExtractor()
    assert adapter.extract(b"\xef\xbb\xbfHello, caf\xc3\xa9.", "notes.TXT") == "Hello, café."


@pytest.mark.parametrize(
    ("content", "filename", "message"),
    [
        (b"", "empty.txt", "empty"),
        (b"text", "book.pdf", "Only .txt"),
        (b"bad\x00text", "bad.txt", "plain text"),
        (b"\xff\xfe", "legacy.txt", "UTF-8"),
    ],
)
def test_rejects_invalid_text(content: bytes, filename: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        TextDocumentExtractor().extract(content, filename)


def test_rejects_oversized_file() -> None:
    adapter = TextDocumentExtractor()
    with pytest.raises(ValueError, match="smaller than 1 MB"):
        adapter.extract(b"a" * (adapter.max_bytes + 1), "large.txt")
