from app.db.connection import supabase
from fastapi import HTTPException

async def create_user(email: str, password: str, user_type: str = "player"):
    # Verifica si el usuario ya existe
    response = supabase.auth.sign_up({"email": email, "password": password})
    if "error" in response:
        raise HTTPException(status_code=400, detail="User already exists")

    # Inserta datos adicionales en la tabla profiles
    user_id = response["user"]["id"]
    profile_data = {"id": user_id, "email": email, "user_type": user_type}
    supabase.table("profiles").insert(profile_data).execute()

    return {"message": "User registered successfully"}
