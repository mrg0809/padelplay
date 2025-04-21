from fastapi import HTTPException
from app.db.connection import supabase


def create_notification(user_id: str, title: str, message: str, route: str = None):
    """
    Crea una notificación para un usuario.

    Args:
        user_id (str): ID del usuario al que se enviará la notificación.
        title (str): Título de la notificación.
        message (str): Mensaje de la notificación.
        route (str, optional): Ruta a la caul enlazar.
    """
    notification = {
        "user_id": user_id,
        "title": title,
        "message": message,
        "route": route,
    }
    response = supabase.table("notifications").insert(notification).execute()

    if not response:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la notificación: {response.error}",
        )