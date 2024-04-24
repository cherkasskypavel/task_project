from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import SARepository
from app.db.database import session_maker


class IUnitOfWork(ABC):
    repositories: List[SARepository]

    @abstractmethod
    def __init__(self):
        ...
    
    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, *args):
        ...

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

    @abstractmethod
    async def flush(self, *objects):
        ...

    @abstractmethod
    async def refresh(self, obj):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = session_maker


    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.repositories = [r(self.session) for r in self.repositories]


    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()
        self.repositories = [r.__class__ for r in self.repositories]

    async def commit(self):
        await self.session.commit()


    async def rollback(self):
        await self.session.rollback()


    async def flush(self, *objects):
        if objects is None:
            await self.session.flush()
        else:
            await self.session.flush(*objects)


    async def refresh(self, obj):
        await self.session.refresh(obj)
