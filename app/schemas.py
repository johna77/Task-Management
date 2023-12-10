from pydantic import BaseModel, EmailStr

class TokenData(BaseModel):
    id: str

class UserCreate(BaseModel):
    username: EmailStr
    password: str
    role_id: int

class UserRegis(BaseModel):
    id: int
    username: EmailStr
    role_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class Userlogout(BaseModel):
    username: EmailStr

class Task(BaseModel):
    task_name: str
    description: str
    status: str

class Assign(BaseModel):
    assigned_to_id: int

class AllTask(BaseModel):
    task_name: str
    description: str
    status: str
    task_id: int