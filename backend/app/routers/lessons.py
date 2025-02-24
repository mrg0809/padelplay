from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.security import get_current_user
from app.db.connection import supabase
import uuid
from datetime import date, time, timedelta, datetime

router = APIRouter()

class LessonCreate(BaseModel):
    club_id: str
    court_id: str
    lesson_date: date
    lesson_time: time
    duration: int
    coach: str
    lesson_type: str
    name: str
    description: Optional[str] = None
    price: float

class LessonResponse(BaseModel):
    id: str
    club_id: str
    court_id: str
    lesson_date: date
    lesson_time: time
    duration: int
    coach: str
    lesson_type: str
    name: str
    description: Optional[str] = None

@router.get("/", response_model=List[LessonResponse])
def get_lessons(club_id: str, current_user: dict = Depends(get_current_user)):
    """
    Obtiene la lista de lecciones públicas de un club.
    """
    response = supabase.from_("lessons") \
        .select("*") \
        .eq("club_id", club_id) \
        .eq("lesson_type", "public") \
        .execute()

    if not response.data:
        return []

    return response.data

from datetime import datetime, timedelta

@router.post("/")
def create_lesson(data: LessonCreate, current_user: dict = Depends(get_current_user)):
    """
    Crea una nueva lección y bloquea la cancha durante el tiempo de la lección.
    """
    # Crear la lección
    new_lesson = {
        "id": str(uuid.uuid4()),
        "club_id": data.club_id,
        "court_id": data.court_id,
        "lesson_date": data.lesson_date.isoformat(),
        "lesson_time": data.lesson_time.isoformat(),
        "duration": data.duration,
        "coach": data.coach,
        "lesson_type": data.lesson_type,
        "name": data.name,
        "description": data.description,
        "price": data.price,
    }

    # Insertar la lección en la tabla lessons
    insert_response = supabase.from_("lessons").insert(new_lesson).execute()

    if not insert_response:
        raise HTTPException(status_code=500, detail="Error al crear la lección")

    # Calcular el end_time de la lección
    lesson_datetime = datetime.combine(data.lesson_date, data.lesson_time)
    end_datetime = lesson_datetime + timedelta(minutes=data.duration)
    end_time = end_datetime.time()

    # Crear el bloqueo de la cancha
    new_block = {
        "id": str(uuid.uuid4()),
        "club_id": data.club_id,
        "court_id": data.court_id,
        "start_date": data.lesson_date.isoformat(),
        "start_time": data.lesson_time.isoformat(),
        "end_time": end_time.isoformat(),
        "end_date": data.lesson_date.isoformat(),  # Asumimos que el bloqueo es para un solo día
        "reason": f"Lección: {new_lesson['name']}",  # Razón del bloqueo
    }

    # Insertar el bloqueo en la tabla court_blocks
    block_response = supabase.from_("court_blocks").insert(new_block).execute()

    if not block_response:
        # Si falla el bloqueo, eliminar la lección creada (rollback)
        supabase.from_("lessons").delete().eq("id", new_lesson["id"]).execute()
        raise HTTPException(status_code=500, detail="Error al bloquear la cancha")

    return {"message": "Lección creada y cancha bloqueada exitosamente"}