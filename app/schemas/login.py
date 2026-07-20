from pydantic import BaseModel, EmailStr

class LoginCreate(BaseModel):
    email : EmailStr
    password : str

class LoginResponse(BaseModel):
    access_token : str
    token_type : str
    