"""Minimal JWT helpers for account sessions."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import jwt


def _secret() -> str:
    return os.environ.get("PHRASEFRAME_SECRET_KEY", "phraseframe-dev-secret-change-me")


def create_access_token(user_id: int, *, hours: int = 168) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(tz=UTC) + timedelta(hours=hours),
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, _secret(), algorithms=["HS256"])
    return int(payload["sub"])
