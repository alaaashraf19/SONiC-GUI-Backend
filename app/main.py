from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.vlans import router as vlans_router

app=FastAPI()



app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(vlans_router, prefix="/vlans",tags=["vlans"])
