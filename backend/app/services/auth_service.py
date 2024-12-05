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

        # Obtén el perfil del usuario de la tabla `profiles`
        profile_response = supabase.from_("profiles").select("user_type").eq("id", user_id).single().execute()

        if profile_response.data is None:  # Revisa si no hay datos en la respuesta
            raise HTTPException(status_code=404, detail="User profile not found")

        user_type = profile_response.data["user_type"]
        print(user_type)

        # Crea un token JWT
        token = create_access_token({"sub": user_id, "email": user_data.email, "user_type": user_type})
        return {"access_token": token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    except gotrue.errors.AuthApiError as e:
        # Manejo de error específico de Supabase
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    except Exception as e:
        # Manejo de cualquier otro error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")