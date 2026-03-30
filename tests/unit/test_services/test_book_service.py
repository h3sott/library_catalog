"""
test_book_service.py - Unit тесты для BookService.
"""
from datetime import datetime, timezone

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from library_catalog.data.models.book import Book
from tests.helpers import make_mock_book
from library_catalog.domain.services.book_service import BookService
from library_catalog.domain.exceptions import (
    BookNotFoundException,
    BookAlreadyExistsException,
)
from library_catalog.api.v1.schemas.book import BookCreate, BookUpdate


@pytest.mark.asyncio
class TestBookService:
    """Unit тесты для BookService."""

    def _make_service(self, book_repo=None, ol_client=None):
        """Создать сервис с моками."""
        if book_repo is None:
            book_repo = AsyncMock()
        if ol_client is None:
            ol_client = AsyncMock()
            ol_client.enrich.return_value = {}
        return BookService(
            book_repository=book_repo,
            openlibrary_client=ol_client,
        )

    async def test_create_book_success(self):
        """Тест успешного создания книги."""
        # Arrange
        ol_client = AsyncMock()
        ol_client.enrich.return_value = {"cover_url": "http://example.com/cover.jpg"}

        book_repo = AsyncMock()
        book_repo.find_by_isbn.return_value = None

        # Мок возвращаемой книги
        mock_book = make_mock_book(extra={"cover_url": "http://example.com/cover.jpg"})
        book_repo.create.return_value = mock_book

        service = self._make_service(book_repo=book_repo, ol_client=ol_client)

        book_data = BookCreate(
            title="Clean Code",
            author="Robert Martin",
            year=2008,
            genre="Programming",
            pages=464,
            isbn="978-0132350884",
        )

        # Act
        result = await service.create_book(book_data)

        # Assert
        assert result.title == "Clean Code"
        assert result.author == "Robert Martin"
        ol_client.enrich.assert_called_once()

    async def test_create_book_duplicate_isbn(self):
        """Тест создания с существующим ISBN."""
        # Arrange
        book_repo = AsyncMock()
        book_repo.find_by_isbn.return_value = MagicMock(spec=Book)

        service = self._make_service(book_repo=book_repo)

        book_data = BookCreate(
            title="Book 1",
            author="Author",
            year=2020,
            genre="Fiction",
            pages=200,
            isbn="978-0132350884",
        )

        # Act & Assert
        with pytest.raises(BookAlreadyExistsException):
            await service.create_book(book_data)

    async def test_get_book_not_found(self):
        """Тест получения несуществующей книги."""
        # Arrange
        book_repo = AsyncMock()
        book_repo.get_by_id.return_value = None

        service = self._make_service(book_repo=book_repo)

        # Act & Assert
        with pytest.raises(BookNotFoundException):
            await service.get_book(uuid4())

    async def test_delete_book_not_found(self):
        """Тест удаления несуществующей книги."""
        # Arrange
        book_repo = AsyncMock()
        book_repo.delete.return_value = False

        service = self._make_service(book_repo=book_repo)

        # Act & Assert
        with pytest.raises(BookNotFoundException):
            await service.delete_book(uuid4())

    async def test_update_book_not_found(self):
        """Тест обновления несуществующей книги."""
        # Arrange
        book_repo = AsyncMock()
        book_repo.get_by_id.return_value = None

        service = self._make_service(book_repo=book_repo)

        # Act & Assert
        with pytest.raises(BookNotFoundException):
            await service.update_book(uuid4(), BookUpdate(title="New Title"))