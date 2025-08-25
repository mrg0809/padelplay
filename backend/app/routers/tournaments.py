from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response
from app.utils.tournament_utils import generate_tournament_preview
from app.utils.notification_utils import create_notification


router = APIRouter()

class TournamentRegisterTeamData(BaseModel):
    tournament_id: UUID
    partner_id: Optional[UUID] = None

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
        player2_id: Optional[UUID] = register_data.partner_id
        
        # Get tournament info to check if it's retas
        tournament = supabase.from_("tournaments").select("id, system").eq("id", register_data.tournament_id).single().execute()
        if not tournament or not tournament.data:
            raise HTTPException(status_code=404, detail="Torneo no encontrado.")
        
        tournament_system = tournament.data.get("system")
        is_retas = tournament_system == "retas"
        
        # For retas, partner_id can be None (individual registration)
        if is_retas and player2_id is None:
            # Check if player is already registered individually
            existing_registration = supabase.from_("tournament_teams").select("*").eq("tournament_id", register_data.tournament_id).eq("player1_id", player1_id).execute().data
            
            if existing_registration:
                raise HTTPException(status_code=400, detail="Ya estás registrado en estas retas.")
            
            # Register player individually for retas
            insert_result = supabase.from_("tournament_teams").insert({
                "tournament_id": str(register_data.tournament_id),
                "player1_id": str(player1_id),
                "player2_id": None,  # No partner for retas
            }).execute()
            
            if insert_result.count == 0:
                raise HTTPException(status_code=500, detail="Error al registrarte en las retas.")

            create_notification(
                player1_id,
                "Inscripción a Retas",
                f"Te inscribiste exitosamente a las retas.",
                f"/tournament/{register_data.tournament_id}",
            )

            return {"message": "Te registraste exitosamente en las retas."}
        
        # For regular tournaments, partner_id is required
        elif not is_retas and player2_id is None:
            raise HTTPException(status_code=400, detail="Se requiere seleccionar una pareja para torneos regulares.")
        
        # Regular tournament registration with partner
        else:
            # Verificar que el equipo no esté ya registrado
            existing_team = supabase.from_("tournament_teams").select("*").eq("tournament_id", register_data.tournament_id).eq("player1_id", player1_id).eq("player2_id", player2_id).execute().data

            if existing_team:
                raise HTTPException(status_code=400, detail="Este equipo ya está registrado en el torneo.")

            # Registrar el equipo
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
                "Invitación Torneo",
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
    Genera un preview completo del cuadro de torneo con estructura y partidos.
    """
    try:
        tournament_structure = generate_tournament_preview(tournament_id)
        
        if "error" in tournament_structure:
            raise HTTPException(status_code=400, detail=tournament_structure["error"])
        
        return tournament_structure
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar preview del torneo: {str(e)}")


@router.post("/{tournament_id}/save-matches")
async def save_matches(tournament_id: str, matches: List[Dict]):
    """
    Guarda los partidos generados en la tabla matches con validación de canchas.
    """
    try:
        # Obtener detalles del torneo para validación
        tournament = supabase.from_("tournaments").select("*").eq("id", tournament_id).single().execute()
        tournament_data = tournament.data
        
        if not tournament_data:
            raise HTTPException(status_code=404, detail="Torneo no encontrado")
        
        club_id = tournament_data["club_id"]
        saved_matches = []
        
        for match in matches:
            # Validar estructura de match
            team1_data = match.get("team1", {})
            team2_data = match.get("team2", {})
            
            if not team1_data.get("id") or not team2_data.get("id"):
                continue  # Saltar matches placeholder o incompletos
                
            match_data = {
                "tournament_id": tournament_id,
                "club_id": club_id,
                "team1_players": [team1_data["id"]],
                "team2_players": [team2_data["id"]],
                "match_date": match["match_date"],
                "match_time": match["match_time"],
                "court_id": match.get("court_id"),
                "gender": tournament_data.get("gender", "open"),
                "category": tournament_data.get("category", "open")
            }
            
            # Insertar match
            result = supabase.from_("matches").insert(match_data).execute()
            
            if result.data:
                saved_matches.append(result.data[0])
                
                # Crear reserva para bloquear la cancha si hay court_id
                if match.get("court_id"):
                    try:
                        from datetime import datetime, timedelta
                        
                        # Calcular end_time (1 hora después)
                        start_datetime = datetime.strptime(f"{match['match_date']} {match['match_time']}", "%Y-%m-%d %H:%M:%S")
                        end_time = (start_datetime + timedelta(hours=1)).time()
                        
                        reservation_data = {
                            "club_id": club_id,
                            "court_id": match["court_id"],
                            "reservation_date": match["match_date"],
                            "start_time": match["match_time"],
                            "end_time": end_time.isoformat(),
                            "total_price": 0,  # Torneo no tiene costo adicional
                            "pay_total": 0,
                            "club_commission": 0,
                            "player_commission": 0,
                            "is_tournament": True,
                            "tournament_id": tournament_id
                        }
                        
                        supabase.from_("reservations").insert(reservation_data).execute()
                        
                    except Exception as reservation_error:
                        print(f"Warning: No se pudo crear reserva para match {match.get('id', 'unknown')}: {reservation_error}")
        
        # Actualizar estado del torneo a cerrado
        supabase.from_("tournaments").update({"status": "closed"}).eq("id", tournament_id).execute()
        
        return {
            "message": f"Se guardaron {len(saved_matches)} partidos exitosamente.",
            "matches_saved": len(saved_matches),
            "tournament_closed": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar los partidos: {str(e)}")