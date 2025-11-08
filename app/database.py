from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase  # New


# Строка подключения для SQLite
DATABASE_URL = "sqlite:///ecommerce.db" # Для абсолютного пути используйте четыре слэша, например, sqlite:////absolute/path/to/ecommerce.db.


# Создаём Engine
engine = create_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
SessionLocal = sessionmaker(bind=engine)

# Также SQLAlchemy поддерживает различные базы данных через единый формат URL:
#
# dialect+driver://username:password@host:port/database


# --------------- Асинхронное подключение к PostgreSQL -------------------------

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Строка подключения для PostgreSQl
DATABASE_URL = "postgresql+asyncpg://ecommerce_user:password@localhost:5432/ecommerce_db"

# Создаём Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

# Определяем базовый класс для моделей
class Base(DeclarativeBase):  # New
    pass