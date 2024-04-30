from app.utils.unitofwork import UnitOfWork
from app.repositories.user_repository import UserRepository
from app.repositories.group_repository import GroupRepository
from app.repositories.task_repository import TaskRepository


class MainUOW(UnitOfWork):

    repositories = [UserRepository, GroupRepository, TaskRepository]

