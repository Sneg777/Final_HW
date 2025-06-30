import contextlib
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from src.conf.config import config


class DataBaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url, echo=True)
        self._session_maker = async_sessionmaker(autoflush=False, autocommit=False, bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session maker not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as e:
            print(f"Rollback because of exception: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DataBaseSessionManager(config.DB_URL)


async def get_db() -> AsyncSession:
    async with sessionmanager.session() as session:
        yield session
