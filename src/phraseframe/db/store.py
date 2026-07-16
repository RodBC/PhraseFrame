"""SQLite persistence for accounts, documents, and reading progress."""

from __future__ import annotations

import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from phraseframe.auth.passwords import hash_password, verify_password


@dataclass(frozen=True, slots=True)
class User:
    id: int
    email: str


@dataclass(frozen=True, slots=True)
class StoredDocument:
    id: str
    user_id: int
    filename: str
    title: str
    source_format: str
    created_at: str


@dataclass(frozen=True, slots=True)
class ReadingProgress:
    document_id: str
    chapter_index: int
    frame_index: int
    wpm: int
    target_words: int
    updated_at: str


@dataclass(frozen=True, slots=True)
class LibraryEntry:
    id: str
    title: str
    filename: str
    source_format: str
    created_at: str
    has_progress: bool


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    id: str
    document_id: str
    frame_index: int
    questions_json: str
    answers_json: str | None
    created_at: str


class LibraryStore:
    """Local SQLite store for v2 account and resume features."""

    def __init__(self, db_path: Path, storage_path: Path) -> None:
        self.db_path = db_path
        self.storage_path = storage_path

    @classmethod
    def from_env(cls) -> LibraryStore:
        data_root = Path(os.environ.get("PHRASEFRAME_DATA_DIR", "data"))
        return cls(
            db_path=data_root / "phraseframe.db",
            storage_path=data_root / "documents",
        )

    def init_schema(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    title TEXT NOT NULL,
                    source_format TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS reading_progress (
                    document_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    chapter_index INTEGER NOT NULL,
                    frame_index INTEGER NOT NULL,
                    wpm INTEGER NOT NULL,
                    target_words INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS checkpoints (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    frame_index INTEGER NOT NULL,
                    questions_json TEXT NOT NULL,
                    answers_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )

    def create_user(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        if not normalized or "@" not in normalized:
            raise ValueError("Enter a valid email address.")
        if len(password) < 8:
            raise ValueError("Passwords must be at least 8 characters.")
        created_at = datetime.now(tz=UTC).isoformat()
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
                    (normalized, hash_password(password), created_at),
                )
                user_id = int(cursor.lastrowid or 0)
                if user_id == 0:
                    raise ValueError("Could not create user.")
        except sqlite3.IntegrityError as error:
            raise ValueError("An account with this email already exists.") from error
        return User(id=user_id, email=normalized)

    def authenticate(self, email: str, password: str) -> User:
        normalized = email.strip().lower()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ?",
                (normalized,),
            ).fetchone()
        if row is None or not verify_password(password, row["password_hash"]):
            raise ValueError("Email or password is incorrect.")
        return User(id=int(row["id"]), email=str(row["email"]))

    def get_user(self, user_id: int) -> User:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if row is None:
            raise ValueError("User not found.")
        return User(id=int(row["id"]), email=str(row["email"]))

    def save_document(
        self,
        user_id: int,
        filename: str,
        title: str,
        source_format: str,
        content: bytes,
    ) -> StoredDocument:
        document_id = uuid.uuid4().hex
        created_at = datetime.now(tz=UTC).isoformat()
        suffix = Path(filename).suffix.lower()
        destination = self.storage_path / str(user_id) / f"{document_id}{suffix}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    id, user_id, filename, title, source_format, storage_path, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document_id,
                    user_id,
                    filename,
                    title,
                    source_format,
                    str(destination),
                    created_at,
                ),
            )
        return StoredDocument(
            id=document_id,
            user_id=user_id,
            filename=filename,
            title=title,
            source_format=source_format,
            created_at=created_at,
        )

    def list_documents_with_progress(self, user_id: int) -> list[LibraryEntry]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    d.id,
                    d.title,
                    d.filename,
                    d.source_format,
                    d.created_at,
                    CASE WHEN rp.document_id IS NOT NULL THEN 1 ELSE 0 END AS has_progress
                FROM documents d
                LEFT JOIN reading_progress rp
                    ON d.id = rp.document_id AND d.user_id = rp.user_id
                WHERE d.user_id = ?
                ORDER BY d.created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            LibraryEntry(
                id=str(row["id"]),
                title=str(row["title"]),
                filename=str(row["filename"]),
                source_format=str(row["source_format"]),
                created_at=str(row["created_at"]),
                has_progress=bool(row["has_progress"]),
            )
            for row in rows
        ]

    def list_documents(self, user_id: int) -> list[StoredDocument]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, user_id, filename, title, source_format, created_at
                FROM documents
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            StoredDocument(
                id=str(row["id"]),
                user_id=int(row["user_id"]),
                filename=str(row["filename"]),
                title=str(row["title"]),
                source_format=str(row["source_format"]),
                created_at=str(row["created_at"]),
            )
            for row in rows
        ]

    def get_document(self, user_id: int, document_id: str) -> StoredDocument:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, user_id, filename, title, source_format, created_at
                FROM documents
                WHERE id = ? AND user_id = ?
                """,
                (document_id, user_id),
            ).fetchone()
        if row is None:
            raise ValueError("Document not found.")
        return StoredDocument(
            id=str(row["id"]),
            user_id=int(row["user_id"]),
            filename=str(row["filename"]),
            title=str(row["title"]),
            source_format=str(row["source_format"]),
            created_at=str(row["created_at"]),
        )

    def read_document_bytes(self, user_id: int, document_id: str) -> bytes:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT storage_path FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        if row is None:
            raise ValueError("Document not found.")
        return Path(str(row["storage_path"])).read_bytes()

    def save_progress(
        self,
        user_id: int,
        document_id: str,
        *,
        chapter_index: int,
        frame_index: int,
        wpm: int,
        target_words: int,
    ) -> ReadingProgress:
        self.get_document(user_id, document_id)
        updated_at = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO reading_progress (
                    document_id, user_id, chapter_index, frame_index, wpm, target_words, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    chapter_index = excluded.chapter_index,
                    frame_index = excluded.frame_index,
                    wpm = excluded.wpm,
                    target_words = excluded.target_words,
                    updated_at = excluded.updated_at
                """,
                (
                    document_id,
                    user_id,
                    chapter_index,
                    frame_index,
                    wpm,
                    target_words,
                    updated_at,
                ),
            )
        return ReadingProgress(
            document_id=document_id,
            chapter_index=chapter_index,
            frame_index=frame_index,
            wpm=wpm,
            target_words=target_words,
            updated_at=updated_at,
        )

    def get_progress(self, user_id: int, document_id: str) -> ReadingProgress | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT document_id, chapter_index, frame_index, wpm, target_words, updated_at
                FROM reading_progress
                WHERE document_id = ? AND user_id = ?
                """,
                (document_id, user_id),
            ).fetchone()
        if row is None:
            return None
        return ReadingProgress(
            document_id=str(row["document_id"]),
            chapter_index=int(row["chapter_index"]),
            frame_index=int(row["frame_index"]),
            wpm=int(row["wpm"]),
            target_words=int(row["target_words"]),
            updated_at=str(row["updated_at"]),
        )

    def save_checkpoint(
        self,
        user_id: int,
        document_id: str,
        *,
        frame_index: int,
        questions_json: str,
        answers_json: str | None = None,
        checkpoint_id: str | None = None,
    ) -> CheckpointRecord:
        self.get_document(user_id, document_id)
        record_id = checkpoint_id or uuid.uuid4().hex
        if answers_json is not None:
            with self._connect() as connection:
                updated = connection.execute(
                    """
                    UPDATE checkpoints
                    SET answers_json = ?
                    WHERE id = ? AND document_id = ? AND user_id = ?
                    """,
                    (answers_json, record_id, document_id, user_id),
                )
                if updated.rowcount == 0:
                    raise ValueError("Checkpoint not found.")
            return self.get_checkpoint(user_id, document_id, record_id)

        created_at = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO checkpoints (
                    id, document_id, user_id, frame_index, questions_json, answers_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    document_id,
                    user_id,
                    frame_index,
                    questions_json,
                    None,
                    created_at,
                ),
            )
        return CheckpointRecord(
            id=record_id,
            document_id=document_id,
            frame_index=frame_index,
            questions_json=questions_json,
            answers_json=None,
            created_at=created_at,
        )

    def get_checkpoint(
        self,
        user_id: int,
        document_id: str,
        checkpoint_id: str,
    ) -> CheckpointRecord:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, document_id, frame_index, questions_json, answers_json, created_at
                FROM checkpoints
                WHERE id = ? AND document_id = ? AND user_id = ?
                """,
                (checkpoint_id, document_id, user_id),
            ).fetchone()
        if row is None:
            raise ValueError("Checkpoint not found.")
        return CheckpointRecord(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            frame_index=int(row["frame_index"]),
            questions_json=str(row["questions_json"]),
            answers_json=str(row["answers_json"]) if row["answers_json"] else None,
            created_at=str(row["created_at"]),
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection
