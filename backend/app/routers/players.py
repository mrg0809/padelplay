from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.security import get_current_user
from app.db.connection import supabase

router = APIRouter()

class PlayerInfo(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    phone: Optional[str] = None
    gender: Optional[str] = None
    preferred_hand: Optional[str] = None
    position: Optional[str] = None
    photo_url: Optional[str] = None

@router.get("/", response_model=PlayerInfo)
def get_player_info(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    response = supabase.from_("players").select("*").eq("user_id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Player information not found")

    return response.data[0]

@router.put("/")
def update_player_info(data: PlayerInfo, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    response = supabase.from_("players").update(data.dict()).eq("user_id", user_id).execute()

    if response.error:
        raise HTTPException(status_code=500, detail=f"Error updating player info: {response.error['message']}")

    return {"message": "Player info updated successfully"}
