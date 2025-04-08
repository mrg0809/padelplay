from fastapi import HTTPException
from app.db.connection import supabase
from datetime import datetime, timedelta, date, time

async def get_available_courts_for_lesson(club_id: str, lesson_date: date, lesson_time: time, duration: int):
    """
    Obtiene las canchas disponibles para una lección en una fecha y hora específicas.
    """
    # 1. Obtener canchas del club
    courts_response = supabase.from_("courts").select("id").eq("club_id", club_id).execute()
    print(courts_response)
    if not courts_response:
        print(f"Error al obtener canchas del club:")
        raise HTTPException(status_code=500, detail="Error al obtener canchas del club")
    courts_in_club = [court["id"] for court in courts_response.data]

    # 2. Calcular el end_time de la lección
    lesson_datetime = datetime.combine(lesson_date, lesson_time)
    end_datetime = lesson_datetime + timedelta(minutes=duration)
    end_time = end_datetime.time()

    # 3. Obtener reservas y bloqueos que se superpongan con el horario de la lección
    conflicting_reservations = supabase.from_("reservations").select("court_id").eq("reservation_date", lesson_date.isoformat()).filter(
        "start_time", "lte", end_time.isoformat()  # Corrected: "lte" for <=
    ).filter(
        "end_time", "gte", lesson_time.isoformat()  # Corrected: "gte" for >=
    ).execute()

    conflicting_blocks = supabase.from_("court_blocks").select("court_id").eq("start_date", lesson_date.isoformat()).filter(
        "start_time", "lte", end_time.isoformat()  # Corrected: "lte" for <=
    ).filter(
        "end_time", "gte", lesson_time.isoformat()  # Corrected: "gte" for >=
    ).execute()

    if not conflicting_reservations:
        print(f"Error al obtener reservas")
        raise HTTPException(status_code=500, detail="Error al obtener reservas")
    if not conflicting_blocks:
        print(f"Error al obtener bloqueos")
        raise HTTPException(status_code=500, detail="Error al obtener bloqueos")

    busy_courts = set(
        [r["court_id"] for r in conflicting_reservations.data] +
        [b["court_id"] for b in conflicting_blocks.data]
    )

    # 4. Filtrar canchas disponibles
    available_courts = [
        {"id": court_id} for court_id in courts_in_club if court_id not in busy_courts
    ]

    return available_courts