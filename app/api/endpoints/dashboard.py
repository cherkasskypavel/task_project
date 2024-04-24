from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security.auth import get_user_from_token
from app.services.connection_manager import ConnectionManager


dashboard = APIRouter(prefix="/dashboard")
manager = ConnectionManager()


@dashboard.websocket("/ws")
async def dashboard_websocket(websocket: WebSocket, token: str):
    user = get_user_from_token(token)
    await manager.connect_user(websocket, user)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect_user(user)

