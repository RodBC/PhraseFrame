from pathlib import Path

import pytest

from phraseframe.adapters.pdf import build_sample_pdf
from phraseframe.db.store import LibraryStore


@pytest.fixture
def store(tmp_path: Path) -> LibraryStore:
    library = LibraryStore(db_path=tmp_path / "test.db", storage_path=tmp_path / "docs")
    library.init_schema()
    return library


def test_user_registration_and_authentication(store: LibraryStore) -> None:
    created = store.create_user("reader@example.com", "secret-pass")
    assert created.email == "reader@example.com"
    authenticated = store.authenticate("reader@example.com", "secret-pass")
    assert authenticated.id == created.id
    with pytest.raises(ValueError, match="incorrect"):
        store.authenticate("reader@example.com", "wrong-pass")


def test_document_upload_and_progress(store: LibraryStore) -> None:
    user = store.create_user("reader@example.com", "secret-pass")
    content = build_sample_pdf()
    document = store.save_document(user.id, "book.pdf", "Think", "pdf", content)
    listed = store.list_documents_with_progress(user.id)
    assert len(listed) == 1
    assert listed[0].title == "Think"
    assert listed[0].has_progress is False
    progress = store.save_progress(
        user.id,
        document.id,
        chapter_index=1,
        frame_index=42,
        wpm=280,
        target_words=4,
    )
    assert progress.frame_index == 42
    resumed = store.get_progress(user.id, document.id)
    assert resumed is not None
    assert resumed.chapter_index == 1
    assert store.read_document_bytes(user.id, document.id) == content
    with_progress = store.list_documents_with_progress(user.id)
    assert with_progress[0].has_progress is True
