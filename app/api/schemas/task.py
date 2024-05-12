import datetime
from typing import List, Optional, Set, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field

from app.api.schemas.group import GroupReturn

class TaskBaseScheme(BaseModel):

    description: str = Field(title='Описание задачи (напр. "Приготовить обед")"',
                             default="", min_length=5)
    priority: Optional[int] = Field(default=1, description="Приоритет от 1 до 3",
                                    ge=1, le=3)
    expire_on: Optional[datetime.date] = Field(default_factory=datetime.datetime.now().date)


class TaskToGroups(TaskBaseScheme):
    groups: List[str] = Field(default=[''])


class TaskToUsers(TaskBaseScheme):
    users: List[str] = Field(default=[''])


class TaskBaseReturnScheme(TaskBaseScheme):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    updated_at: Optional[datetime.date]


class TaskToGroupReturnScheme(TaskBaseScheme):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    updated_at: Optional[datetime.date]
    groups: List[GroupReturn]

    @field_validator("groups")
    @classmethod
    def correct_output(cls, groups) -> List[str]:
        return [g.name for g in groups]


class TaskReturnList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def total(self) -> int:
        return len(self.tasks)

    tasks: Union[List[TaskBaseReturnScheme], Set[TaskBaseReturnScheme]]
    
    @field_validator("tasks")
    @classmethod
    def sort_tasks(cls,  tasks: List) -> List[TaskToGroupReturnScheme]:
        return sorted(tasks, key=lambda x: (x.expire_on, x.priority), reverse=True)
