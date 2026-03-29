import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import make_book_kwargs
from library_catalog.data.models.book import Book
from library_catalog.data.repositories.book_repository import BookRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def repo(test_db: AsyncSession) -> BookRepository:
    return BookRepository(test_db)


@pytest_asyncio.fixture
async def book(repo: BookRepository) -> Book:
    """Single persisted book used across multiple tests."""
    return await repo.create(**make_book_kwargs())


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------

class TestCreate:
    async def test_returns_book_with_generated_id(self, repo: BookRepository):
        book = await repo.create(**make_book_kwargs())

        assert book.book_id is not None
        assert book.title == "Clean Code"

    async def test_created_at_is_populated(self, repo: BookRepository):
        book = await repo.create(**make_book_kwargs())

        assert book.created_at is not None

    async def test_duplicate_isbn_raises(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(isbn="978-0132350884", title="First"))

        with pytest.raises(Exception):  # asyncpg IntegrityError
            await repo.create(**make_book_kwargs(isbn="978-0132350884", title="Second"))


# ---------------------------------------------------------------------------
# get_by_id
# ---------------------------------------------------------------------------

class TestGetById:
    async def test_returns_correct_book(self, repo: BookRepository, book: Book):
        found = await repo.get_by_id(book.book_id)

        assert found is not None
        assert found.book_id == book.book_id

    async def test_returns_none_for_unknown_id(self, repo: BookRepository):
        found = await repo.get_by_id(uuid.uuid4())

        assert found is None


# ---------------------------------------------------------------------------
# find_by_isbn
# ---------------------------------------------------------------------------

class TestFindByIsbn:
    async def test_finds_existing_isbn(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(isbn="978-0132350884"))

        found = await repo.find_by_isbn("978-0132350884")

        assert found is not None
        assert found.isbn == "978-0132350884"

    async def test_returns_none_for_unknown_isbn(self, repo: BookRepository):
        found = await repo.find_by_isbn("000-0000000000")

        assert found is None


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------

class TestUpdate:
    async def test_updates_given_fields(self, repo: BookRepository, book: Book):
        updated = await repo.update(book.book_id, title="Refactoring", pages=500)

        assert updated is not None
        assert updated.title == "Refactoring"
        assert updated.pages == 500

    async def test_untouched_fields_stay_unchanged(self, repo: BookRepository, book: Book):
        original_author = book.author

        await repo.update(book.book_id, title="New Title")
        refreshed = await repo.get_by_id(book.book_id)

        assert refreshed.author == original_author

    async def test_returns_none_for_unknown_id(self, repo: BookRepository):
        result = await repo.update(uuid.uuid4(), title="Ghost")

        assert result is None


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------

class TestDelete:
    async def test_deletes_book_and_returns_true(self, repo: BookRepository, book: Book):
        result = await repo.delete(book.book_id)

        assert result is True
        assert await repo.get_by_id(book.book_id) is None

    async def test_returns_false_for_unknown_id(self, repo: BookRepository):
        result = await repo.delete(uuid.uuid4())

        assert result is False


# ---------------------------------------------------------------------------
# get_all
# ---------------------------------------------------------------------------

class TestGetAll:
    async def test_returns_created_books(self, repo: BookRepository):
        for i in range(3):
            await repo.create(**make_book_kwargs(title=f"Book {i}", isbn=f"isbn-all-{i}"))

        books = await repo.get_all()

        assert len(books) >= 3

    async def test_limit_is_respected(self, repo: BookRepository):
        for i in range(5):
            await repo.create(**make_book_kwargs(title=f"Lim {i}", isbn=f"isbn-lim-{i}"))

        page = await repo.get_all(limit=2)

        assert len(page) == 2

    async def test_offset_returns_different_page(self, repo: BookRepository):
        for i in range(4):
            await repo.create(**make_book_kwargs(title=f"Off {i}", isbn=f"isbn-off-{i}"))

        first = {b.book_id for b in await repo.get_all(limit=2, offset=0)}
        second = {b.book_id for b in await repo.get_all(limit=2, offset=2)}

        assert first.isdisjoint(second)


# ---------------------------------------------------------------------------
# find_by_filters
# ---------------------------------------------------------------------------

