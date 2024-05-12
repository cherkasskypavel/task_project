
from app.repositories.base_repository import SARepository
from app.db.models import Task, Group



class TaskRepository(SARepository):
    model = Task


    async def add_group_task_record(self, task: Task, group: Group) -> None:
        task.groups.append(group)


        

    