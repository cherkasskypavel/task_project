from app.core.config import settings
import sqlalchemy.ext.asyncio as asql
from sqlalchemy.orm import DeclarativeBase


engine = asql.create_async_engine(url=settings.MAIN_DB,
                                  echo=True)


session_maker = asql.async_sessionmaker(bind=engine,
                                        autoflush=False
                                        )


class Base(DeclarativeBase):
    pass