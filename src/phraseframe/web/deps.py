"""FastAPI dependencies for authenticated routes."""

from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from phraseframe.auth.jwt import decode_access_token
from phraseframe.db.store import LibraryStore, User

security = HTTPBearer(auto_error=False)


def get_store(request: Request) -> LibraryStore:
    store = getattr(request.app.state, "store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="Library storage is unavailable.")
    return cast(LibraryStore, store)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    store: Annotated[LibraryStore, Depends(get_store)],
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Sign in to access your library.")
    try:
        user_id = decode_access_token(credentials.credentials)
        return store.get_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=401, detail="Session expired. Sign in again.") from error
    except Exception as error:
        raise HTTPException(status_code=401, detail="Session expired. Sign in again.") from error
