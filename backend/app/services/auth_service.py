import gotrue
from app.db.connection import supabase
from fastapi import HTTPException
from app.core.security import create_access_token

def authenticate_user(email: str, password: str):
    try:
        # Verifica las credenciales con Supabase
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # Asegúrate de que la respuesta contiene el atributo 'user'
        if response.user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_data = response.user  # 'user' es un objeto, no un diccionario
        user_id = user_data.id
        user_email = user_data.email

        if not user_id or not user_email:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Crear el token JWT
        token = create_access_token({"sub": user_id, "email": user_email})

        return {"access_token": token, "token_type": "bearer"}
    
    except gotrue.errors.AuthApiError as e:
        # Manejo de error específico de Supabase
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    except Exception as e:
        # Manejo de cualquier otro error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")