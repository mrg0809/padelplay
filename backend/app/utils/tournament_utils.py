from datetime import datetime, timedelta
from app.db.connection import supabase

def generate_tournament_preview(tournament_id: str):
    """
    Genera un preview del rol de juegos para un torneo.
    :param tournament_id: ID del torneo.
    :return: Lista de partidos con fechas y horarios preliminares.
    """
    # Obtener detalles del torneo
    tournament = supabase.from_("tournaments").select("*").eq("id", tournament_id).single().execute()
    tournament = tournament.data

    # Obtener equipos inscritos
    teams = supabase.from_("tournament_teams").select("*").eq("tournament_id", tournament_id).execute()
    teams = teams.data

    matches = []
    num_teams = len(teams)
    start_date = datetime.strptime(tournament["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(tournament["end_date"], "%Y-%m-%d").date()
    start_time = datetime.strptime(tournament["start_time"], "%H:%M:%S").time()
    system = tournament["system"]

    # Intervalo entre partidos (1 hora y 20 minutos)
    match_interval = timedelta(hours=1, minutes=20)

    if start_date == end_date:
        # Torneo de un solo día
        current_time = datetime.combine(start_date, start_time)
        if system == "liga":
            # Todos contra todos
            for i in range(num_teams):
                for j in range(i + 1, num_teams):
                    match = {
                        "tournament_id": tournament_id,
                        "team1": teams[i]["id"],
                        "team2": teams[j]["id"],
                        "match_date": start_date.isoformat(),
                        "match_time": current_time.time().isoformat(),
                    }
                    matches.append(match)
                    current_time += match_interval
        elif system == "round-robin":
            # Round-Robin con grupos (simplificado)
            group_size = 4  # Tamaño de cada grupo
            groups = [teams[i:i + group_size] for i in range(0, num_teams, group_size)]
            for group in groups:
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        match = {
                            "tournament_id": tournament_id,
                            "team1": group[i]["id"],
                            "team2": group[j]["id"],
                            "match_date": start_date.isoformat(),
                            "match_time": current_time.time().isoformat(),
                        }
                        matches.append(match)
                        current_time += match_interval
    else:
        # Torneo de varios días
        current_date = start_date
        if system == "liga":
            # Todos contra todos
            for i in range(num_teams):
                for j in range(i + 1, num_teams):
                    match = {
                        "tournament_id": tournament_id,
                        "team1": teams[i]["id"],
                        "team2": teams[j]["id"],
                        "match_date": current_date.isoformat(),
                        "match_time": start_time.isoformat(),
                    }
                    matches.append(match)
                    current_date += timedelta(days=1)  # Un partido por día
        elif system == "round-robin":
            # Round-Robin con grupos (simplificado)
            group_size = 4  # Tamaño de cada grupo
            groups = [teams[i:i + group_size] for i in range(0, num_teams, group_size)]
            for group in groups:
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        match = {
                            "tournament_id": tournament_id,
                            "team1": group[i]["id"],
                            "team2": group[j]["id"],
                            "match_date": current_date.isoformat(),
                            "match_time": start_time.isoformat(),
                        }
                        matches.append(match)
                        current_date += timedelta(days=1)  # Un partido por día

    return matches