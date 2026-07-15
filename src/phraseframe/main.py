"""PhraseFrame ASGI application."""

from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from phraseframe.web.routes import router

app = FastAPI(
    title="PhraseFrame",
    description="Phrase-paced local reading and MP4 export",
    version="0.1.0",
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
