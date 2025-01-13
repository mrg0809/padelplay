from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.core.security import get_current_user
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response

router = APIRouter()

class ClubBlock(BaseModel):
    courts: List[str]
    club_id: str
    start_date: str
    end_date:str
    start_time: str  # HH:MM:SS
    end_time: str    # HH:MM:SS
    reason: Optional[str] = None

class CourtBlock(BaseModel):
    court_id: str
    club_id: str
    start_date: str
    end_date:str
    start_time: str  # HH:MM:SS
    end_time: str    # HH:MM:SS
    reason: Optional[str] = None  



@router.post("/block-court")
async def block_court(data: CourtBlock, current_user: dict = Depends(get_current_user)):
    try:
        # Insertar el bloqueo en la tabla court_blocks
        response = supabase.table("court_blocks").insert({
            "court_id": data.court_id,
            "club_id": data.club_id,
            "start_date": data.start_date,
            "end_date": data.end_date,
            "start_time": data.start_time,
            "end_time": data.end_time,
            "reason": data.reason
        }).execute()
        handle_supabase_response(response)

        return {
            "message": "Bloqueo de cancha agregado exitosamente.",
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar bloqueo de cancha: {str(e)}")


@router.post("/block-club")
async def block_club(data: ClubBlock, current_user: dict = Depends(get_current_user)):
    try:
        # Iterar sobre la lista de canchas
        for court_id in data.courts:
            # Insertar el bloqueo en la tabla court_blocks para cada cancha
            response = supabase.table("court_blocks").insert({
                "court_id": court_id,
                "club_id": data.club_id,
                "start_date": data.start_date,
                "end_date": data.end_date,
                "start_time": data.start_time,
                "end_time": data.end_time,
                "reason": data.reason
            }).execute()
            handle_supabase_response(response)

        return {
            "message": "Bloqueo de club agregado exitosamente.",
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar bloqueo de club: {str(e)}")