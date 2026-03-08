from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# ====================== Создание книги ======================
class BookCreate(BaseModel):
    title: str
    author: str
    year: int
    genre: Optional[str] = None
    pages: int
    isbn: Optional[str] = None
    description: Optional[str] = None

# ====================== Обновление книги ======================
class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None
    pages: Optional[int] = None
    isbn: Optional[str] = None
    description: Optional[str] = None

# ====================== DTO для отображения книги ======================
class ShowBook(BaseModel):
    book_id: UUID
    title: str
    author: str
    year: int
    genre: Optional[str] = None
    pages: int
    isbn: Optional[str] = None
    description: Optional[str] = None
    extra: Optional[dict] = None
    available: bool
    created_at: datetime
    updated_at: datetime
