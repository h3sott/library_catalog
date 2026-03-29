from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    def _build_filter_conditions(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
    ) -> list:
        conditions = []
        if title is not None:
            conditions.append(Book.title.ilike(f"%{title}%"))
        if author is not None:
            conditions.append(Book.author.ilike(f"%{author}%"))
        if genre is not None:
            conditions.append(Book.genre == genre)
        if year is not None:
            conditions.append(Book.year == year)
        if available is not None:
            conditions.append(Book.available == available)
        return conditions

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
        for condition in self._build_filter_conditions(title, author, genre, year, available):
            stmt = stmt.where(condition)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN."""
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
    ) -> int:
        """Подсчитать количество книг по фильтрам."""
        stmt = select(func.count()).select_from(Book)
        for condition in self._build_filter_conditions(title, author, genre, year, available):
            stmt = stmt.where(condition)
        result = await self.session.execute(stmt)
        return result.scalar_one()
