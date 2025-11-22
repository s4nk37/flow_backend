from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class EmailCheck(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str | None = None

    model_config = {"from_attributes": True}
