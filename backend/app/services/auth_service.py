import gotrue
from app.db.connection import supabase
from fastapi import HTTPException
from app.core.security import create_access_token

def authenticate_user(email: str, password: str):
    try:
        # Autenticación con Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if response.user is None:  # Revisa si no hay usuario
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_data = response.user  # Accede al objeto `user`
        user_id = user_data.id

        # Obtén el perfil del usuario de la tabla `profiles`, incluyendo `user_type` y `club_id`
        profile_response = supabase.from_("profiles") \
            .select("user_type, club_id") \
            .eq("id", user_id) \
            .single() \
            .execute()

        if profile_response.data is None:  # Revisa si no hay datos en la respuesta
            raise HTTPException(status_code=404, detail="User profile not found")

        user_type = profile_response.data["user_type"]
        club_id = profile_response.data.get("club_id")  # Puede ser None si no aplica

        # Crea un token JWT
        token = create_access_token({
            "sub": user_id,
            "email": user_data.email,
            "user_type": user_type,
            "club_id": club_id  # Incluye `club_id` en el token
        })
        return {"access_token": token, "token_type": "bearer"}

    except gotrue.errors.AuthApiError as e:
        raise HTTPException(status_code=401, detail="Authentication failed: Invalid credentials")
    
    except HTTPException:
        # Re-levantar excepciones esperadas
        raise
    
    except Exception as e:
        # Manejar cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")