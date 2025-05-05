from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from uuid import UUID
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response
from app.utils.tournament_utils import generate_tournament_preview
from app.utils.notification_utils import create_notification


router = APIRouter()

class TournamentRegisterTeamData(BaseModel):
    tournament_id: UUID
    partner_id: UUID

@router.post("/")
async def create_tournament(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        club_id = current_user["club_id"]
        club_user_id = current_user["id"]

        tournament_data = {
            "name": data["name"],
            "club_id": club_id,
            "start_date": data["start_date"],
            "start_time": data["start_time"],
            "end_date": data["end_date"],
            "end_time": data["end_time"],
            "category": data["category"],
            "gender": data["gender"],
            "system": data["system"],
            "min_pairs": data["min_pairs"],
            "max_pairs": data["max_pairs"],
            "courts_used": data["courts_used"],
            "price_per_pair": data["price_per_pair"],
            "prize": data["prize"],
        }

        # Insertar el torneo en la base de datos
        response = supabase.from_("tournaments").insert(tournament_data).execute()

        if not response:
            raise HTTPException(status_code=400, detail=response.error.message)
        
        create_notification(
            club_user_id,
            "Torneo Creado",
            f"Haz creado el torneo {data['name']}",
            "/club/torneos",
        )

        return {"message": "Torneo creado exitosamente.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el torneo: {str(e)}")
    

@router.put("/{tournament_id}")
async def update_tournament(tournament_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    try:
        # Verificar que el usuario sea del club que creó el torneo
        club_id = current_user.get("club_id")
        tournament = supabase.from_("tournaments").select("*").eq("id", tournament_id).single().execute()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Torneo no encontrado.")
        
        if tournament.data["club_id"] != club_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para editar este torneo.")

        # Actualizar el torneo con los nuevos datos
        update_response = supabase.from_("tournaments").update(data).eq("id", tournament_id).execute()

        if not update_response:
            raise HTTPException(status_code=500, detail=f"Error al actualizar el torneo: {update_response.error.message}")

        return {"message": "Torneo actualizado exitosamente.", "data": update_response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el torneo: {str(e)}")
    

@router.post("/register-team")
async def register_team(
    register_data: TournamentRegisterTeamData,
    current_user: dict = Depends(get_current_user),
):
    try:
        player1_id: UUID = UUID(current_user["id"])  # Obtenemos player1_id del usuario autenticado
        player2_id: UUID = register_data.partner_id  

        # 1. Verificar que el equipo no esté ya registrado
        existing_team = supabase.from_("tournament_teams").select("*").eq("tournament_id", register_data.tournament_id).eq("player1_id", player1_id).eq("player2_id", player2_id).execute().data

        if existing_team:
            raise HTTPException(status_code=400, detail="Este equipo ya está registrado en el torneo.")

        # 2. Registrar el equipo
        insert_result = supabase.from_("tournament_teams").insert({
            "tournament_id": str(register_data.tournament_id),
            "player1_id": str(player1_id),
            "player2_id": str(player2_id),
        }).execute()

        if insert_result.count == 0:
            raise HTTPException(status_code=500, detail="Error al registrar el equipo en el torneo.")

        create_notification(
            player1_id,
            "Inscripción a Torneo",
            f"Te inscribiste exitosamente al Torneo.",
            f"/tournament/{register_data.tournament_id}",
        )
        
        create_notification(
            player2_id,
            "invitación Torneo",
            "Te han escogido como pareja para el torneo",
            f"/tournament/{register_data.tournament_id}",
        )

        return {"message": "Equipo registrado exitosamente."}

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")





@router.get("/{tournament_id}/preview")
async def get_tournament_preview(tournament_id: str):
    """
    Genera un preview del rol de juegos para un torneo.
    """
    matches = generate_tournament_preview(tournament_id)
    return {"matches": matches}


@router.post("/{tournament_id}/save-matches")
async def save_matches(tournament_id: str, matches: List[Dict]):
    """
    Guarda los partidos generados en la tabla matches.
    """
    for match in matches:
        supabase.from_("matches").insert({
            "tournament_id": tournament_id,
            "team1_players": [match["team1"]],
            "team2_players": [match["team2"]],
            "match_date": match["match_date"],
            "match_time": match["match_time"],
            "court_id": match.get("court_id"),  # Asignar cancha si es necesario
        }).execute()
    return {"message": "Partidos guardados exitosamente."}