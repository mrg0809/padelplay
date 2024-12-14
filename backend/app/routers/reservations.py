from fastapi import APIRouter, HTTPException, Depends
from app.db.connection import supabase
from app.core.security import get_current_user

# Inicializa el router
router = APIRouter()

# Crear una reserva
@router.post("/")
def create_reservation(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        player_id = current_user["id"]
        court_id = data["court_id"]
        reservation_date = data["reservation_date"]
        start_time = data["start_time"]
        end_time = data["end_time"]

        # Verificar disponibilidad
        overlapping_reservations = supabase.from_("reservations").select("*").match({
            "court_id": court_id,
            "reservation_date": reservation_date,
        }).execute()

        overlapping_blocks = supabase.from_("court_blocks").select("*").match({
            "court_id": court_id,
            "block_date": reservation_date,
        }).execute()

        if overlapping_reservations.data or overlapping_blocks.data:
            raise HTTPException(status_code=400, detail="La cancha no está disponible para este rango de tiempo.")

        # Insertar reserva
        response = supabase.from_("reservations").insert({
            "player_id": player_id,
            "court_id": court_id,
            "reservation_date": reservation_date,
            "start_time": start_time,
            "end_time": end_time,
            "status": "active",
        }).execute()

        return {"message": "Reserva creada exitosamente.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la reserva: {str(e)}")


# Obtener reservas
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
