from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers.Auth_Router import router as auth_router
from app.routers.Vlans_Router import router as vlans_router
from app.routers.Port_Oper_Router import router as port_op_router
from app.routers.SSH_Router import router as ssh_router
from app.routers.Chatbot_Router import router as chatbot_router
from app.routers.chatbot_server import router as chatbot_server
from app.core.Security import get_current_user


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)
router = APIRouter()

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"]
    }


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(vlans_router, prefix="/vlans",tags=["Vlans"])
app.include_router(port_op_router, prefix="/portOp",tags=["Port Operations"])
app.include_router(ssh_router, prefix="/switch", tags=["SSH"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(chatbot_server, prefix="/chatServer", tags=["Chatbot Server"])
app.include_router(router, tags=["token"])


