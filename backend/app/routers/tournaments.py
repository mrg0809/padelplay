from fastapi import APIRouter, HTTPException, Depends
from app.db.connection import supabase
from app.core.security import get_current_user
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

@router.post("/{tournament_id}/teams")
async def register_team(tournament_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    """
    Registrar una pareja en un torneo y enviar invitación si el segundo jugador no está registrado.
    """
    try:
        # Obtener el ID del jugador actual (player1)
        player1_id = current_user["id"]

        # Validar si el torneo existe
        tournament_response = supabase.from_("tournaments").select("*").eq("id", tournament_id).execute()
        if not tournament_response.data:
            raise HTTPException(status_code=404, detail="Torneo no encontrado.")

        # Preparar datos para insertar en la tabla `tournament_teams`
        team_data = {
            "tournament_id": tournament_id,
            "player1_id": player1_id,
            "player2_email": data.get("player2_email"),
            "player2_id": data.get("player2_id"),
            "status": "pending" if not data.get("player2_id") else "confirmed"
        }

        # Insertar el equipo en la base de datos
        response = supabase.from_("tournament_teams").insert(team_data).execute()
        if response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        # Enviar invitación si `player2_email` está presente pero no registrado
        if data.get("player2_email") and not data.get("player2_id"):
            send_invitation_email(data["player2_email"], tournament_response.data[0]["name"])

        return {"message": "Equipo registrado exitosamente.", "data": response.data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar el equipo: {str(e)}")


def send_invitation_email(recipient_email: str, tournament_name: str):
    """
    Enviar un correo de invitación para registrarse en el torneo.
    """
    try:
        # Configuración del correo
        sender_email = "info@padelplay.mx"
        sender_password = "RMs1stem@s"
        smtp_server = "smtp.zoho.com"
        smtp_port = 587

        subject = f"Te han invitado a un torneo: {tournament_name}"
        body = f"""
        Hola,

        Has sido invitado a participar en el torneo "{tournament_name}".
        Para unirte, regístrate en nuestra plataforma a través del siguiente enlace:

        [ENLACE A TU SITIO DE REGISTRO]

        ¡Esperamos verte pronto!

        Saludos,
        El equipo de PadelPlay.
        """

        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Conexión al servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print(f"Correo enviado exitosamente a {recipient_email}")

    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se pudo enviar la invitación a {recipient_email}.")
    
    

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