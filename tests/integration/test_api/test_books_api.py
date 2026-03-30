"""
test_books_api.py - Integration тесты для Books API.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from library_catalog.data.models.book import Book


class TestBooksIntegration:
    """Integration тесты для Books API."""

    async def test_create_book_persisted_in_db(
            self, client: AsyncClient, test_db: AsyncSession
    ):
        """Тест что созданная книга реально сохранилась в БД."""
        book_data = {
            "title": "Persisted Book",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }

        response = await client.post("/api/v1/books/", json=book_data)
        assert response.status_code == 201
        book_id = response.json()["book_id"]

        # Проверить напрямую в БД
        result = await test_db.execute(
            select(Book).where(Book.book_id == book_id)
        )
        book = result.scalar_one_or_none()
        assert book is not None
        assert book.title == "Persisted Book"

    async def test_delete_book_removed_from_db(
            self, client: AsyncClient, test_db: AsyncSession
    ):
        """Тест что удалённая книга удалена из БД."""
        book_data = {
            "title": "To Delete",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }
        create_response = await client.post("/api/v1/books/", json=book_data)
        book_id = create_response.json()["book_id"]

        await client.delete(f"/api/v1/books/{book_id}")

        result = await test_db.execute(
            select(Book).where(Book.book_id == book_id)
        )
        book = result.scalar_one_or_none()
        assert book is None

    async def test_update_book_persisted_in_db(
            self, client: AsyncClient, test_db: AsyncSession
    ):
        """Тест что обновление книги сохранилось в БД."""
        book_data = {
            "title": "Original",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }
        create_response = await client.post("/api/v1/books/", json=book_data)
        book_id = create_response.json()["book_id"]

        await client.patch(f"/api/v1/books/{book_id}", json={"title": "Updated"})

        result = await test_db.execute(
            select(Book).where(Book.book_id == book_id)
        )
        book = result.scalar_one_or_none()
        assert book.title == "Updated"

    async def test_create_book_success(self, client: AsyncClient):
        """Тест успешного создания книги."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }

        response = await client.post("/api/v1/books/", json=book_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Book"
        assert data["author"] == "Test Author"
        assert "book_id" in data

    async def test_create_book_invalid_year(self, client: AsyncClient):
        """Тест создания книги с невалидным годом."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "year": 99999,
            "genre": "Fiction",
            "pages": 200,
        }

        response = await client.post("/api/v1/books/", json=book_data)

        assert response.status_code == 422

    async def test_create_book_invalid_pages(self, client: AsyncClient):
        """Тест создания книги с невалидным количеством страниц."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": -1,
        }

        response = await client.post("/api/v1/books/", json=book_data)

        assert response.status_code == 422

    async def test_get_book_success(self, client: AsyncClient):
        """Тест получения книги по ID."""
        # Создать книгу
        book_data = {
            "title": "Get Test Book",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }
        create_response = await client.post("/api/v1/books/", json=book_data)
        book_id = create_response.json()["book_id"]

        # Получить книгу
        response = await client.get(f"/api/v1/books/{book_id}")

        assert response.status_code == 200
        assert response.json()["book_id"] == book_id

    async def test_get_book_not_found(self, client: AsyncClient):
        """Тест получения несуществующей книги."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/books/{fake_id}")

        assert response.status_code == 404

    async def test_get_books_list(self, client: AsyncClient):
        """Тест получения списка книг."""
        response = await client.get("/api/v1/books/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data

    async def test_update_book_success(self, client: AsyncClient):
        """Тест обновления книги."""
        # Создать книгу
        book_data = {
            "title": "Original Title",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }
        create_response = await client.post("/api/v1/books/", json=book_data)
        book_id = create_response.json()["book_id"]

        # Обновить
        update_data = {"title": "Updated Title"}
        response = await client.patch(f"/api/v1/books/{book_id}", json=update_data)

        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    async def test_delete_book_success(self, client: AsyncClient):
        """Тест удаления книги."""
        # Создать книгу
        book_data = {
            "title": "Delete Test Book",
            "author": "Author",
            "year": 2020,
            "genre": "Fiction",
            "pages": 200,
        }
        create_response = await client.post("/api/v1/books/", json=book_data)
        book_id = create_response.json()["book_id"]

        # Удалить
        response = await client.delete(f"/api/v1/books/{book_id}")
        assert response.status_code == 204

        # Проверить что удалена
        response = await client.get(f"/api/v1/books/{book_id}")
        assert response.status_code == 404

    async def test_full_crud_flow(self, client: AsyncClient):
        """Тест полного CRUD цикла."""
        # CREATE
        book_data = {
            "title": "CRUD Test Book",
            "author": "CRUD Author",
            "year": 2021,
            "genre": "Science",
            "pages": 300,
        }
        response = await client.post("/api/v1/books/", json=book_data)
        assert response.status_code == 201
        book_id = response.json()["book_id"]

        # READ
        response = await client.get(f"/api/v1/books/{book_id}")
        assert response.status_code == 200

        # UPDATE
        response = await client.patch(
            f"/api/v1/books/{book_id}",
            json={"title": "Updated CRUD Book"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated CRUD Book"

        # DELETE
        response = await client.delete(f"/api/v1/books/{book_id}")
        assert response.status_code == 204