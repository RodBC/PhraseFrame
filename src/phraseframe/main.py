"""PhraseFrame ASGI application."""

import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from phraseframe.db.store import LibraryStore
from phraseframe.web.routes import router


def _is_production_runtime() -> bool:
    data_dir = os.environ.get("PHRASEFRAME_DATA_DIR", "data")
    return data_dir.startswith("/data") or bool(os.environ.get("PORT"))


def _configure_production_secret() -> None:
    """Use PHRASEFRAME_SECRET_KEY when set; otherwise persist one under the data dir."""
    if not _is_production_runtime():
        return

    secret = os.environ.get("PHRASEFRAME_SECRET_KEY", "").strip()
    if secret:
        return

    data_root = Path(os.environ.get("PHRASEFRAME_DATA_DIR", "data"))
    secret_file = data_root / ".secret_key"
    if secret_file.exists():
        os.environ["PHRASEFRAME_SECRET_KEY"] = secret_file.read_text().strip()
        return

    secret = secrets.token_urlsafe(48)
    data_root.mkdir(parents=True, exist_ok=True)
    secret_file.write_text(secret)
    os.environ["PHRASEFRAME_SECRET_KEY"] = secret


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    _configure_production_secret()
    store = LibraryStore.from_env()
    store.init_schema()
    app.state.store = store
    yield


app = FastAPI(
    title="PhraseFrame",
    description="Phrase-paced local reading and MP4 export",
    version="0.2.0",
    lifespan=lifespan,
)
app.include_router(router)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "web" / "static"),
    name="static",
)


def run() -> None:
    """Start the local development server."""

    uvicorn.run("phraseframe.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
