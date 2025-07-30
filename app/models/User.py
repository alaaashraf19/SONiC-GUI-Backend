
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    @field_validator("password")
    def validate_password(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must include at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must include at least one lowercase letter.")
        if not re.search(r"\d", value):
            raise ValueError("Password must include at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must include at least one special character.")
        return value


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=64)

class UserLoginResponse(BaseModel):
    token_type: str = "bearer"
    access_token: str
