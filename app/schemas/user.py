from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):

    email : EmailStr
    fullname : str | None = None
    password : str

class UserResponse(BaseModel):

    id : int
    email : EmailStr
    fullname : str | None = None

    class Config:
        from_attributes = True