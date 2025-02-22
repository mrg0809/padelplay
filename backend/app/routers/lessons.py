from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.security import get_current_user
from app.db.connection import supabase
import uuid

router = APIRouter()

class Availability(BaseModel):
    day: str 
    start_time: str
    end_time: str

class CoachCreate(BaseModel):
    user_id: str  # ID del jugador que se agregará como coach
    club_id: str  # ID del club que lo agrega
    name: str
    price_for_one: Optional[float] = None
    price_for_two: Optional[float] = None
    price_for_three: Optional[float] = None
    price_for_four: Optional[float] = None
    coach_resume: str
    coach_focus: str
    availability: List[Availability]

class CoachResponse(BaseModel):
    user_id: str
    name: str
    gender: Optional[str]
    photo_url: Optional[str]
    category: Optional[str]

@router.get("/search-coaches", response_model=List[CoachResponse])
def search_coaches(current_user: dict = Depends(get_current_user)):
    """
    Devuelve la lista de jugadores que tienen is_coach=True y aún no están en un club como coach.
    """
    response = supabase.from_("players") \
        .select("user_id, first_name, last_name, gender, photo_url, category") \
        .eq("is_coach", True) \
        .execute()

    if not response.data:
        return []

    return [
        {
            "user_id": player["user_id"],
            "name": f"{player['first_name']} {player['last_name']}",
            "gender": player["gender"],
            "photo_url": player["photo_url"],
            "category": player["category"],
        }
        for player in response.data
    ]

@router.post("/add-coach")
def add_coach(data: CoachCreate, current_user: dict = Depends(get_current_user)):
    """
    Permite que un club agregue un jugador como coach con sus precios establecidos.
    """
    # Verificar si el jugador ya es coach en otro club
    response = supabase.from_("coaches") \
        .select("id") \
        .eq("user_id", data.user_id) \
        .execute()

    if response.data:
        raise HTTPException(status_code=400, detail="Este jugador ya está registrado como coach en un club.")

    print(data.user_id)
    # Obtener la información del jugador
    player_response = supabase.from_("players") \
        .select("first_name, last_name") \
        .eq("user_id", data.user_id) \
        .execute()

    if not player_response.data:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    player = player_response.data[0]
    coach_name = f"{player['first_name']} {player['last_name']}"

    availability_dict = [availability.model_dump() for availability in data.availability]

    # Insertar el coach en la tabla coaches
    new_coach = {
        "id": str(uuid.uuid4()),
        "club_id": data.club_id,
        "user_id": data.user_id,
        "name": coach_name,
        "price_for_one": data.price_for_one,
        "price_for_two": data.price_for_two,
        "price_for_three": data.price_for_three,
        "price_for_four": data.price_for_four,
        "is_active": True,
        "coach_resume": data.coach_resume,
        "coach_focus": data.coach_focus,
        "availability": availability_dict,
    }

    insert_response = supabase.from_("coaches").insert(new_coach).execute()

    if not insert_response:
        raise HTTPException(status_code=500, detail="Error al agregar el coach")

    return {"message": "Coach agregado exitosamente"}
