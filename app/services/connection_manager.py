

from typing import Dict
from fastapi import WebSocket

from app.api.schemas.notification import GroupTaskNotification
from app.api.schemas.user import UserFromToken, UserSafeReturn


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    
    async def connect_user(self, websocket: WebSocket,
                           user: UserFromToken):
        await websocket.accept()
        self.active_connections.update({user.username: websocket})

    
    def disconnect_user(self, user: UserFromToken):
        del self.active_connections[user.username]


    async def send_group_notification(self, notification: GroupTaskNotification,
                                 user: UserSafeReturn):
        connected_user = self.active_connections.get(user.username)
        if connected_user is None:
            raise ValueError("Пользователь не подключен")
        else:
            try:
                await connected_user.send_bytes(notification.model_dump_json(indent=2))
            except RuntimeError as err:
                raise ValueError(f"Пользователь отключился: {err}")
        