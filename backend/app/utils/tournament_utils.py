from datetime import datetime, timedelta
from app.db.connection import supabase
import math
import random


def generate_tournament_preview(tournament_id: str):
    """
    Genera un preview completo del cuadro de torneo con horarios y asignación de canchas.
    :param tournament_id: ID del torneo.
    :return: Diccionario con estructura del torneo incluyendo partidos y metadatos.
    """
    # Obtener detalles del torneo
    tournament = supabase.from_("tournaments").select("*").eq("id", tournament_id).single().execute()
    tournament = tournament.data

    # Obtener equipos inscritos con detalles de jugadores
    teams = supabase.from_("tournament_teams").select("""
        id, player1_id, player2_id, status,
        player1:profiles!tournament_teams_player1_id_fkey(first_name, last_name),
        player2:profiles!tournament_teams_player2_id_fkey(first_name, last_name)
    """).eq("tournament_id", tournament_id).eq("status", "confirmed").execute()
    teams = teams.data

    if not teams:
        return {"error": "No hay equipos confirmados inscritos en el torneo"}

    system = tournament["system"]
    courts_used = tournament.get("courts_used", [])
    
    # Generar estructura según el sistema del torneo
    if system == "round-robin":
        return _generate_round_robin_preview(tournament, teams, courts_used)
    elif system == "eliminacion directa":
        return _generate_elimination_preview(tournament, teams, courts_used)
    elif system == "combinado":
        return _generate_combined_preview(tournament, teams, courts_used)
    elif system == "liga":
        return _generate_league_preview(tournament, teams, courts_used)
    else:
        return {"error": f"Sistema de torneo '{system}' no soportado"}


def _generate_round_robin_preview(tournament, teams, courts_used):
    """Genera preview para sistema round-robin con grupos."""
    tournament_id = tournament["id"]
    num_teams = len(teams)
    
    # Determinar tamaño de grupos óptimo
    if num_teams <= 8:
        group_size = 4
    elif num_teams <= 12:
        group_size = 4
    else:
        group_size = 5
    
    # Crear grupos balanceados
    random.shuffle(teams)  # Mezclar equipos para distribución aleatoria
    groups = []
    for i in range(0, num_teams, group_size):
        group_teams = teams[i:i + group_size]
        if group_teams:  # Solo agregar si hay equipos
            groups.append({
                "name": f"Grupo {chr(65 + len(groups))}",  # A, B, C, etc.
                "teams": group_teams
            })
    
    # Generar partidos por grupo
    all_matches = []
    group_matches = {}
    
    start_date = datetime.strptime(tournament["start_date"], "%Y-%m-%d").date()
    start_time = datetime.strptime(tournament["start_time"], "%H:%M:%S").time()
    current_datetime = datetime.combine(start_date, start_time)
    court_index = 0
    
    for group in groups:
        group_name = group["name"]
        group_matches[group_name] = []
        group_teams = group["teams"]
        
        # Generar todos los partidos del grupo (todos contra todos)
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                match = {
                    "id": f"group_{group_name.lower().replace(' ', '_')}_{i}_{j}",
                    "tournament_id": tournament_id,
                    "phase": "Fase de Grupos",
                    "group": group_name,
                    "team1": {
                        "id": group_teams[i]["id"],
                        "player1": group_teams[i]["player1"],
                        "player2": group_teams[i]["player2"],
                        "name": f"{group_teams[i]['player1']['first_name']} {group_teams[i]['player1']['last_name']} / {group_teams[i]['player2']['first_name']} {group_teams[i]['player2']['last_name']}"
                    },
                    "team2": {
                        "id": group_teams[j]["id"],
                        "player1": group_teams[j]["player1"],
                        "player2": group_teams[j]["player2"], 
                        "name": f"{group_teams[j]['player1']['first_name']} {group_teams[j]['player1']['last_name']} / {group_teams[j]['player2']['first_name']} {group_teams[j]['player2']['last_name']}"
                    },
                    "match_date": current_datetime.date().isoformat(),
                    "match_time": current_datetime.time().isoformat(),
                    "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                    "editable": True
                }
                
                group_matches[group_name].append(match)
                all_matches.append(match)
                
                # Avanzar tiempo y cancha
                current_datetime += timedelta(hours=1, minutes=20)
                court_index += 1
    
    return {
        "tournament_id": tournament_id,
        "system": "round-robin",
        "structure": {
            "groups": groups,
            "group_matches": group_matches,
            "playoffs": None  # Solo grupos en round-robin puro
        },
        "matches": all_matches,
        "editable": True,
        "court_assignments": True
    }


