from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.db.connection import supabase
from app.core.security import get_current_user
import uuid
from app.core.config import settings

router = APIRouter(prefix="/clubs", tags=["Clubs"])

@router.get("/")
def get_club_info(current_user=Depends(get_current_user)):
    try:
        # Verifica que el usuario sea un club
        if current_user["user_type"] != "club":
            raise HTTPException(status_code=403, detail="Access denied")

        # Obtén la información del club
        response = supabase.table("clubs").select("*").eq("id", current_user["club_id"]).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Club not found")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/")
def update_club_info(updates: dict, current_user=Depends(get_current_user)):
    try:
        # Verifica que el usuario sea un club
        if current_user["user_type"] != "club":
            raise HTTPException(status_code=403, detail="Access denied")

        # Actualiza la información del club
        response = supabase.table("clubs").update(updates).eq("id", current_user["club_id"]).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update club information")

        return {"message": "Club information updated successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedules")
def add_schedule(schedule: dict, current_user=Depends(get_current_user)):
    try:
        # Verifica que el usuario sea un club
        if current_user["user_type"] != "club":
            raise HTTPException(status_code=403, detail="Access denied")

        # Crea un horario
        response = supabase.table("schedules").insert(schedule).execute()

        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to add schedule")

        return {"message": "Schedule added successfully", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schedules")
def get_schedules(current_user=Depends(get_current_user)):
    try:
        response = supabase.table("schedules").select("*").eq("court_id", current_user["club_id"]).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Schedules not found")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-logo")
def upload_logo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        # Ruta del archivo en el bucket
        bucket_name = "club-logos"
        club_id = current_user["club_id"]
        file_name = f"{club_id}/{uuid()}.{file.filename.split('.')[-1]}"
        
        # Verifica si ya existe un archivo en la carpeta del club
        existing_files = supabase.storage.from_(bucket_name).list(path=club_id)
        for existing_file in existing_files:
            supabase.storage.from_(bucket_name).remove([f"{club_id}/{existing_file['name']}"])

        # Subir el nuevo archivo
        response = supabase.storage.from_(bucket_name).upload(file_name, file.file)
        if not response:
            raise HTTPException(status_code=500, detail="Error al subir el logo")
        
        # Generar la URL del archivo subido
        logo_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"
        return {"logo_url": logo_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")