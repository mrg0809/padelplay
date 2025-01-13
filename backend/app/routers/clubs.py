from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.db.connection import supabase
from app.core.security import get_current_user
import uuid
from app.core.config import settings

router = APIRouter()

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

        if apply_to_all:
            # Obtener todas las canchas del club
            courts_response = supabase.from_("courts").select("id").eq("club_id", club_id).execute()
            courts = courts_response.data if courts_response.data else []

            if not courts:
                raise HTTPException(status_code=400, detail="No hay canchas disponibles para este club.")

            # Eliminar horarios específicos existentes
            delete_response = supabase.rpc("delete_schedules_not_null", {"p_club_id": club_id}).execute()
            print(f"Respuesta de eliminación de horarios específicos: {delete_response}")  # Log de eliminación

            # Inserta horarios para cada cancha
            for court in courts:
                for schedule in schedules:
                    insert_response = supabase.from_("schedules").insert({
                        "club_id": club_id,
                        "court_id": court["id"],
                        "day_of_week": schedule["day_of_week"],
                        "opening_time": schedule["opening_time"],
                        "closing_time": schedule["closing_time"],
                    }).execute()

        else:
            # Eliminar horarios generales previos para la cancha seleccionada
            selected_court_id = data.get("court_id")
            if not selected_court_id:
                raise HTTPException(status_code=400, detail="Court ID es obligatorio para aplicar cambios individuales.")

            delete_response = supabase.from_("schedules").delete().eq("club_id", club_id).eq("court_id", selected_court_id).execute()
            print(f"Respuesta de eliminación de horarios para cancha {selected_court_id}: {delete_response}")

            # Inserta o actualiza horarios para la cancha seleccionada
            for schedule in schedules:
                insert_response = supabase.from_("schedules").insert({
                    "club_id": club_id,
                    "court_id": selected_court_id,
                    "day_of_week": schedule["day_of_week"],
                    "opening_time": schedule["opening_time"],
                    "closing_time": schedule["closing_time"],
                }).execute()
                print(f"Insertando horario para cancha {selected_court_id}: {insert_response}")

        return {"message": "Horarios guardados exitosamente."}

    except Exception as e:
        print(f"Error en save_schedules: {e}")  # Log detallado del error
        raise HTTPException(status_code=500, detail=f"Error al guardar horarios: {str(e)}")






@router.get("/schedules")
def get_club_schedules(current_user: dict = Depends(get_current_user)):
    try:
        club_id = current_user["club_id"]
        response = supabase.table("schedules").select("*").eq("club_id", club_id).execute()

        if response.data is None or len(response.data) == 0:
            return {"message": "No schedules found", "data": []}

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
    


@router.put("/schedules")
def update_schedules(data: dict, current_user: dict = Depends(get_current_user)):
    """
    Actualiza los horarios del club, manejando días cerrados (NULL para opening_time y closing_time).
    """
    try:
        # Depuración: Log de los datos recibidos
        print(f"Datos recibidos: {data}")

        club_id = current_user["club_id"]
        schedules = data.get("schedules", [])
        selected_court = data.get("court_id")

        # Validar que se haya enviado el court_id
        if not selected_court or not isinstance(selected_court, dict) or "id" not in selected_court:
            raise HTTPException(status_code=400, detail="Court ID es obligatorio y debe ser un UUID válido.")

        selected_court_id = selected_court["id"]

        # Validar que schedules no esté vacío
        if not schedules or not isinstance(schedules, list):
            raise HTTPException(status_code=400, detail="La lista de horarios es obligatoria.")

        # Validar y procesar cada horario
        for schedule in schedules:
            # Verificar que el horario tiene los datos requeridos
            if not isinstance(schedule, dict):
                raise HTTPException(status_code=400, detail="Cada horario debe ser un objeto JSON.")
            
            day_of_week = schedule.get("day_of_week")
            opening_time = schedule.get("opening_time")
            closing_time = schedule.get("closing_time")

            if day_of_week is None:
                raise HTTPException(status_code=400, detail="Falta el día de la semana en un horario.")

            # Verificar si ya existe un horario para el mismo día
            existing_schedule = (
                supabase.from_("schedules")
                .select("*")
                .eq("club_id", club_id)
                .eq("court_id", selected_court_id)
                .eq("day_of_week", day_of_week)
                .execute()
            )

            if existing_schedule.data:
                # Actualizar horario existente
                update_response = (
                    supabase.from_("schedules")
                    .update({
                        "opening_time": opening_time,
                        "closing_time": closing_time,
                    })
                    .eq("club_id", club_id)
                    .eq("court_id", selected_court_id)
                    .eq("day_of_week", day_of_week)
                    .execute()
                )
                if not update_response.data:
                    raise HTTPException(status_code=500, detail=f"Error al actualizar horario para el día {day_of_week}.")
            else:
                # Insertar nuevo horario
                insert_response = (
                    supabase.from_("schedules")
                    .insert({
                        "club_id": club_id,
                        "court_id": selected_court_id,
                        "day_of_week": day_of_week,
                        "opening_time": opening_time,
                        "closing_time": closing_time,
                    })
                    .execute()
                )
                if not insert_response.data:
                    raise HTTPException(status_code=500, detail=f"Error al insertar horario para el día {day_of_week}.")

        return {"message": "Horarios actualizados exitosamente."}

    except Exception as e:
        print(f"Error en update_schedules: {e}")  # Log detallado del error
        raise HTTPException(status_code=500, detail=f"Error al actualizar horarios: {str(e)}")


