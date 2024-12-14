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
def save_schedules(data: dict, current_user: dict = Depends(get_current_user)):
    """
    Guarda los horarios del club, generales o específicos por cancha.
    """
    try:
        club_id = current_user["club_id"]
        apply_to_all = data.get("apply_to_all", True)
        schedules = data.get("schedules", [])

        # Si se selecciona aplicar a todas las canchas
        if apply_to_all:
            # Elimina horarios específicos existentes
            supabase.from_("schedules").delete().eq("club_id", club_id).neq("court_id", None).execute()

            # Elimina horarios generales previos
            supabase.from_("schedules").delete().eq("club_id", club_id).eq("court_id", None).execute()

            # Inserta nuevos horarios generales
            for schedule in schedules:
                supabase.from_("schedules").insert({
                    "club_id": club_id,
                    "court_id": None,
                    "day_of_week": schedule["day_of_week"],
                    "opening_time": schedule["opening_time"],
                    "closing_time": schedule["closing_time"],
                }).execute()
        else:
            # Elimina horarios generales
            supabase.from_("schedules").delete().eq("club_id", club_id).eq("court_id", None).execute()

            # Inserta o actualiza horarios específicos
            for schedule in schedules:
                court_id = schedule.get("court_id")
                existing_schedule = supabase.from_("schedules").select("*").match({
                    "club_id": club_id,
                    "court_id": court_id,
                    "day_of_week": schedule["day_of_week"],
                }).execute()

                if existing_schedule.data:
                    # Actualizar horario
                    supabase.from_("schedules").update({
                        "opening_time": schedule["opening_time"],
                        "closing_time": schedule["closing_time"],
                    }).eq("id", existing_schedule.data[0]["id"]).execute()
                else:
                    # Crear horario
                    supabase.from_("schedules").insert({
                        "club_id": club_id,
                        "court_id": court_id,
                        "day_of_week": schedule["day_of_week"],
                        "opening_time": schedule["opening_time"],
                        "closing_time": schedule["closing_time"],
                    }).execute()

        return {"message": "Horarios guardados exitosamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar horarios: {str(e)}")


@router.get("/schedules")
def get_club_schedules(current_user: dict = Depends(get_current_user)):
    try:
        club_id = current_user["club_id"]
        response = supabase.table("schedules").select("*").eq("club_id", club_id).execute()

        if response.data is None or len(response.data) == 0:
            print("No schedules found for club_id:", club_id)
            return {"message": "No schedules found", "data": []}

        print("Schedules found:", response.data)
        return {"data": response.data}

    except Exception as e:
        print(f"Error fetching schedules: {str(e)}")  # Log detallado
        raise HTTPException(status_code=500, detail=f"Error fetching schedules: {str(e)}")

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