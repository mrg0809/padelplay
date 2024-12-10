from fastapi import APIRouter, HTTPException, Depends
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response
from pydantic import BaseModel, Field
from typing import Optional
from app.core.security import get_current_user

router = APIRouter(prefix="/courts", tags=["Courts"])

class CourtCreate(BaseModel):
    club_id: str
    name: str
    is_indoor: bool
    price_per_hour: float = Field(..., gt=0, description="Precio por hora (debe ser mayor a 0)")
    price_per_hour_and_half: Optional[float] = Field(None, gt=0, description="Precio por hora y media (opcional, mayor a 0)")
    is_active: Optional[bool] = True


@router.post("/")
def create_court(court: CourtCreate):
    try:
        # Inserta el registro en la tabla de Supabase
        response = supabase.table("courts").insert(court.dict()).execute()
        
        if not response.data:  # Si no se insertaron datos
            raise HTTPException(status_code=400, detail="Failed to create court")

        return response.data[0]  # Retorna la información del registro creado

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def get_club_courts(current_user: dict = Depends(get_current_user)):
    club_id = current_user.get("club_id")
    if not club_id:
        raise HTTPException(status_code=403, detail="User is not associated with a club")
    response = supabase.table("courts").select("*").execute()
    return handle_supabase_response(response)

@router.get("/{court_id}")
def get_court_by_id_endpoint(court_id: str):
    response = supabase.table("courts").select("*").eq("id", court_id).execute()
    if response.error or not response.data:
        raise HTTPException(status_code=404, detail="Court not found")
    return response.data[0]

@router.put("/{court_id}")
def update_court_endpoint(court_id: str, updates: dict):
    response = supabase.table("courts").update(updates).eq("id", court_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return response.data

@router.delete("/{court_id}")
def delete_court_endpoint(court_id: str):
    response = supabase.table("courts").delete().eq("id", court_id).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)
    return {"message": "Court deleted successfully"}
