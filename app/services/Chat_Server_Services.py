from fastapi import WebSocket, WebSocketDisconnect
import httpx

DUMMY_CHATBOT_URL = "http://127.0.0.1:9000/chat"

async def chat_Service(websocket : WebSocket):
    await websocket.accept()
    try:
          while True:
            user_input = await websocket.receive_text()  
            async with httpx.AsyncClient(verify=False, timeout = 10.0) as client:
                response= await client.post(DUMMY_CHATBOT_URL, json= {"message" :user_input})   
                server_reply = response.json().get("bot_reply")
            await websocket.send_text(server_reply)

    except WebSocketDisconnect:
        print("Client disconnected, stopping...")

    except Exception as e:
        print("⚠️ Chatbot crashed with error:", e)
        await websocket.close()

