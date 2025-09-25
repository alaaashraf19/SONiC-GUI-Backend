from fastapi import WebSocket, WebSocketDisconnect

async def chat_Service(websocket : WebSocket):
    await websocket.accept()
    try:
          while True:
            user_input = await websocket.receive_text()         
            await websocket.send_text(user_input)
    except WebSocketDisconnect:
        print("Client disconnected, stopping...")

    except Exception as e:
        print("⚠️ Chatbot crashed with error:", e)
        await websocket.close()

