from app.db.connection import supabase
from fastapi import Depends, HTTPException
from datetime import date

#CREACION DE USUARIO PLAYER
async def create_user(full_name: str, email: str, password: str):
    try:
        # Crear un nuevo usuario en Supabase
        response = supabase.auth.sign_up({"full_name": full_name, "email": email, "password": password})

        if response.user is None:
            raise HTTPException(status_code=400, detail="User creation failed")

        user_id = response.user.id  # ID del usuario creado

        # Insertar datos adicionales en la tabla 'profiles'
        supabase.table("profiles").insert(
            {
                "id": user_id,         # ID del usuario
                "full_name": full_name,  # Nombre completo del usuario
                "user_type": "player",  # Por defecto 'player'
                "created_by": user_id,  # El propio usuario es el creador inicial
            }
        ).execute()

        # Insertar datos iniciales en la tabla 'players'
        player_data = {
            "user_id": user_id,
            "first_name": full_name.split()[0] if full_name.split() else None,
            "last_name": full_name.split()[1] if len(full_name.split()) > 1 else None,
            "birth_date": date(1900, 1, 1).isoformat(),
            "category": "sexta",
        }
        supabase.table("players").insert([player_data]).execute()

        return {"message": "User created successfully", "user_id": user_id}
    except Exception as e:
        # Manejo de errores
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


'''
#CREACION USUARIO ESPECIALES
async def create_special_user(
    email: str, password: str, full_name: str, user_type: str, created_by: str = Depends(verify_token)
):
    # Verificar permisos
    if created_by["user_type"] not in ["superuser", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to create this user type")

    if created_by["user_type"] == "admin" and user_type not in ["club"]:
        raise HTTPException(status_code=403, detail="Admins can only create club users")

    try:
        response = supabase.auth.sign_up({"email": email, "password": password})

        if response.user is None:
            raise HTTPException(status_code=400, detail="User creation failed")

        user_id = response.user.id

        # Insertar en profiles
        supabase.table("profiles").insert(
            {
                "id": user_id,
                "full_name": full_name,
                "user_type": user_type,
                "created_by": created_by["id"],  # ID del creador
            }
        ).execute()

        return {"message": f"User with role {user_type} created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
'''