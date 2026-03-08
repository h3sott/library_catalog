from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.data.models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    async def find_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> list[Book]:

        stmt = select(Book)

        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if genre:
            stmt = stmt.where(Book.genre == genre)
        if year:
            stmt = stmt.where(Book.year == year)
        if available is not None:
            stmt = stmt.where(Book.available == available)

        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN."""
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count_by_filters(
            self,
            title: Optional[str] = None,
            author: Optional[str] = None,
            genre: Optional[str] = None,
            year: Optional[int] = None,
            available: Optional[bool] = None,
    ) -> int:
        """Подсчитать количество книг по фильтрам."""
        stmt = select(func.count()).select_from(Book)

        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if genre:
            stmt = stmt.where(Book.genre == genre)
        if year:
            stmt = stmt.where(Book.year == year)
        if available is not None:
            stmt = stmt.where(Book.available == available)

        result = await self.session.execute(stmt)
        return result.scalar_one()
