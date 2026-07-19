from pydantic import BaseModel, EmailStr

class LoginCreate(BaseModel):
    email : EmailStr
    password : str

class LoginResponse(BaseModel):
    message : str
    