
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.api.endpoints.tasks import get_task_service
from app.api.schemas.task import TaskReturnList
from app.api.schemas.user import UserFromToken
from app.core.security.auth import get_user_from_token
from app.services.connection_manager import ConnectionManager
from app.services.task_service import TaskService


dashboard = APIRouter(prefix="/dashboard")
manager = ConnectionManager()


@dashboard.websocket("/ws")
async def dashboard_websocket(websocket: WebSocket, token: str,
                              task_service: TaskService = Depends(get_task_service)):


    user: UserFromToken = get_user_from_token(token)

    await manager.connect_user(websocket, user)
    tasks = await task_service.get_tasks(group=None, user=user)
    task_list = TaskReturnList(tasks=tasks)
    await manager.show_tasks_after_connect(task_list, user)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_user(user)

