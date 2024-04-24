import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class TaskToGroupReturnScheme(TaskBaseScheme):
    model_config = ConfigDict(from_attributes=True)
    id: int
    groups: List[GroupReturn]

    @field_validator("groups")
    @classmethod
    def correct_output(cls, value):
        return [g.name for g in value]

    
class TaskUpdateScheme(BaseModel):
    id: int
    status: str

