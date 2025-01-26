from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response
from app.utils.email_utils import send_match_invitation_email

router = APIRouter()

class AddPlayerPayload(BaseModel):
    email_or_phone: str
    match_id: str
    team: int
    position: int
    club_name: str
    player_name: str
    match_date: str
    match_time: str


@router.get("/match/{match_id}")
def get_match_details(match_id: str):
    try:
        # Obtener los detalles básicos del partido
        match = supabase.from_("matches").select("*").eq("id", match_id).single().execute()

        if not match.data:
            raise HTTPException(status_code=404, detail="Partido no encontrado.")

        match_data = match.data

        # Obtener información del club
        club = supabase.from_("clubs").select("name, latitude, longitude").eq("id", match_data["club_id"]).single().execute()
        match_data["club_name"] = club.data.get("name", "Club no disponible") if club.data else "Club no disponible"
        match_data["latitude"] = club.data.get("latitude", "Latitud no disponible") if club.data else "Latitud no disponible"
        match_data["longitude"] = club.data.get("longitude", "Longitud no disponible") if club.data else "Longitud no disponible"

        # Obtener información de la cancha
        court = supabase.from_("courts").select("name").eq("id", match_data["court_id"]).single().execute()
        match_data["court_name"] = court.data.get("name", "Cancha no disponible") if court.data else "Cancha no disponible"

        # Obtener información de los jugadores
        team1_info = []
        team2_info = []

        if match_data["team1_players"]:
            players_team1 = supabase.from_("players").select("user_id, first_name, photo_url, category").in_("user_id", match_data["team1_players"]).execute()
            team1_info = [{"first_name": player["first_name"], "photo_url": player["photo_url"], "category": player["category"]} for player in players_team1.data] if players_team1.data else []

        if match_data["team2_players"]:
            players_team2 = supabase.from_("players").select("user_id, first_name, photo_url, category").in_("user_id", match_data["team2_players"]).execute()
            team2_info = [{"first_name": player["first_name"], "photo_url": player["photo_url"], "category": player["category"]} for player in players_team2.data] if players_team2.data else []

        match_data["team1_players"] = team1_info
        match_data["team2_players"] = team2_info

        return match_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los detalles del partido: {str(e)}")


@router.put("/match/{match_id}")
def update_match_score(match_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    try:
        score = data.get("score")
        if score is None:
            raise HTTPException(status_code=400, detail="El marcador es requerido.")

        supabase.from_("matches").update({"score": score}).eq("id", match_id).execute()

        return {"message": "Marcador actualizado exitosamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el marcador: {str(e)}")

@router.get("/upcoming")
def get_upcoming_matches(current_user: dict = Depends(get_current_user)):
    try:
        player_id = current_user["id"]
        
        # Obtener partidos donde el jugador está en team1_players o team2_players
        response = supabase.from_("matches").select(
            """
            id, match_date, match_time, 
            team1_players, team2_players,
            club_id, court_id,
            clubs(name) as club_name, 
            courts(name) as court_name
            """
        ).or_(
            f"team1_players.cs.{{{player_id}}},team2_players.cs.{{{player_id}}}"
        ).order("match_date").execute()

        if not response:
            raise HTTPException(status_code=500, detail="Error al obtener los partidos.")

        matches = response.data

        # Filtrar solo partidos futuros
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        upcoming_matches = [
            match for match in matches
            if f"{match['match_date']} {match['match_time']}" > now
        ]

        return {"matches": upcoming_matches}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los partidos: {str(e)}")
    

    
@router.post("/add-player")
async def add_player(data: AddPlayerPayload, current_user: dict = Depends(get_current_user)):
    try:
        print(data)
        # Verificar si el partido existe
        match_response = supabase.from_("matches").select("*").eq("id", data.match_id).execute()
        match_data = handle_supabase_response(match_response)
        if not match_data or len(match_data) == 0:
            raise HTTPException(status_code=404, detail="Partido no encontrado.")

        # Obtener el primer y único partido de los datos
        match = match_data[0]

        # Buscar al jugador por correo o teléfono
        player_response = supabase.from_("players").select("*").or_(
            f"email.eq.{data.email_or_phone},phone.eq.{data.email_or_phone}"
        ).execute()
        player_data = handle_supabase_response(player_response)

        player_id = None
        is_registered = False

        if player_data and len(player_data["data"]) > 0:
            # Si el jugador está registrado, obtener su ID
            player_id = player_data[0]["user_id"]
            is_registered = True
        else:
            # Enviar invitación si no está registrado
            send_match_invitation_email(data.email_or_phone, data)

        # Verificar si el jugador ya está en algún equipo del partido
        all_players = (match.get("team1_players", []) + match.get("team2_players", []))
        if player_id and player_id in all_players:
            raise HTTPException(status_code=400, detail="El jugador ya está registrado en el partido.")

        # Verificar si la posición en el equipo ya está ocupada
        team_column = "team1_players" if data.team == 1 else "team2_players"
        current_team = match.get(team_column, [])  # Obtener jugadores del equipo
        if len(current_team) >= 2:
            raise HTTPException(status_code=400, detail="El equipo ya tiene todas las posiciones ocupadas.")

        # Agregar el jugador al equipo correspondiente
        updated_team = current_team + [player_id] if is_registered else current_team
        update_response = supabase.from_("matches").update({team_column: updated_team}).eq("id", data.match_id).execute()
        handle_supabase_response(update_response)


        return {
            "message": "Jugador agregado exitosamente.",
            "status": "success" if is_registered else "invited",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al agregar el jugador: {str(e)}")

