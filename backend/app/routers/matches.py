from fastapi import APIRouter, HTTPException, Depends
from app.db.connection import supabase
from app.core.security import get_current_user

router = APIRouter()

@router.get("/match/{match_id}")
def get_match_details(match_id: str):
    try:
        # Obtener los detalles básicos del partido
        match = supabase.from_("matches").select("*").eq("id", match_id).single().execute()

        if not match.data:
            raise HTTPException(status_code=404, detail="Partido no encontrado.")

        match_data = match.data

        # Obtener información del club
        club = supabase.from_("clubs").select("name").eq("id", match_data["club_id"]).single().execute()
        match_data["club_name"] = club.data.get("name", "Club no disponible") if club.data else "Club no disponible"

        # Obtener información de la cancha
        court = supabase.from_("courts").select("name").eq("id", match_data["court_id"]).single().execute()
        match_data["court_name"] = court.data.get("name", "Cancha no disponible") if court.data else "Cancha no disponible"

        # Obtener información de los jugadores
        team1_names = []
        team2_names = []

        if match_data["team1_players"]:
            players_team1 = supabase.from_("profiles").select("id, full_name").in_("id", match_data["team1_players"]).execute()
            team1_names = [player["full_name"] for player in players_team1.data] if players_team1.data else []

        if match_data["team2_players"]:
            players_team2 = supabase.from_("profiles").select("id, full_name").in_("id", match_data["team2_players"]).execute()
            team2_names = [player["full_name"] for player in players_team2.data] if players_team2.data else []

        match_data["team1_players"] = team1_names
        match_data["team2_players"] = team2_names

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