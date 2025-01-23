from fastapi import APIRouter, HTTPException, Depends
from app.db.connection import supabase
from app.core.security import get_current_user
from datetime import time, timedelta, datetime


# Inicializa el router
router = APIRouter()

# Crear una reserva
@router.post("/")
def create_reservation(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        # Validar campos obligatorios
        required_fields = ["club_id", "court_id", "reservation_date", "start_time", "end_time", "total_price"]
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Falta el campo obligatorio: {field}")

        player_id = current_user["id"]
        club_id = data["club_id"]
        court_id = data["court_id"]
        reservation_date = data["reservation_date"]
        start_time = data["start_time"]
        end_time = data["end_time"]
        total_price = data["total_price"]

        # Verificar disponibilidad en reservas
        overlapping_reservations = supabase.from_("reservations").select("*").match({
            "court_id": court_id,
            "reservation_date": reservation_date,
        }).execute()

        overlapping_blocks = supabase.from_("court_blocks").select("*").match({
            "court_id": court_id,
            "start_date": reservation_date,
            "end_date": reservation_date,
        }).execute()

        # Verificar si los datos fueron obtenidos
        if not overlapping_reservations or not overlapping_blocks:
            raise HTTPException(
                status_code=500,
                detail="Error al verificar disponibilidad en reservas o bloques."
            )

        # Verificar si hay conflictos
        if overlapping_reservations.data or overlapping_blocks.data:
            raise HTTPException(status_code=400, detail="La cancha no está disponible para este rango de tiempo.")

        # Insertar reserva
        reservation_response = supabase.from_("reservations").insert({
            "player_id": player_id,
            "court_id": court_id,
            "reservation_date": reservation_date,
            "start_time": start_time,
            "end_time": end_time,
            "status": "active",
            "total_price": total_price,
        }).execute()

        if not reservation_response or not reservation_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error al crear la reserva."
            )
        
        #Obtener ID de la reserva
        reservation_id = reservation_response.data[0]["id"]

        # Crear partido relacionado
        match_response = supabase.from_("matches").insert({
            "team1_players": [player_id],
            "team2_players": [],
            "club_id": club_id,
            "court_id": court_id,
            "match_date": reservation_date,
            "match_time": start_time,
            "reservation_id": reservation_id,
        }).execute()

        if not match_response or not match_response.data:
            raise HTTPException(
                status_code=500,
                detail="Error al crear el partido."
            )

        return {
            "message": "Reserva y partido creados exitosamente.",
            "reservation": reservation_response.data,
            "match": match_response.data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la reserva: {str(e)}")



# Obtener reservas de jugador
@router.get("/")
def get_reservations(current_user: dict = Depends(get_current_user)):
    try:
        user_role = current_user["role"]
        if user_role == "player":
            player_id = current_user["id"]
            reservations = supabase.from_("reservations").select("*").match({
                "player_id": player_id,
            }).execute()
        elif user_role == "club":
            club_id = current_user["club_id"]
            reservations = supabase.rpc("get_reservations_by_club", {"club_id": club_id}).execute()
        else:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver reservas.")

        return {"data": reservations.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reservas: {str(e)}")


# Cancelar una reserva
@router.delete("/{reservation_id}")
def cancel_reservation(reservation_id: str, current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.from_("reservations").delete().eq("id", reservation_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Reserva no encontrada.")

        return {"message": "Reserva cancelada exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cancelar la reserva: {str(e)}")


# Checar disponibilidad
@router.get("/available-times")
def get_available_times(club_id: str, date: str, current_user: dict = Depends(get_current_user)):
    try:
        print("Current User:", current_user)  # Debug para verificar el usuario actual

        # Validar el tipo de usuario
        user_type = current_user.get("user_type")
        if not user_type:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver horarios disponibles.")

        # Determinar el día de la semana
        day_of_week = datetime.strptime(date, "%Y-%m-%d").weekday()  # 0 = Lunes, 6 = Domingo

        # Obtener horarios de apertura y cierre para las canchas del club en ese día
        schedules_response = supabase.from_("schedules").select("court_id, opening_time, closing_time").match({
            "club_id": club_id,
            "day_of_week": day_of_week,
        }).execute()

        if not schedules_response.data:
            raise HTTPException(status_code=404, detail="No se encontraron horarios para este club y día.")

        schedules = schedules_response.data

        # Determinar la hora actual si la fecha es hoy
        current_time = None
        if date == datetime.now().strftime("%Y-%m-%d"):
            current_time = datetime.now().time()

        # Generar horarios disponibles para cada cancha
        available_times = {}
        for schedule in schedules:
            opening_time = datetime.strptime(schedule["opening_time"], "%H:%M:%S").time()
            closing_time = datetime.strptime(schedule["closing_time"], "%H:%M:%S").time()

            # Validar que apertura y cierre están definidos
            if not opening_time or not closing_time:
                continue

            # Filtrar horarios pasados si es hoy
            if current_time:
                opening_time = max(opening_time, current_time)

            # Generar intervalos de 30 minutos
            times = []
            current = datetime.combine(datetime.today(), opening_time)
            closing_limit = datetime.combine(datetime.today(), closing_time) - timedelta(minutes=60)

            while current.time() < closing_limit.time():
                times.append(current.strftime("%H:%M"))
                current += timedelta(minutes=30)

            available_times[schedule["court_id"]] = times

        # Obtener reservas y bloqueos para las canchas en la fecha seleccionada
        reservations_response = supabase.from_("reservations").select("court_id, start_time").match({
            "reservation_date": date,
        }).execute()
        blocked_times_response = supabase.from_("court_blocks").select("court_id, start_time").match({
            "start_date": date,
        }).execute()

        reserved_times = {
            (r["court_id"], r["start_time"]) for r in reservations_response.data
        }
        blocked_times_set = {
            (b["court_id"], b["start_time"]) for b in blocked_times_response.data
        }

        # Excluir horarios reservados o bloqueados
        final_available_times = {}
        for court_id, times in available_times.items():
            final_available_times[court_id] = [
                time for time in times if (court_id, time) not in reserved_times and (court_id, time) not in blocked_times_set
            ]

        return {"available_times": final_available_times}

    except Exception as e:
        print(f"Error in get_available_times: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener horarios disponibles: {str(e)}")

# Checar disponibilidad  por cancha sin transpapelarse con otras reservas
@router.get("/available-courts")
def get_available_courts(club_id: str, date: str, time: str):
    try:
        # Convertir hora y fecha a objetos de datetime
        start_time = datetime.strptime(time, "%H:%M")
        end_time = start_time + timedelta(minutes=60)  # Suponiendo que la duración es 1 hora

        # Obtener todas las canchas del club
        courts = supabase.from_("courts").select("*").eq("club_id", club_id).execute()

        if not courts.data:
            raise HTTPException(status_code=404, detail="No se encontraron canchas para este club.")

        available_courts = []

        for court in courts.data:
            # Verificar si la cancha tiene reservas superpuestas
            overlapping_reservations = supabase.from_("reservations").select("*").match({
                "court_id": court["id"],
                "reservation_date": date,
            }).execute()

            if overlapping_reservations.data:
                is_available = True
                for reservation in overlapping_reservations.data:
                    reservation_start = datetime.strptime(reservation["start_time"], "%H:%M:%S")
                    reservation_end = datetime.strptime(reservation["end_time"], "%H:%M:%S")

                    # Verificar si los rangos de tiempo se superponen
                    if not (end_time <= reservation_start or start_time >= reservation_end):
                        is_available = False
                        break

                if not is_available:
                    continue

            # Verificar si la cancha está bloqueada
            overlapping_blocks = supabase.from_("court_blocks").select("*").match({
                "court_id": court["id"],
                "start_date": date,
                "end_date": date,
            }).execute()

            if overlapping_blocks.data:
                for block in overlapping_blocks.data:
                    block_start = datetime.strptime(block["start_time"], "%H:%M:%S")
                    block_end = datetime.strptime(block["end_time"], "%H:%M:%S")

                    # Verificar si los rangos de tiempo se superponen
                    if not (end_time <= block_start or start_time >= block_end):
                        is_available = False
                        break

                if not is_available:
                    continue

            # Si pasó todas las verificaciones, agregar a la lista de disponibles
            available_courts.append(court)

        return {"available_courts": available_courts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener canchas disponibles: {str(e)}")
    

