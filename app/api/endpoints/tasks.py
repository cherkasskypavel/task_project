from fastapi import APIRouter, Depends

from app.services.task_service import TaskService
from app.utils.unitofwork import IUnitOfWork
from app.utils.main_uow import MainUOW
from app.api.schemas.user import UserFromToken
from app.api.schemas.task import TaskToGroups
from app.core.security.auth import get_user_from_token

tasks = APIRouter(prefix="/tasks")

async def get_task_service(uow: IUnitOfWork = Depends(MainUOW)) -> TaskService:
    return TaskService(uow)


@tasks.post("/create")
async def assign_group_task(task_scheme: TaskToGroups,
                    service: TaskService = Depends(get_task_service),
                    author: UserFromToken = Depends(get_user_from_token)):
    new_task = await service.create_group_task(task_scheme, author)
    await service.send_task_to_groups(new_task)
    return new_task