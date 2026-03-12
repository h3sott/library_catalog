# 📚 Library Catalog API

REST API для управления библиотечным каталогом на FastAPI с многослойной архитектурой.

## Технологии

| Компонент | Технология |
|-----------|------------|
| Web Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| HTTP Client | httpx |
| Dependencies | Poetry |

## Архитектура

Проект построен на четырёх независимых слоях:

```
API Layer (api/)          — HTTP эндпоинты, валидация запросов
      ↓
Domain Layer (domain/)    — Бизнес-логика, правила
      ↓
Data Layer (data/)        — Работа с БД, репозитории
External Layer (external/) — HTTP клиенты к внешним API
```

## Функциональность

- CRUD операции с книгами
- Поиск и фильтрация по названию, автору, жанру, году, доступности
- Автоматическое обогащение данных из Open Library API
- Пагинация результатов
- Обработка ошибок

## Структура проекта

```
src/library_catalog/
├── api/v1/
│   ├── routers/        # HTTP эндпоинты
│   └── schemas/        # Pydantic схемы
├── core/               # Конфиг, БД, логирование, исключения
├── data/
│   ├── models/         # SQLAlchemy модели
│   └── repositories/   # CRUD операции
├── domain/
│   ├── services/       # Бизнес-логика
│   ├── mappers/        # Entity ↔ DTO
│   └── exceptions.py   # Доменные исключения
└── external/
    └── openlibrary/    # Open Library API клиент
```

## Установка и запуск

### Требования

- Python 3.11+
- Poetry
- Docker Desktop

### Запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/h3sott/library_catalog.git
cd library_catalog

# 2. Установить зависимости
poetry install

# 3. Создать .env файл
cp .env.example .env

# 4. Запустить PostgreSQL
docker-compose up -d postgres

# 5. Применить миграции
alembic upgrade head

# 6. Запустить сервер
poetry run uvicorn library_catalog.main:app --reload --app-dir src
```

### Переменные окружения

```env
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_catalog
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
```

## API Документация

После запуска доступна по адресам:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/v1/books | Создать книгу |
| GET | /api/v1/books | Получить список книг |
| GET | /api/v1/books/{id} | Получить книгу по ID |
| PATCH | /api/v1/books/{id} | Обновить книгу |
| DELETE | /api/v1/books/{id} | Удалить книгу |
| GET | /api/v1/health | Health check |

## Миграции

```bash
# Создать миграцию
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить миграцию
alembic downgrade -1
```