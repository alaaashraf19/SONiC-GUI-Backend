from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.vlans import router as vlans_router
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(vlans_router, prefix="/vlans",tags=["vlans"])