class TestFindByFilters:
    async def test_filter_by_title_case_insensitive(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="Design Patterns"))

        results = await repo.find_by_filters(title="design")

        assert any(b.title == "Design Patterns" for b in results)

    async def test_filter_by_author_case_insensitive(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="TDD", author="Kent Beck"))

        results = await repo.find_by_filters(author="kent")

        assert any(b.author == "Kent Beck" for b in results)

    async def test_filter_by_genre(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="Genre Book", genre="Fiction"))
        await repo.create(**make_book_kwargs(title="Other Book", genre="Science", isbn="isbn-sci"))

        results = await repo.find_by_filters(genre="Fiction")

        assert all(b.genre == "Fiction" for b in results)

    async def test_filter_by_year(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="Old Book", year=1999, isbn="isbn-1999"))
        await repo.create(**make_book_kwargs(title="New Book", year=2020, isbn="isbn-2020"))

        results = await repo.find_by_filters(year=1999)

        assert all(b.year == 1999 for b in results)

    async def test_filter_by_available_true(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="Available", available=True, isbn="isbn-av"))
        await repo.create(**make_book_kwargs(title="Unavailable", available=False, isbn="isbn-unav"))

        results = await repo.find_by_filters(available=True)

        assert all(b.available is True for b in results)

    async def test_filter_by_available_false(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(title="Taken", available=False, isbn="isbn-taken"))

        results = await repo.find_by_filters(available=False)

        assert all(b.available is False for b in results)

    async def test_combined_filters(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(
            title="Python Cookbook", author="David Beazley",
            genre="Programming", year=2013, isbn="isbn-pyc"
        ))
        await repo.create(**make_book_kwargs(
            title="Fluent Python", author="Luciano Ramalho",
            genre="Programming", year=2015, isbn="isbn-fp"
        ))

        results = await repo.find_by_filters(genre="Programming", year=2013)

        assert len(results) == 1
        assert results[0].title == "Python Cookbook"

    async def test_no_results_for_unmatched_filter(self, repo: BookRepository):
        results = await repo.find_by_filters(title="zzz_nonexistent_zzz")

        assert results == []

    async def test_limit_and_offset_in_filters(self, repo: BookRepository):
        for i in range(5):
            await repo.create(**make_book_kwargs(
                title=f"Filter Pag {i}", genre="Mystery", isbn=f"isbn-myst-{i}"
            ))

        first = await repo.find_by_filters(genre="Mystery", limit=2, offset=0)
        second = await repo.find_by_filters(genre="Mystery", limit=2, offset=2)

        assert len(first) == 2
        ids_first = {b.book_id for b in first}
        ids_second = {b.book_id for b in second}
        assert ids_first.isdisjoint(ids_second)


# ---------------------------------------------------------------------------
# count_by_filters
# ---------------------------------------------------------------------------

class TestCountByFilters:
    async def test_counts_all_books(self, repo: BookRepository):
        initial = await repo.count_by_filters()

        await repo.create(**make_book_kwargs(isbn="isbn-cnt-1"))
        await repo.create(**make_book_kwargs(isbn="isbn-cnt-2", title="Another"))

        total = await repo.count_by_filters()

        assert total == initial + 2

    async def test_counts_by_genre(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(genre="History", isbn="isbn-hist-1"))
        await repo.create(**make_book_kwargs(genre="History", isbn="isbn-hist-2", title="B"))
        await repo.create(**make_book_kwargs(genre="Math", isbn="isbn-math-1", title="C"))

        count = await repo.count_by_filters(genre="History")

        assert count == 2

    async def test_counts_by_year(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(year=2000, isbn="isbn-y2k-1"))
        await repo.create(**make_book_kwargs(year=2000, isbn="isbn-y2k-2", title="B"))

        count = await repo.count_by_filters(year=2000)

        assert count == 2

    async def test_count_zero_for_no_match(self, repo: BookRepository):
        count = await repo.count_by_filters(title="zzz_nonexistent_zzz")

        assert count == 0

    async def test_combined_filters_count(self, repo: BookRepository):
        await repo.create(**make_book_kwargs(
            genre="Physics", available=True, isbn="isbn-phys-av"
        ))
        await repo.create(**make_book_kwargs(
            genre="Physics", available=False, isbn="isbn-phys-unav", title="B"
        ))

        count = await repo.count_by_filters(genre="Physics", available=True)

        assert count == 1