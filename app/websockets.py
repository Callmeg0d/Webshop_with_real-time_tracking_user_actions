from typing import List

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


# Функция для отправки обновлений
async def send_product_update(product_id: int, product_quantity: int):
    await manager.broadcast({"product_id": product_id, "product_quantity": product_quantity})