from abc import ABC, abstractmethod
import datetime
from sqlalchemy import insert, select, update, delete
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):

    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError
    
    @abstractmethod
    async def get_one(self, **filter):
        raise NotImplementedError
    
    @abstractmethod
    async def get_all(self, **filter):
        raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, id: int):
        raise NotImplementedError    
    
    
    async def update_many(self, data: dict, **criteria):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self, **criteria):
        raise NotImplementedError


class SARepository(AbstractRepository):
    model = None

    SQL_COMPARE = {
        int: "==",
        str: "LIKE",
        datetime.date: "<"
    }

    def __init__(self, session: AsyncSession):
        self.session = session


    async def add_one(self, data: dict):
        stmt = insert(self.model)\
            .values(**data)\
            .returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()
    

    async def get_all(self, **filter):
        if filter:
            stmt = select(self.model)\
                .filter_by(**filter)
        else:
            stmt = select(self.model)
        res = await self.session.execute(stmt)
        return res.scalars().all()
    

    async def get_one(self, **filter):
        if filter:
            stmt = select(self.model)\
                .filter_by(**filter)
        else:
            stmt = select(self.model)
            
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()


    async def update(self, data: dict, id: int):
        stmt = update(self.model)\
            .where(self.model.id == id)\
            .values(**data)\
            .returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    
    async def delete(self, id: int):
        stmt = delete(self.model)\
            .where(self.model.id == id)\
            .returning(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    

    async def delete_many(self, **criteria):
        criteria_string = " AND ".join([f"{x[0]} {self.SQL_COMPARE[type(x[1])]} {repr(str(x[1]))}" for x in criteria.items()])
        stmt = text(
            f'''DELETE FROM {self.model.__tablename__}
            WHERE {self.model.__tablename__}.{criteria_string} 
            RETURNING {self.model.__tablename__}.id;'''
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
        

    async def update_many(self, data: dict, **criteria):
        criteria_string = " AND ".join([f"{x[0]} {self.SQL_COMPARE[type(x[1])]} {repr(str(x[1]))}" for x in criteria.items()])
        values_string = ", ".join([f"{x[0]} = {repr(str(x[1]))}" for x in data.items()])
        stmt = text(
            f'''UPDATE {self.model.__tablename__}
            SET {values_string}
            WHERE {self.model.__tablename__}.{criteria_string} 
            RETURNING {self.model.__tablename__}.id;'''
        )
        print(stmt)

        result = await self.session.execute(stmt)
        
        return result.scalars().all()