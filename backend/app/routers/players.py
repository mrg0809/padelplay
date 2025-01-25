from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.core.security import get_current_user
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response
import uuid
from app.core.config import settings

router = APIRouter()

class PlayerInfo(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    category: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    preferred_hand: Optional[str] = None
    position: Optional[str] = None

@router.get("/", response_model=PlayerInfo)
def get_player_info(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    response = supabase.from_("players").select("*").eq("user_id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Player information not found")

    return response.data[0]

@router.put("/")
def update_player_info(data: PlayerInfo, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]

    # Convertir birth_date a string si está presente
    update_data = data.dict()
    if "birth_date" in update_data and update_data["birth_date"] is not None:
        update_data["birth_date"] = update_data["birth_date"].isoformat()

    # Realizar la actualización en Supabase
    response = supabase.from_("players").update(update_data).eq("user_id", user_id).execute()
    
    # Manejar la respuesta usando handle_supabase_response
    try:
        updated_data = handle_supabase_response(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating player info: {str(e)}")

    return {"message": "Player info updated successfully", "data": updated_data}


@router.post("/upload-photo")
def upload_photo(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Solo se permiten archivos de imagen")

        # Ruta del archivo en el bucket
        bucket_name = "club-logos"
        user_id = current_user["id"]
        file_extension = file.filename.split(".")[-1]
        file_name = f"playersphotos/{user_id}/{uuid.uuid4()}.{file_extension}"

        file_content = file.file.read()

        # Eliminar fotos existentes
        existing_files = supabase.storage.from_(bucket_name).list(path=f"playersphotos/{user_id}")
        if existing_files and "data" in existing_files:
            for existing_file in existing_files["data"]:
                supabase.storage.from_(bucket_name).remove([f"{user_id}/{existing_file['name']}"])

        # Subir el nuevo archivo
        response = supabase.storage.from_(bucket_name).upload(
            file_name,
            file_content,
            {"content-type": file.content_type}
            )
        if not response:
            raise HTTPException(status_code=500, detail="Error al subir la foto")

        # Generar la URL de acceso público
        photo_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_name}"

        #Actualizar campo photo id en supabase
        data = supabase.table('players').update({'photo_url': photo_url}).eq('user_id', current_user['id']).execute()

        if not data:
            raise HTTPException(status_code=500, detail=f"Error al actualizar la foto del jugador: {data.error}")

        return {"success": True, "photo_url": photo_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la solicitud: {str(e)}")