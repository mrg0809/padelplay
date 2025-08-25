from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 360
    ESPIRAL_API_URL: str = os.getenv("ESPIRAL_API_URL")
    ESPIRAL_API_KEY: str = os.getenv("ESPIRAL_API_KEY")
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: str = os.getenv("STRIPE_PUBLIC_KEY")
    MERCADOPAGO_ACCESS_TOKEN: str = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    MERCADOPAGO_CURRENCY: str = os.getenv("MERCADOPAGO_CURRENCY", "ARS")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")



    class Config:
        env_file = ".env"

settings = Settings()
