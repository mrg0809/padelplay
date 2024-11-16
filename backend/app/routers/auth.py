from fastapi import APIRouter, HTTPException, Depends
from app.services.user_service import create_user
from app.services.auth_service import authenticate_user

router = APIRouter()

@router.post("/register")
async def register(email: str, password: str):
    try:
        await create_user(email=email, password=password)
        return {"message": "User registered successfully"}
    except HTTPException as e:
        raise e

@router.post("/login")
async def login(email: str, password: str):
    try:
        token = authenticate_user(email=email, password=password)
        return token
    except HTTPException as e:
        raise e
