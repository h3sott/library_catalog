from uuid import UUID
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ShowBook(BaseModel):
    """DTO для отображения книги в API."""

    book_id: UUID
    title: str
    author: str
    year: int
    genre: str | None = None
    pages: int
    available: bool
    isbn: str | None = None
    description: str | None = None
    extra: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True