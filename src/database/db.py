from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from src.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.ASYNC_SQLITE_ALCHEMY_URI, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
