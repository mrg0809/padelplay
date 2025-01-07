from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.security import get_current_user
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response 

router = APIRouter()

class PlayerInfo(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    category: str
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

    # Convertir birth_date a string si está presente
    update_data = data.dict()
    if "birth_date" in update_data and update_data["birth_date"] is not None:
        update_data["birth_date"] = update_data["birth_date"].isoformat()

    # Realizar la actualización en Supabase
    response = supabase.from_("players").update(update_data).eq("user_id", user_id).execute()
    
    # Manejar la respuesta usando handle_supabase_response
    try:
        updated_data = handle_supabase_response(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating player info: {str(e)}")

    return {"message": "Player info updated successfully", "data": updated_data}
