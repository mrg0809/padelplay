from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.user_service import create_user
from app.services.auth_service import authenticate_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str

@router.post("/register")
async def register(request: RegisterRequest):
    try:
        await create_user(full_name=request.full_name,
                          email=request.email,
                          password=request.password)
        return {"message": "User registered successfully"}
    except HTTPException as e:
        raise e

@router.post("/login")
async def login(data: LoginRequest):
    try:
        token = authenticate_user(email=data.email, password=data.password)
        return token
    except HTTPException as e:
        raise e
