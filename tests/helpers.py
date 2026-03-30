from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4
from library_catalog.data.models.book import Book

def make_book_kwargs(**overrides) -> dict:
    """Return minimal valid kwargs for creating a Book."""
    defaults = dict(
        title="Clean Code",
        author="Robert C. Martin",
        year=2008,
        genre="Programming",
        pages=431,
        available=True,
        isbn=None,
        description=None,
        extra=None,
    )
    defaults.update(overrides)
    return defaults


def make_mock_book(**overrides):
    """Return MagicMock that mimics a Book ORM object."""
    mock_book = MagicMock(spec=Book)
    mock_book.book_id = uuid4()
    mock_book.title = "Clean Code"
    mock_book.author = "Robert Martin"
    mock_book.year = 2008
    mock_book.genre = "Programming"
    mock_book.pages = 464
    mock_book.available = True
    mock_book.isbn = "978-0132350884"
    mock_book.description = None
    mock_book.extra = None
    mock_book.created_at = datetime.now(timezone.utc)
    mock_book.updated_at = datetime.now(timezone.utc)
    for key, value in overrides.items():
        setattr(mock_book, key, value)
    return mock_book