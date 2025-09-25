from fastapi import APIRouter, WebSocket
from app.services.Chat_Server_Services import chat_Service

router = APIRouter()

@router.websocket("/chat/{username}")
async def chatbot_server(websocket: WebSocket):
    return chat_Service(websocket)