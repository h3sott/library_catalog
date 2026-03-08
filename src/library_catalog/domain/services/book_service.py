from uuid import UUID
from ...api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from ...data.repositories.book_repository import BookRepository
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import *
from ..mappers.book_mapper import BookMapper


class BookService:
    """
    Сервис для работы с книгами.

    Содержит всю бизнес-логику приложения.
    """

    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    async def create_book(self, book_data: BookCreate) -> ShowBook:
        """
        Создать новую книгу с обогащением из Open Library.
        """

        # 1. Валидация
        self._validate_book_data(book_data)

        # 2. Проверка уникальности ISBN
        if book_data.isbn:
            existing = await self.book_repo.find_by_isbn(book_data.isbn)
            if existing:
                raise BookAlreadyExistsException(book_data.isbn)

        # 3. Обогащение данных
        extra = await self._enrich_book_data(book_data)

        # 4. Создание
        book = await self.book_repo.create(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            genre=book_data.genre,
            pages=book_data.pages,
            isbn=book_data.isbn,
            description=book_data.description,
            extra=extra,
        )

        return BookMapper.to_show_book(book)

    async def get_book(self, book_id: UUID) -> ShowBook:
        """Получить книгу по ID."""

        book = await self.book_repo.get_by_id(book_id)

        if book is None:
            raise BookNotFoundException(book_id)

        return BookMapper.to_show_book(book)

    async def update_book(
        self,
        book_id: UUID,
        book_data: BookUpdate,
    ) -> ShowBook:
        """Обновить книгу."""

        existing = await self.book_repo.get_by_id(book_id)

        if existing is None:
            raise BookNotFoundException(book_id)

        if book_data.year is not None:
            self._validate_year(book_data.year)

        if book_data.pages is not None:
            self._validate_pages(book_data.pages)

        updated = await self.book_repo.update(
            book_id,
            **book_data.dict(exclude_unset=True)
        )

        return BookMapper.to_show_book(updated)

    async def delete_book(self, book_id: UUID) -> None:
        """Удалить книгу."""

        deleted = await self.book_repo.delete(book_id)

        if not deleted:
            raise BookNotFoundException(book_id)

    async def search_books(
        self,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        year: int | None = None,
        available: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[ShowBook], int]:
        """
        Поиск книг.
        """

        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        total = await self.book_repo.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )

        return BookMapper.to_show_books(books), total

    # =========================
    # PRIVATE METHODS
    # =========================

    def _validate_book_data(self, data: BookCreate) -> None:
        """Валидация новой книги."""
        self._validate_year(data.year)
        self._validate_pages(data.pages)

    def _validate_year(self, year: int) -> None:
        """Проверить год."""

        from datetime import datetime

        current_year = datetime.now().year

        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    def _validate_pages(self, pages: int) -> None:
        """Проверить страницы."""

        if pages <= 0:
            raise InvalidPagesException(pages)

    async def _enrich_book_data(
        self,
        book_data: BookCreate
    ) -> dict | None:
        """
        Получить дополнительные данные из OpenLibrary.
        """

        try:
            extra = await self.ol_client.enrich(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
            )

            return extra if extra else None

        except OpenLibraryException:

            import logging

            logger = logging.getLogger(__name__)

            logger.warning(
                "Failed to enrich book data from Open Library",
                extra={
                    "title": book_data.title,
                    "author": book_data.author,
                },
            )

            return None