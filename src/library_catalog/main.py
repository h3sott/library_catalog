"""
Library Catalog API - Точка входа приложения.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import dispose_engine
from .core.exceptions import register_exception_handlers
from .core.logging_config import setup_logging
from .api.v1.routers import books, health


# ========== LIFECYCLE EVENTS ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager для FastAPI.

    Выполняется при:
    - startup: настройка логирования
    - shutdown: закрытие подключений к БД
    """
    # Startup
    setup_logging()
    print("🚀 Application started")

    yield

    # Shutdown
    await dispose_engine()
    print("👋 Application stopped")


# ========== CREATE APP ==========

app = FastAPI(
    title=settings.app_name,
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

# ========== MIDDLEWARE ==========

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== EXCEPTION HANDLERS ==========

register_exception_handlers(app)

# ========== ROUTERS ==========

# Версия 1 API
app.include_router(
    books.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    health.router,
    prefix=settings.api_v1_prefix,
)


# ========== ROOT ENDPOINT ==========

@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Welcome to Library Catalog API",
        "docs": settings.docs_url,
        "version": "1.0.0",
    }


# ========== RUN ==========

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )