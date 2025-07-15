from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.user import UserCreate, UserLoginResponse,UserLogin
from app.db.mongo import db,users,otps
from app.services.auth_services import verify_password, hash_pasword
import uuid
from app.models.otp import OTPRequest, OTPVerification
from app.services.otp_service import send_otp_email,generate_otp
from datetime import datetime, timedelta
from app.core.security import create_access_token, get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserLoginResponse)
async def signup(request: Request,user: UserCreate):
    # Check if user already exists
    db_user = await db.users.find_one({"username": user.username})
    email_exists = await db.users.find_one({"email": user.email.lower()})
    if db_user:
        raise HTTPException(status_code=401, detail="Username already exists")
    elif  email_exists:
        raise HTTPException(status_code=401, detail="email already exists")

    # Insert new user into the database with hased password
    hashed_pw = hash_pasword(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    user_data["user_id"] = str(uuid.uuid4())

    result = await users.insert_one(user_data)
    return {
        "message": "User created successfully",
        "id": str(result.inserted_id),
        "username": user.username.lower(),
        "email": user.email.lower(),
        "role": "user"
    }


@router.post("/login", response_model=UserLoginResponse)
async def login(request: Request,user: UserLogin):
    
    # Check if user already exists
    db_user = await db.users.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401,detail="User does not exist")
    
    elif not verify_password(user.password,db_user["hashed_password"]):
        raise HTTPException(status_code=401,detail="invalid password")

    access_token = create_access_token(data={"sub": db_user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.put("admin/chaneRole/{username}")
async def changeRole(username:str, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change the role of a user")
    result = await db.users.update_one({"username": username}, {"$set": {"role": "admin"}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404,detail="User not found or is already an admin")
    return {
        "message": f"Role of '{username}' changed to admin"
    }


@router.post("/request-otp")
async def request_otp(data: OTPRequest):
    """
    Generates and sends a one-time password (OTP) to the user's email.
    Stores the OTP in the database with an expiration time (5 minutes).
    """

    # Generate a 6-digit OTP
    otp_code = generate_otp()

    # Prepare OTP document for storage
    otp_entry = {
        "otp": otp_code,
        "user_id": data.user_id.lower(),
        "intent": data.intent,  # 'signup' or 'login'
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }

    # Save OTP entry to the database (overwrite any existing OTP for the user)
    await otps.delete_many({"user_id": data.user_id.lower()})
    await otps.insert_one(otp_entry)

    # Send the OTP via email (function must be implemented separately)
    await send_otp_email(data.email, otp_code)  # type: ignore if needed

    return {"message": "OTP sent to your email"}


@router.post("/verify-otp")
async def verify_otp(data: OTPVerification):
    """
    Verifies the provided OTP against the stored one.
    Returns different messages based on the intent (signup/login).
    """

    # Fetch OTP record from database
    db_otp = await otps.find_one({"user_id": data.user_id.lower()})

    if not db_otp:
        raise HTTPException(status_code=401, detail="User does not exist")

    # Check if OTP is expired
    if datetime.utcnow() > db_otp["expires_at"]:
        raise HTTPException(status_code=401, detail="OTP has expired")

    # Check if OTP matches
    if db_otp["otp"] != data.otp:
        raise HTTPException(status_code=401, detail="Wrong OTP")

    # Optionally delete OTP after verification
    await otps.delete_one({"user_id": data.user_id.lower()})

    # Return appropriate message based on intent
    if db_otp["intent"] == "signup":
        return {"message": "Signed up successfully"}
    else:
        return {"message": "Logged in successfully"}