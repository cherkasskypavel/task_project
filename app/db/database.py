import sqlalchemy.ext.asyncio as asql
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = asql.create_async_engine(url=settings.MAIN_DB,
                                  echo=True)


session_maker = asql.async_sessionmaker(bind=engine,
                                        autoflush=False
                                        )


# async def get_session():
#     async with session_maker() as session:
#         yield session


class Base(DeclarativeBase):
    pass