def _generate_elimination_preview(tournament, teams, courts_used):
    """Genera preview para sistema de eliminación directa."""
    tournament_id = tournament["id"]
    num_teams = len(teams)
    
    # Calcular número de rondas necesarias (potencia de 2 más cercana)
    bracket_size = 2 ** math.ceil(math.log2(num_teams))
    num_rounds = int(math.log2(bracket_size))
    
    # Mezclar equipos para distribución aleatoria
    random.shuffle(teams)
    
    # Crear estructura del bracket
    bracket_structure = {}
    all_matches = []
    
    start_date = datetime.strptime(tournament["start_date"], "%Y-%m-%d").date()
    start_time = datetime.strptime(tournament["start_time"], "%H:%M:%S").time()
    current_datetime = datetime.combine(start_date, start_time)
    
    # Generar nombres de rondas
    round_names = _get_round_names(num_rounds)
    
    # Primera ronda - emparejar equipos reales
    first_round_matches = []
    court_index = 0
    
    for i in range(0, min(len(teams), bracket_size // 2 * 2), 2):
        if i + 1 < len(teams):
            match = {
                "id": f"round_1_match_{i//2 + 1}",
                "tournament_id": tournament_id,
                "phase": round_names[0],
                "round": 1,
                "match_number": i//2 + 1,
                "team1": {
                    "id": teams[i]["id"],
                    "player1": teams[i]["player1"],
                    "player2": teams[i]["player2"],
                    "name": f"{teams[i]['player1']['first_name']} {teams[i]['player1']['last_name']} / {teams[i]['player2']['first_name']} {teams[i]['player2']['last_name']}"
                },
                "team2": {
                    "id": teams[i + 1]["id"], 
                    "player1": teams[i + 1]["player1"],
                    "player2": teams[i + 1]["player2"],
                    "name": f"{teams[i + 1]['player1']['first_name']} {teams[i + 1]['player1']['last_name']} / {teams[i + 1]['player2']['first_name']} {teams[i + 1]['player2']['last_name']}"
                },
                "match_date": current_datetime.date().isoformat(),
                "match_time": current_datetime.time().isoformat(),
                "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                "editable": True
            }
            
            first_round_matches.append(match)
            all_matches.append(match)
            
            # Avanzar tiempo y cancha
            current_datetime += timedelta(hours=1, minutes=20)
            court_index += 1
    
    bracket_structure[round_names[0]] = first_round_matches
    
    # Generar rondas siguientes (partidos placeholder)
    matches_in_previous_round = len(first_round_matches)
    
    for round_num in range(2, num_rounds + 1):
        round_matches = []
        matches_in_round = matches_in_previous_round // 2
        
        if matches_in_round == 0:
            break
            
        for i in range(matches_in_round):
            match = {
                "id": f"round_{round_num}_match_{i + 1}",
                "tournament_id": tournament_id,
                "phase": round_names[round_num - 1],
                "round": round_num,
                "match_number": i + 1,
                "team1": {
                    "id": f"winner_r{round_num-1}_m{i*2 + 1}",
                    "name": f"Ganador Partido {i*2 + 1} - {round_names[round_num - 2]}"
                },
                "team2": {
                    "id": f"winner_r{round_num-1}_m{i*2 + 2}",
                    "name": f"Ganador Partido {i*2 + 2} - {round_names[round_num - 2]}"
                },
                "match_date": (current_datetime + timedelta(days=round_num - 1)).date().isoformat(),
                "match_time": current_datetime.time().isoformat(),
                "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                "editable": True,
                "depends_on": [f"round_{round_num-1}_match_{i*2 + 1}", f"round_{round_num-1}_match_{i*2 + 2}"]
            }
            
            round_matches.append(match)
            all_matches.append(match)
            court_index += 1
        
        bracket_structure[round_names[round_num - 1]] = round_matches
        matches_in_previous_round = matches_in_round
    
    return {
        "tournament_id": tournament_id,
        "system": "eliminacion directa",
        "structure": {
            "bracket": bracket_structure,
            "rounds": num_rounds,
            "bracket_size": bracket_size
        },
        "matches": all_matches,
        "editable": True,
        "court_assignments": True
    }


def _generate_combined_preview(tournament, teams, courts_used):
    """Genera preview para sistema combinado (grupos + playoffs)."""
    tournament_id = tournament["id"]
    num_teams = len(teams)
    
    # Fase de grupos (similar a round-robin)
    group_size = 4 if num_teams <= 16 else 5
    random.shuffle(teams)
    
    groups = []
    for i in range(0, num_teams, group_size):
        group_teams = teams[i:i + group_size]
        if group_teams:
            groups.append({
                "name": f"Grupo {chr(65 + len(groups))}",
                "teams": group_teams
            })
    
    # Generar partidos de grupos
    all_matches = []
    group_matches = {}
    
    start_date = datetime.strptime(tournament["start_date"], "%Y-%m-%d").date()
    start_time = datetime.strptime(tournament["start_time"], "%H:%M:%S").time()
    current_datetime = datetime.combine(start_date, start_time)
    court_index = 0
    
    # Partidos de grupos
    for group in groups:
        group_name = group["name"] 
        group_matches[group_name] = []
        group_teams = group["teams"]
        
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                match = {
                    "id": f"group_{group_name.lower().replace(' ', '_')}_{i}_{j}",
                    "tournament_id": tournament_id,
                    "phase": "Fase de Grupos",
                    "group": group_name,
                    "team1": {
                        "id": group_teams[i]["id"],
                        "player1": group_teams[i]["player1"],
                        "player2": group_teams[i]["player2"],
                        "name": f"{group_teams[i]['player1']['first_name']} {group_teams[i]['player1']['last_name']} / {group_teams[i]['player2']['first_name']} {group_teams[i]['player2']['last_name']}"
                    },
                    "team2": {
                        "id": group_teams[j]["id"],
                        "player1": group_teams[j]["player1"],
                        "player2": group_teams[j]["player2"],
                        "name": f"{group_teams[j]['player1']['first_name']} {group_teams[j]['player1']['last_name']} / {group_teams[j]['player2']['first_name']} {group_teams[j]['player2']['last_name']}"
                    },
                    "match_date": current_datetime.date().isoformat(),
                    "match_time": current_datetime.time().isoformat(),
                    "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                    "editable": True
                }
                
                group_matches[group_name].append(match)
                all_matches.append(match)
                
                current_datetime += timedelta(hours=1, minutes=20)
                court_index += 1
    
    # Fase de playoffs (eliminación directa con clasificados)
    # Asumir que clasifican los primeros 2 de cada grupo
    playoff_teams = len(groups) * 2
    playoff_bracket = {}
    
    # Avanzar fecha para playoffs
    current_datetime = current_datetime + timedelta(days=1)
    
    # Generar estructura de playoffs
    playoff_rounds = int(math.log2(playoff_teams)) if playoff_teams > 1 else 1
    round_names = _get_playoff_round_names(playoff_rounds)
    
    matches_in_round = playoff_teams // 2
    
    for round_num in range(1, playoff_rounds + 1):
        round_matches = []
        
        for i in range(matches_in_round):
            if round_num == 1:
                # Primera ronda de playoffs - equipos por determinar
                team1_name = f"1° {chr(65 + i * 2)}"  # 1° A, 1° C, etc.
                team2_name = f"2° {chr(65 + i * 2 + 1)}"  # 2° B, 2° D, etc.
            else:
                team1_name = f"Ganador PO {i*2 + 1}"
                team2_name = f"Ganador PO {i*2 + 2}"
            
            match = {
                "id": f"playoff_round_{round_num}_match_{i + 1}",
                "tournament_id": tournament_id,
                "phase": f"Playoffs - {round_names[round_num - 1]}",
                "round": round_num,
                "match_number": i + 1,
                "team1": {
                    "id": f"playoff_tbd_{round_num}_{i*2 + 1}",
                    "name": team1_name
                },
                "team2": {
                    "id": f"playoff_tbd_{round_num}_{i*2 + 2}",
                    "name": team2_name
                },
                "match_date": current_datetime.date().isoformat(),
                "match_time": current_datetime.time().isoformat(),
                "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                "editable": True
            }
            
            round_matches.append(match)
            all_matches.append(match)
            
            current_datetime += timedelta(hours=1, minutes=20)
            court_index += 1
        
        playoff_bracket[round_names[round_num - 1]] = round_matches
        matches_in_round //= 2
        
        if matches_in_round == 0:
            break
    
    return {
        "tournament_id": tournament_id,
        "system": "combinado",
        "structure": {
            "groups": groups,
            "group_matches": group_matches,
            "playoffs": playoff_bracket,
            "playoff_rounds": playoff_rounds
        },
        "matches": all_matches,
        "editable": True,
        "court_assignments": True
    }


def _generate_league_preview(tournament, teams, courts_used):
    """Genera preview para sistema de liga (todos contra todos)."""
    tournament_id = tournament["id"]
    num_teams = len(teams)
    
    all_matches = []
    start_date = datetime.strptime(tournament["start_date"], "%Y-%m-%d").date()
    start_time = datetime.strptime(tournament["start_time"], "%H:%M:%S").time()
    current_datetime = datetime.combine(start_date, start_time)
    court_index = 0
    
    # Generar todos los partidos (todos contra todos)
    for i in range(num_teams):
        for j in range(i + 1, num_teams):
            match = {
                "id": f"league_match_{i}_{j}",
                "tournament_id": tournament_id,
                "phase": "Liga",
                "team1": {
                    "id": teams[i]["id"],
                    "player1": teams[i]["player1"],
                    "player2": teams[i]["player2"],
                    "name": f"{teams[i]['player1']['first_name']} {teams[i]['player1']['last_name']} / {teams[i]['player2']['first_name']} {teams[i]['player2']['last_name']}"
                },
                "team2": {
                    "id": teams[j]["id"],
                    "player1": teams[j]["player1"],
                    "player2": teams[j]["player2"],
                    "name": f"{teams[j]['player1']['first_name']} {teams[j]['player1']['last_name']} / {teams[j]['player2']['first_name']} {teams[j]['player2']['last_name']}"
                },
                "match_date": current_datetime.date().isoformat(),
                "match_time": current_datetime.time().isoformat(),
                "court_id": courts_used[court_index % len(courts_used)] if courts_used else None,
                "editable": True
            }
            
            all_matches.append(match)
            
            # Avanzar tiempo y cancha
            current_datetime += timedelta(hours=1, minutes=20)
            court_index += 1
    
    return {
        "tournament_id": tournament_id,
        "system": "liga",
        "structure": {
            "type": "round_robin_single",
            "total_matches": len(all_matches)
        },
        "matches": all_matches,
        "editable": True,
        "court_assignments": True
    }


def _get_round_names(num_rounds):
    """Genera nombres de rondas para eliminación directa."""
    if num_rounds == 1:
        return ["Final"]
    elif num_rounds == 2:
        return ["Semifinal", "Final"]
    elif num_rounds == 3:
        return ["Cuartos de Final", "Semifinal", "Final"]
    elif num_rounds == 4:
        return ["Octavos de Final", "Cuartos de Final", "Semifinal", "Final"]
    elif num_rounds == 5:
        return ["Dieciseisavos de Final", "Octavos de Final", "Cuartos de Final", "Semifinal", "Final"]
    else:
        # Para más rondas, usar nomenclatura genérica
        names = []
        for i in range(num_rounds - 3):
            names.append(f"Ronda {i + 1}")
        names.extend(["Cuartos de Final", "Semifinal", "Final"])
        return names


def _get_playoff_round_names(num_rounds):
    """Genera nombres de rondas para playoffs."""
    if num_rounds == 1:
        return ["Final"]
    elif num_rounds == 2:
        return ["Semifinal", "Final"]
    elif num_rounds == 3:
        return ["Cuartos de Final", "Semifinal", "Final"] 
    else:
        names = []
        for i in range(num_rounds - 2):
            names.append(f"Ronda {i + 1}")
        names.extend(["Semifinal", "Final"])
        return names