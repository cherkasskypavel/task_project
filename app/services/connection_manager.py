
from fastapi import WebSocket
from typing import Dict

from app.api.schemas.notification import GroupTaskNotification
from app.api.schemas.task import TaskReturnList
from app.api.schemas.user import UserFromToken, UserSafeReturn


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    
    async def connect_user(self, websocket: WebSocket,
                           user: UserFromToken) -> None:
        await websocket.accept()
        self.active_connections.update({user.username: websocket})


    
    def disconnect_user(self, user: UserFromToken) -> None:
        del self.active_connections[user.username]


    async def send_group_notification(self, notification: GroupTaskNotification,
                                 user: UserSafeReturn) -> None:
        connected_user: WebSocket = self.active_connections.get(user.username)
        if connected_user is None:
            raise ValueError("Пользователь не подключен")
        else:
            try:
                await connected_user.send_json(notification.model_dump_json(indent=2))
            except RuntimeError as err:
                raise ValueError(f"Пользователь отключился: {err}")
        

    async def show_tasks_after_connect(self, task_list: TaskReturnList,
                                       user: UserFromToken) -> None:
        connected_user: WebSocket = self.active_connections.get(user.username)
        if connected_user is None:
            raise ValueError("Пользователь не подключен")
        else:
            try:
                await connected_user.send_bytes(task_list.model_dump_json(indent=2))
            except RuntimeError as err:
                raise ValueError(f"Пользователь отключился: {err}") 