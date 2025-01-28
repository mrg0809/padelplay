from fastapi import APIRouter, HTTPException, Depends, status
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
def get_notifications(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    response = supabase.from_("notifications").select("*").eq("user_id", user_id).execute()
    notifications = handle_supabase_response(response)
    return {"data": notifications}

@router.post("/")
def create_notification(notification: dict):
    response = supabase.from_("notifications").insert(notification).execute()
    created_notification = handle_supabase_response(response)
    return {"message": "Notification created successfully", "data": created_notification}

@router.put("/{notification_id}/read")
def mark_notification_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    response = supabase.from_("notifications").update({"is_read": True}).eq("id", notification_id).eq("user_id", user_id).execute()
    updated_notification = handle_supabase_response(response)
    return {"message": "Notification marked as read", "data": updated_notification}

@router.delete("/{notification_id}")
def delete_notification(notification_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    response = supabase.table("notifications").delete().eq("id", notification_id).eq("user_id", user_id).execute()
    
    # Verifica si no hubo errores y si se borró al menos una fila
    if response.data:
        return {"message": "Notification deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you do not have permission to delete it"
        )