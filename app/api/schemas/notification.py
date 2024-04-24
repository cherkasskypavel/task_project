from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

from app.api.schemas.task import TaskToGroupReturnScheme


class BaseNotification(BaseModel):
    message: str
    task: Optional[Any]  # добавить TypeVar, как только для юзеров добавится ендпоинт


class NewGroupTaskNotification(BaseNotification):
    model_config = ConfigDict(from_attributes=True)
    

    message: str = "Назначена новая задача для группы"
    task: TaskToGroupReturnScheme