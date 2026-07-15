"""Plain-text document adapter."""

from pathlib import Path


class TextDocumentExtractor:
    """Decode small UTF-8 text files with actionable validation errors."""

    max_bytes = 1_000_000

    def extract(self, content: bytes, filename: str) -> str:
        if Path(filename).suffix.lower() != ".txt":
            raise ValueError("Only .txt files are supported in this POC.")
        if not content:
            raise ValueError("The selected file is empty.")
        if len(content) > self.max_bytes:
            raise ValueError("Text files must be smaller than 1 MB.")
        if b"\x00" in content:
            raise ValueError("The selected file does not appear to be plain text.")
        try:
            return content.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("Save the file as UTF-8 and try again.") from error
