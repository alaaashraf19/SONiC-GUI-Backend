from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.post_oper import router as post_oper_router
from app.routers.vlans import router as vlans_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.PutOper import router as put_oper_vlan_router
from app.routers.DeleteOper import delete_oper_vlan_router


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(post_oper_router, prefix="/post_oper",tags=["post_oper"])
app.include_router(vlans_router, prefix="/network",tags=["vlans"])
app.include_router(put_oper_vlan_router, prefix="/network", tags=["vlans"])
app.include_router(delete_oper_vlan_router, prefix="/network", tags=["vlans"])


