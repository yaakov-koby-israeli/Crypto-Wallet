from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # Map user_id to active WebSocket connection
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: str, user_id: int) -> None:
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)


manager = ConnectionManager()
