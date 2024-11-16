from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = "https://ytfwprdrnvgujxdmvvnr.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl0ZndwcmRybnZndWp4ZG12dm5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE3MDkzOTAsImV4cCI6MjA0NzI4NTM5MH0.fwaLYvcufyShNhg0fprZekQr4oeL02VceSVB5FAm0rw"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
