from fastapi import HTTPException
from app.models.User import UserCreate, UserLogin
from app.db.tiny import users_table, User
from app.core.Security import hash_password, create_access_token, verify_password
import os


def signup(user: UserCreate):
    db_user = users_table.get(User.username == user.username.lower())
    email_exists = users_table.get(User.email == user.email.lower())

    if db_user:
        raise HTTPException(
            status_code=409,
            detail=[{"loc": ["body", "username"], "msg": "Username already exists"}]
        )
    elif email_exists:
        raise HTTPException(
            status_code=409,
            detail=[{"loc": ["body", "email"], "msg": "Email already exists"}]
        )


    hashed_pw = hash_password(user.password)
    user_data = user.model_dump()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    user_data["role"] = "admin"

    users_table.insert(user_data)

    print("Using DB file:", os.getenv("DB_PATH"))

    return "User created successfully"



def login(user: UserLogin):
    db_user = users_table.get(User.username == user.username.lower())
    hashed_pw = db_user.get("hashed_password") if db_user else None

    if not db_user:
        raise HTTPException(status_code=403, detail="Invalid username or password")

    if not hashed_pw or not verify_password(user.password, hashed_pw):
        raise HTTPException(status_code=403, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": db_user["username"], "role": db_user["role"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
