from __future__ import annotations
import datetime
from enum import Enum
from typing import Optional

from fastapi import HTTPException, status


from app.utils.unitofwork import IUnitOfWork
from app.api.schemas.user import UserFromToken, UserSafeReturn
from app.api.schemas.task import TaskToGroups, TaskToGroupReturnScheme, TaskReturnList, TaskBaseReturnScheme
from app.api.schemas.notification import GroupTaskNotification
from app.api.endpoints.dashboard import manager as ws_manager


class TaskStatus(Enum):
    created = 0
    in_work = 1
    completed = 2
    expired = 3
    deleted = 4    


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
        
        notification = GroupTaskNotification(
            task=TaskBaseReturnScheme.model_validate(task)
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
 

    async def update_task_status(self, task_id: int, author: UserFromToken):

        async with self.uow:
            task_repo = self.uow.repositories[2]
            user_repo = self.uow.repositories[0]

            db_task = await task_repo.get_one(id=task_id)
            db_user = await user_repo.get_one(username=author.username)

            today = datetime.datetime.now().date()

            if db_task is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Задача {task_id} не найдена")

            if set(db_task.groups).isdisjoint(db_user.group) and \
                            author.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail=f"Вы не можете работать с задачей {task_id}")
            

            if db_task.status in (TaskStatus.completed.name, TaskStatus.expired.name):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Задача {task_id} неактивна: {db_task.status}")

            
            if db_task.expire_on < today:
                new_status_data = {"status": TaskStatus.expired.name}
            else:
                current_status = TaskStatus[db_task.status].value
                new_status_data = {"status": TaskStatus(current_status + 1).name}
                    
            updated_task = await task_repo.update(new_status_data, id=db_task.id)
            await self.uow.commit()
            await self.uow.refresh(updated_task)
            task_to_return = TaskToGroupReturnScheme.model_validate(updated_task)
        
        return task_to_return


    async def get_tasks(self, group: Optional[str], 
                        user: UserFromToken):
        async with self.uow:
            user_repo = self.uow.repositories[0]
            group_repo = self.uow.repositories[1]

            task_list = []

            db_user = await user_repo.get_one(username=user.username)
            
            if group is None:
                for g in db_user.group:
                    task_list.extend(g.tasks)
            else:
                db_group = await group_repo.get_one(name=group)
                if db_group not in db_user.group and user.role != "admin":
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                        detail="Вы не состоите в этой группе")
                task_list.extend(db_group.tasks)
        
            result = TaskReturnList(tasks=task_list)
        return result
    

    async def get_one_task(self, id: int, user: UserFromToken):
        async with self.uow:
            task_repo = self.uow.repositories[2]
            user_repo = self.uow.repositories[0]

            db_task = await task_repo.get_one(id=id)
            if db_task is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Задача {id} не найдена")
            
            db_user = await user_repo.get_one(username=user.username)

            if set(db_user.group).isdisjoint(db_task.groups) and\
                            user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Вы не можете работать с этой задачей")
            
            return TaskBaseReturnScheme.model_validate(db_task)
        

    async def delete_one_task(self, id: int, user: UserFromToken):
        async with self.uow:
            task_repo = self.uow.repositories[2]
            deleted_tasks = await task_repo.delete(id=id)

            if not deleted_tasks:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Задачи не найдены")
            if deleted_tasks[0].author != user.username and user.role != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Вы не можете удалять эту задачу")
    
            result = TaskToGroupReturnScheme.model_validate(deleted_tasks[0])
            result.status = TaskStatus.deleted.name
            await self.uow.commit()
            return result
        
    
    async def delete_expired(self, user: UserFromToken):
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вы не можете выполнять это действие")
        
        async with self.uow:
            task_repo = self.uow.repositories[2]
            deleted_tasks = await task_repo.delete_many(status=TaskStatus.expired.name)
            result = len(deleted_tasks)
            await self.uow.commit()
        return result 
    

    async def mark_expired(self, user: UserFromToken):
        if user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вы не можете выполнять это действие")
        
        status_data = {"status": TaskStatus.expired.name}
        today = datetime.datetime.now().date()
        async with self.uow:
            task_repo = self.uow.repositories[2]
            expired_tasks = await task_repo.update_many(status_data, expire_on=today)

            result = len(expired_tasks)
            await self.uow.commit()
        return result