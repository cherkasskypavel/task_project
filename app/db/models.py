from __future__ import annotations
from typing import List, Optional
from datetime import date, datetime

from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint
from sqlalchemy import func, event
from sqlalchemy.orm import relationship 
from sqlalchemy.orm import Mapped, MappedColumn
from sqlalchemy.orm import validates
from sqlalchemy.orm import ORMExecuteState, with_expression, with_loader_criteria

from app.db.database import Base


user_group_table = Table(
    "usergroup",
    Base.metadata,
    Column("user_id", ForeignKey("user.id", primary_key=True)),
    Column("group_id", ForeignKey("group.id", primary_key=True)),
    UniqueConstraint('user_id', 'group_id')
)


# user_task_table = Table(
#     "user_task",
#     Base.metadata,
#     Column("user_id", ForeignKey("user.id", primary_key=True)),
#     Column("task_id", ForeignKey("task.id", primary_key=True)),
#     UniqueConstraint("user_id", "task_id")
# )


group_task_table = Table(
    "group_task",
    Base.metadata,
    Column("group_id", ForeignKey("group.id", primary_key=True)),
    Column("task_id", ForeignKey("task.id", primary_key=True, ondelete="CASCADE")),
    UniqueConstraint('group_id', 'task_id')
)




class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    email: Mapped[str] = MappedColumn()
    username: Mapped[str] = MappedColumn()
    password: Mapped[str] = MappedColumn()
    role: Mapped[str] = MappedColumn(default="user")

    group: Mapped[List[Group]] = relationship(
        "Group", secondary=user_group_table,
        back_populates="members",
        lazy="selectin"
    )
    

class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    name: Mapped[str] = MappedColumn()
    description: Mapped[Optional[str]] = MappedColumn()

    members: Mapped[List[User]] = relationship(
        "User", secondary=user_group_table,
        back_populates="group",
        lazy="selectin"
    )

    tasks: Mapped[List[Task]] = relationship(
        "Task", secondary=group_task_table,
            back_populates="groups",
            lazy="selectin",
    )



class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = MappedColumn(primary_key=True, autoincrement=True)
    description: Mapped[str] = MappedColumn()
    author: Mapped[str] = MappedColumn()
    priority: Mapped[int] = MappedColumn(default=1)
    expire_on: Mapped[date] = MappedColumn(server_default=func.current_date())
    status: Mapped[str] = MappedColumn(default="created")
    updated_at: Mapped[date] = MappedColumn(server_default=func.current_date(),
                                            onupdate=func.current_date())

    groups: Mapped[List[Group]] = relationship(
        "Group", secondary=group_task_table,
        back_populates="tasks",
        lazy="selectin",
        cascade="all, delete"
    )
    
    @validates('status')
    def validate_task_status(self, key, value):
        if self.expire_on < self.updated_at:
            return "expired"
        return value
    
# @event.listens_for(Task, 'do_orm_execute')
# def recieve_do_orm_execute(execute_state: ORMExecuteState):
#     print(execute_state, "<-------------------------------------------orm_execute_state")
#     if execute_state.is_update:
#         execute_state
