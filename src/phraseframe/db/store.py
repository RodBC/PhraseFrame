"""SQLite persistence for accounts, documents, and reading progress."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

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
    stop_every_words: int | None
    updated_at: str


@dataclass(frozen=True, slots=True)
class LibraryEntry:
    id: str
    title: str
    filename: str
    source_format: str
    created_at: str
    has_progress: bool
    comprehension_rate: float | None
    progress_updated_at: str | None = None


@dataclass(frozen=True, slots=True)
class LibrarySummary:
    pending_flashcards: int
    average_comprehension: float | None
    weak_stop_count: int
    last_read_at: str | None


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    id: str
    document_id: str
    frame_index: int
    questions_json: str
    answers_json: str | None
    confidence_json: str | None
    score: float | None
    weak: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class FlashcardRecord:
    id: str
    document_id: str
    checkpoint_id: str
    front: str
    back: str
    due_at: str
    created_at: str
    interval: int
    ease_factor: float
    repetitions: int


@dataclass(frozen=True, slots=True)
class ReviewQueueEntry:
    card: FlashcardRecord
    document_title: str
    source_frame_index: int


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

                CREATE TABLE IF NOT EXISTS flashcards (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    checkpoint_id TEXT NOT NULL,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    due_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES documents(id),
                    FOREIGN KEY(checkpoint_id) REFERENCES checkpoints(id),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE UNIQUE INDEX IF NOT EXISTS idx_checkpoints_doc_frame
                    ON checkpoints(document_id, frame_index);
                """
            )
            self._ensure_column(connection, "reading_progress", "stop_every_words", "INTEGER")
            self._ensure_column(connection, "checkpoints", "confidence_json", "TEXT")
            self._ensure_column(connection, "checkpoints", "score", "REAL")
            self._ensure_column(connection, "checkpoints", "weak", "INTEGER DEFAULT 0")
            self._ensure_column(connection, "flashcards", "interval", "INTEGER DEFAULT 1")
            self._ensure_column(connection, "flashcards", "ease_factor", "REAL DEFAULT 2.5")
            self._ensure_column(connection, "flashcards", "repetitions", "INTEGER DEFAULT 0")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    document_id TEXT,
                    event_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    chapter_index INTEGER,
                    frame_index INTEGER,
                    wpm INTEGER,
                    self_check_score REAL,
                    card_grade TEXT,
                    due_interval INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE INDEX IF NOT EXISTS idx_learning_events_user_type
                    ON learning_events(user_id, event_type, created_at);
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
        doc_dir = self.storage_path / str(user_id) / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)
        destination = doc_dir / f"source{suffix}"
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

    def write_chapters_cache(
        self,
        user_id: int,
        document_id: str,
        chapters_meta: list[dict[str, object]],
        chapter_texts: list[str],
    ) -> None:
        cache_dir = self._chapter_cache_dir(user_id, document_id)
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "chapters.json").write_text(
            json.dumps(chapters_meta),
            encoding="utf-8",
        )
        for index, text in enumerate(chapter_texts):
            (cache_dir / f"chapter_{index}.txt").write_text(text, encoding="utf-8")

    def read_chapters_meta(self, user_id: int, document_id: str) -> list[dict[str, object]] | None:
        meta_path = self._chapter_cache_dir(user_id, document_id) / "chapters.json"
        if not meta_path.exists():
            return None
        return cast(list[dict[str, object]], json.loads(meta_path.read_text(encoding="utf-8")))

    def read_chapter_text(self, user_id: int, document_id: str, index: int) -> str | None:
        chapter_path = self._chapter_cache_dir(user_id, document_id) / f"chapter_{index}.txt"
        if not chapter_path.exists():
            return None
        return chapter_path.read_text(encoding="utf-8")

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
                    CASE WHEN rp.document_id IS NOT NULL THEN 1 ELSE 0 END AS has_progress,
                    rp.updated_at AS progress_updated_at,
                    (
                        SELECT AVG(c.score)
                        FROM checkpoints c
                        WHERE c.document_id = d.id
                          AND c.user_id = d.user_id
                          AND c.score IS NOT NULL
                    ) AS comprehension_rate
                FROM documents d
                LEFT JOIN reading_progress rp
                    ON d.id = rp.document_id AND d.user_id = rp.user_id
                WHERE d.user_id = ?
                ORDER BY COALESCE(rp.updated_at, d.created_at) DESC
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
                comprehension_rate=(
                    float(row["comprehension_rate"])
                    if row["comprehension_rate"] is not None
                    else None
                ),
                progress_updated_at=(
                    str(row["progress_updated_at"])
                    if row["progress_updated_at"] is not None
                    else None
                ),
            )
            for row in rows
        ]

    def library_summary(self, user_id: int) -> LibrarySummary:
        now = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    (
                        SELECT COUNT(*)
                        FROM flashcards f
                        WHERE f.user_id = ? AND f.due_at <= ?
                    ) AS pending_flashcards,
                    (
                        SELECT AVG(c.score)
                        FROM checkpoints c
                        WHERE c.user_id = ? AND c.score IS NOT NULL
                    ) AS average_comprehension,
                    (
                        SELECT COUNT(*)
                        FROM checkpoints c
                        WHERE c.user_id = ? AND c.weak = 1 AND c.score IS NOT NULL
                    ) AS weak_stop_count,
                    (
                        SELECT MAX(rp.updated_at)
                        FROM reading_progress rp
                        WHERE rp.user_id = ?
                    ) AS last_read_at
                """,
                (user_id, now, user_id, user_id, user_id),
            ).fetchone()
        if row is None:
            return LibrarySummary(0, None, 0, None)
        return LibrarySummary(
            pending_flashcards=int(row["pending_flashcards"]),
            average_comprehension=(
                float(row["average_comprehension"])
                if row["average_comprehension"] is not None
                else None
            ),
            weak_stop_count=int(row["weak_stop_count"]),
            last_read_at=str(row["last_read_at"]) if row["last_read_at"] is not None else None,
        )

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
        storage_path = self._storage_path(user_id, document_id)
        return storage_path.read_bytes()

    def save_progress(
        self,
        user_id: int,
        document_id: str,
        *,
        chapter_index: int,
        frame_index: int,
        wpm: int,
        target_words: int,
        stop_every_words: int | None = None,
    ) -> ReadingProgress:
        self.get_document(user_id, document_id)
        updated_at = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO reading_progress (
                    document_id, user_id, chapter_index, frame_index, wpm, target_words,
                    stop_every_words, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    chapter_index = excluded.chapter_index,
                    frame_index = excluded.frame_index,
                    wpm = excluded.wpm,
                    target_words = excluded.target_words,
                    stop_every_words = excluded.stop_every_words,
                    updated_at = excluded.updated_at
                """,
                (
                    document_id,
                    user_id,
                    chapter_index,
                    frame_index,
                    wpm,
                    target_words,
                    stop_every_words,
                    updated_at,
                ),
            )
        return ReadingProgress(
            document_id=document_id,
            chapter_index=chapter_index,
            frame_index=frame_index,
            wpm=wpm,
            target_words=target_words,
            stop_every_words=stop_every_words,
            updated_at=updated_at,
        )

    def get_progress(self, user_id: int, document_id: str) -> ReadingProgress | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT document_id, chapter_index, frame_index, wpm, target_words,
                       stop_every_words, updated_at
                FROM reading_progress
                WHERE document_id = ? AND user_id = ?
                """,
                (document_id, user_id),
            ).fetchone()
        if row is None:
            return None
        stop_every_words = row["stop_every_words"]
        return ReadingProgress(
            document_id=str(row["document_id"]),
            chapter_index=int(row["chapter_index"]),
            frame_index=int(row["frame_index"]),
            wpm=int(row["wpm"]),
            target_words=int(row["target_words"]),
            stop_every_words=int(stop_every_words) if stop_every_words is not None else None,
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
        confidence_json: str | None = None,
        score: float | None = None,
        weak: bool = False,
        checkpoint_id: str | None = None,
    ) -> CheckpointRecord:
        self.get_document(user_id, document_id)
        record_id = checkpoint_id or uuid.uuid4().hex
        if answers_json is not None:
            with self._connect() as connection:
                updated = connection.execute(
                    """
                    UPDATE checkpoints
                    SET answers_json = ?, confidence_json = ?, score = ?, weak = ?
                    WHERE id = ? AND document_id = ? AND user_id = ?
                    """,
                    (
                        answers_json,
                        confidence_json,
                        score,
                        int(weak),
                        record_id,
                        document_id,
                        user_id,
                    ),
                )
                if updated.rowcount == 0:
                    raise ValueError("Checkpoint not found.")
            return self.get_checkpoint(user_id, document_id, record_id)

        created_at = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT id FROM checkpoints
                WHERE document_id = ? AND user_id = ? AND frame_index = ?
                """,
                (document_id, user_id, frame_index),
            ).fetchone()
            if existing is not None:
                record_id = str(existing["id"])
                connection.execute(
                    """
                    UPDATE checkpoints
                    SET questions_json = ?, answers_json = NULL, confidence_json = NULL,
                        score = NULL, weak = 0, created_at = ?
                    WHERE id = ?
                    """,
                    (questions_json, created_at, record_id),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO checkpoints (
                        id, document_id, user_id, frame_index, questions_json,
                        answers_json, confidence_json, score, weak, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        document_id,
                        user_id,
                        frame_index,
                        questions_json,
                        None,
                        None,
                        None,
                        0,
                        created_at,
                    ),
                )
        return CheckpointRecord(
            id=record_id,
            document_id=document_id,
            frame_index=frame_index,
            questions_json=questions_json,
            answers_json=None,
            confidence_json=None,
            score=None,
            weak=False,
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
                SELECT id, document_id, frame_index, questions_json, answers_json,
                       confidence_json, score, weak, created_at
                FROM checkpoints
                WHERE id = ? AND document_id = ? AND user_id = ?
                """,
                (checkpoint_id, document_id, user_id),
            ).fetchone()
        if row is None:
            raise ValueError("Checkpoint not found.")
        return self._checkpoint_from_row(row)

    def list_checkpoints(self, user_id: int, document_id: str) -> list[CheckpointRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, document_id, frame_index, questions_json, answers_json,
                       confidence_json, score, weak, created_at
                FROM checkpoints
                WHERE document_id = ? AND user_id = ?
                ORDER BY frame_index ASC
                """,
                (document_id, user_id),
            ).fetchall()
        return [self._checkpoint_from_row(row) for row in rows]

    def last_checkpoint_frame(self, user_id: int, document_id: str, before: int) -> int | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT frame_index FROM checkpoints
                WHERE document_id = ? AND user_id = ? AND frame_index < ?
                ORDER BY frame_index DESC
                LIMIT 1
                """,
                (document_id, user_id, before),
            ).fetchone()
        return int(row["frame_index"]) if row is not None else None

    def save_flashcards(
        self,
        user_id: int,
        document_id: str,
        checkpoint_id: str,
        cards: list[tuple[str, str]],
    ) -> list[FlashcardRecord]:
        self.get_document(user_id, document_id)
        created_at = datetime.now(tz=UTC).isoformat()
        due_at = created_at
        records: list[FlashcardRecord] = []
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT 1 FROM flashcards
                WHERE user_id = ? AND document_id = ? AND checkpoint_id = ?
                LIMIT 1
                """,
                (user_id, document_id, checkpoint_id),
            ).fetchone()
            if existing is not None:
                return records
            for front, back in cards:
                record_id = uuid.uuid4().hex
                connection.execute(
                    """
                    INSERT INTO flashcards (
                        id, document_id, user_id, checkpoint_id, front, back, due_at, created_at,
                        interval, ease_factor, repetitions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        document_id,
                        user_id,
                        checkpoint_id,
                        front,
                        back,
                        due_at,
                        created_at,
                        1,
                        2.5,
                        0,
                    ),
                )
                records.append(
                    FlashcardRecord(
                        id=record_id,
                        document_id=document_id,
                        checkpoint_id=checkpoint_id,
                        front=front,
                        back=back,
                        due_at=due_at,
                        created_at=created_at,
                        interval=1,
                        ease_factor=2.5,
                        repetitions=0,
                    )
                )
        return records

    def list_flashcards(self, user_id: int, document_id: str) -> list[FlashcardRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, document_id, checkpoint_id, front, back, due_at, created_at,
                       interval, ease_factor, repetitions
                FROM flashcards
                WHERE document_id = ? AND user_id = ?
                ORDER BY due_at ASC, created_at ASC
                """,
                (document_id, user_id),
            ).fetchall()
        return [self._flashcard_from_row(row) for row in rows]

    def list_due_flashcards(
        self,
        user_id: int,
        *,
        due_at: str | None = None,
    ) -> list[ReviewQueueEntry]:
        cutoff = due_at or datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT f.id, f.document_id, f.checkpoint_id, f.front, f.back, f.due_at,
                       f.created_at, f.interval, f.ease_factor, f.repetitions,
                       d.title AS document_title, c.frame_index AS source_frame_index
                FROM flashcards f
                JOIN documents d ON d.id = f.document_id AND d.user_id = f.user_id
                JOIN checkpoints c ON c.id = f.checkpoint_id AND c.user_id = f.user_id
                WHERE f.user_id = ? AND f.due_at <= ?
                ORDER BY f.due_at ASC, f.created_at ASC
                """,
                (user_id, cutoff),
            ).fetchall()
        return [
            ReviewQueueEntry(
                card=self._flashcard_from_row(row),
                document_title=str(row["document_title"]),
                source_frame_index=int(row["source_frame_index"]),
            )
            for row in rows
        ]

    def delete_flashcard(self, user_id: int, document_id: str, flashcard_id: str) -> None:
        with self._connect() as connection:
            deleted = connection.execute(
                """
                DELETE FROM flashcards
                WHERE id = ? AND document_id = ? AND user_id = ?
                """,
                (flashcard_id, document_id, user_id),
            )
        if deleted.rowcount == 0:
            raise ValueError("Flashcard not found.")

    def update_flashcard_due(
        self,
        user_id: int,
        document_id: str,
        flashcard_id: str,
        *,
        due_at: str,
        interval: int | None = None,
        ease_factor: float | None = None,
        repetitions: int | None = None,
    ) -> FlashcardRecord:
        self.get_document(user_id, document_id)
        with self._connect() as connection:
            updated = connection.execute(
                """
                UPDATE flashcards
                SET due_at = ?,
                    interval = COALESCE(?, interval),
                    ease_factor = COALESCE(?, ease_factor),
                    repetitions = COALESCE(?, repetitions)
                WHERE id = ? AND document_id = ? AND user_id = ?
                """,
                (
                    due_at,
                    interval,
                    ease_factor,
                    repetitions,
                    flashcard_id,
                    document_id,
                    user_id,
                ),
            )
            if updated.rowcount == 0:
                raise ValueError("Flashcard not found.")
        cards = self.list_flashcards(user_id, document_id)
        for card in cards:
            if card.id == flashcard_id:
                return card
        raise ValueError("Flashcard not found.")

    def _storage_path(self, user_id: int, document_id: str) -> Path:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT storage_path FROM documents WHERE id = ? AND user_id = ?",
                (document_id, user_id),
            ).fetchone()
        if row is None:
            raise ValueError("Document not found.")
        return Path(str(row["storage_path"]))

    def _chapter_cache_dir(self, user_id: int, document_id: str) -> Path:
        storage_path = self._storage_path(user_id, document_id)
        if storage_path.name.startswith("source."):
            return storage_path.parent
        return storage_path.parent / f"{storage_path.stem}_cache"

    @staticmethod
    def _checkpoint_from_row(row: sqlite3.Row) -> CheckpointRecord:
        return CheckpointRecord(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            frame_index=int(row["frame_index"]),
            questions_json=str(row["questions_json"]),
            answers_json=str(row["answers_json"]) if row["answers_json"] else None,
            confidence_json=str(row["confidence_json"]) if row["confidence_json"] else None,
            score=float(row["score"]) if row["score"] is not None else None,
            weak=bool(row["weak"]),
            created_at=str(row["created_at"]),
        )

    @staticmethod
    def _flashcard_from_row(row: sqlite3.Row) -> FlashcardRecord:
        return FlashcardRecord(
            id=str(row["id"]),
            document_id=str(row["document_id"]),
            checkpoint_id=str(row["checkpoint_id"]),
            front=str(row["front"]),
            back=str(row["back"]),
            due_at=str(row["due_at"]),
            created_at=str(row["created_at"]),
            interval=int(row["interval"]),
            ease_factor=float(row["ease_factor"]),
            repetitions=int(row["repetitions"]),
        )

    def record_learning_event(
        self,
        user_id: int,
        event_type: str,
        *,
        document_id: str | None = None,
        chapter_index: int | None = None,
        frame_index: int | None = None,
        wpm: int | None = None,
        self_check_score: float | None = None,
        card_grade: str | None = None,
        due_interval: int | None = None,
    ) -> None:
        created_at = datetime.now(tz=UTC).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO learning_events (
                    user_id, document_id, event_type, created_at,
                    chapter_index, frame_index, wpm, self_check_score,
                    card_grade, due_interval
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    document_id,
                    event_type,
                    created_at,
                    chapter_index,
                    frame_index,
                    wpm,
                    self_check_score,
                    card_grade,
                    due_interval,
                ),
            )

    def checkpoint_scores_with_wpm(
        self,
        user_id: int,
        *,
        since: str | None = None,
    ) -> list[tuple[int, float]]:
        query = """
            SELECT rp.wpm, c.score
            FROM checkpoints c
            JOIN reading_progress rp
              ON rp.document_id = c.document_id AND rp.user_id = c.user_id
            WHERE c.user_id = ? AND c.score IS NOT NULL
        """
        params: list[object] = [user_id]
        if since:
            query += " AND c.created_at >= ?"
            params.append(since)
        query += " ORDER BY c.created_at DESC"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [(int(row["wpm"]), float(row["score"])) for row in rows]

    def aggregate_time_to_first_check(self, user_id: int) -> float | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT AVG(
                    (julianday(c.created_at) - julianday(d.created_at)) * 86400000
                ) AS avg_ms
                FROM checkpoints c
                JOIN documents d ON d.id = c.document_id AND d.user_id = c.user_id
                WHERE c.user_id = ?
                  AND c.score IS NOT NULL
                  AND c.id = (
                      SELECT c2.id FROM checkpoints c2
                      WHERE c2.document_id = c.document_id
                        AND c2.user_id = c.user_id
                        AND c2.score IS NOT NULL
                      ORDER BY c2.created_at ASC LIMIT 1
                  )
                """,
                (user_id,),
            ).fetchone()
        if row is None or row["avg_ms"] is None:
            return None
        return float(row["avg_ms"])

    def aggregate_weak_stop_review_rate(self, user_id: int) -> float | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(DISTINCT c.id) AS weak_total,
                    COUNT(DISTINCT CASE
                        WHEN f.created_at IS NOT NULL
                         AND date(f.created_at) = date(c.created_at)
                        THEN c.id END) AS same_day
                FROM checkpoints c
                LEFT JOIN flashcards f
                  ON f.checkpoint_id = c.id AND f.user_id = c.user_id
                WHERE c.user_id = ? AND c.weak = 1 AND c.score IS NOT NULL
                """,
                (user_id,),
            ).fetchone()
        if row is None or not row["weak_total"]:
            return None
        return round(float(row["same_day"]) / float(row["weak_total"]), 3)

    def aggregate_again_rate(self, user_id: int) -> float | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    SUM(CASE WHEN card_grade = 'again' THEN 1 ELSE 0 END) AS again_count,
                    COUNT(*) AS total
                FROM learning_events
                WHERE user_id = ? AND event_type = 'review_grade'
                """,
                (user_id,),
            ).fetchone()
        if row is None or not row["total"]:
            return None
        return round(float(row["again_count"]) / float(row["total"]), 3)

    def aggregate_resume_rate(self, user_id: int, *, days: int) -> float | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(DISTINCT document_id) AS resumed,
                    (SELECT COUNT(*) FROM documents WHERE user_id = ?) AS total
                FROM learning_events
                WHERE user_id = ?
                  AND event_type = 'resume'
                  AND created_at >= datetime('now', ?)
                """,
                (user_id, user_id, f"-{days} days"),
            ).fetchone()
        if row is None or not row["total"]:
            return None
        return round(float(row["resumed"]) / float(row["total"]), 3)

    def aggregate_wpm_band_scores(self, user_id: int) -> list[dict[str, object]]:
        rows = self.checkpoint_scores_with_wpm(user_id)
        bands: dict[str, list[float]] = {}
        for wpm, score in rows:
            if wpm <= 250:
                label = "reflective"
            elif wpm <= 320:
                label = "deep"
            elif wpm <= 350:
                label = "stretch"
            else:
                label = "skim_risk"
            bands.setdefault(label, []).append(score)
        return [
            {
                "band": band,
                "average_self_check": round(sum(scores) / len(scores), 3),
                "count": len(scores),
            }
            for band, scores in sorted(bands.items())
        ]

    @staticmethod
    def _ensure_column(
        connection: sqlite3.Connection,
        table: str,
        column: str,
        definition: str,
    ) -> None:
        columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})").fetchall()}
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection
