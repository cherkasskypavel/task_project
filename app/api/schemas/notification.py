from typing import Any, Optional
from pydantic import BaseModel, ConfigDict

from app.api.schemas.task import TaskBaseReturnScheme


class BaseNotification(BaseModel):
    message: str
    task: Optional[Any]  # добавить TypeVar, как только для юзеров добавится ендпоинт


class GroupTaskNotification(BaseNotification):
    model_config = ConfigDict(from_attributes=True)
    

    message: str = "Задача обновлена"
    task: TaskBaseReturnScheme

