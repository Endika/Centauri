from fastapi import APIRouter, FastAPI, WebSocket

from app.adapters.memory_adapter import MemoryManager
from app.adapters.websocket_api import WebSocketAPI
from app.core.chat_service import ChatService

app = FastAPI()

websocket_router = APIRouter()

memory_manager = MemoryManager()
chat_service = ChatService(memory_manager)
websocket_api = WebSocketAPI(chat_service)


@websocket_router.websocket("/chat/")
async def websocket_endpoint_no_chat_id(websocket: WebSocket):
    await websocket_api.handle_connection(websocket, chat_id=None)


@websocket_router.websocket("/chat/{chat_id}")
async def websocket_endpoint_with_chat_id(websocket: WebSocket, chat_id: str):
    await websocket_api.handle_connection(websocket, chat_id)


app.include_router(websocket_router)


@app.get(
    "/check",
    summary="Health Check",
    description="Verifies that the service is running.",
)
async def check():
    return {
        "status": "OK",
        "message": "Service is running correctly",
        "version": "1.0.0",
        "dependencies": {
            "memory_manager": "OK" if memory_manager else "ERROR",
            "chat_service": "OK" if chat_service else "ERROR",
        },
    }
