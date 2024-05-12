from typing import Optional
from fastapi import APIRouter, Depends

from app.api.schemas.task import TaskToGroups
from app.api.schemas.user import UserFromToken
from app.core.security.auth import get_user_from_token
from app.services.task_service import TaskService
from app.utils.main_uow import MainUOW
from app.utils.unitofwork import IUnitOfWork

tasks = APIRouter(prefix="/tasks")

async def get_task_service(uow: IUnitOfWork = Depends(MainUOW)) -> TaskService:
    return TaskService(uow)


@tasks.post("/create")
async def assign_group_task(task_scheme: TaskToGroups,
                    service: TaskService = Depends(get_task_service),
                    author: UserFromToken = Depends(get_user_from_token)):
    new_task = await service.create_group_task(task_scheme, author)
    await service.send_task_to_groups(new_task)
    return {"message": "Задача создана", "Задача": new_task}


@tasks.patch("/update")
async def update_task(task_id: int,
                      service: TaskService = Depends(get_task_service),
                      author: UserFromToken = Depends(get_user_from_token)):
    updated_task = await service.update_task_status(task_id, author)
    await service.send_task_to_groups(updated_task)
    return {"message": "Задача обновлена", "Задача": updated_task}


@tasks.get("/check")
async def check_tasks(group: Optional[str] = None,
                      service: TaskService = Depends(get_task_service),
                      user: UserFromToken = Depends(get_user_from_token)):
    tasks = await service.get_tasks(group, user)
    return tasks


@tasks.get("/check_one")
async def check_one_task(id: int,
                         service: TaskService = Depends(get_task_service),
                         user: UserFromToken = Depends(get_user_from_token)):
    task = await service.get_one_task(id, user)
    return task


@tasks.delete("/delete")
async def delete_task(id: int,
                      service: TaskService = Depends(get_task_service),
                      user: UserFromToken = Depends(get_user_from_token)):
    task = await service.delete_one_task(id, user)
    return {"message": "Задача удалена", "Задача": task}


@tasks.delete("/delete_expired")
async def delete_expired_tasks(service: TaskService = Depends(get_task_service),
                               admin: UserFromToken = Depends(get_user_from_token)):
    result = await service.delete_expired(admin)
    return {"message": "Успешно", "Задач удалено": result}


@tasks.patch("/mark_expired")
async def mark_expired_tasks(service: TaskService = Depends(get_task_service),
                             admin: UserFromToken = Depends(get_user_from_token)):
    result = await service.mark_expired(admin)
    return {"message": "Успешно", "Устаревших задач": result}