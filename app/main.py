from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.post_oper import router as post_oper_router
from app.routers.vlans import router as vlans_router

app=FastAPI()



app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(post_oper_router, prefix="/post_oper",tags=["post_oper"])
app.include_router(vlans_router, prefix="/vlans",tags=["vlans"])
