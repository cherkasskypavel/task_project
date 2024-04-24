from __future__ import annotations

from fastapi import HTTPException, status

from app.utils.unitofwork import IUnitOfWork
from app.api.schemas.user import UserFromToken, UserSafeReturn
from app.api.schemas.task import TaskToGroups, TaskToGroupReturnScheme
from app.api.schemas.notification import NewGroupTaskNotification
from app.api.endpoints.dashboard import manager as ws_manager


class TaskService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow


    async def create_group_task(self,
                          task_scheme: TaskToGroups,
                          author: UserFromToken):
        
        task_data = task_scheme.model_dump(exclude_none=True,
                                          exclude_defaults=True,
                                          exclude=["groups"])
        task_data["author"] = author.username

        async with self.uow:
            group_repo = self.uow.repositories[1]
            task_repo = self.uow.repositories[2]

            db_task = await task_repo.add_one(task_data)
            await self.uow.flush()
            await self.uow.refresh(db_task)

            for group in task_scheme.groups:
                db_group = await group_repo.get_one(name=group)
                if db_group is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail=f"Группа {group} не существует. Задача не поставлена.")
                else:
                    await task_repo.add_group_task_record(db_task, db_group)

            await self.uow.commit()
            await self.uow.refresh(db_task)
            new_task = TaskToGroupReturnScheme.model_validate(db_task)
        
        return new_task

    
    async def send_task_to_groups(self, task: TaskToGroupReturnScheme):
        
        notification = NewGroupTaskNotification(
            task=task
        ) 
        uniq_members = set()
        
        async with self.uow:
            group_repo = self.uow.repositories[1]
            for group in task.groups:
                db_group = await group_repo.get_one(name=group)
                for member in db_group.members:
                    uniq_members.add(UserSafeReturn.model_validate(member))

            for member in uniq_members:
                try:
                    await ws_manager.send_group_notification(notification, member)    
                except ValueError:
                    continue
 





