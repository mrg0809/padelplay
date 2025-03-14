from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response
from app.utils.email_utils import send_tournament_invitation_email
from app.utils.tournament_utils import generate_tournament_preview


router = APIRouter()

@router.post("/")
async def create_tournament(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        club_id = current_user["club_id"]

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

        return {"message": "Torneo creado exitosamente.", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el torneo: {str(e)}")
    

@router.post("/{tournament_id}/register-team")
async def register_team(tournament_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """
    Registrar una pareja en un torneo y enviar invitación si el segundo jugador no está registrado.
    """
    try:
        # Obtener el ID del jugador actual (player1)
        player1_id = current_user["id"]
        print(f"Player1 ID: {player1_id}")

        # Validar si el torneo existe
        tournament_response = supabase.from_("tournaments").select("*").eq("id", tournament_id).execute()
        tournament_data = handle_supabase_response(tournament_response)
        if not tournament_data or not isinstance(tournament_data, list) or len(tournament_data) == 0:
            raise HTTPException(status_code=404, detail="Torneo no encontrado.")
        print(f"Tournament data: {tournament_data}")

        # Asegurarse de que el email del segundo jugador esté en los datos
        player2_email = data.get("player2")
        if not player2_email:
            raise HTTPException(status_code=400, detail="El email del segundo jugador es obligatorio.")
        print(f"Player2 Email: {player2_email}")

        # Validar si ya existe un equipo con este jugador en el torneo
        existing_team_response = supabase.from_("tournament_teams").select("id").eq("tournament_id", tournament_id).eq("player1_id", player1_id).execute()
        existing_team_data = handle_supabase_response(existing_team_response)
        print(f"Existing Team Data: {existing_team_data}")

        if isinstance(existing_team_data, dict) and "data" in existing_team_data and len(existing_team_data["data"]) > 0:
            raise HTTPException(status_code=400, detail="Ya estás registrado en este torneo.")

        # Buscar al segundo jugador en la tabla `players` utilizando el email
        player2_response = supabase.from_("players").select("user_id").eq("email", player2_email).execute()
        player2_data = handle_supabase_response(player2_response)
        print(f"Player2 Data: {player2_data}")

        player2_id = None
        if isinstance(player2_data, dict) and "data" in player2_data and len(player2_data["data"]) > 0:
            # Si el jugador está registrado, obtener su ID de usuario
            player2_id = player2_data["data"][0]["user_id"]
        else:
            # Si el jugador no está registrado, enviar invitación
            send_tournament_invitation_email(player2_email, tournament_data[0]["name"])

        # Preparar datos para insertar en la tabla `tournament_teams`
        team_data = {
            "tournament_id": tournament_id,
            "player1_id": player1_id,
            "player2_email": player2_email,
            "player2_id": player2_id,  # Será `None` si el jugador no está registrado
            "status": "pending" if not player2_id else "confirmed"
        }

        # Insertar el equipo en la base de datos
        response = supabase.from_("tournament_teams").insert(team_data).execute()
        inserted_team = handle_supabase_response(response)

        return {"message": "Equipo registrado exitosamente.", "data": inserted_team}

    except HTTPException as e:
        print(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        print(f"Unexpected Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al registrar el equipo: {str(e)}")
    
    

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