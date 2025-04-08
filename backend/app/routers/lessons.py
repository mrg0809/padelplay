from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from app.core.security import get_current_user
from app.db.connection import supabase
import uuid
from datetime import date, time, timedelta, datetime
from app.utils.lesson_utils import get_available_courts_for_lesson

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

class PrivateLessonBooking(BaseModel):
    club_id: str
    coach_id: str
    lesson_date: date
    lesson_time: time
    duration: int
    participants: int
    price_paid: float
    payment_order_id: str
    payment_intent_id: str
    additional_items: Optional[list] = None

class PrivateLessonBookingResponse(BaseModel):
    booking_id: str
    message: str


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


@router.get("/available-times")
def get_available_times(club_id: str, date: str, coach_id: str, current_user: dict = Depends(get_current_user)):
    try:
        requested_date = datetime.strptime(date, "%Y-%m-%d").date()
        day_of_week = requested_date.weekday()

        # 1. Obtener horarios de apertura y cierre para las canchas
        schedules_response = supabase.from_("schedules").select("court_id, opening_time, closing_time").match({
            "club_id": club_id,
            "day_of_week": day_of_week,
        }).execute()

        available_times = {}
        if schedules_response.data:
            for schedule in schedules_response.data:
                opening_time = datetime.strptime(schedule["opening_time"], "%H:%M:%S").time()
                closing_time = datetime.strptime(schedule["closing_time"], "%H:%M:%S").time()

                # Generar intervalos de 1 hora
                times = []
                current = datetime.combine(datetime.today(), opening_time)
                closing_limit = datetime.combine(datetime.today(), closing_time) - timedelta(hours=1)

                while current.time() <= closing_limit.time(): # Correccion para tomar el cierre correcto.
                    times.append(current.strftime("%H:%M"))
                    current += timedelta(hours=1)
                available_times[schedule["court_id"]] = times

        # 2. Obtener reservas y bloqueos para canchas
        reservations_response = supabase.from_("reservations").select("court_id, start_time").match({
            "reservation_date": date,
        }).execute()

        blocked_times_response = supabase.from_("court_blocks").select("court_id, start_time").match({
            "start_date": date,
        }).execute()

        reserved_times = {
            (r["court_id"], r["start_time"]) for r in reservations_response.data
        }

        blocked_times = {
            (b["court_id"], b["start_time"]) for b in blocked_times_response.data
        }

        # 3. Obtener disponibilidad del coach desde la tabla coaches.
        coach_response = supabase.from_("coaches").select("availability").eq("id", coach_id).execute()
        coach_schedule = {}

        if coach_response.data and coach_response.data[0] and coach_response.data[0]['availability']:
          availability = coach_response.data[0]['availability']
          for item in availability:
              if item['day'].lower() == ['lunes','martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][day_of_week].lower():
                  start = datetime.strptime(item['start_time'], "%H:%M").time()
                  end = datetime.strptime(item['end_time'], "%H:%M").time()
                  coach_schedule = [
                    datetime.combine(datetime.today(), start) + timedelta(hours=i)
                    for i in range(0, int((datetime.combine(datetime.today(), end)-datetime.combine(datetime.today(), start)).seconds / 3600))
                  ]
                  coach_schedule = [item.strftime('%H:%M') for item in coach_schedule]
                  break

        # 4. Filtrar horarios basados en reservas, bloqueos y disponibilidad del coach
        final_available_times = {}
        for court_id, times in available_times.items():
            final_available_times[court_id] = [
                time
                for time in times
                if (court_id, time) not in reserved_times and
                (court_id, time) not in blocked_times and
                (time in coach_schedule)
            ]

        return {"available_times": final_available_times}

    except Exception as e:
        print(f"Error in get_available_times: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener horarios disponibles: {str(e)}")
    

@router.post("/private-booking", response_model=PrivateLessonBookingResponse)
async def create_private_lesson_booking(data: PrivateLessonBooking, current_user: dict = Depends(get_current_user)):
    """
    Crea una reserva para una lección privada, asigna una cancha disponible y añade el jugador.
    """
    try:
        lesson_id = str(uuid.uuid4())

        # 1. Buscar una cancha disponible
        available_courts = await get_available_courts_for_lesson(
            data.club_id, data.lesson_date, data.lesson_time, data.duration
        )

        if not available_courts:
            raise HTTPException(status_code=400, detail="No hay canchas disponibles para esta hora.")

        # Asignar la primera cancha disponible
        assigned_court_id = available_courts[0]["id"]

        # 2. Crear la lección
        new_lesson = {
            "id": lesson_id,
            "club_id": data.club_id,
            "coach": data.coach_id,
            "court_id": assigned_court_id,
            "lesson_date": data.lesson_date.isoformat(),
            "lesson_time": data.lesson_time.isoformat(),
            "duration": data.duration,
            "lesson_type": "private",
            "name": f"Clase Privada con {data.coach_id}",
            "participants": data.participants,
            "price": data.price_paid,
            "payment_order_id": data.payment_order_id,
            "players": [current_user["id"]], 
        }

        # Insertar la lección
        lesson_response = supabase.from_("lessons").insert(new_lesson).execute()
        if not lesson_response:
            print(f"Error al crear la lección")
            raise HTTPException(status_code=500, detail="Error al crear la lección")

        # 3. Calcular el end_time para el bloqueo de cancha
        lesson_datetime = datetime.combine(data.lesson_date, data.lesson_time)
        end_datetime = lesson_datetime + timedelta(minutes=data.duration)
        end_time = end_datetime.time()

        # 4. Crear el bloqueo de la cancha
        new_block = {
            "id": str(uuid.uuid4()),
            "club_id": data.club_id,
            "court_id": assigned_court_id,  # Usar la cancha asignada
            "start_date": data.lesson_date.isoformat(),
            "start_time": data.lesson_time.isoformat(),
            "end_time": end_time.isoformat(),
            "end_date": data.lesson_date.isoformat(),
            "reason": f"Clase Privada con {data.coach_id}",
        }

        # Insertar el bloqueo de la cancha
        block_response = supabase.from_("court_blocks").insert(new_block).execute()
        if not block_response:
            print(f"Error al bloquear la cancha")
            # Rollback: Eliminar la lección
            await supabase.from_("lessons").delete().eq("id", lesson_id).execute()
            raise HTTPException(status_code=500, detail="Error al bloquear la cancha")

        return PrivateLessonBookingResponse(booking_id=lesson_id, message="Reserva de clase privada creada exitosamente")

    except Exception as e:
        print(f"Error en create_private_lesson_booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear reserva de clase privada: {str(e)}")
